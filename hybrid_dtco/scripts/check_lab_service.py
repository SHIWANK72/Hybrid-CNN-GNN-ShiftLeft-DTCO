"""Exercise the trained checkpoint through real local HTTP and the public CLI."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib import error, request

import numpy as np
import torch

from hybrid_dtco.api.predictor import LabPredictor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / "service-check.json").exists():
        raise ValueError("Service evidence already exists; preserve the previous check")
    corpus = json.loads((root / "corpus.json").read_text())
    sample = next(
        s for s in corpus["samples"] if s["split"] == "test" and s["status"] == "passed"
    )
    graph_path = root / sample["id"] / "early-graph.json"
    graph = json.loads(graph_path.read_text())
    payload = {
        "graph": graph,
        "clock_period_ns": sample["clock_period_ns"],
        "utilization_percent": sample["utilization_percent"],
    }
    checkpoint = root / "training/model.pt"
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    log = (root / "api-server.log").open("w")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "hybrid_dtco.lab",
            "serve",
            "--checkpoint",
            str(checkpoint),
            "--port",
            str(port),
        ],
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 35
        health = None
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("API exited before ready; see api-server.log")
            try:
                with request.urlopen(base + "/health", timeout=1) as response:
                    health = json.load(response)
                break
            except (error.URLError, TimeoutError):
                time.sleep(0.1)
        if not health or not health["checkpoint_loaded"]:
            raise RuntimeError("API did not become ready")
        started = time.perf_counter()
        message = request.Request(
            base + "/predict",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(message, timeout=20) as response:
            prediction = json.load(response)
        seconds = time.perf_counter() - started
        torch.set_num_threads(2)
        direct = LabPredictor(checkpoint).predict(
            graph, sample["utilization_percent"], sample["clock_period_ns"]
        )
        np.testing.assert_allclose(
            prediction["predicted_global_route_utilization"],
            direct["predicted_global_route_utilization"],
            atol=1e-6,
            rtol=1e-5,
        )
        assert (
            abs(
                prediction["predicted_effective_delay_ns"]
                - direct["predicted_effective_delay_ns"]
            )
            < 1e-6
        )
        invalid = request.Request(
            base + "/predict",
            data=json.dumps({**payload, "graph": {}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            request.urlopen(invalid, timeout=10)
        except error.HTTPError as failure:
            if failure.code != 422:
                raise
        else:
            raise AssertionError("Invalid graph did not fail")
        cli_path = root / "cli-prediction.json"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "hybrid_dtco.lab",
                "predict",
                "--checkpoint",
                str(checkpoint),
                "--graph",
                str(graph_path),
                "--clock-period",
                str(sample["clock_period_ns"]),
                "--utilization",
                str(sample["utilization_percent"]),
                "--output",
                str(cli_path),
            ],
            check=True,
            timeout=30,
        )
        cli = json.loads(cli_path.read_text())
        np.testing.assert_allclose(
            cli["predicted_global_route_utilization"],
            prediction["predicted_global_route_utilization"],
            atol=1e-6,
            rtol=1e-5,
        )
        result = {
            "status": "passed",
            "sample_id": sample["id"],
            "real_http_health": True,
            "real_http_prediction_matches_direct_checkpoint": True,
            "invalid_input_status": 422,
            "cli_matches_http": True,
            "http_feature_and_inference_seconds": seconds,
            "scope": "Local-only lab service; latency excludes upstream EDA.",
        }
        (root / "service-check.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()


if __name__ == "__main__":
    main()
