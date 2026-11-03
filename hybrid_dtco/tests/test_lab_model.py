"""Numerical and integration checks for the actual trainable model components."""
import pytest
import torch

from hybrid_dtco.models.hybrid_core import HybridDTCOModel
from hybrid_dtco.models.scatter_fusion import ScatterFusionLayer


torch.set_num_threads(2)


def graph(count=5):
    return {
        "x": torch.randn(count, 10),
        "edge_index": torch.tensor(
            [[i for i in range(count - 1)], [i + 1 for i in range(count - 1)]],
            dtype=torch.long,
        ),
        "pos": torch.rand(count, 2),
        "spatial": torch.randn(1, 3, 16, 16),
        "global_features": torch.randn(1, 6),
    }


def test_collision_mean_and_grid_to_node_alignment():
    layer = ScatterFusionLayer(1, 1, (4, 4))
    with torch.no_grad():
        layer.project.weight.fill_(1)
        layer.project.bias.zero_()
    x = torch.tensor([[2.0], [4.0]], requires_grad=True)
    nodes, grid = layer(x, torch.tensor([[0.625, 0.625], [0.625, 0.625]]))
    assert grid[0, 0, 2, 2].item() == 3
    torch.testing.assert_close(nodes, torch.tensor([[3.0], [3.0]]))
    grid.sum().backward()
    torch.testing.assert_close(x.grad, torch.tensor([[0.5], [0.5]]))


def test_graph_spatial_and_fusion_receive_congestion_gradients():
    torch.manual_seed(7)
    model = HybridDTCOModel({"hidden_channels": 8})
    data = graph()
    predictions = model(**data)
    assert predictions["congestion"].shape == (1, 1, 16, 16)
    assert predictions["timing"].shape == (1,)
    predictions["congestion"].sum().backward()
    for name in ("gnn_encoder", "fusion_module", "cnn_decoder"):
        gradients = [
            p.grad for p in getattr(model, name).parameters() if p.grad is not None
        ]
        assert gradients and all(torch.isfinite(g).all() for g in gradients)
        assert sum(g.abs().sum() for g in gradients) > 0


def test_batch_has_no_graph_cross_contamination():
    torch.manual_seed(17)
    model = HybridDTCOModel({"hidden_channels": 8}).eval()
    first, second = graph(4), graph(6)
    with torch.no_grad():
        a, b = model(**first), model(**second)
        together = model(
            x=torch.cat([first["x"], second["x"]]),
            edge_index=torch.cat(
                [first["edge_index"], second["edge_index"] + 4], dim=1
            ),
            pos=torch.cat([first["pos"], second["pos"]]),
            batch=torch.tensor([0] * 4 + [1] * 6),
            spatial=torch.cat([first["spatial"], second["spatial"]]),
            global_features=torch.cat(
                [first["global_features"], second["global_features"]]
            ),
        )
    torch.testing.assert_close(
        together["congestion"],
        torch.cat([a["congestion"], b["congestion"]]),
        atol=1e-6,
        rtol=1e-5,
    )
    torch.testing.assert_close(
        together["timing"], torch.cat([a["timing"], b["timing"]]), atol=1e-6, rtol=1e-5
    )


def test_invalid_coordinates_and_indices_fail_explicitly():
    model = HybridDTCOModel({"hidden_channels": 8})
    data = graph()
    data["pos"][0, 0] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        model(**data)
    data = graph()
    data["edge_index"][0, 0] = 100
    with pytest.raises(ValueError, match="outside"):
        model(**data)
