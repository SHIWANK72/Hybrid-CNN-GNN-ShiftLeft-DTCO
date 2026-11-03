"""Compact spatial encoder/decoder retaining the original raster resolution."""
from torch import nn
from torch.nn import functional as F


def block(inputs, outputs):
    return nn.Sequential(
        nn.Conv2d(inputs, outputs, 3, padding=1),
        nn.ReLU(),
        nn.Conv2d(outputs, outputs, 3, padding=1),
        nn.ReLU(),
    )


class SpatialUNet(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.encoder = block(in_channels, hidden_channels)
        self.bottleneck = block(hidden_channels, hidden_channels * 2)
        self.decoder = block(hidden_channels * 3, hidden_channels)

    def forward(self, raster):
        early = self.encoder(raster)
        coarse = self.bottleneck(F.avg_pool2d(early, 2))
        up = F.interpolate(
            coarse, size=early.shape[-2:], mode="bilinear", align_corners=False
        )
        import torch

        return self.decoder(torch.cat((early, up), dim=1))
