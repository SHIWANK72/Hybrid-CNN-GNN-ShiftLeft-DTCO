"""Differentiable, batch-aware mean scatter and bilinear grid-to-node fusion."""

from typing import Optional, Tuple

import torch
from torch import nn
from torch.nn import functional as F


class ScatterFusionLayer(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, grid_size: Tuple[int, int]):
        super().__init__()
        if min(in_channels, out_channels, *grid_size) <= 0:
            raise ValueError("Channels and grid dimensions must be positive")
        self.grid_size = tuple(grid_size)
        self.project = nn.Linear(in_channels, out_channels)

    def forward(
        self,
        node_features: torch.Tensor,
        node_coordinates: torch.Tensor,
        spatial_tensor: Optional[torch.Tensor] = None,
        batch: Optional[torch.Tensor] = None,
    ):
        if node_features.ndim != 2 or node_features.shape[0] == 0:
            raise ValueError("Expected a nonempty [N, F] node tensor")
        if node_coordinates.shape != (node_features.shape[0], 2):
            raise ValueError("Coordinates must have shape [N, 2]")
        if (
            not torch.isfinite(node_features).all()
            or not torch.isfinite(node_coordinates).all()
        ):
            raise ValueError("Node features and positions must be finite")
        if ((node_coordinates < 0) | (node_coordinates > 1)).any():
            raise ValueError("Coordinates must be normalized to [0, 1]")
        if batch is None:
            batch = torch.zeros(
                len(node_features), device=node_features.device, dtype=torch.long
            )
        if (
            batch.shape != (len(node_features),)
            or batch.dtype != torch.long
            or (batch < 0).any()
        ):
            raise ValueError("Invalid batch assignments")
        b = int(batch.max().item()) + 1
        if not torch.equal(torch.unique(batch), torch.arange(b, device=batch.device)):
            raise ValueError("Batch identifiers must be contiguous from zero")
        height, width = self.grid_size
        x = (node_coordinates[:, 0] * width).long().clamp(max=width - 1)
        y = (node_coordinates[:, 1] * height).long().clamp(max=height - 1)
        indices = batch * height * width + y * width + x
        projected = self.project(node_features)
        flat = projected.new_zeros((b * height * width, projected.shape[1]))
        flat.index_add_(0, indices, projected)
        counts = projected.new_zeros((b * height * width, 1))
        counts.index_add_(0, indices, projected.new_ones((len(indices), 1)))
        grid = (
            (flat / counts.clamp_min(1)).view(b, height, width, -1).permute(0, 3, 1, 2)
        )
        if spatial_tensor is not None:
            if spatial_tensor.shape != grid.shape:
                raise ValueError("Spatial tensor shape does not match fusion grid")
            grid = grid + spatial_tensor
        # Preserve original node order even when nodes of different graphs interleave.
        result = projected.new_zeros(projected.shape)
        for graph in range(b):
            selected = batch == graph
            positions = node_coordinates[selected].mul(2).sub(1).view(1, -1, 1, 2)
            sample = F.grid_sample(
                grid[graph : graph + 1],
                positions,
                align_corners=False,
                padding_mode="border",
            )
            result[selected] = sample[0, :, :, 0].T
        return result, grid
