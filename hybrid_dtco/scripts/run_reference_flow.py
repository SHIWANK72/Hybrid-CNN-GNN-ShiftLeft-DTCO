"""Run the pinned Sky130 GCD experiment and retain evidence outside the checkout."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


IMAGE = "dtco/orfs:reference-5849e1dde67b"
UPSTREAM_DIGEST = (
    "sha256:5849e1dde67ba70b36194cf90a172d6c0e4cb2cf5502d6e0dd7c1d251a6d4584"
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output == project or project in output.parents:
        parser.error("Keep experiment outputs outside the project checkout")
    # Refuse reused paths: stale artifacts cannot masquerade as a new run.
    output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    for key in (
        "DOCKER_HOST",
        "DOCKER_CONTEXT",
        "DOCKER_TLS",
        "DOCKER_TLS_VERIFY",
        "DOCKER_CERT_PATH",
    ):
        environment.pop(key, None)
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    details = json.loads(
        subprocess.check_output(docker + ["image", "inspect", IMAGE], env=environment)
    )[0]
    if (
        details["Config"].get("Labels", {}).get("org.dtco.upstream.digest")
        != UPSTREAM_DIGEST
    ):
        raise RuntimeError("Wrong toolchain source; run prepare_reference_toolchain.sh")
    manifest = {
        "schema_version": "0.1.0",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "image_id": details["Id"],
        "upstream_image_digest": UPSTREAM_DIGEST,
        "design": "gcd",
        "platform": "sky130hd",
        "clock_period_ns": 20.0,
        "threads": 2,
        "stages": {},
        "project_input_sha256": {
            str(path.relative_to(project)): digest(path)
            for path in [
                *sorted((project / "examples/gcd").glob("*")),
                project / "scripts/run_reference_flow.py",
                project / "scripts/check_gcd.py",
                project / "scripts/extract_reference_graph.py",
                project / "scripts/summarize_reference_run.py",
                project / "scripts/export_reference_graph.tcl.in",
            ]
            if path.is_file()
        },
    }
    manifest_path = output / "manifest.json"

    def save():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    def run(stage, command, extra_env=()):
        arguments = docker + [
            "run",
            "--rm",
            "--network=none",
            "--cpus=2",
            "--memory=8g",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--mount",
            f"type=bind,src={project},dst=/project,readonly",
            "--mount",
            f"type=bind,src={output},dst=/work",
            "--workdir",
            "/work",
        ]
        for item in extra_env:
            arguments += ["--env", item]
        arguments += [IMAGE, "bash", "-c", command]
        print(f"Starting {stage}; log: {output / (stage + '.log')}", flush=True)
        start = time.monotonic()
        with (output / f"{stage}.log").open("w") as log:
            result = subprocess.run(
                arguments, stdout=log, stderr=subprocess.STDOUT, env=environment
            )
        manifest["stages"][stage] = {
            "exit_code": result.returncode,
            "elapsed_seconds": time.monotonic() - start,
        }
        save()
        if result.returncode:
            raise RuntimeError(
                f"{stage} failed with exit {result.returncode}; see {output / (stage + '.log')}"
            )

    save()
    try:
        run(
            "functional",
            "python3 /project/scripts/check_gcd.py --yosys /OpenROAD-flow-scripts/tools/install/yosys/bin/yosys --rtl /project/examples/gcd/gcd.v --output /work/functional",
        )
        run(
            "flow",
            "source /OpenROAD-flow-scripts/env.sh && make -f /OpenROAD-flow-scripts/flow/Makefile FLOW_HOME=/OpenROAD-flow-scripts/flow WORK_HOME=/work DESIGN_CONFIG=/project/examples/gcd/config.mk NUM_CORES=2 finish",
        )
        run(
            "graph",
            "/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -exit -threads 2 /project/scripts/export_reference_graph.tcl.in && python3 /project/scripts/extract_reference_graph.py --input /work/early-graph.tsv --output /work/early-graph.json",
            (
                "DTCO_EARLY_ODB=/work/results/sky130hd/gcd/base/3_3_place_gp.odb",
                "DTCO_GRAPH_OUTPUT=/work/early-graph.tsv",
            ),
        )
        subprocess.run(
            [
                sys.executable,
                str(project / "scripts/summarize_reference_run.py"),
                "--run",
                str(output),
            ],
            check=True,
        )
        manifest["status"] = "passed"
    except Exception:
        manifest["status"] = "failed"
        raise
    finally:
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        manifest["artifact_sha256"] = {
            str(path.relative_to(output)): digest(path)
            for path in sorted(output.rglob("*"))
            if path.is_file() and path != manifest_path
        }
        save()
    print(f"Reference flow passed; evidence: {output}")


if __name__ == "__main__":
    main()
