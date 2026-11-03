"""Post-global-placement CNN–GNN laboratory predictor.

Outputs spatial global-route utilization and a normalized design-level timing
regression value. Checkpoint preprocessing supplies its physical-unit inverse.
DRC, foundry sign-off and pre-placement prediction are outside this model.
"""
from typing import Any, Dict

import torch
from torch import nn
from torch_geometric.nn import global_mean_pool

from .cnn_unet import SpatialUNet
from .gnn_cluster import GraphEncoder
from .scatter_fusion import ScatterFusionLayer


class HybridDTCOModel(nn.Module):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = dict(config)
        hidden = config.get("hidden_channels", 24)
        grid = tuple(config.get("grid_size", (16, 16)))
        self.node_channels = config.get("node_channels", 10)
        self.spatial_channels = config.get("spatial_channels", 3)
        self.global_channels = config.get("global_channels", 6)
        self.grid_size = grid
        self.gnn_encoder = GraphEncoder(self.node_channels, hidden)
        self.fusion_module = ScatterFusionLayer(hidden, hidden, grid)
        self.cnn_decoder = SpatialUNet(self.spatial_channels + hidden, hidden)
        self.congestion_head = nn.Conv2d(hidden, 1, 1)
        self.timing_head = nn.Sequential(
            nn.Linear(hidden * 2 + self.global_channels, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(
        self, x, edge_index, pos, batch=None, spatial=None, global_features=None
    ):
        if x.ndim != 2 or x.shape[1] != self.node_channels:
            raise ValueError("Wrong node feature dimensions")
        if (
            edge_index.ndim != 2
            or edge_index.shape[0] != 2
            or edge_index.dtype != torch.long
        ):
            raise ValueError("Edges must be a [2, E] integer tensor")
        if edge_index.numel() and (edge_index.min() < 0 or edge_index.max() >= len(x)):
            raise ValueError("Edge index outside node range")
        if batch is None:
            batch = torch.zeros(len(x), dtype=torch.long, device=x.device)
        if edge_index.numel() and not torch.equal(
            batch[edge_index[0]], batch[edge_index[1]]
        ):
            raise ValueError("Edges may not cross graph boundaries")
        encoded = self.gnn_encoder(x, edge_index)
        _, raster = self.fusion_module(encoded, pos, batch=batch)
        b = raster.shape[0]
        if spatial is None:
            spatial = x.new_zeros((b, self.spatial_channels, *self.grid_size))
        if spatial.shape != (b, self.spatial_channels, *self.grid_size):
            raise ValueError("Wrong spatial feature dimensions")
        if global_features is None:
            global_features = x.new_zeros((b, self.global_channels))
        if global_features.shape != (b, self.global_channels):
            raise ValueError("Wrong global feature dimensions")
        if (
            not torch.isfinite(spatial).all()
            or not torch.isfinite(global_features).all()
        ):
            raise ValueError("Features must be finite")
        decoded = self.cnn_decoder(torch.cat((spatial, raster), dim=1))
        timing_input = torch.cat(
            (
                global_mean_pool(encoded, batch),
                decoded.mean(dim=(2, 3)),
                global_features,
            ),
            dim=1,
        )
        return {
            "congestion": torch.nn.functional.softplus(self.congestion_head(decoded)),
            "timing": self.timing_head(timing_input).squeeze(-1),
        }
