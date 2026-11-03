"""Reproducible lab training with train-only scaling and validation selection."""
import copy
import hashlib
import json
from pathlib import Path
import random
import time

import numpy as np
import torch

from hybrid_dtco.data.lab_dataset import LabDataset
from hybrid_dtco.models.hybrid_core import HybridDTCOModel


def fit_preprocessing(training):
    def stats(values, dim):
        return {
            "mean": values.mean(dim=dim).tolist(),
            "std": values.std(dim=dim, unbiased=False).clamp_min(1e-3).tolist(),
        }

    return {
        "node": stats(torch.cat([s["x"] for s in training]), 0),
        "spatial": stats(torch.stack([s["spatial"] for s in training]), (0, 2, 3)),
        "global": stats(torch.stack([s["global_features"] for s in training]), 0),
        "timing": stats(torch.stack([s["delay"] for s in training]), 0),
        "fit_sample_ids": [s["id"] for s in training],
        "clip_standardized_features": 8.0,
    }


def model_inputs(sample, preprocessing):
    def standard(value, key, shape=None):
        stats = preprocessing[key]
        mean, std = value.new_tensor(stats["mean"]), value.new_tensor(stats["std"])
        if shape:
            mean, std = mean.view(shape), std.view(shape)
        return ((value - mean) / std).clamp(-8, 8)

    return {
        "x": standard(sample["x"], "node"),
        "pos": sample["pos"],
        "edge_index": sample["edge_index"],
        "spatial": standard(sample["spatial"], "spatial", (3, 1, 1)).unsqueeze(0),
        "global_features": standard(sample["global_features"], "global").unsqueeze(0),
    }


def loss_for(prediction, sample, preprocessing):
    mask = sample["mask"].unsqueeze(0)
    grid_loss = (
        (prediction["congestion"] - sample["target_grid"].unsqueeze(0))
        .square()[mask]
        .mean()
    )
    stats = preprocessing["timing"]
    timing = (sample["delay"] - stats["mean"]) / stats["std"]
    return grid_loss + 0.25 * (prediction["timing"][0] - timing).square()


def validate(model, samples, preprocessing):
    model.eval()
    with torch.no_grad():
        return float(
            np.mean(
                [
                    loss_for(
                        model(**model_inputs(s, preprocessing)), s, preprocessing
                    ).item()
                    for s in samples
                ]
            )
        )


def train_candidate(training, validation, preprocessing, hidden, seed, epochs, output):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    config = {
        "node_channels": 10,
        "spatial_channels": 3,
        "global_channels": 6,
        "hidden_channels": hidden,
        "grid_size": [16, 16],
    }
    model = HybridDTCOModel(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)
    initial = validate(model, training, preprocessing)
    best, best_epoch, state = float("inf"), -1, None
    history = []
    gradient_evidence = {}
    cached_inputs = [model_inputs(s, preprocessing) for s in training]
    started = time.monotonic()
    for epoch in range(epochs):
        model.train()
        order = torch.randperm(len(training)).tolist()
        total = 0.0
        for index in order:
            optimizer.zero_grad(set_to_none=True)
            prediction = model(**cached_inputs[index])
            loss = loss_for(prediction, training[index], preprocessing)
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite training loss")
            loss.backward()
            if epoch == 0:
                for name in (
                    "gnn_encoder",
                    "fusion_module",
                    "cnn_decoder",
                    "timing_head",
                ):
                    values = [
                        p.grad
                        for p in getattr(model, name).parameters()
                        if p.grad is not None
                    ]
                    gradient_evidence[name] = max(
                        gradient_evidence.get(name, 0),
                        sum(float(g.abs().sum()) for g in values),
                    )
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5)
            optimizer.step()
            total += float(loss.detach())
        if epoch % 10 == 0 or epoch == epochs - 1:
            score = validate(model, validation, preprocessing)
            history.append(
                {
                    "epoch": epoch,
                    "training_loss": total / len(training),
                    "validation_loss": score,
                }
            )
            if score < best:
                best, best_epoch = score, epoch
                state = copy.deepcopy(model.state_dict())
    model.load_state_dict(state)
    checkpoint = {
        "format_version": "0.1.0",
        "model_config": config,
        "state_dict": state,
        "preprocessing": preprocessing,
        "target_definition": {
            "grid": "aggregate global-route utilization",
            "timing": "effective delay ns = clock period - post-route worst setup slack",
        },
        "seed": seed,
        "selected_epoch": best_epoch,
    }
    torch.save(checkpoint, output)
    result = {
        "seed": seed,
        "hidden": hidden,
        "initial_training_loss": initial,
        "selected_training_loss": validate(model, training, preprocessing),
        "validation_loss": best,
        "selected_epoch": best_epoch,
        "branch_gradient_l1": gradient_evidence,
        "history": history,
        "elapsed_seconds": time.monotonic() - started,
    }
    return result


def train_lab(dataset_dir, output_dir, epochs=300):
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    training, validation = list(LabDataset(dataset_dir, "train")), list(
        LabDataset(dataset_dir, "validation")
    )
    if {s["family"] for s in training} & {s["family"] for s in validation}:
        raise ValueError("Family leakage between training and validation")
    preprocessing = fit_preprocessing(training)
    candidates = []
    for hidden, seed in [(16, 7), (24, 17), (32, 29)]:
        print(f"Training hidden={hidden}, seed={seed}", flush=True)
        path = output_dir / f"candidate-{hidden}-{seed}.pt"
        candidates.append(
            train_candidate(
                training, validation, preprocessing, hidden, seed, epochs, path
            )
        )
        print(f"Validation loss: {candidates[-1]['validation_loss']:.6g}", flush=True)
    selected = min(candidates, key=lambda r: r["validation_loss"])
    source = output_dir / f"candidate-{selected['hidden']}-{selected['seed']}.pt"
    import shutil

    shutil.copyfile(source, output_dir / "model.pt")
    report = {
        "selection_basis": "validation only; test data not loaded",
        "epochs_budget": epochs,
        "candidates": candidates,
        "selected": {k: v for k, v in selected.items() if k != "history"},
        "training_families": sorted({s["family"] for s in training}),
        "validation_families": sorted({s["family"] for s in validation}),
    }
    source_root = Path(__file__).resolve().parents[1]
    report["source_sha256"] = {
        str(p.relative_to(source_root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(source_root.rglob("*.py"))
    }
    report["dataset_index_sha256"] = hashlib.sha256(
        (Path(dataset_dir) / "dataset.json").read_bytes()
    ).hexdigest()
    report["deterministic_algorithms"] = True
    (output_dir / "training.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
