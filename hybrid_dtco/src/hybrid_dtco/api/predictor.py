"""Checkpoint inference with identical early-only feature construction."""
from pathlib import Path

import numpy as np
import torch

from hybrid_dtco.data.lab_dataset import features
from hybrid_dtco.models.hybrid_core import HybridDTCOModel
from hybrid_dtco.train.trainer import model_inputs


class LabPredictor:
    def __init__(self, checkpoint):
        self.path = Path(checkpoint)
        payload = torch.load(self.path, map_location="cpu", weights_only=True)
        if payload.get("format_version") != "0.1.0":
            raise ValueError("Unsupported checkpoint format")
        self.preprocessing = payload["preprocessing"]
        self.model = HybridDTCOModel(payload["model_config"])
        self.model.load_state_dict(payload["state_dict"])
        self.model.eval()
        self.grid_size = payload["model_config"]["grid_size"][0]

    def predict(self, graph, utilization_percent, clock_period_ns):
        arrays = features(graph, utilization_percent, clock_period_ns, self.grid_size)
        sample = {key: torch.from_numpy(value) for key, value in arrays.items()}
        with torch.no_grad():
            result = self.model(**model_inputs(sample, self.preprocessing))
        statistics = self.preprocessing["timing"]
        delay = float(result["timing"][0]) * statistics["std"] + statistics["mean"]
        grid = result["congestion"][0, 0].numpy()
        if not np.isfinite(grid).all() or not np.isfinite(delay):
            raise ValueError("Nonfinite prediction")
        ws = clock_period_ns - delay
        # The tiny pilot does not support a calibrated uncertainty interval.
        return {
            "schema_version": "0.1.0",
            "grid_geometry": {
                "core_bbox_um": graph["core_bbox_um"],
                "rows": self.grid_size,
                "columns": self.grid_size,
                "origin": "lower",
                "row_axis": "y",
                "column_axis": "x",
            },
            "predicted_global_route_utilization": grid.tolist(),
            "predicted_effective_delay_ns": delay,
            "predicted_worst_setup_slack_ns": ws,
            "predicted_wns_ns": min(ws, 0.0),
            "limits": "Laboratory prototype, tiny original-design corpus, Sky130HD typical corner only; no calibrated uncertainty or sign-off claim.",
        }
