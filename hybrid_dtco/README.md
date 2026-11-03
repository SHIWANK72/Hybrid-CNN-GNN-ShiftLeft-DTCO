# Hybrid DTCO laboratory prototype

A post-global-placement CNN–GNN research prototype for spatial routing-load
and later timing prediction, with a pinned Sky130HD EDA reference flow.
The master's final product deadline is **3 May 2027**.

- [First reference flow](docs/reference_flow.md): original GCD through physical
  design, graph extraction, scalar labels and artifact provenance.
- [Laboratory validation](docs/lab_validation.md): model, six-family data
  protocol, training/evaluation, CLI/API demo and readiness evidence.

Use the prepared cloud Python environment at `/workspace/.venvs/dtco`.
Run the repository tests from this directory with `python -m pytest`.
The general LMDB ingestion, DFT, packaging, optimization-loop qualification,
additional reliability targets and production deployment remain future work.
