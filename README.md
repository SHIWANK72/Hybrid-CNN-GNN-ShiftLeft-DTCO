# Hybrid CNN–GNN Shift-Left DTCO

A post-global-placement research prototype combining netlist connectivity and
spatial features to predict routing load and later timing outcomes.
The master's final-product deadline is **3 May 2027**.

The current implementation includes a GraphSAGE encoder, differentiable scatter
fusion, a compact spatial U-Net, training/evaluation, and local CLI/API inference.
Its six-family Sky130HD experiment is a **TRL 4 candidate evidence package**
for the restricted predictor; formal assessment remains pending.

- [Implementation and commands](hybrid_dtco/README.md)
- [Measured laboratory results and figures](hybrid_dtco/reports/lab-2026-11-03/README.md)
- [Reproduction and inference guide](hybrid_dtco/docs/lab_validation.md)
- [Project vision and six-month roadmap](hybrid_dtco/docs/project_roadmap.md)

The prototype passed 16 tests and completed 18 EDA runs. The CNN–GNN improved
spatial routing-utilization MAE over the tested baselines; ridge remained better
on timing. Wider generalization, optimization-loop qualification, calibrated
uncertainty, DFT, physical packaging and production deployment remain future work.
