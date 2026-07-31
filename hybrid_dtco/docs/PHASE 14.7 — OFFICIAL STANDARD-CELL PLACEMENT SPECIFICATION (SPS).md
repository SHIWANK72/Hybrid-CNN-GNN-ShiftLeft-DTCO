# PHASE 14.7 — OFFICIAL STANDARD-CELL PLACEMENT SPECIFICATION (SPS)

**Paper:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target Venue:** IEEE International Conference on Microelectronics (ICM 2026)
**Scope Boundary:** This phase begins at the VALIDATED FLOORPLAN (Phase 14.6 output) and terminates at a VALIDATED LEGAL STANDARD-CELL PLACEMENT with complete placement QoR extraction. Clock Tree Synthesis, clock optimization, routing, timing sign-off, physical verification, DRC/LVS sign-off, extraction, and tapeout are explicitly out of scope and are deferred to Phase 14.8 onward.

---

## PART 1 — PLACEMENT PHILOSOPHY

**Purpose.** Standard-cell placement converts the technology-mapped, floorplanned netlist into a spatially legal, physically realizable arrangement of standard cells on the placement rows defined in Phase 14.6. The stage exists to resolve the combinatorial problem of assigning finite silicon area to a finite set of instances such that wirelength, timing, congestion, and density constraints are jointly satisfiable prior to clock insertion.

**Theory.** Placement is treated as a constrained multi-objective optimization problem over a mixed discrete-continuous solution space: cell positions are continuous during global placement (analytical relaxation) and discretized to legal sites during detailed placement. The governing objective function combines half-perimeter wirelength (HPWL) minimization, density-penalty terms (electrostatic/Poisson-based spreading), and optional timing/congestion weighting terms, subject to non-overlap and site-legality constraints.

**Engineering rationale.** A staged global→detailed pipeline is adopted rather than a single monolithic solver because (a) analytical global placement scales well to 10^5–10^7 instance counts but produces illegal (overlapping, off-grid) solutions, and (b) detailed placement/legalization is a combinatorial correction step that is only tractable once global placement has produced a low-wirelength initial distribution. Decoupling the two stages is the industry-standard approach (RePlAce, OpenROAD `gpl`/`dpl`) and preserves determinism because each stage has an independently fixable seed and convergence criterion.

**Inputs.** Validated floorplan DEF/ODB, technology-mapped gate-level netlist, LEF (technology + cell), Liberty timing views, SDC constraints, floorplan QoR record, placement configuration manifest.

**Outputs.** Legalized placed DEF, placed ODB, placement QoR JSON, placement reports, placement visualization artifacts, updated manifest/config snapshot.

**Dependencies.** Requires a floorplan that has passed Phase 14.6 validation gates (row legality, macro placement, power grid pre-plan, blockage definitions). Requires a fully technology-mapped, DRC-clean-at-cell-level netlist (no unmapped generic cells).

**Runtime expectations.** For benchmark designs in the 10K–500K instance range on a 16-thread commodity workstation, global placement is expected to complete in 2–40 minutes and detailed placement/legalization in 30 seconds–5 minutes, scaling approximately linearly to slightly super-linearly with instance count under RePlAce's nesterov-based solver. Runtime is logged per-stage and is a first-class QoR metric, not an incidental measurement.

**Memory expectations.** Peak RSS is dominated by the global-placement density grid resolution and instance count; expected range 500 MB–8 GB for the benchmark corpus sizes targeted in this project (up to ~1M instances). Memory is sampled at fixed intervals and recorded per stage.

**Failure conditions.** Divergence of the analytical solver (non-decreasing HPWL over a rolling window), legalization failure (residual overlap after maximum legalization iterations), density overflow beyond configured threshold, and off-grid/off-site placement after legalization are all treated as hard failures that halt the pipeline and are logged to the failure ledger (Part 12).

**Validation.** A placement is accepted only if it passes all gates enumerated in Part 5, Stage J: zero overlaps, 100% site/row legality, density within configured bounds, and QoR JSON schema validation.

**Industrial notes.** This specification mirrors OpenROAD's `gpl` (global placement, RePlAce-derived) and `dpl` (OpenDP-derived detailed placement/legalization) flow as orchestrated by OpenLane2's `Odb.CoarsePlacement` / `Odb.DetailedPlacement` steps, chosen for reproducibility, open licensing, and deterministic seeding, all of which are prerequisites for artifact-evaluated, dataset-generating research.

**Reviewer expectations.** Reviewers evaluating this phase under IEEE ICM Artifact Evaluation criteria will expect: explicit tool versions, explicit seeds, explicit convergence criteria, and a QoR record sufficient to reproduce reported wirelength/density/timing numbers without re-running the full flow.

**Future scalability.** The staged architecture is designed to scale from single-instance debug runs (10^2 cells) to full ML-corpus generation runs (10^3–10^6 designs × multiple PVT/utilization sweeps) without structural modification — only manifest-level parallelism (Part 13) changes.

---

## PART 2 — OBJECTIVES

1. **Deterministic placement.** Identical inputs (netlist, floorplan, config, seed) must produce bit-identical placed DEF across runs and machines. *Rationale:* determinism is a non-negotiable precondition for ML dataset generation and IEEE reproducibility. *Validation:* checksum comparison of placed DEF across ≥3 independent re-runs.
2. **Technology independence.** Placement rules, stage definitions, and QoR schema must be expressible without hard-coding a specific PDK. *Rationale:* enables corpus generation across multiple technology nodes (e.g., sky130, gf180mcu, ASAP7) without flow rewrites. *Validation:* successful execution of the identical pipeline against ≥2 distinct open PDKs.
3. **Reproducibility.** Every run must emit a self-contained configuration snapshot sufficient to reconstruct the run. *Rationale:* required for Zenodo/Artifact Evaluation packaging. *Validation:* fresh-environment replay from snapshot alone.
4. **Legal placement.** 100% of instances must reside on-grid, on-site, non-overlapping, within row boundaries and orientation constraints. *Rationale:* legality is a hard physical precondition for CTS and routing; illegal placement invalidates all downstream phases. *Validation:* automated legality checker (Part 5, Stage H/J).
5. **Timing-aware placement.** Placement must incorporate SDC-derived net criticality weighting so that timing-critical nets are preferentially shortened. *Rationale:* pre-CTS timing estimates materially affect final sign-off timing; ignoring timing at placement produces irrecoverable slack loss. *Validation:* correlation check between placement-stage slack estimate and post-legalization slack estimate (should not regress beyond configured tolerance).
6. **Congestion-aware placement.** Placement must estimate and bound routing congestion prior to detailed routing. *Rationale:* congestion hotspots discovered only at routing are expensive to fix; early estimation enables cheap global-placement-stage correction. *Validation:* RUDY/RUDY-like overflow estimate below configured threshold.
7. **Density consistency.** Local density must remain within the configured target density band across all placement bins. *Rationale:* uniform density is a proxy for legalizability and routability. *Validation:* bin-wise density histogram check.
8. **QoR completeness.** Every run must emit the full metric set defined in Part 10 with no missing fields. *Rationale:* incomplete QoR breaks downstream ML pipelines that consume this data as feature vectors. *Validation:* schema validation against the fixed QoR JSON schema.

**Engineering rationale (aggregate).** These objectives are jointly necessary and mutually constraining: legality without density consistency yields legal-but-unroutable placements; timing-awareness without determinism yields non-reproducible research claims. The objective set is therefore evaluated as a conjunction, not independently.

**Validation.** A placement run is marked PASS only if all eight objectives above independently pass their respective gates; any single failure marks the run FAIL and routes to Part 12 failure handling.

**Industrial notes.** These objectives correspond directly to the acceptance criteria used in OpenROAD-derived industrial flows (`gpl` density penalty convergence, `dpl` legality check, `psn`/`rsz`-adjacent timing estimation hooks) and are not project-specific inventions.

**Future scalability.** Objective thresholds (density band, congestion overflow limit, timing tolerance) are externalized to the placement configuration manifest (Part 3) so that objective *definitions* remain fixed while objective *thresholds* can be swept for ML dataset diversity generation.

---

## PART 3 — INPUTS

| Input | Description | Format | Source |
|---|---|---|---|
| Validated Floorplan DEF | Die/core area, rows, tracks, macros, blockages, pins | DEF 5.8 | Phase 14.6 output |
| ODB | Binary OpenDB database mirroring the floorplan DEF | `.odb` | Phase 14.6 output |
| Technology-mapped netlist | Gate-level netlist post synthesis/tech-mapping | Verilog (structural) | Upstream synthesis phase |
| LEF | Technology LEF + cell LEF (site, layer, macro geometry) | LEF 5.8 | PDK |
| Liberty | Timing/power views (typical, and optionally best/worst corners) | `.lib`/`.lib.gz` | PDK |
| SDC | Clock definitions, I/O delays, false paths, multicycle paths | SDC | Upstream constraint phase |
| Floorplan QoR | Core utilization, row count, macro count, blockage area | JSON | Phase 14.6 output |
| Placement configuration | Target density, algorithm parameters, weighting coefficients | YAML/JSON | This phase, user/manifest-supplied |
| Benchmark metadata | Design name, benchmark suite ID, technology node ID | JSON | Project-level manifest |
| Manifest | Run identifier, timestamp, tool versions, seed | JSON | Auto-generated |
| Configuration snapshots | Frozen copy of all config files used in the run | Directory snapshot | Auto-generated |

**Engineering rationale.** Every input is versioned and hashed at ingestion time so that the manifest can later prove exactly which artifact set produced a given placement, satisfying both determinism (Part 2, Objective 1) and Artifact Evaluation requirements (Part 16).

**Validation.** Input ingestion performs: (a) DEF/LEF/Liberty/SDC syntactic validation via OpenDB parser round-trip, (b) netlist-to-floorplan instance-count cross-check, (c) hash verification against manifest-recorded hashes for any resumed/rerun job.

**Failure conditions.** Missing or unparsable DEF/LEF/Liberty/SDC; instance-count mismatch between netlist and floorplan-declared instance set; missing or malformed placement configuration; hash mismatch on resume. All input-validation failures are logged as `STAGE_A_INPUT_FAILURE` and halt before any placement computation begins.

---

## PART 4 — PLACEMENT ENVIRONMENT

**OpenROAD.** Provides the core placement engines used in this specification: `gpl` (global placement, RePlAce-derived nesterov solver) and `dpl` (OpenDP-derived detailed placement/legalizer). OpenROAD operates directly on the OpenDB in-memory database, avoiding lossy DEF round-trips between internal stages.

**OpenLane2.** Supplies the orchestration layer (`Odb.*` placement steps, `Yosys`/`OpenROAD` step chaining, `Odbpy` utility scripts) that sequences floorplanning → placement → (downstream CTS) as manifest-driven, resumable steps with per-step artifact snapshotting.

**OpenDB.** The shared physical database (LEF/DEF-consistent) that both `gpl` and `dpl` read/write; used here as the canonical intermediate representation instead of repeated DEF re-parsing, to preserve numerical determinism.

**RePlAce.** The analytical global placement algorithm underlying `gpl`: an electrostatics-inspired, Nesterov-accelerated solver that treats cell density as a charge-density field and minimizes a combined wirelength + density-penalty objective.

**Detailed Placement Engine.** OpenDP-derived legalizer (`dpl`) that snaps the continuous RePlAce solution to legal sites via minimum-displacement local search, cell shifting/swapping, and row-consistent legalization.

**Coordinate system.** Cartesian, origin at core-area lower-left corner (consistent with Phase 14.6 floorplan convention), units in Database Units (DBU).

**Database Units.** Fixed at the PDK-declared DBU-per-micron (e.g., 1000 DBU/µm for sky130), inherited unchanged from the floorplan; no re-scaling occurs at placement.

**Placement Grid.** The manufacturing/placement grid defined by site width × site height, inherited from LEF `SITE` definitions; all legal cell origins must align to this grid.

**Placement Rows.** Horizontal rows of fixed height (single-height or multi-height per LEF `SITE` class) generated in Phase 14.6 and consumed unmodified in this phase, except where Part 5 Stage B performs row-consistency re-verification.

**Placement Sites.** Discrete horizontal positions within a row, spaced at site width, onto which cell origins are legalized.

**Legal Sites.** Sites not overlapped by hard blockages, macro halos, or reserved regions; the legal-site set is recomputed at the start of this phase from the validated floorplan blockage map.

**Cell Rows.** Row records carrying orientation (N/FS/FN/S alternating per standard flip convention), site count, and row-to-row abutment metadata.

**Placement Constraints.** Fence regions, keepout margins, macro halos, pin-side accessibility constraints, and I/O-adjacent placement blockages, all inherited from the floorplan and enforced as hard constraints during both global and detailed placement.

**Technology Constraints.** Minimum spacing, site definitions, multi-height cell legality rules, and any PDK-specific placement DRC rules (e.g., N-well/P-well abutment rules relevant to placement-adjacent cells) as declared in the technology LEF.

**Engineering rationale.** Using OpenDB as the single source of truth across `gpl`→`dpl` avoids DEF-format precision loss and guarantees that legalization operates on the exact same coordinate representation the global placer emitted, which is essential for the minimum-displacement legalization philosophy (Part 8).

**Industrial notes.** This environment definition is intentionally identical in spirit to the OpenLane2 default flow configuration, deviating only in explicit configuration exposure (Part 3) needed for ML-corpus parameter sweeps.

**Future scalability.** Because the placement engine boundary is OpenDB-based rather than file-based, swapping in an alternative global placer (e.g., a learned/ML-based placer) in a future phase requires only that it read/write the same OpenDB schema — the staged architecture (Part 5) does not need to change.

---

## PART 5 — PLACEMENT ARCHITECTURE

The placement stage is a deterministic ten-stage pipeline (Stage A–J). Each stage consumes the OpenDB state emitted by the prior stage and emits an updated OpenDB state plus a stage-local log/QoR fragment.

### Stage A — Database Initialization
**Purpose.** Load floorplan ODB, netlist, LEF, Liberty, SDC into a single consistent OpenDB/OpenSTA session.
**Theory.** Establishes the shared in-memory representation all subsequent stages operate on; avoids repeated re-parsing.
**Engineering rationale.** A single initialization point guarantees that every stage sees an identical starting database, which is required for determinism.
**Inputs.** All Part 3 inputs.
**Outputs.** Initialized OpenDB session; input-validation report.
**Dependencies.** None (first stage).
**Runtime.** Seconds to low tens of seconds depending on netlist size.
**Memory.** Proportional to design size; dominated by Liberty timing-arc data for large cell libraries.
**Failure conditions.** Parse errors, instance/pin mismatches, missing technology data.
**Validation.** Instance count, pin count, and net count cross-checked against netlist statistics.
**Industrial notes.** Mirrors OpenLane2's `Odb.LoadDesign` equivalent step.
**Reviewer expectations.** Exact tool/library versions logged.
**Future scalability.** Supports incremental/partial reloads for ECO-style re-placement in later research extensions.

### Stage B — Placement Row Generation / Verification
**Purpose.** Re-verify row legality inherited from the floorplan and recompute the legal-site bitmap accounting for any blockage changes.
**Theory.** Rows are treated as immutable geometric resources; this stage audits rather than regenerates them, except in rare cases where fence-region configuration in this phase's manifest narrows the legal-site set further than the floorplan default.
**Engineering rationale.** Explicit re-verification catches any floorplan/placement-configuration mismatch before expensive global placement is attempted.
**Inputs.** Initialized OpenDB, placement configuration (fence/keepout overrides).
**Outputs.** Verified row table; legal-site bitmap.
**Dependencies.** Stage A.
**Runtime.** Sub-second to a few seconds.
**Memory.** Negligible relative to other stages.
**Failure conditions.** Row/site inconsistency, contradictory fence-region definitions.
**Validation.** 100% of rows pass site-alignment and orientation checks.
**Industrial notes.** Corresponds to OpenDP's internal row-consistency pass.
**Reviewer expectations.** Row table hash recorded for reproducibility.
**Future scalability.** Extensible to non-uniform row height (multi-height cell) libraries without structural change.

### Stage C — Global Placement
**Purpose.** Produce a low-wirelength, density-aware, non-legal (continuous-coordinate) initial placement via the RePlAce/`gpl` analytical solver.
**Theory.** Minimizes a combined objective: HPWL (wirelength) + λ·density-penalty (electrostatic potential), solved via Nesterov-accelerated gradient descent over a bin-density field.
**Engineering rationale.** Analytical placement is chosen over simulated annealing/partitioning-based approaches for scalability to 10^5–10^7 instances at reproducible runtime.
**Inputs.** Verified OpenDB, deterministic seed, target density, net-weighting configuration.
**Outputs.** Continuous-coordinate cell positions; global-placement HPWL/density convergence trace.
**Dependencies.** Stage B.
**Runtime.** Minutes, scaling with instance count and target density.
**Memory.** Dominated by bin-density grid resolution × instance count.
**Failure conditions.** Non-convergence (HPWL fails to decrease within a rolling window), NaN/divergent solver state.
**Validation.** Monotonic (within tolerance) HPWL decrease; final density-penalty below convergence threshold.
**Industrial notes.** Directly corresponds to OpenROAD's `gpl` command with `-density`, `-init_density_penalty`, and related flags fixed by the placement configuration manifest.
**Reviewer expectations.** Full convergence trace (iteration vs. HPWL vs. density-penalty) archived for reproducibility audit.
**Future scalability.** Net-weighting hooks (timing/congestion) are stage-local parameters, enabling future ML-guided weighting without pipeline restructuring.

### Stage D — Density Optimization
**Purpose.** Refine bin-level density distribution beyond Stage C's coarse convergence, targeting the configured density band uniformly across the die.
**Theory.** Iterative local density-penalty re-weighting pass on top of the Stage C solution.
**Engineering rationale.** Separating coarse convergence (Stage C) from fine density refinement (Stage D) allows independent tuning/measurement of each concern, improving debuggability of QoR regressions.
**Inputs.** Stage C continuous placement.
**Outputs.** Density-refined continuous placement; bin-density histogram.
**Dependencies.** Stage C.
**Runtime.** Tens of seconds to a few minutes.
**Memory.** Comparable to Stage C.
**Failure conditions.** Persistent local density overflow beyond configured threshold after maximum iterations.
**Validation.** Bin-wise density histogram within configured band for ≥ configured percentile of bins.
**Industrial notes.** Corresponds to `gpl`'s internal density-penalty iteration loop when configured for stricter uniformity than default.
**Reviewer expectations.** Histogram artifact archived.
**Future scalability.** Threshold externalized for dataset-diversity sweeps (loose vs. tight density targets).

### Stage E — Timing-Driven Optimization
**Purpose.** Re-weight net criticality using SDC-derived static timing estimates and re-optimize cell positions to reduce estimated critical-path length.
**Theory.** Incremental STA (via OpenSTA) on the current placement provides slack estimates; nets on the top-K critical paths receive increased weight in a subsequent bounded RePlAce re-solve.
**Engineering rationale.** Performing timing-awareness as an explicit, bounded, post-density-convergence pass (rather than folding it into Stage C) keeps the wirelength/density solver simple and isolates timing-driven movement for independent QoR attribution.
**Inputs.** Stage D placement; SDC; Liberty.
**Outputs.** Timing-weighted, re-optimized continuous placement; pre-CTS slack estimate report.
**Dependencies.** Stage D.
**Runtime.** Comparable to Stage D, plus incremental STA overhead.
**Failure conditions.** STA parse/constraint errors; non-convergence of the bounded re-solve.
**Validation.** Estimated worst slack does not regress relative to Stage D's non-timing-aware estimate.
**Industrial notes.** Analogous to OpenROAD's `gpl -timing_driven` mode combined with `sta` incremental analysis hooks.
**Reviewer expectations.** Slack histogram and top-K critical net list archived.
**Future scalability.** Top-K criticality threshold is a manifest parameter for ML-corpus timing-difficulty sweeps.

### Stage F — Congestion Optimization
**Purpose.** Estimate routing congestion (RUDY-style routing demand map) and apply bounded cell re-distribution to relieve high-demand bins prior to legalization.
**Theory.** A fast routing-demand estimator computes per-bin demand from net bounding boxes; bins exceeding configured supply are flagged, and local density-penalty weighting is increased in those bins for a bounded re-solve.
**Engineering rationale.** Congestion correction is placed after timing optimization (Stage E) and before legalization (Stage H) so that legalization operates on an already congestion-aware distribution rather than fighting congestion post-hoc.
**Inputs.** Stage E placement; routing-layer supply model from technology LEF.
**Outputs.** Congestion-relieved continuous placement; routing demand/supply overflow map.
**Dependencies.** Stage E.
**Runtime.** Tens of seconds.
**Failure conditions.** Residual overflow above configured threshold after maximum bounded-re-solve iterations.
**Validation.** Estimated overflow below configured threshold for ≥ configured percentile of bins.
**Industrial notes.** Corresponds to OpenROAD's RUDY-based congestion estimation utilities used ahead of `grt` (global routing), consumed here only as an estimator, not as full global routing (explicitly out of scope).
**Reviewer expectations.** Overflow heatmap archived.
**Future scalability.** Supply model is technology-parametric, preserving technology independence (Part 2, Objective 2).

### Stage G — Detailed Placement (Pre-Legalization Refinement)
**Purpose.** Perform local, still-near-continuous refinement (small-scale cell shifting) as a bridge between the analytical solution and discrete legalization.
**Theory.** Greedy local search minimizing incremental HPWL subject to soft non-overlap, preparing the solution for minimum-displacement legalization.
**Engineering rationale.** Directly legalizing the raw analytical output (skipping this bridge stage) produces larger legalization displacement and worse post-legalization HPWL; this stage reduces the legalization "distance to travel."
**Inputs.** Stage F placement.
**Outputs.** Refined near-legal continuous placement.
**Dependencies.** Stage F.
**Runtime.** Seconds to tens of seconds.
**Failure conditions.** Local search failing to reduce residual overlap below configured pre-legalization tolerance.
**Validation.** Residual overlap area below configured pre-legalization threshold.
**Industrial notes.** Corresponds to OpenDP's pre-legalization refinement pass.
**Reviewer expectations.** Pre/post refinement HPWL delta logged.
**Future scalability.** N/A structural — parameter-only tuning surface.

### Stage H — Legalization
**Purpose.** Snap all cells to legal sites/rows with zero residual overlap, honoring orientation and row-flip conventions, using minimum-displacement local search.
**Theory.** Formulated as an assignment problem: minimize total (or maximum) displacement subject to one-cell-per-site, row-height compatibility, and blockage-avoidance constraints; solved via OpenDP's row-based greedy/local-search legalizer.
**Engineering rationale.** Minimum-displacement is prioritized (over, e.g., minimum-runtime legalization) because it best preserves the wirelength/timing/congestion properties established by Stages C–G.
**Inputs.** Stage G placement; legal-site bitmap (Stage B).
**Outputs.** Fully legal placed DEF/ODB.
**Dependencies.** Stage G.
**Runtime.** Seconds to a few minutes depending on instance count and required displacement.
**Failure conditions.** Legalization failure (unassignable cells, insufficient legal sites, contradictory blockages).
**Validation.** Zero overlap; 100% site/row legality; orientation legality.
**Industrial notes.** Directly OpenDP's `dpl` legalizer as integrated in OpenROAD/OpenLane2 (`Odb.DetailedPlacement`).
**Reviewer expectations.** Displacement statistics (mean/max) archived as primary legalization-cost evidence.
**Future scalability.** Legalizer is swappable behind the same OpenDB interface without touching Stages A–G.

### Stage I — QoR Extraction
**Purpose.** Compute and serialize the complete placement QoR metric set (Part 10) from the final legal placement.
**Theory.** Post-hoc, read-only computation over the legalized OpenDB state; no cell movement occurs in this stage.
**Engineering rationale.** Isolating QoR extraction as a distinct, side-effect-free stage guarantees that QoR numbers reflect the exact legalized state validated in Stage H/J, with no possibility of measurement-induced drift.
**Inputs.** Legalized OpenDB/DEF.
**Outputs.** Placement QoR JSON (Part 10 schema).
**Dependencies.** Stage H.
**Runtime.** Seconds.
**Failure conditions.** Schema validation failure; missing metric computation.
**Validation.** JSON schema conformance check.
**Industrial notes.** Corresponds to OpenLane2's post-step metrics aggregation.
**Reviewer expectations.** QoR JSON is the primary artifact reviewers will inspect for reproducibility claims.
**Future scalability.** Schema is versioned to allow additive metric extension without breaking existing ML-consumer pipelines.

### Stage J — Placement Validation
**Purpose.** Final automated gate-check confirming the placement satisfies every objective in Part 2 before the pipeline is marked complete.
**Theory.** A deterministic checklist evaluator over the QoR JSON and legality report.
**Engineering rationale.** Centralizing all pass/fail logic in one final stage (rather than distributing accept/reject decisions across stages) gives a single, auditable PASS/FAIL record per run, which is the unit Part 16's Artifact Evaluation claims are built on.
**Inputs.** QoR JSON, legality report, all stage logs.
**Outputs.** PASS/FAIL verdict; validation report.
**Dependencies.** Stage I.
**Runtime.** Sub-second.
**Failure conditions.** Any Part 2 objective gate failing.
**Validation.** This *is* the validation stage; its own output is the validation record.
**Industrial notes.** Equivalent to OpenLane2's step-level `Metric` assertion checks aggregated into a single go/no-go.
**Reviewer expectations.** Validation report is what reviewers cite when confirming a design "passed placement" in the dataset.
**Future scalability.** Gate thresholds are manifest-driven, allowing stricter/looser corpora to be generated from the same codebase.

---

## PART 6 — PLACEMENT PLANNING

- **Placement utilization.** Defined as (total cell area)/(usable row area). Configured target range: 45%–75% depending on benchmark tier; utilization above ~80% is flagged as a legalization-risk zone and requires explicit manifest override.
- **Cell density.** Bin-local instantiation of utilization; tracked per Stage D bin grid (typically 1–4 row-heights per bin edge).
- **Whitespace.** The complement of utilization; explicitly reserved, not incidental — whitespace budget is planned per-design to accommodate legalization slack and future ECO headroom.
- **Cell padding.** Configurable left/right site-padding per cell (technology- and cell-class-dependent) to reserve pin-access and routing headroom; applied uniformly during legalization (Stage H) and factored into the padding-ratio QoR metric (Part 10).
- **Placement rows.** Treated as immutable resources inherited from floorplanning (Part 4); planning here concerns only *consumption* of row capacity, not row generation.
- **Fence regions.** Soft constraints restricting specific instance groups (e.g., hierarchical partitions) to sub-regions of the die; enforced as bounded re-solve constraints in Stages C–G and as hard constraints in Stage H.
- **Hard blockages.** Macro keepouts, IO keepouts, and PDK-mandated exclusion zones; absolutely prohibited for any cell origin.
- **Soft blockages.** Partial-density-allowed regions (e.g., reduced-density regions near power straps); enforced as density-penalty weighting rather than hard exclusion.
- **Placement regions.** Named sub-regions (e.g., per-hierarchy-block regions) used for fence-region and QoR-attribution bookkeeping.
- **Keepout interaction.** Legal-site bitmap (Stage B) is the single mechanism reconciling hard blockages, macro halos, and IO keepouts; no stage bypasses this bitmap.
- **Macro interaction.** Cells may not violate macro-declared halo margins; halo-adjacent legal sites are explicitly excluded from the Stage B bitmap.
- **Engineering tradeoffs.** Higher utilization reduces die area (cost) but increases legalization displacement and congestion risk (QoR risk); the placement configuration manifest exposes utilization as a first-class sweep parameter specifically to let the downstream ML corpus capture this tradeoff empirically rather than assuming a fixed operating point.

---

## PART 7 — GLOBAL PLACEMENT STRATEGY

**Analytical placement.** The global placement problem is relaxed from a discrete assignment problem to a continuous optimization over real-valued cell coordinates, solved by gradient-based methods rather than combinatorial search, trading exact legality (deferred to Stage H) for tractable scaling.

**Quadratic optimization.** An initial quadratic-wirelength relaxation (log-sum-exp or bound2bound net models) seeds the solver with a smooth, differentiable approximation of HPWL before the sharper electrostatic-density term is introduced.

**Electrostatic placement model.** Cell density is modeled as an electric charge density over the placement bin grid; the density-penalty gradient is derived from the resulting electrostatic potential field (RePlAce's core technique), providing a physically-motivated, smoothly differentiable spreading force.

**Wirelength minimization.** The primary driving objective term; computed as a smooth (differentiable) approximation of HPWL to remain compatible with gradient-based solving.

**Timing weighting.** Applied only from Stage E onward as a bounded re-weighting of net importance, not a change to the underlying solver formulation.

**Congestion weighting.** Applied only from Stage F onward, analogous in mechanism to timing weighting (bin-local density-penalty bias).

**Density balancing.** The Nesterov-accelerated solver alternates between wirelength-gradient steps and density-penalty-gradient steps until both converge within the Stage C/D tolerance bands.

**Anchor cells.** Fixed (immovable) cells — typically IO pads, pre-placed macros, and tie-cells — are excluded from the movable-instance set but retained in the wirelength/density computation as fixed obstacles/pin sources.

**Macro awareness.** Macros (already placed in Phase 14.6) act as fixed density obstacles in the electrostatic model, ensuring standard-cell spreading correctly avoids macro-occupied bins without requiring separate special-case logic.

**Net weighting.** Per-net scalar weights (default 1.0) are the single mechanism through which timing- and congestion-driven passes influence the solver, keeping the core solver formulation unchanged across Stages C, E, and F.

**Hierarchy preservation.** Where the manifest specifies hierarchy-aware fencing (Part 6), net-weighting and fence constraints jointly bias the solver to keep hierarchically-related instances spatially co-located, improving downstream floorplan-to-placement QoR correlation.

**Deterministic seed handling.** A single top-level seed (recorded in the manifest) is propagated to all stochastic elements of the solver (initial coordinate perturbation, any randomized tie-breaking in bin assignment); identical seed + identical inputs is required to reproduce bit-identical Stage C output.

**Engineering rationale.** Separating the *what* (wirelength + density objective, fixed across Stages C–F) from the *how much* (net weighting, varied per stage) is what allows this specification to add timing- and congestion-awareness without redefining the solver, which is essential for maintaining Part 2's determinism and reproducibility objectives across configuration sweeps.

---

## PART 8 — DETAILED PLACEMENT STRATEGY

**Legalization.** The discrete assignment of each cell to a unique legal site within a row-height-compatible row, formulated as a minimum-total-displacement (or minimum-max-displacement, per configuration) assignment problem.

**Cell shifting.** Local, row-preserving translation of a cell along its row to resolve overlap with a neighbor, applied greedily in ascending order of required displacement.

**Cell swapping.** Exchange of two same-row-height cells' positions when doing so reduces total displacement more than sequential shifting alone; used sparingly, bounded by a configured swap-search radius to keep legalization runtime deterministic and bounded.

**Cell mirroring.** Row-flip-consistent vertical mirroring (N↔FN, FS↔S) applied automatically per the alternating-row orientation convention; not a free optimization variable, but a fixed consequence of final row assignment.

**Site alignment.** Every legalized cell origin must coincide exactly with a legal site coordinate on the placement grid (Part 4); enforced as a hard post-condition checked in Stage J.

**Orientation.** Determined by row parity per the standard alternating-row (abutment-consistent) convention established in Phase 14.6; legalization must not violate this convention when reassigning rows.

**Padding.** Applied as reserved site-width margin around each cell during site-assignment search, per Part 6's padding configuration; increases effective cell footprint during legalization without altering the cell's declared LEF geometry.

**Pin accessibility.** Legalization search explicitly avoids site assignments that would place a cell's pin layer directly under a macro halo or blockage edge in a way that is known (from the technology LEF) to create unresolvable pin-access DRC risk; this is a heuristic pre-check, not a full DRC (DRC sign-off is out of scope).

**Incremental legalization.** Legalization proceeds row-by-row and bin-by-bin in a fixed deterministic order (left-to-right, bottom-to-top) so that the same input state always produces the same legalization decision sequence.

**Minimum displacement philosophy.** Displacement is the primary legalization cost function because it is the metric most directly correlated (empirically, in the RePlAce/OpenDP literature this flow derives from) with post-legalization wirelength and timing degradation relative to the Stage F pre-legalization estimate.

**Engineering rationale.** Bounding swap-search radius and fixing scan order trades a small amount of potential displacement-optimality for strict determinism — a deliberate, documented tradeoff consistent with Part 2 Objective 1 taking precedence over marginal QoR gains.

---

## PART 9 — PLACEMENT OPTIMIZATION (PRE-CTS ONLY)

**Timing-driven optimization.** Bounded, incremental re-weighting and re-solving (Stage E) using top-K critical-net identification from incremental STA; scope is strictly limited to cell repositioning — no buffer insertion/sizing that depends on clock structure is performed, since clock structure does not exist yet at this phase.

**Congestion optimization.** Bounded, incremental re-weighting and re-solving (Stage F) using RUDY-style demand estimation; scope is strictly limited to routing-layer-agnostic demand/supply estimation, not actual global routing.

**Wirelength refinement.** Ongoing secondary objective throughout Stages C, E, F, and G; measured and reported independently at each stage boundary to allow attribution of wirelength delta to each optimization pass.

**Buffer movement.** Existing pre-placed buffers (inserted by upstream synthesis-stage optimization, if any) are treated as ordinary movable standard cells during Stages C–H; no new buffer insertion occurs in this phase.

**Gate movement.** All combinational and sequential (non-clock-tree) standard cells are freely movable subject to fence/blockage constraints throughout Stages C–G, then discretely reassigned in Stage H.

**Incremental optimization.** Each of Stages E and F operates as a bounded incremental re-solve seeded from the immediately prior stage's solution, rather than a full re-run from Stage C, to keep runtime predictable and to preserve most of the prior stage's already-validated properties.

**ECO friendliness.** The stage-boundary QoR snapshots (emitted at the end of every stage, not only Stage I) are retained specifically so that a future ECO-style re-placement (out of scope for this phase, but anticipated in Part 1's future-scalability note) can resume from any intermediate stage rather than from Stage A.

**Power-awareness.** Where Liberty leakage/dynamic power data is available, Stage F's bounded re-solve may additionally down-weight high-leakage-cell relocation cost when doing so does not conflict with the primary congestion objective; this is a secondary, non-blocking heuristic and does not participate in the Part 2/Part 5-Stage-J pass/fail gating.

**Engineering rationale.** Confining all timing/congestion optimization strictly to bounded, incremental, clock-structure-agnostic passes is what keeps this phase's scope cleanly separated from Phase 14.8 (CTS), while still allowing pre-CTS placement to be timing- and congestion-aware — a documented industrial best practice, since post-CTS re-placement is far more expensive than getting placement approximately right pre-CTS.

---

## PART 10 — PLACEMENT QUALITY METRICS

Each metric below is emitted in the Stage I QoR JSON with: definition, importance, engineering rationale, measurement method, and ML relevance.

1. **Placement legality (bool + violation count).** *Definition:* fraction of instances satisfying site/row/orientation/non-overlap constraints. *Importance:* hard gating metric. *Rationale:* legality is a precondition for all downstream phases. *Measurement:* exhaustive geometric overlap and grid-alignment check. *ML relevance:* binary/near-binary feature useful for filtering corrupt corpus entries.
2. **HPWL.** *Definition:* sum over nets of half the bounding-box perimeter. *Importance:* primary wirelength proxy. *Rationale:* strongly correlated with routed wirelength and power. *Measurement:* direct geometric computation from legalized DEF. *ML relevance:* core regression target/feature for wirelength-prediction models.
3. **Estimated Steiner Wirelength.** *Definition:* RSMT (rectilinear Steiner minimal tree)-based wirelength estimate per net, summed. *Importance:* tighter wirelength proxy than HPWL for multi-pin nets. *Rationale:* HPWL under-estimates true wirelength for high-fanout nets. *Measurement:* fast RSMT heuristic (e.g., FLUTE-class algorithm). *ML relevance:* secondary wirelength feature, useful for fanout-sensitivity studies.
4. **Average Cell Displacement.** *Definition:* mean Euclidean/Manhattan distance between Stage G (pre-legalization) and Stage H (post-legalization) positions. *Importance:* legalization-cost proxy. *Rationale:* correlates with QoR degradation from the analytical optimum. *Measurement:* direct coordinate delta. *ML relevance:* feature for predicting legalization-induced QoR loss.
5. **Maximum Cell Displacement.** *Definition:* max of the same distribution. *Importance:* worst-case legalization stress indicator. *Rationale:* a single large-displacement outlier can indicate a local blockage/density conflict. *Measurement:* direct coordinate delta, max-reduced. *ML relevance:* outlier-detection feature.
6. **Density.** *Definition:* per-bin utilization at Stage I. *Importance:* routability/legalizability proxy. *Rationale:* directly tied to Objective 7 (Part 2). *Measurement:* bin-grid area accumulation. *ML relevance:* spatial feature map (image-like) for CNN-based QoR predictors.
7. **Local Density Overflow.** *Definition:* fraction of bins exceeding target density band. *Importance:* direct legality-risk and congestion-risk indicator. *Rationale:* high-overflow bins are the primary source of legalization and routing failure. *Measurement:* bin-wise threshold comparison. *ML relevance:* classification feature for failure-prediction models.
8. **Congestion Estimate.** *Definition:* RUDY-style routing demand per bin. *Importance:* pre-routing routability proxy. *Rationale:* the earliest, cheapest congestion signal available in the flow. *Measurement:* net-bounding-box-based demand accumulation. *ML relevance:* spatial feature map for routability prediction.
9. **Timing Estimate.** *Definition:* placement-stage STA slack distribution (pre-CTS, ideal-clock assumption). *Importance:* early timing-risk indicator. *Rationale:* correlates directionally (not exactly) with post-CTS/post-route timing. *Measurement:* incremental OpenSTA run on legalized netlist with ideal clocks. *ML relevance:* regression target for timing-prediction research.
10. **Slack Estimate.** *Definition:* worst negative slack (WNS) and total negative slack (TNS) at placement stage. *Importance:* summary timing-risk scalars. *Rationale:* standard industry timing summary statistics. *Measurement:* derived from Timing Estimate. *ML relevance:* scalar regression targets.
11. **Critical Path Estimate.** *Definition:* identity and length (stage count, estimated delay) of the current worst path. *Importance:* diagnostic/interpretability metric. *Rationale:* enables path-level QoR attribution. *Measurement:* STA path report extraction. *ML relevance:* structured feature for path-classification models.
12. **Pin Accessibility.** *Definition:* fraction of instances flagged by the Stage H heuristic pre-check (Part 8) as pin-access-risk. *Importance:* early routability-risk proxy at the cell level. *Rationale:* cheap proxy for a DRC concern that is expensive to check exactly pre-routing. *Measurement:* heuristic geometric check against halo/blockage edges. *ML relevance:* auxiliary classification feature.
13. **Padding Ratio.** *Definition:* (padded footprint area)/(declared LEF footprint area), aggregate. *Importance:* whitespace-consumption accounting metric. *Rationale:* explains part of the utilization-vs-legalizability tradeoff (Part 6). *Measurement:* direct configuration-derived computation. *ML relevance:* control feature for tradeoff studies.
14. **Routing Demand.** *Definition:* aggregate per-layer routing track demand estimate. *Importance:* component of congestion estimate. *Rationale:* layer-resolved detail beyond the aggregate congestion estimate. *Measurement:* per-layer RUDY-style accumulation. *ML relevance:* multi-channel spatial feature map.
15. **Routing Supply.** *Definition:* per-layer available routing track supply from technology LEF. *Importance:* denominator for overflow computation. *Rationale:* technology-dependent constant needed to normalize demand. *Measurement:* direct LEF-derived computation. *ML relevance:* normalization feature, technology-conditioning input.
16. **Estimated Routing Overflow.** *Definition:* max(0, demand − supply) aggregated per bin/layer. *Importance:* primary pre-routing routability-risk scalar. *Rationale:* direct proxy for Stage F's congestion-optimization target. *Measurement:* derived from Routing Demand/Supply. *ML relevance:* primary regression/classification target for routability-prediction research.
17. **Placement Runtime.** *Definition:* wall-clock time per stage and total. *Importance:* engineering/scalability metric. *Rationale:* required for the runtime-expectation claims in Part 1. *Measurement:* stage-boundary timestamps. *ML relevance:* auxiliary feature for runtime-prediction/scheduling research.
18. **Memory Usage.** *Definition:* peak RSS per stage and total. *Importance:* engineering/scalability metric. *Rationale:* required for the memory-expectation claims in Part 1. *Measurement:* periodic RSS sampling. *ML relevance:* auxiliary feature for resource-prediction research.
19. **Cell Movement Statistics.** *Definition:* distribution (mean/median/std/max) of per-stage cell displacement across Stages C→D→E→F→G→H. *Importance:* stage-attribution diagnostic. *Rationale:* isolates which optimization pass contributed most movement, aiding QoR-regression debugging. *Measurement:* per-stage coordinate deltas. *ML relevance:* stage-attribution feature set.
20. **Macro Interaction Statistics.** *Definition:* count and total area of standard cells adjacent to (within a configured margin of) macro halos, plus any halo-margin near-violations flagged. *Importance:* macro-standard-cell interface QoR indicator. *Rationale:* macro-adjacent regions are a common source of legalization and routing difficulty. *Measurement:* geometric proximity computation against macro halo boundaries. *ML relevance:* feature for macro-heavy-design QoR studies.
21. **Additional meaningful metrics** (reserved schema extension fields): net-count-weighted density skew, row-utilization variance, fence-region-local utilization, and configuration-echoed parameters (target density, utilization) for direct feature-label pairing in ML corpus construction.

---

## PART 11 — OUTPUTS

- **Placed DEF.** Final legalized DEF, schema-identical in convention to the Phase 14.6 floorplan DEF plus fully-specified instance placements.
- **Placed ODB.** Binary OpenDB snapshot of the same final state, used as the direct input to Phase 14.8 (CTS) without requiring DEF re-parsing.
- **Placement reports.** Human-readable per-stage summary reports (text/log) mirroring the QoR JSON for manual review.
- **Placement QoR JSON.** Schema-validated, versioned JSON containing every metric in Part 10.
- **Visualization.** Bin-density heatmap, congestion heatmap, and displacement-vector overlay images (PNG/SVG), generated from Stage I data for both manual review and dataset documentation.
- **Metadata.** Design name, benchmark ID, technology node, tool versions, seed, timestamps.
- **Logs.** Full stage-by-stage execution logs, retained unredacted for Artifact Evaluation.
- **Manifest updates.** Placement-stage completion status, output artifact hashes, and stage timing appended to the running project manifest.
- **Configuration snapshots.** Frozen copies of every configuration file consumed by this phase's run.

**Engineering rationale.** Emitting both DEF and ODB (rather than DEF alone) avoids a redundant re-parse step at the start of Phase 14.8 and preserves any OpenDB-internal metadata not fully representable in DEF, supporting the Stage-to-Stage database-continuity principle established in Part 4.

**Validation.** All outputs are validated against their respective schemas/formats before the run is marked complete; a run producing a Stage J PASS verdict but failing output schema validation is itself marked FAIL and logged to the failure ledger.

---

## PART 12 — FAILURE HANDLING

| Failure Mode | Detection Point | Recovery Strategy |
|---|---|---|
| Placement overlap | Stage H/J geometric check | Re-run Stage G/H with increased legalization search radius; if persistent, flag design as `LEGALIZATION_INFEASIBLE` |
| Legalization failure | Stage H | Attempt relaxed swap-radius legalization pass; if still failing, escalate to `LEGALIZATION_FAILURE` and halt |
| Density overflow | Stage D/F | Increase density-penalty weighting and re-run bounded re-solve up to configured max iterations; else flag `DENSITY_OVERFLOW` |
| Routing overflow estimate | Stage F/I | Increase congestion-weighting and re-run bounded re-solve; else flag `CONGESTION_RISK` (non-fatal, logged as WARN if below hard threshold) |
| Timing infeasibility | Stage E/I | Re-run with increased top-K criticality weighting; if WNS still regresses beyond tolerance, flag `TIMING_RISK` |
| Off-grid placement | Stage H/J | Immediate hard failure — indicates a legalizer or database defect; halts pipeline, escalated as `DATABASE_INTEGRITY_FAILURE` |
| Site violation | Stage H/J | Same as off-grid; hard failure |
| Orientation violation | Stage H/J | Same as off-grid; hard failure |
| Database corruption | Any stage | Immediate halt; manifest marks run `CORRUPTED`; no partial artifacts are promoted to the deliverable corpus |
| Manifest handling | N/A (cross-cutting) | Every failure updates the manifest's failure ledger with stage, error class, and timestamp before halting |

**Engineering rationale.** Failures are stratified into *recoverable-via-bounded-retry* (density, congestion, timing) and *hard/fatal* (overlap after retry, off-grid, site/orientation, corruption) because conflating these would either mask real legality defects behind retries or waste runtime retrying unrecoverable database defects.

**Logging.** Every failure emits a structured log entry (stage, error class, relevant metric values, retry count) to both the run-local log and the project-level failure ledger, the latter being a first-class Part 15 deliverable for ML corpus researchers who need negative (failed) examples, not only positive ones.

---

## PART 13 — AUTOMATION

- **`placement.py`** — top-level orchestrator invoking Stages A–J in order, reading the placement configuration manifest and writing all Part 11 outputs.
- **`global_place.py`** — invokes Stages C–D (global placement + density optimization) as an isolable sub-pipeline for standalone debugging/tuning.
- **`detailed_place.py`** — invokes Stages E–G (timing, congestion, pre-legalization refinement) as an isolable sub-pipeline.
- **`legalize.py`** — invokes Stage H alone, supporting rapid legalizer-only re-runs against a previously computed Stage G snapshot.
- **`placement_opt.py`** — utility entry point for re-running only Stages E/F with alternate weighting configurations against a fixed Stage D snapshot (used heavily for ML-corpus configuration sweeps).
- **`validate_placement.py`** — invokes Stage I–J standalone against any previously produced placed ODB, for post-hoc re-validation without re-running the full pipeline.

**Resume capability.** Every script checkpoints OpenDB state at its stage boundary; `placement.py` can resume from any completed stage's checkpoint rather than restarting from Stage A, keyed by the manifest's stage-completion record.

**Parallel execution.** Independent designs (distinct netlist/floorplan pairs) are trivially parallelizable across processes/nodes; within a single design, Stages A–J remain strictly sequential (no intra-design stage parallelism), preserving determinism.

**Cluster execution.** The manifest-driven checkpoint scheme supports a simple job-array submission model (one job per design × configuration-sweep combination) on SLURM-like schedulers, with `placement.py` as the per-job entry point.

**Manifest-driven execution.** All scripts read their full parameter set from the frozen configuration snapshot (Part 3/11), never from ad hoc CLI flags alone, so that any job can be replayed byte-for-byte from its manifest entry alone.

**Dry-run mode.** All scripts support a `--dry-run` flag that performs Stage A input validation and configuration echoing without executing any placement computation, used for fast manifest-correctness checking across large sweep batches.

**Engineering rationale.** Exposing per-stage-group entry points (`global_place.py`, `detailed_place.py`, `legalize.py`, `placement_opt.py`) in addition to the monolithic `placement.py` directly supports the ML-corpus-generation use case, where researchers frequently need to re-sweep only the timing/congestion weighting (Stages E/F) or only the legalizer (Stage H) without paying the full Stage A–D cost repeatedly.

---

## PART 14 — REPOSITORY STRUCTURE

```
phase14_7_standard_cell_placement/
├── configs/
│   ├── placement_default.yaml
│   ├── placement_density_sweep/
│   │   ├── util_45.yaml
│   │   ├── util_60.yaml
│   │   └── util_75.yaml
│   └── technology/
│       ├── sky130.yaml
│       └── gf180mcu.yaml
├── scripts/
│   ├── placement.py
│   ├── global_place.py
│   ├── detailed_place.py
│   ├── legalize.py
│   ├── placement_opt.py
│   └── validate_placement.py
├── stages/
│   ├── stage_a_init.py
│   ├── stage_b_rows.py
│   ├── stage_c_global_place.py
│   ├── stage_d_density_opt.py
│   ├── stage_e_timing_opt.py
│   ├── stage_f_congestion_opt.py
│   ├── stage_g_predetail_refine.py
│   ├── stage_h_legalize.py
│   ├── stage_i_qor_extract.py
│   └── stage_j_validate.py
├── schema/
│   ├── placement_qor.schema.json
│   └── manifest.schema.json
├── runs/
│   └── <design>/<config_id>/<run_id>/
│       ├── placed.def
│       ├── placed.odb
│       ├── qor.json
│       ├── reports/
│       ├── logs/
│       ├── visualization/
│       │   ├── density_heatmap.png
│       │   ├── congestion_heatmap.png
│       │   └── displacement_vectors.svg
│       └── manifest_snapshot.json
├── failure_ledger/
│   └── <design>/<config_id>/<run_id>/failure.json
└── docs/
    └── phase14_7_specification.md
```

**Engineering rationale.** The `runs/<design>/<config_id>/<run_id>/` hierarchy directly encodes the three axes (design, configuration sweep point, run/seed) that an ML corpus needs for feature/label pairing, keeping the repository structure itself a machine-readable index rather than requiring a separate database.

---

## PART 15 — DELIVERABLES

1. **Placement flow.** The full Stage A–J pipeline implementation (scripts + stage modules) as described in Parts 5 and 13.
2. **Placed DEF corpus.** The complete set of legalized DEF files across all design × configuration × seed combinations executed for this project.
3. **Placed ODB corpus.** The corresponding binary OpenDB snapshots.
4. **QoR dataset.** The aggregate Part 10 metric set across the full corpus, in a single indexed dataset file (in addition to per-run JSON) suitable for direct ML consumption.
5. **Failure ledger.** The complete record of all failed runs (Part 12) with stage, error class, and metric context, retained as first-class negative-example data.
6. **Metadata.** Full manifest set across the corpus (design/config/seed/tool-version indexing).
7. **Visualization corpus.** All density/congestion/displacement visualizations across the full run set.
8. **Configuration snapshots.** All frozen configuration files across the full sweep space.

**Engineering rationale.** Treating the failure ledger as a formal deliverable (rather than discarding failed runs) is deliberate: failure-mode data is directly useful for training failure-prediction classifiers, a stated downstream research goal of this project's broader DTCO/ML objective.

---

## PART 16 — PUBLICATION READINESS

**IEEE reproducibility.** Every deliverable in Part 15 is produced under the determinism guarantees of Part 2 Objective 1 and Part 7's deterministic seed handling, satisfying IEEE's expectation that reported QoR numbers be independently regenerable from the released artifact set.

**Artifact Evaluation.** The repository structure (Part 14), manifest schema, and dry-run mode (Part 13) are specifically designed to satisfy typical AE-track requirements: a reviewer can execute `validate_placement.py` against any released placed ODB to independently re-derive and confirm the published QoR JSON without re-running the full multi-minute pipeline.

**Industrial deployment.** Because the pipeline is built directly on OpenROAD/OpenLane2 primitives with no proprietary substitutions, the specification is directly portable to industrial open-source-EDA-based flows without translation.

**Zenodo compatibility.** The `runs/` and `failure_ledger/` hierarchies are structured as flat, self-describing directory trees suitable for direct Zenodo archival with manifest-derived checksums as the integrity-verification mechanism.

**Reviewer expectations.** Reviewers should expect, and this specification provides: explicit tool/version pinning, explicit seed/config provenance per run, a versioned QoR schema, and an explicit, auditable PASS/FAIL gate (Stage J) rather than qualitative claims of placement quality.

**Future scalability.** This phase's manifest-driven, stage-checkpointed architecture is designed to scale unmodified from single-design debugging to full corpus-scale generation runs, and hands off cleanly — via the Placed ODB/DEF and QoR JSON — to Phase 14.8 (Clock Tree Synthesis), which will consume this phase's legalized placement as its own validated starting state without needing to re-derive any placement-stage information.

---

*End of Phase 14.7 — Standard-Cell Placement Specification. This document establishes the validated legal placement and complete placement QoR record that Phase 14.8 (Clock Tree Synthesis) will consume as its starting input, consistent with the phase-boundary discipline established in Phase 14.5 and Phase 14.6.*
