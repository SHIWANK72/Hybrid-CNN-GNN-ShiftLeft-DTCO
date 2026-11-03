"""Local laboratory inference API. Start through `python -m hybrid_dtco.lab serve`."""
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .predictor import LabPredictor


class PredictionRequest(BaseModel):
    graph: Dict[str, Any]
    utilization_percent: float = Field(gt=0, lt=100)
    clock_period_ns: float = Field(gt=0, le=10000)


def create_app(checkpoint):
    predictor = LabPredictor(checkpoint)
    app = FastAPI(title="DTCO laboratory predictor", version="0.1.0")

    @app.get("/health")
    def health():
        return {
            "status": "ready",
            "scope": "laboratory prototype",
            "checkpoint_loaded": True,
        }

    @app.post("/predict")
    def predict(request: PredictionRequest):
        if (
            len(request.graph.get("nodes", [])) > 10000
            or len(request.graph.get("nets", [])) > 50000
        ):
            raise HTTPException(
                status_code=413, detail="Input exceeds laboratory operating limits"
            )
        try:
            return predictor.predict(
                request.graph, request.utilization_percent, request.clock_period_ns
            )
        except (ValueError, KeyError, TypeError, IndexError) as error:
            raise HTTPException(
                status_code=422, detail=f"Invalid early graph: {error}"
            ) from error

    return app
