"""Optional scientific evidence figures; requires NumPy and Matplotlib."""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/workspace/.cache/matplotlib")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root
    report = json.loads((root / "evaluation/evaluation.json").read_text())
    metrics = report["metrics"]
    figures = root / "figures"
    figures.mkdir(exist_ok=True)
    names = ["Training mean", "Ridge", "CNN–GNN"]
    colors = ["#81909e", "#b6c5d0", "#216b99"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), layout="constrained")
    axes[0].bar(
        names,
        [
            metrics[k]
            for k in (
                "mean_baseline_delay_mae_ns",
                "ridge_baseline_delay_mae_ns",
                "hybrid_delay_mae_ns",
            )
        ],
        color=colors,
    )
    axes[0].set(ylabel="Effective timing-delay MAE (ns)", title="Held-out timing")
    axes[1].bar(
        names,
        [
            metrics[k]
            for k in (
                "mean_baseline_grid_mae",
                "ridge_baseline_grid_mae",
                "hybrid_grid_mae",
            )
        ],
        color=colors,
    )
    axes[1].set(
        ylabel="Aggregate routing-utilization MAE",
        title="Held-out spatial routing load",
    )
    fig.suptitle(
        f"{report['held_out_samples']} samples from two held-out small RTL families — preliminary lab results",
        fontsize=10,
    )
    for suffix in ("png", "svg"):
        fig.savefig(figures / f"baseline-comparison.{suffix}", dpi=200)
    plt.close(fig)
    sample = report["samples"][0]["id"]
    with np.load(
        root / "evaluation" / f"{sample}-predictions.npz", allow_pickle=False
    ) as data:
        truth, prediction, mask = (
            data["target_grid"][0],
            data["predicted_grid"][0],
            data["mask"][0],
        )
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), layout="constrained")
    maximum = max(float(truth[mask].max()), float(prediction[mask].max()))
    for axis, values, title in zip(
        axes,
        [truth, prediction, abs(truth - prediction)],
        ["EDA reference", "CNN–GNN prediction", "Absolute error"],
    ):
        image = axis.imshow(
            np.ma.masked_where(~mask, values),
            origin="lower",
            extent=[0, 1, 0, 1],
            vmin=0,
            vmax=maximum if title != "Absolute error" else None,
            cmap="viridis" if title != "Absolute error" else "magma",
            interpolation="nearest",
        )
        axis.set(title=title, xlabel="Normalized core x", ylabel="Normalized core y")
        fig.colorbar(image, ax=axis, shrink=0.8)
    fig.suptitle(
        f"{sample}: global-route utilization proxy on registered 16×16 core grid"
    )
    for suffix in ("png", "svg"):
        fig.savefig(figures / f"spatial-prediction.{suffix}", dpi=200)
    plt.close(fig)
    histories = json.loads((root / "training/training.json").read_text())["candidates"]
    fig, axis = plt.subplots(figsize=(7, 3.8), layout="constrained")
    for candidate in histories:
        history = candidate["history"]
        axis.plot(
            [r["epoch"] for r in history],
            [r["validation_loss"] for r in history],
            label=f"hidden={candidate['hidden']}, seed={candidate['seed']}",
        )
    axis.set(
        xlabel="Epoch",
        ylabel="Validation objective",
        title="Candidate selection used validation only",
        yscale="log",
    )
    axis.legend()
    for suffix in ("png", "svg"):
        fig.savefig(figures / f"validation-curves.{suffix}", dpi=200)
    plt.close(fig)
    print(f"Figures written to {figures}; Matplotlib {matplotlib.__version__}")


if __name__ == "__main__":
    main()
