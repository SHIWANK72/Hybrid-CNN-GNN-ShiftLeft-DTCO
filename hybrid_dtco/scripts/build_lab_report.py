"""Assemble a candid engineering readiness assessment from completed evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import torch


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--tests", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    corpus = json.loads((root / "corpus.json").read_text())
    index = json.loads((root / "dataset/dataset.json").read_text())
    training = json.loads((root / "training/training.json").read_text())
    evaluation = json.loads((root / "evaluation/evaluation.json").read_text())
    service = json.loads((root / "service-check.json").read_text())
    accepted = [s for s in corpus["samples"] if s["status"] == "passed"]
    families = {s["family"] for s in accepted}
    splits = {
        split: {s["family"] for s in accepted if s["split"] == split}
        for split in ("train", "validation", "test")
    }
    verified = 0
    for sample in accepted:
        for relative, expected in sample["artifact_sha256"].items():
            if digest(root / sample["id"] / relative) != expected:
                raise ValueError(f"Changed EDA artifact: {sample['id']}/{relative}")
            verified += 1
    grid_values, delays = [], []
    for sample in index["samples"]:
        with np.load(
            root / "dataset" / f"{sample['id']}.npz", allow_pickle=False
        ) as arrays:
            grid_values.extend(arrays["target_grid"][arrays["mask"]].tolist())
            delays.append(float(arrays["delay"]))
    selected = training["selected"]
    metrics = evaluation["metrics"]
    import xml.etree.ElementTree as ET

    tests = ET.parse(args.tests).getroot()
    suites = list(tests.iter("testsuite"))
    test_count = sum(int(s.get("tests", "0")) for s in suites)
    test_failures = sum(
        int(s.get("failures", "0")) + int(s.get("errors", "0")) for s in suites
    )
    gates = {
        "six_original_design_families": len(families) >= 6,
        "disjoint_family_splits": not (
            splits["train"] & splits["validation"]
            or splits["train"] & splits["test"]
            or splits["validation"] & splits["test"]
        ),
        "nonconstant_real_spatial_labels": float(np.std(grid_values)) > 1e-4,
        "nonconstant_real_timing_labels": float(np.std(delays)) > 1e-4,
        "all_model_branches_receive_gradients": all(
            v > 0 and np.isfinite(v) for v in selected["branch_gradient_l1"].values()
        ),
        "training_loss_improved": selected["selected_training_loss"]
        < selected["initial_training_loss"],
        "fresh_checkpoint_reload_matches": all(
            s["checkpoint_reload_matches"] for s in evaluation["samples"]
        ),
        "trained_checkpoint_cli_and_real_http": service["status"] == "passed"
        and service["cli_matches_http"]
        and service["real_http_prediction_matches_direct_checkpoint"],
        "meaningful_tests_pass": test_count >= 15 and test_failures == 0,
        "beats_training_mean_timing_baseline": metrics["hybrid_delay_mae_ns"]
        < metrics["mean_baseline_delay_mae_ns"],
        "beats_training_mean_spatial_baseline": metrics["hybrid_grid_mae"]
        < metrics["mean_baseline_grid_mae"],
    }
    engineered = all(v for k, v in gates.items() if not k.startswith("beats_"))
    useful = (
        gates["beats_training_mean_timing_baseline"]
        and gates["beats_training_mean_spatial_baseline"]
    )
    project = Path(__file__).resolve().parents[1]
    source_files = [
        p
        for folder in ("src", "scripts", "tests", "examples")
        for p in (project / folder).rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix not in (".pyc", ".log")
    ]
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "system": "Restricted post-global-placement CNN-GNN laboratory prototype; one Sky130HD toolchain",
        "status": (
            "laboratory validation candidate"
            if engineered and useful
            else "proof of concept; validation gaps remain"
        ),
        "trl_assessment": (
            "Evidence supports review toward TRL4 for this restricted prototype; independent/institutional assessment remains pending."
            if engineered and useful
            else "Do not claim overall TRL4: one or more laboratory/performance gates remain unmet."
        ),
        "gates": gates,
        "passed_samples": len(accepted),
        "failed_samples": [s for s in corpus["samples"] if s["status"] == "failed"],
        "families": {k: sorted(v) for k, v in splits.items()},
        "verified_eda_artifact_hashes": verified,
        "test_count": test_count,
        "test_failures": test_failures,
        "held_out_metrics": metrics,
        "stronger_baseline_comparison": {
            "timing_beats_ridge": metrics["hybrid_delay_mae_ns"]
            < metrics["ridge_baseline_delay_mae_ns"],
            "spatial_beats_ridge": metrics["hybrid_grid_mae"]
            < metrics["ridge_baseline_grid_mae"],
        },
        "versions": {
            "python": platform.python_version(),
            "torch": str(torch.__version__),
        },
        "source_sha256": {
            str(p.relative_to(project)): digest(p) for p in sorted(source_files)
        },
        "limitations": evaluation["limitations"]
        + [
            "API prototype is local only, without production deployment qualification.",
            "No calibrated uncertainty, optimization-loop qualification, DFT or physical packaging.",
        ],
    }
    (root / "readiness.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Laboratory validation evidence — 3 November 2026",
        "",
        report["trl_assessment"],
        "",
        f"Successful EDA samples: {len(accepted)}; families: {len(families)}; tests: {test_count}, failures/errors: {test_failures}.",
        "",
        "| Gate | Result |",
        "|---|---|",
    ]
    lines += [
        f"| {name} | {'PASS' if passed else 'NOT MET'} |"
        for name, passed in gates.items()
    ]
    lines += ["", "## Held-out results", "", "| Metric | Value |", "|---|---|"]
    lines += [f"| {name} | {value:.6g} |" for name, value in metrics.items()]
    lines += ["", "## Failed EDA attempts", ""]
    failures = [s for s in corpus["samples"] if s["status"] == "failed"]
    if failures:
        lines += [f"- {s['id']} ({s['split']}): {s['error']}" for s in failures]
        lines += [
            "",
            "Failed attempts lack accepted final labels and are excluded. This limits the operating-envelope and evaluation claims.",
        ]
    else:
        lines += ["None in this run."]
    lines += ["", "## Limits", ""] + ["- " + limit for limit in report["limitations"]]
    (root / "READINESS.md").write_text("\n".join(lines) + "\n")
    print(report["trl_assessment"])
    print(json.dumps(gates, indent=2))


if __name__ == "__main__":
    main()
