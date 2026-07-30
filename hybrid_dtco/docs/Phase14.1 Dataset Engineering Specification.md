# Industrial Dataset Engineering Specification
## Pre-Training Experiment Generation Pipeline for RTL→GDSII ML Prediction Models (CNN/GNN Ground-Truth Datasets)

**Scope of this document:** Everything required *before* CNN/GNN training begins — dataset generation, benchmark curation, leakage-free splitting, ground-truth label generation, feature extraction, storage engineering, validation, statistics, and automation. No model code. No training code.

**Target venues:** IEEE TCAD, IEEE TVLSI, DAC, ICCAD, DATE — Artifact Evaluation (AE) compliant.

---

## PART 1 — Dataset Generation Pipeline (RTL → Training Dataset)

### 1.0 Pipeline Overview

```
RTL (Verilog/VHDL)
   │
   ▼
[Stage A] Synthesis — Yosys
   │  (gate-level netlist, generic/tech-mapped)
   ▼
[Stage B] Floorplan + Physical Init — OpenROAD/OpenLane
   │
   ▼
[Stage C] Global Placement — OpenROAD (RePlAce/DREAMPlace backend)
   │
   ▼
[Stage D] (Optional) Detailed Placement + Global Route — for label generation only
   │
   ▼
[Stage E] Feature Extraction (graph + spatial + global)
   │
   ▼
[Stage F] Ground Truth Generation (lithography, thermal, EM, congestion, timing, power)
   │
   ▼
[Stage G] Dataset Storage (LMDB/HDF5 + manifests)
   │
   ▼
[Stage H] Validation + Statistics
   │
   ▼
Training / Validation / Zero-shot / OOD Dataset Shards
```

Each stage is a **checkpointed, idempotent unit of work** identified by a content hash of its inputs (`design_id + stage_config_hash`), so the pipeline can resume after failure without recomputation — critical at benchmark-suite scale (hundreds of designs × multiple PDKs × multiple utilization targets).

---

### Stage A — RTL Elaboration & Synthesis (Yosys)

| Field | Specification |
|---|---|
| **Purpose** | Convert behavioral RTL into a technology-mapped gate-level netlist that is structurally representative of what downstream physical design tools will place and route. This is the root of the data-generation DAG — all label quality depends on synthesis quality/determinism. |
| **Input** | RTL sources (`.v`/`.sv`/`.vhd`), top-module name, synthesis constraints (`.sdc` clock definitions), target standard-cell library (`.lib`/`.lef`) |
| **Output** | Gate-level netlist (`.v`), synthesis statistics report, cell-count report, area report |
| **Required Files** | `synth.tcl` (Yosys script), `constraints.sdc`, PDK `.lib`/`.lef`, `design_config.yaml` (per-design metadata: top module, clock period, reset polarity) |
| **Software Used** | Yosys ≥0.35 (with `abc` for technology mapping), optional `yosys-slang` frontend for modern SystemVerilog |
| **Expected Runtime** | 10 s (PicoRV32-class, ~5k cells) to 15 min (CVA6/Ariane-class, ~150k cells) on 8-core workstation |
| **Failure Conditions** | Elaboration errors (undeclared signals, width mismatches), unsupported SV constructs, missing clock definitions, combinational loops detected post-mapping |
| **Validation Checks** | Netlist connectivity check (no dangling nets), gate count sanity range check per design class, `check` command with no unmapped cells, area report within 3σ of historical runs for that design family |
| **Memory Requirements** | 2–8 GB depending on design size |
| **Parallelization Strategy** | Fully embarrassingly parallel across designs; one Yosys process per design; batch via GNU parallel or Slurm array jobs, 1 task = 1 (design, PDK) pair |

**Determinism note:** Yosys `abc` mapping can be non-deterministic across versions/seeds. The pipeline pins Yosys version + `abc` script + random seed and records them in the manifest, since label reproducibility (Part 12) depends on netlist reproducibility.

---

### Stage B — Floorplanning & Physical Initialization (OpenROAD/OpenLane)

| Field | Specification |
|---|---|
| **Purpose** | Establish die/core area, I/O pin placement, power distribution network (PDN), and macro placement (if any) — the physical canvas onto which global placement and all spatial ground truth are computed. |
| **Input** | Gate-level netlist from Stage A, `.lef`/`.lib` (tech + cell), floorplan config (utilization target, aspect ratio, core margin) |
| **Output** | Initialized floorplan DEF, PDN-annotated DEF, I/O placement report |
| **Required Files** | `floorplan.tcl`, `pdn.tcl`, `openlane_config.json` (or `.tcl` for classic flow) |
| **Software Used** | OpenROAD (`init_floorplan`, `pdngen`), OpenLane 2 flow orchestration |
| **Expected Runtime** | 30 s – 3 min |
| **Failure Conditions** | Utilization target infeasible for cell/macro area budget, PDN generation failure (stripe overlap), I/O pin count exceeds perimeter capacity |
| **Validation Checks** | Core area vs. cell area utilization ratio within configured target ± tolerance, DEF syntax validity, PDN connectivity (LVS-lite check) |
| **Memory Requirements** | 2–4 GB |
| **Parallelization Strategy** | Parallel across designs; **not** parallel within a single floorplan run (sequential internal steps) |

**Dataset design decision:** For the same netlist, generate **multiple floorplan variants** (utilization ∈ {50%, 65%, 75%, 85%}, aspect ratio ∈ {1:1, 1:2}) to inject controlled distributional diversity for congestion/EM/thermal labels — this multiplies effective dataset size without new RTL and is standard practice in ML-for-EDA congestion/timing papers (e.g., CongestionNet, RouteNet lineage).

---

### Stage C — Global Placement (OpenROAD, RePlAce/DREAMPlace backend)

| Field | Specification |
|---|---|
| **Purpose** | Produce the placement solution that is the primary geometric input to feature extraction. Global placement (not detailed placement) is used as the model's *predictive input* because it is what's available early in the flow — the entire value proposition of the ML model is early-stage prediction before expensive detailed P&R. |
| **Input** | Initialized floorplan DEF, netlist, target density |
| **Output** | Placed DEF (cell x/y coordinates), placement density map, overflow/HPWL convergence log |
| **Required Files** | `global_place.tcl`, density/overflow convergence config |
| **Software Used** | OpenROAD `global_placement` (RePlAce-based); DREAMPlace as an optional faster alternative for large designs |
| **Expected Runtime** | 1–20 min depending on cell count (roughly linear-to-superlinear in cell count) |
| **Failure Conditions** | Non-convergence (overflow doesn't reach target after max iterations), NaN in placement solver (numerical instability with degenerate nets) |
| **Validation Checks** | Final overflow < 0.1, all cells within core bounds, no overlapping macros, HPWL monotonic decrease trend in log |
| **Memory Requirements** | 4–16 GB (GPU-accelerated DREAMPlace path: 8–24 GB VRAM for large designs) |
| **Parallelization Strategy** | One design per GPU/CPU worker; DREAMPlace itself is internally GPU-parallel (CUDA); cluster-level parallelism across (design × floorplan variant) pairs |

---

### Stage D — Detailed Placement + Global Route (label-generation only, not model input)

| Field | Specification |
|---|---|
| **Purpose** | Detailed placement legalization and global routing are **not exposed to the model as input** — they exist solely to generate high-fidelity ground truth (routing congestion, realistic parasitics for timing/power/EM). This separation (early-stage input → late-stage label) is what makes the dataset scientifically meaningful for *predictive* ML. |
| **Input** | Global-placed DEF |
| **Output** | Legalized DEF, global-route guide (`.guide`), routing congestion map |
| **Required Files** | `detailed_place.tcl`, `global_route.tcl`, routing layer config |
| **Software Used** | OpenROAD `detailed_placement`, `global_route` (FastRoute-based) |
| **Expected Runtime** | 1–10 min |
| **Failure Conditions** | Legalization failure (insufficient whitespace), routing overflow beyond fixable threshold |
| **Validation Checks** | Zero placement overlaps post-legalization, routing overflow map bounded, DRC-lite clean |
| **Memory Requirements** | 4–12 GB |
| **Parallelization Strategy** | Per-design parallel; internal steps sequential |

---

## PART 2 — Benchmark Selection

### 2.1 Selected Suites and Rationale

| Suite | Why Included | Design Character |
|---|---|---|
| **ISCAS-85/89** | Canonical, decades of prior EDA-ML literature use it — required for comparability with baselines (CongestionNet, GRANNITE, etc.) | Small combinational/sequential, low macro count |
| **ITC-99** | Extends ISCAS with larger, more structurally diverse benchmarks; standard for scalability studies | Medium complexity, moderate hierarchy |
| **EPFL Combinational Benchmark Suite** | Modern, arithmetic-heavy (adders, multipliers, ALUs) — stresses feature extractors on high-fanout/arithmetic structures absent from ISCAS | Combinational-only, wide datapaths |
| **OpenCores** | Real-world IP diversity (UARTs, controllers, DSP cores) — improves generalization beyond academic benchmarks | Highly heterogeneous |
| **PicoRV32** | Minimal RISC-V core — good "easy" anchor for sanity-checking pipeline correctness | Small RV32I core |
| **Ibex** | Small-to-medium RISC-V core (lowRISC), realistic pipeline/hazard structures | Medium, in-order pipeline |
| **RocketChip / TinyRocket** | Parameterizable, generates a *family* of related-but-distinct netlists from one generator — used carefully to avoid leakage (see Part 3) | Medium–large, configurable |
| **CVA6 (Ariane)** | Larger, out-of-order-capable RISC-V core with FPU/MMU — stresses macro-heavy, high cell-count regime | Large, complex hierarchy |

### 2.2 Split Assignment by Suite

| Split | Suites/Designs |
|---|---|
| **Train** | ISCAS-89 (majority), ITC-99 (majority), EPFL (majority), OpenCores (majority), PicoRV32 |
| **Validation** | Held-out subset (~15%) from each of the above, stratified by cell-count bucket |
| **Zero-shot** | Ibex (entirely excluded from train) — tests generalization to an unseen but architecturally related RISC-V core |
| **OOD (out-of-distribution)** | CVA6/Ariane, RocketChip variants — larger, structurally distinct, tests extrapolation beyond training cell-count/macro-count envelope |

**Design principle:** Zero-shot = *unseen instance, seen design family/domain*. OOD = *unseen instance AND shifted structural/statistical regime* (larger scale, different microarchitecture class, different macro density). This distinction must be stated explicitly in the paper — reviewers at TCAD/ICCAD routinely reject papers that conflate the two.

---

## PART 3 — Dataset Split Strategy & Leakage Prevention

### 3.1 Split Axes

1. **Design-level split** — train/val/zero-shot/OOD as above, split at the *design* granularity, never at the *sample* (floorplan variant) granularity for the same design.
2. **Cross-PDK split** — same netlist synthesized/placed against ≥2 open PDKs (e.g., SkyWater Sky130, GlobalFoundries GF180MCU) to test technology-transfer generalization.
3. **Cross-node split** — where feasible with open PDKs at different nodes, held out entirely for OOD technology-node evaluation.
4. **Cross-technology split** — standard-cell library variant (HD vs. HS cell libraries) held out similarly.

### 3.2 Leakage Prevention Mechanisms

| Mechanism | Purpose | Method |
|---|---|---|
| **Netlist Weighted-Level (WL) Graph Hash** | Detect near-duplicate netlists across suites (e.g., RocketChip configs sharing sub-blocks with TinyRocket) | Weisfeiler-Lehman graph hashing on the gate-level netlist graph (cell-type-labeled, degree-refined); any WL-hash collision between splits triggers exclusion |
| **Subgraph Isomorphism Screening** | Catch cases where a large design *contains* a smaller benchmark as a hierarchical sub-block | VF2/VF3 subgraph isomorphism check between all OOD/zero-shot designs and all train designs above a similarity threshold |
| **Placement Similarity** | Prevent leakage via near-identical floorplan variants of the same netlist landing in different splits | Only one design → all its floorplan variants stay together in a single split |
| **Macro Similarity** | Prevent generalization inflation from shared macro instances (SRAM/register-file generators) across designs | Macro fingerprint (name + size + pin config) tracked in a global macro registry; any macro reused across splits is flagged, and its host design reassigned or the macro instance parameterized-and-varied |
| **Netlist Overlap (n-gram on gate sequences)** | Catch partial/copy-paste RTL reuse across "different" benchmark suites | Structural n-gram fingerprinting over topologically-sorted gate sequences |

All leakage checks run as an automated **pre-flight gate** (`split_dataset.py`, Part 9) before any data enters a split; violations are logged and block dataset finalization until resolved.

---

## PART 4 — Ground Truth Generation

| Label | EDA Tool | Input | Output | Runtime | Expected Accuracy | Storage Format | Normalization |
|---|---|---|---|---|---|---|---|
| **Lithography (hotspot risk)** | Simplified litho simulator (e.g., open litho-hotspot proxy, or OPC-lite tool) | Detailed-routed layout clips | Per-region hotspot probability map | 1–5 min/clip | Proxy-level (correlative, not full lithography simulation) — must be stated as a limitation | HDF5 float32 raster | Min-max per design, then global z-score across dataset |
| **Thermal** | OpenROAD `psm`/thermal analysis or external steady-state solver on power density map | Power map + floorplan | 2D/3D temperature map | 30 s – 2 min | ±5–10% vs. reference solver (documented in validation appendix) | HDF5 float32 raster | Per-die normalization to ΔT above ambient |
| **Electromigration (EM)** | OpenROAD `psm` current density analysis | PDN geometry + power map | Per-segment current density | 30 s – 1 min | Rule-of-thumb J_max comparison, not signoff-grade | CSV (per-segment) + raster overlay | Normalized to library J_max threshold (ratio ≤1 = safe) |
| **Routing congestion** | OpenROAD `global_route` overflow report | Global route guide | Per-GCell overflow/demand map | already produced in Stage D | High (direct tool output, not proxy) | HDF5 float32 raster (GCell grid) | Per-layer normalization by supply capacity |
| **Timing (WNS/TNS proxy)** | OpenSTA post-global-route with estimated parasitics | Placed/routed netlist + SPEF-lite | Per-endpoint slack | 1–5 min | Estimated-parasitic accuracy (~70–85% correlation to signoff STA — must be stated) | CSV per endpoint + aggregated WNS/TNS scalar | Slack normalized by clock period |
| **Power** | OpenROAD/OpenSTA power report (or external power tool) | Placed netlist + switching activity (default toggle-rate assumption, documented) | Per-cell/per-region power density | 1–3 min | Vector-less estimate (no real testbench activity) — documented as a limitation and a future-work item | HDF5 float32 raster + CSV per-cell | Normalized by die-area power density |

**Reviewer-facing caveat (mandatory in paper):** All labels are generated at global-placement/global-route fidelity, not signoff fidelity. This is a deliberate scientific choice (predicting late-stage outcomes from early-stage data) and must be framed as such, with a documented accuracy gap analysis against a signoff-grade subset (see Part 12, statistical validity).

---

## PART 5 — Feature Extraction

### 5.1 Node Features (per standard cell / macro instance)

| Feature | Datatype | Range | Normalization | Units |
|---|---|---|---|---|
| Cell type (one-hot / learned embedding index) | int32 → embedding | [0, N_celltypes) | categorical embedding | — |
| Cell width, height | float32 | (0, max_cell_dim] | min-max per PDK | μm |
| Pin count | int16 | [1, 64] | log-scale then min-max | count |
| Input/output pin ratio | float32 | [0, 1] | none needed | ratio |
| x, y global-placement coordinate | float32 | [0, die_width/height] | die-normalized to [0,1] | μm |
| Static power (leakage) | float32 | (0, max_leak] | log + z-score | μW |
| Fanout degree | int16 | [0, max_fanout] | log-scale | count |
| Is-macro flag | bool | {0,1} | — | — |
| Is-sequential flag | bool | {0,1} | — | — |
| Local placement density (window) | float32 | [0,1] | none needed | ratio |

### 5.2 Edge Features (per net / graph edge)

| Feature | Datatype | Range | Normalization | Units |
|---|---|---|---|---|
| Net HPWL (at global placement) | float32 | (0, max_hpwl] | log + z-score | μm |
| Fanout count of net | int16 | [1, max_fanout] | log-scale | count |
| Wire capacitance estimate | float32 | (0, max_cap] | z-score | fF |
| Is-clock-net flag | bool | {0,1} | — | — |
| Is-critical-path flag (from timing) | bool | {0,1} | — | — |
| Edge type (driver-pin → sink-pin encoding) | categorical | fixed vocab | embedding | — |

### 5.3 Spatial Channels (rasterized grid, for CNN branch)

| Channel | Datatype | Layout | Normalization |
|---|---|---|---|
| Cell density map | float32 raster, GCell-resolution | HWC single channel | [0,1] |
| Pin density map | float32 raster | single channel | [0,1] |
| Macro mask | binary raster | single channel | {0,1} |
| RUDY (Rectangular Uniform wire DensitY) congestion estimate | float32 raster | single channel | z-score |
| Power density map | float32 raster | single channel | z-score |
| Net-count-per-layer (if multi-layer channels retained) | float32 raster stack | multi-channel | per-layer z-score |

### 5.4 Global Features (per-design scalar vector)

| Feature | Datatype | Notes |
|---|---|---|
| Total cell count | int32 | log-scale before use |
| Total macro count | int16 | — |
| Die area | float32 | μm² |
| Target utilization | float32 | [0,1] |
| Clock period | float32 | ns |
| PDK identifier | categorical | for cross-PDK conditioning |

**Memory layout:** node/edge features stored as columnar arrays (structure-of-arrays, not array-of-structs) for efficient batched tensor loading; spatial rasters stored as CHW float32 tensors compatible with direct `torch.from_numpy` zero-copy loading.

---

## PART 6 — Storage Design

### 6.1 Storage Backend Split

- **LMDB**: primary store for graph-structured samples (node/edge feature arrays, adjacency, per-sample metadata) — chosen for fast random-access reads during training with memory-mapped I/O and no daemon process.
- **HDF5**: primary store for large spatial raster tensors (density/congestion/thermal/EM maps) — chosen for chunked/compressed access patterns and native N-D array support, with per-design groups.

### 6.2 Directory Hierarchy

```
dataset_root/
├── manifest.yaml
├── VERSION
├── checksums.sha256
├── raw/
│   └── <design_id>/<pdk>/<util_variant>/
│       ├── netlist.v
│       ├── placed.def
│       └── routed.guide
├── graphs.lmdb/
├── rasters.hdf5
├── labels/
│   └── <design_id>/<pdk>/<util_variant>/
│       ├── thermal.h5
│       ├── em.csv
│       ├── congestion.h5
│       ├── timing.csv
│       └── power.h5
├── splits/
│   ├── train.json
│   ├── val.json
│   ├── zero_shot.json
│   └── ood.json
├── stats/
│   ├── feature_histograms.json
│   └── dataset_statistics.csv
└── logs/
    └── <design_id>/<stage>.log
```

### 6.3 Naming Convention

`<design_id>__<pdk>__<util_pct>__<aspect_ratio>__<seed>` — fully deterministic, encodes every axis of variation, enables exact reproduction and unambiguous leakage auditing.

### 6.4 Versioning, Metadata, Checksums, Manifest

- **Versioning:** semantic (`MAJOR.MINOR.PATCH`); MAJOR bump on any label-generation methodology change, MINOR on new designs added, PATCH on bugfix regeneration of existing samples.
- **Metadata:** every sample's manifest entry records tool versions (Yosys, OpenROAD commit hash), PDK version, random seeds, and generation timestamp — full provenance chain.
- **Checksums:** SHA-256 per file, aggregated into `checksums.sha256`; dataset load routine verifies checksums before use.
- **Manifest files:** `manifest.yaml` is the single source of truth mapping every `design_id` to its file locations, split assignment, and provenance metadata.

---

## PART 7 — Dataset Validation

Automated validation (`validate_dataset.py`, Part 9) runs the following checks on every sample before it is admitted to a split:

| Check | Method |
|---|---|
| **NaN / Inf** | Elementwise scan of all float tensors (node/edge features, rasters, labels); any NaN/Inf → sample quarantined |
| **Disconnected graphs** | Connected-component count on the netlist graph; components >1 beyond expected (e.g., separate scan-chain islands) flagged for manual review |
| **Incorrect coordinates** | Bounds check: all cell coordinates within [0, die_width] × [0, die_height]; zero-area or negative-dimension cells flagged |
| **Power mismatch** | Cross-check per-cell power sum vs. tool-reported total design power (tolerance ±2%) |
| **Feature mismatch** | Schema validation — every sample must match the declared feature schema (dtype, shape, channel count) exactly |
| **Missing labels** | Manifest completeness check — every sample must have all six label types present or be explicitly marked "label unavailable" with reason |
| **Corrupted files** | Checksum re-verification + file-open sanity test (HDF5/LMDB integrity check) |
| **Graph symmetry** | Sanity check that bidirectional edge encodings (if used) are consistent; that no self-loops exist unless intentionally modeling feedback |

Failed samples are moved to `quarantine/` with a structured failure report, never silently dropped — this preserves auditability for AE reviewers.

---

## PART 8 — Dataset Statistics

`dataset_statistics.py` automatically computes and renders (as both CSV and publication-ready tables/figures):

- Mean/variance/histogram for every node, edge, and global feature
- Node count, edge count, macro count, cell count distributions (per split, with box plots)
- Power distribution (log-scale histogram, per split)
- Temperature distribution (ΔT above ambient, per split)
- EM distribution (current-density-to-J_max ratio histogram)
- Routing utilization distribution (mean/percentile congestion per design)
- Cross-split distributional distance (e.g., Wasserstein distance between train and OOD feature distributions) — this is the quantitative evidence that the OOD split is *actually* out-of-distribution, which reviewers will ask for

All tables generated in both Markdown (for repo docs) and LaTeX `booktabs` format (for direct paper inclusion).

---

## PART 9 — Automation

| Script | Responsibility |
|---|---|
| `generate_dataset.py` | Orchestrates Stages A–G end-to-end per design; supports `--resume` via per-stage checkpoint hashing; supports `--cluster slurm` / `--cluster k8s` execution backends |
| `validate_dataset.py` | Runs Part 7 checks; quarantines failures; emits pass/fail report |
| `dataset_statistics.py` | Runs Part 8 computations; emits CSV/LaTeX/plots |
| `dataset_manifest.py` | Builds/updates `manifest.yaml`; verifies completeness against expected design list |
| `hash_dataset.py` | Computes WL graph hashes and file checksums; feeds leakage screening (Part 3) |
| `split_dataset.py` | Applies split rules from Part 3; runs leakage pre-flight gate; emits `splits/*.json`; **fails the build** on any unresolved leakage flag |

**Cluster execution:** Slurm array jobs (`--array=0-N`) map one array task to one (design × PDK × utilization-variant) unit; Kubernetes path uses a Job with an indexed completion mode for equivalent semantics; both paths write to a shared network filesystem or object store with the same manifest-driven resume logic, so a killed/preempted job re-enters the pipeline at its last completed stage.

---

## PART 10 — Expected Repository Structure (Post Phase 14.1)

```
project_root/
├── pipeline/
│   ├── stage_a_synth/
│   ├── stage_b_floorplan/
│   ├── stage_c_global_place/
│   ├── stage_d_route_labels/
│   ├── stage_e_feature_extract/
│   ├── stage_f_ground_truth/
│   └── stage_g_storage/
├── scripts/
│   ├── generate_dataset.py
│   ├── validate_dataset.py
│   ├── dataset_statistics.py
│   ├── dataset_manifest.py
│   ├── hash_dataset.py
│   └── split_dataset.py
├── configs/
│   ├── pdks/
│   ├── benchmarks/
│   └── floorplan_variants/
├── benchmarks/
│   ├── iscas/  itc99/  epfl/  opencores/
│   ├── picorv32/  ibex/  rocketchip/  cva6/
├── dataset_root/            (as in Part 6)
├── docs/
│   ├── dataset_card.md
│   ├── reproducibility.md
│   └── leakage_audit_report.md
├── cluster/
│   ├── slurm/
│   └── k8s/
└── tests/
    └── validation_unit_tests/
```

---

## PART 11 — Deliverables (Complete File Inventory)

- `dataset_root/graphs.lmdb` — all graph-structured samples
- `dataset_root/rasters.hdf5` — all spatial channel tensors
- `labels/**/*.h5`, `labels/**/*.csv` — per-label ground truth
- `splits/train.json`, `val.json`, `zero_shot.json`, `ood.json`
- `manifest.yaml`, `VERSION`, `checksums.sha256`
- `stats/dataset_statistics.csv`, `stats/feature_histograms.json`
- Publication-ready tables (`stats/*.tex`)
- Plots: distribution histograms, split-distance plots, per-benchmark coverage plots (`stats/plots/*.pdf`)
- `docs/dataset_card.md` — structured dataset card (per ML dataset-documentation norms)
- `docs/leakage_audit_report.md` — full leakage-screening evidence
- `docs/reproducibility.md` — exact tool versions, seeds, and commands to regenerate any single sample
- `logs/<design_id>/<stage>.log` — full per-stage execution logs

---

## PART 12 — Publication Readiness

**IEEE TCAD / TVLSI / DAC / ICCAD / DATE fit:**
- The Stage A–D fidelity choice (early-stage predictive input, late-stage generated label) is the paper's core scientific contribution framing and must be stated explicitly in the Methods section.
- **Artifact Evaluation:** manifest + checksums + versioned dataset + `reproducibility.md` satisfy AE badges (Available, Functional, Reproducible) at DAC/ICCAD/DATE AE tracks.
- **Reproducibility:** every sample traceable to exact tool commit hashes and seeds (Part 6.4); regeneration script provided per sample.
- **Zero-shot / OOD evaluation:** explicit split rationale (Part 2.2/3) plus quantitative distributional-distance evidence (Part 8) pre-empts the most common reviewer objection — "how do you know your test set isn't just memorized training data?"
- **Statistical validity:** report label-generation accuracy gaps against a signoff-grade subset (Part 4) so claims are appropriately bounded; avoid over-claiming signoff-level ground-truth accuracy.
- **No data leakage:** WL-hash + subgraph isomorphism + macro-registry + n-gram overlap screening (Part 3.2), with a machine-checkable pre-flight gate that blocks dataset finalization — this is the strongest defensible claim against the most common desk-reject reason in ML-for-EDA submissions.

**Industrial note:** this pipeline mirrors production dataset-engineering practice at large EDA/silicon organizations (provenance-first, checkpointed, leakage-audited) rather than academic one-off script pipelines — this is itself a citable engineering contribution distinct from the model architecture.

**Future scalability:** the manifest-driven, hash-checkpointed design generalizes directly to (a) additional PDKs/nodes without pipeline redesign, (b) commercial tool backends (Synopsys/Cadence) behind the same stage interfaces, and (c) additional label types (routability-driven DRC hotspot maps, IR-drop) as new Stage-F modules without touching Stages A–E.
