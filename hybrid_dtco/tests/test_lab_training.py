"""A synthetic, short optimizer/checkpoint integration check, not ML evidence."""
import math
import torch

from hybrid_dtco.api.predictor import LabPredictor
from hybrid_dtco.data.lab_dataset import features
from hybrid_dtco.train.trainer import fit_preprocessing, train_candidate
from .test_lab_dataset import small_graph


def test_training_saves_a_reloadable_checkpoint_without_validation_scaling(tmp_path):
    def sample(identifier, delay, utilization):
        arrays = features(small_graph(), utilization, 10)
        values = {k: torch.from_numpy(v) for k, v in arrays.items()}
        values.update(
            {
                "id": identifier,
                "family": identifier,
                "delay": torch.tensor(delay),
                "target_grid": torch.full((1, 16, 16), 0.4),
                "mask": torch.ones((1, 16, 16), dtype=torch.bool),
            }
        )
        return values

    training = [sample("train-a", 3.0, 30), sample("train-b", 4.0, 50)]
    validation = [sample("val", 8.0, 70)]
    preprocessing = fit_preprocessing(training)
    assert preprocessing["fit_sample_ids"] == ["train-a", "train-b"]
    assert preprocessing["timing"]["mean"] == 3.5
    path = tmp_path / "model.pt"
    report = train_candidate(
        training, validation, preprocessing, hidden=8, seed=7, epochs=2, output=path
    )
    assert report["selected_epoch"] in (0, 1)
    assert all(value > 0 for value in report["branch_gradient_l1"].values())
    prediction = LabPredictor(path).predict(small_graph(), 40, 10)
    assert math.isfinite(prediction["predicted_effective_delay_ns"])
