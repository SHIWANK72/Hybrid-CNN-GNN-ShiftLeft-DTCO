"""Checkpoint and ASGI request tests; fixtures are synthetic unit-test inputs."""
import asyncio
import json

import numpy as np
import pytest
import torch

from hybrid_dtco.api.predictor import LabPredictor
from hybrid_dtco.api.server import create_app
from hybrid_dtco.data.lab_dataset import features
from hybrid_dtco.models.hybrid_core import HybridDTCOModel
from hybrid_dtco.train.trainer import fit_preprocessing
from .test_lab_dataset import small_graph


@pytest.fixture
def checkpoint(tmp_path):
    graph = small_graph()
    values = {k: torch.from_numpy(v) for k, v in features(graph, 40, 10).items()}
    values.update({"id": "synthetic-test", "delay": torch.tensor(3.0)})
    configuration = {"hidden_channels": 8, "grid_size": [16, 16]}
    model = HybridDTCOModel(configuration)
    path = tmp_path / "unit-test.pt"
    torch.save(
        {
            "format_version": "0.1.0",
            "model_config": configuration,
            "state_dict": model.state_dict(),
            "preprocessing": fit_preprocessing([values]),
        },
        path,
    )
    return path


def test_reloaded_checkpoint_reproduces_label_free_prediction(checkpoint):
    first = LabPredictor(checkpoint).predict(small_graph(), 40, 10)
    second = LabPredictor(checkpoint).predict(small_graph(), 40, 10)
    np.testing.assert_allclose(
        first["predicted_global_route_utilization"],
        second["predicted_global_route_utilization"],
        atol=1e-7,
    )
    assert first["predicted_effective_delay_ns"] == pytest.approx(
        second["predicted_effective_delay_ns"]
    )
    assert np.isfinite(first["predicted_global_route_utilization"]).all()
    assert first["predicted_wns_ns"] <= 0


def request(app, method, path, body=None):
    messages = []
    data = json.dumps(body).encode() if body is not None else b""
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 1234),
        "server": ("127.0.0.1", 8000),
    }

    async def run():
        async def receive():
            return {"type": "http.request", "body": data, "more_body": False}

        async def send(message):
            messages.append(message)

        await app(scope, receive, send)

    asyncio.run(run())
    status = next(m["status"] for m in messages if m["type"] == "http.response.start")
    result = b"".join(
        m.get("body", b"") for m in messages if m["type"] == "http.response.body"
    )
    return status, json.loads(result)


def test_api_serves_prediction_and_rejects_missing_graph_fields(checkpoint):
    app = create_app(checkpoint)
    status, body = request(app, "GET", "/health")
    assert status == 200 and body["checkpoint_loaded"]
    status, body = request(
        app,
        "POST",
        "/predict",
        {"graph": small_graph(), "utilization_percent": 40, "clock_period_ns": 10},
    )
    assert status == 200 and len(body["predicted_global_route_utilization"]) == 16
    status, _ = request(
        app,
        "POST",
        "/predict",
        {"graph": {}, "utilization_percent": 40, "clock_period_ns": 10},
    )
    assert status == 422
    status, _ = request(
        app,
        "POST",
        "/predict",
        {"graph": small_graph(), "utilization_percent": 120, "clock_period_ns": 10},
    )
    assert status == 422


def test_wrong_checkpoint_format_is_rejected(tmp_path):
    path = tmp_path / "wrong.pt"
    torch.save({"format_version": "wrong"}, path)
    with pytest.raises(ValueError, match="Unsupported"):
        LabPredictor(path)
