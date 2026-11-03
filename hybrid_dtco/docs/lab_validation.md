# Laboratory prototype and TRL evidence

Delivery deadline for the master's final product: **3 May 2027**. This lab
milestone targets integrated component validation, corresponding to evidence
needed for a restricted TRL 4 assessment. It does not qualify the entire
RTL-to-packaged-device vision.

## Implemented laboratory scope

The model consumes a netlist graph and three spatial channels from **global
placement**. A two-layer GraphSAGE encoder projects embeddings through a
batch-aware differentiable scatter mean into a small U-Net. The output heads
predict a 16×16 routing-utilization map and design-level timing regression.

The spatial target is area-weighted aggregate demand/capacity across routing
layers from the **global-routing** OpenDB grid. It is a routing-load proxy;
it is not overflow probability, DRC, lithography or manufacturing yield.
The timing target is effective delay = clock period − worst setup slack from
**post-route extracted** analysis. Inference converts that to worst setup
slack and WNS = min(slack, 0). Effective delay includes constraint effects and
must not be relabeled as an isolated path's physical propagation delay.

The model does not predict DRC or uncertainty. Its API and checkpoint make
that scope explicit. Closed-loop optimization remains a later milestone.

## Corpus and leakage controls

Six original Apache-2.0 RTL families are used: GCD, accumulator, FIFO, FIR,
ALU and priority arbiter. Each has three declared utilization/clock settings.
All variants of GCD/accumulator/FIFO are training; FIR is validation; ALU and
arbiter are held out. These small examples establish a laboratory protocol,
not a public benchmark or statistically strong generalization study.

The variants vary utilization and clock together, so their effects are
confounded; do not interpret this pilot as a causal design-space study.
The sources are implemented independently, but share ordinary RTL idioms and
technology cells; "family-held-out" does not prove complete structural novelty.

- Every accepted sample has actual EDA artifacts and hashes; failures remain
  recorded and excluded from training, never converted into zero labels.
- Features read only the early graph. Routed demand, final slack, extracted
  capacitance and final critical-path information are not feature inputs.
- Physical-only unconnected instances are omitted from the ML graph. Signal
  connectivity is expanded from drivers to sinks, then symmetrized for GNN use.
- Spatial input channels are cell-area density, pin-count density, and a
  cell-centre/RUDY-like net bounding-box estimate. Port geometry and exact pin
  shapes are not modeled in this initial feature schema.
- Physical box intersection registers inputs and later GCell labels to the
  same core coordinates. Capacity-free target cells are masked.
- All normalization statistics and baseline coefficients are fit on training
  samples only. Validation selects a candidate and epoch; held-out results
  are evaluated after selection.

## Reproduce the experiment

The cloud environment already has the Python development virtual environment.
The pinned EDA container is restored/prepared with the existing script.
A complete fresh laboratory run uses:

```sh
cd /workspace/Hybrid-CNN-GNN-ShiftLeft-DTCO/hybrid_dtco
bash scripts/run_lab_validation.sh /workspace/experiments/new-lab-run
```

This requires Docker socket/local IPC access, the existing ML virtual
environment, and package-registry access only if the EDA toolchain must be
restored. EDA containers themselves run offline with two CPUs/8 GiB memory.
Use a fresh output directory; existing evidence is not overwritten. The
wrapper removes only its own EDA container when it exits.

Individual ML stages are:

```sh
source /workspace/.venvs/dtco/bin/activate
python -m hybrid_dtco.lab pack --corpus /workspace/experiments/trl4-lab-20261103 --output /workspace/experiments/trl4-lab-20261103/dataset
python -m hybrid_dtco.lab train --dataset /workspace/experiments/trl4-lab-20261103/dataset --output /workspace/experiments/trl4-lab-20261103/training --epochs 300
python -m hybrid_dtco.lab evaluate --dataset /workspace/experiments/trl4-lab-20261103/dataset --checkpoint /workspace/experiments/trl4-lab-20261103/training/model.pt --output /workspace/experiments/trl4-lab-20261103/evaluation
```

Do not rerun selection after inspecting the held-out report and present that
same test set as untouched. Source/configuration changes require a new,
explicitly versioned experiment and an honest evaluation protocol.

## Demonstrate label-free inference

After training, supply an early graph, its declared utilization, and clock:

```sh
python -m hybrid_dtco.lab predict --checkpoint /workspace/experiments/trl4-lab-20261103/training/model.pt --graph /workspace/experiments/trl4-lab-20261103/alu-v0/early-graph.json --clock-period 20 --utilization 32 --output /workspace/experiments/trl4-lab-20261103/example-prediction.json
python -m hybrid_dtco.lab serve --checkpoint /workspace/experiments/trl4-lab-20261103/training/model.pt --port 8000
```

The local API provides `GET /health` and `POST /predict`. The request contains
`graph`, `clock_period_ns` and `utilization_percent`. Prediction needs no routed
layout or target labels. The CLI creates a new output file; the API has no
production deployment, authentication, workload isolation or public exposure
claim. Keep it local for this laboratory demonstration.

## Evidence and readiness

`corpus.json` records run identity, input hashes, splits, actual labels and
failed runs. `dataset/` contains safe NumPy tensor archives and a versioned
index. `training/training.json` records seeds, histories, source hashes,
train-only preprocessing and validation-based selection. The checkpoint has
weights plus its normalization/configuration. `evaluation/evaluation.json`
records individual held-out errors, family summaries and mean/ridge baselines.
`tests.xml`, `readiness.json` and `READINESS.md` assemble the engineering gates
and disclose gaps.

A better-than-mean result is only a preliminary usefulness check. Stronger
ridge comparisons are reported too; architecture superiority is not assumed.
With only two held-out families there is no reliable population confidence
interval or calibrated uncertainty claim. Tensor-only inference latency
excludes feature construction and required upstream EDA, so it is not an
end-to-end speedup measurement.

TRL assessment must name this restricted system and its operating conditions.
An institutional or independent assessor must review the evidence before any
formal certification claim. Passing unit tests alone does not establish TRL 4.

## Completed experiment — 3 November 2026

Evidence root: `/workspace/experiments/trl4-lab-20261103`.

- All **18/18** EDA configurations completed, including the dense ALU case
  that needed approximately eight minutes of detailed routing.
- Split: **9 training / 3 validation / 6 held-out samples**, with no family
  overlap. Normalization and baseline coefficients used training only.
- Three predeclared candidates trained for a 300-epoch budget each. Validation
  selected hidden size 32, seed 29, epoch 50. Training objective decreased
  from 0.32810 at initialization to 0.006918 for the selected checkpoint.
- The selected checkpoint had finite nonzero gradients in all model branches.
- All **16 tests passed**. A separate real local HTTP test verified health,
  trained-model predictions, invalid-input rejection, and agreement with CLI
  and direct-checkpoint inference. The temporary server was stopped afterward.
- All **2,199** recorded EDA artifact hashes were verified.

| Held-out measure, lower is better | Training mean | Ridge baseline | CNN–GNN |
|---|---:|---:|---:|
| Effective timing-delay MAE (ns) | 0.9235 | **0.3127** | 0.3822 |
| Aggregate routing-utilization MAE | 0.08700 | 0.09078 | **0.07038** |

The hybrid improves over both mean baselines and over spatial ridge, while
ridge remains the better overall timing predictor. These findings are retained;
there was no test-set-driven retuning. The spatial prediction captures broad
load patterns but smooths some local peaks, visible in the saved error map.
No calibrated hotspot probability or bound on unseen-design error is claimed.

The frozen engineering gates passed. The evidence supports a **TRL 4 candidate
assessment for this restricted laboratory predictor**, pending independent or
institutional review. It does not establish TRL 4 for the broader final
optimization/DFT/packaging product or certify an industrial service.

Saved files: `READINESS.md`, `readiness.json`, `training/model.pt`,
`training/training.json`, `evaluation/evaluation.json`, `service-check.json`,
`tests.xml`, `prototype-source.tar.gz`, and PNG/SVG figures under `figures/`.
The complete raw experiment remains available for audit and reproduction.
