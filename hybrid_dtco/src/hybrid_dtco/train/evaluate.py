"""One locked held-out evaluation; baseline parameters come only from training."""
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from hybrid_dtco.api.predictor import LabPredictor
from hybrid_dtco.data.lab_dataset import LabDataset
from hybrid_dtco.train.trainer import model_inputs


def ridge(x, y, strength=1.0):
    x = np.column_stack([np.ones(len(x)), x])
    penalty = np.eye(x.shape[1]) * strength
    penalty[0, 0] = 0
    return np.linalg.solve(x.T @ x + penalty, x.T @ y)


def evaluate_lab(dataset_dir, checkpoint, output_dir):
    torch.set_num_threads(2)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    training, test = list(LabDataset(dataset_dir, "train")), list(
        LabDataset(dataset_dir, "test")
    )
    validation = list(LabDataset(dataset_dir, "validation"))
    train_families = {s["family"] for s in training}
    test_families = {s["family"] for s in test}
    if train_families & test_families or test_families & {
        s["family"] for s in validation
    }:
        raise ValueError("Family overlap in held-out evaluation")
    predictor = LabPredictor(checkpoint)
    if set(predictor.preprocessing["fit_sample_ids"]) != {s["id"] for s in training}:
        raise ValueError("Preprocessing was not fit exclusively on this training split")
    mean_delay = np.mean([float(s["delay"]) for s in training])
    masks = np.stack([s["mask"].numpy() for s in training])
    grids = np.stack([s["target_grid"].numpy() for s in training])
    mean_grid = (grids * masks).sum(axis=0) / masks.sum(axis=0).clip(min=1)
    normalized_training = [model_inputs(s, predictor.preprocessing) for s in training]
    timing_x = np.stack([s["global_features"][0].numpy() for s in normalized_training])
    timing_weights = ridge(timing_x, np.array([float(s["delay"]) for s in training]))
    grid_x = np.concatenate(
        [
            s["spatial"][0].numpy().reshape(3, -1).T[m["mask"].numpy().ravel()]
            for s, m in zip(normalized_training, training)
        ]
    )
    grid_y = np.concatenate(
        [s["target_grid"].numpy()[s["mask"].numpy()] for s in training]
    )
    grid_weights = ridge(grid_x, grid_y)
    rows = []
    for sample in test:
        prepared = model_inputs(sample, predictor.preprocessing)
        started = time.perf_counter()
        with torch.no_grad():
            raw = predictor.model(**prepared)
        seconds = time.perf_counter() - started
        stats = predictor.preprocessing["timing"]
        delay = float(raw["timing"][0]) * stats["std"] + stats["mean"]
        grid = raw["congestion"][0].numpy()
        # A separate fresh checkpoint instance must reproduce outputs.
        reloaded = LabPredictor(checkpoint)
        with torch.no_grad():
            again = reloaded.model(**prepared)
        if not torch.allclose(
            raw["congestion"], again["congestion"], atol=1e-7, rtol=1e-6
        ) or not torch.allclose(raw["timing"], again["timing"], atol=1e-7, rtol=1e-6):
            raise ValueError("Checkpoint reload did not reproduce inference")
        features = prepared["spatial"][0].numpy().reshape(3, -1).T
        ridge_grid = np.maximum(
            0, np.column_stack([np.ones(len(features)), features]) @ grid_weights
        ).reshape(grid.shape)
        ridge_delay = float(
            np.r_[1, prepared["global_features"][0].numpy()] @ timing_weights
        )
        target_grid, mask = sample["target_grid"].numpy(), sample["mask"].numpy()
        truth_delay = float(sample["delay"])
        if not np.isfinite(grid).all() or not np.isfinite(delay):
            raise ValueError("Nonfinite held-out prediction")
        row = {
            "id": sample["id"],
            "family": sample["family"],
            "truth_effective_delay_ns": truth_delay,
            "prediction_effective_delay_ns": delay,
            "truth_worst_setup_slack_ns": float(sample["clock_period"]) - truth_delay,
            "prediction_worst_setup_slack_ns": float(sample["clock_period"]) - delay,
            "hybrid_delay_mae_ns": abs(delay - truth_delay),
            "mean_baseline_delay_mae_ns": abs(mean_delay - truth_delay),
            "ridge_baseline_delay_mae_ns": abs(ridge_delay - truth_delay),
            "hybrid_grid_mae": float(np.abs(grid - target_grid)[mask].mean()),
            "mean_baseline_grid_mae": float(
                np.abs(mean_grid - target_grid)[mask].mean()
            ),
            "ridge_baseline_grid_mae": float(
                np.abs(ridge_grid - target_grid)[mask].mean()
            ),
            "tensor_inference_seconds": seconds,
            "checkpoint_reload_matches": True,
        }
        rows.append(row)
        np.savez_compressed(
            output_dir / f"{sample['id']}-predictions.npz",
            predicted_grid=grid,
            target_grid=target_grid,
            mask=mask,
        )
    metric_keys = [key for key in rows[0] if "mae" in key]
    metrics = {key: float(np.mean([r[key] for r in rows])) for key in metric_keys}
    by_family = {
        family: {
            key: float(np.mean([r[key] for r in rows if r["family"] == family]))
            for key in metric_keys
        }
        for family in sorted(test_families)
    }
    report = {
        "schema_version": "0.1.0",
        "checkpoint_sha256": hashlib.sha256(Path(checkpoint).read_bytes()).hexdigest(),
        "split_protocol": "All variants of a family remain in one split; candidate selection used validation only.",
        "training_families": sorted(train_families),
        "held_out_families": sorted(test_families),
        "held_out_samples": len(test),
        "metrics": metrics,
        "by_family": by_family,
        "samples": rows,
        "baseline_protocol": "Training mean spatial map/effective delay and fixed-strength ridge models fit only to training; spatial ridge uses early raster channels.",
        "limitations": [
            "Only two tiny held-out original-design families: not a generalization benchmark.",
            "Global-route utilization is a proxy, not overflow/DRC qualification.",
            "Reported latency excludes feature extraction and all required upstream EDA.",
            "No independent assessor or calibrated uncertainty.",
        ],
    }
    (output_dir / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
