"""Protect geometric registration and the early/late information boundary."""
import copy
import numpy as np
import pytest

from hybrid_dtco.data.lab_dataset import features, overlaps, routing_target


def small_graph():
    return {
        "feature_checkpoint": "global_placement",
        "core_bbox_um": [0, 0, 10, 10],
        "nodes": [
            {
                "id": 0,
                "name": "a",
                "cell_type": "buf",
                "x_um": 1,
                "y_um": 1,
                "width_um": 1,
                "height_um": 1,
            },
            {
                "id": 1,
                "name": "b",
                "cell_type": "dfxtp",
                "x_um": 8,
                "y_um": 8,
                "width_um": 1,
                "height_um": 1,
            },
        ],
        "nets": [
            {
                "name": "n",
                "pins": [
                    {"node": 0, "pin": "Y", "direction": "OUTPUT"},
                    {"node": 1, "pin": "D", "direction": "INPUT"},
                ],
                "ports": [],
            }
        ],
    }


def test_overlap_conserves_clipped_physical_area():
    values = list(overlaps([-1, 2, 6, 8], [0, 0, 10, 10], 16))
    assert sum(area for _, _, area in values) == pytest.approx(36)
    assert all(area > 0 and 0 <= r < 16 and 0 <= c < 16 for r, c, area in values)


def test_features_do_not_consult_downstream_labels():
    graph = small_graph()
    first = features(graph, 40, 10)
    changed = copy.deepcopy(graph)
    changed["labels"] = {"final_slack": -1000, "post_route_demand": [100] * 50}
    second = features(changed, 40, 10)
    for key in first:
        np.testing.assert_array_equal(first[key], second[key])
    assert first["x"].shape == (2, 10)
    assert first["spatial"].shape == (3, 16, 16)
    assert first["edge_index"].shape == (2, 2)


def test_constant_utilization_registered_to_core(tmp_path):
    rows = ["META\t1000\t0\t0\t10000\t10000", "X\t0\t5000", "Y\t0\t5000"]
    rows += [f"CELL\tmet1\t{x}\t{y}\t10\t5" for x in range(2) for y in range(2)]
    path = tmp_path / "routing.tsv"
    path.write_text("\n".join(rows))
    target, mask = routing_target(path, [2, 2, 8, 8], 16)
    assert mask.all()
    np.testing.assert_allclose(target, 0.5)
    path.write_text("\n".join(rows[:3]))
    with pytest.raises(ValueError, match="empty"):
        routing_target(path, [2, 2, 8, 8], 16)


def test_zero_capacity_is_masked_not_a_zero_risk_label(tmp_path):
    rows = [
        "META\t1000\t0\t0\t10000\t10000",
        "X\t0\t5000",
        "Y\t0\t5000",
        "CELL\tmet1\t0\t0\t10\t5",
        "CELL\tmet1\t1\t1\t0\t0",
    ]
    path = tmp_path / "routing.tsv"
    path.write_text("\n".join(rows))
    target, mask = routing_target(path, [0, 0, 10, 10], 16)
    assert mask[0, 0, 0]
    assert not mask[0, -1, -1]
    assert target[0, 0, 0] == pytest.approx(0.5)
