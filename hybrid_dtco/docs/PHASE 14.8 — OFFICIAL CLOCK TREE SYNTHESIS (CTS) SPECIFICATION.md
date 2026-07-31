# PHASE 14.8 — OFFICIAL CLOCK TREE SYNTHESIS (CTS) SPECIFICATION

**Paper:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target Venue:** IEEE International Conference on Microelectronics (ICM 2026)
**Scope Boundary:** This phase begins at the VALIDATED LEGAL STANDARD-CELL PLACEMENT produced by Phase 14.7 and terminates at a VALIDATED POST-CTS CLOCK TREE with complete CTS QoR extraction. Clock routing, signal routing, parasitic extraction, STA sign-off, DRC/LVS sign-off, IR-drop analysis, electromigration (EM) analysis, and tapeout are explicitly out of scope and are deferred to Phase 14.9 onward. Clock optimization as defined in this phase terminates when the clock tree is topologically complete and buffer-legalized; it does not extend into post-route clock optimization.

---

## PART 1 — CTS PHILOSOPHY

**Purpose.** Clock Tree Synthesis constructs a physically realizable, buffered distribution network that delivers the clock signal from a single clock root to every sequential clock sink (flip-flop, latch, clock-gating cell, integrated clock-gate cell) in the design, subject to skew, latency, slew, and fanout constraints established by the SDC and by the timing budget carried forward from Phase 14.7's pre-CTS slack estimate.

**Theory.** CTS is formulated as a constrained tree/DAG construction problem over the fixed sink locations produced by placement: given a set of sink coordinates and required-arrival-time (or balance) constraints, construct a topology (H-tree, X-tree, spine, or hybrid) and insert buffering such that induced insertion delay, skew, and slew fall within configured bounds, while keeping total buffer count, capacitance, and area consumption minimized as secondary objectives.

**Engineering rationale.** CTS is treated as a phase strictly downstream of placement (never interleaved with global/detailed placement) because clock-sink locations must be geometrically fixed and legal before a topology-aware, capacitance-balanced tree can be constructed; attempting clock synthesis against a non-final placement would invalidate every skew/latency computation as soon as any subsequent placement perturbation occurred. This ordering also matches the industrial OpenROAD/OpenLane2 flow, in which `cts` strictly follows `Odb.DetailedPlacement`.

**Inputs.** Validated placed DEF/ODB (Phase 14.7 output), placement QoR record, Liberty timing/power views, SDC (clock definitions, uncertainty, latency constraints), CTS configuration manifest, clock-buffer library metadata.

**Outputs.** Post-CTS DEF/ODB (buffered, buffer-legalized clock network with topology recorded), CTS QoR JSON, clock-tree visualization artifacts, updated manifest/config snapshot.

**Dependencies.** Requires a Phase 14.7 run that produced a Stage J PASS verdict (100% placement legality, density/congestion/timing objectives satisfied); a placement that failed Phase 14.7 validation must not be admitted into this phase.

**Runtime expectations.** For benchmark designs in the 10K–500K sink range on a 16-thread commodity workstation, CTS construction and buffer legalization together are expected to complete in 1–15 minutes, scaling primarily with sink count and target skew tightness (tighter skew targets require deeper trees and more balancing iterations).

**Memory expectations.** Peak RSS is dominated by the sink-count-proportional clustering/tree-construction data structures and the incremental STA session held open for slew/latency estimation; expected range 300 MB–4 GB for the benchmark corpus sizes targeted in this project.

**Failure conditions.** Non-convergent skew balancing, buffer-legalization failure (no legal site available for an inserted buffer), fanout violations that cannot be resolved within the configured maximum buffer-insertion depth, and slew violations that persist after maximum re-buffering iterations are all treated as hard failures routed to the failure ledger (Part 12).

**Validation.** A clock tree is accepted only if it passes all gates in Part 5 Stage J: 100% sink connectivity, zero unbuffered-fanout violations, global and local skew within configured bounds, slew within configured bounds at every stage of the tree, and 100% buffer legality.

**Industrial notes.** This specification mirrors OpenROAD's TritonCTS 2.0 engine as orchestrated by OpenLane2's `Odb.CTS` step, chosen for the same reproducibility, open-licensing, and deterministic-seeding rationale established in Phase 14.6 and Phase 14.7.

**Reviewer expectations.** Reviewers evaluating this phase under IEEE ICM Artifact Evaluation criteria will expect explicit clock-buffer library identification, explicit skew/latency/slew targets and their SDC provenance, and a QoR record sufficient to reproduce reported skew/latency/buffer-count numbers without re-running the full flow.

**Future scalability.** The staged architecture (Part 5) is designed to extend from single-clock-domain debug designs to multi-clock-domain, multi-corner CTS runs required for full ML-corpus generation without structural modification — only manifest-level clock-domain enumeration and parallelism (Part 13) change.

---

## PART 2 — OBJECTIVES

1. **Deterministic clock tree construction.** Identical inputs (placed DEF, SDC, buffer library, config, seed) must produce a bit-identical post-CTS DEF across runs and machines. *Rationale:* determinism is a non-negotiable precondition for ML dataset generation and IEEE reproducibility, carried forward unchanged from Phase 14.7 Objective 1. *Validation:* checksum comparison of post-CTS DEF across ≥3 independent re-runs.
2. **Technology independence.** Clock topology selection, buffer-sizing rules, and QoR schema must be expressible without hard-coding a specific PDK or a specific clock-buffer cell name. *Rationale:* enables corpus generation across multiple technology nodes and buffer libraries without flow rewrites. *Validation:* successful execution of the identical pipeline against ≥2 distinct open PDKs with distinct clock-buffer cell sets.
3. **Reproducibility.** Every run must emit a self-contained configuration snapshot (including the resolved buffer library and skew/latency targets) sufficient to reconstruct the run. *Rationale:* required for Zenodo/Artifact Evaluation packaging. *Validation:* fresh-environment replay from snapshot alone.
4. **Complete sink connectivity.** 100% of clock sinks declared in the SDC clock definition must be reachable from the clock root through the constructed tree. *Rationale:* an unconnected sink is a functional failure, not merely a QoR degradation. *Validation:* exhaustive sink-reachability graph traversal (Part 5, Stage J).
5. **Skew-bounded balancing.** Global skew and local (register-pair) skew must fall within configured bounds derived from the SDC clock uncertainty and the design's timing budget. *Rationale:* skew directly consumes setup/hold margin; unbounded skew invalidates the Phase 14.7 pre-CTS slack estimate. *Validation:* global/local skew histogram check against configured thresholds.
6. **Latency-bounded insertion delay.** Clock insertion delay (root-to-sink propagation) must remain within the configured latency budget. *Rationale:* excessive insertion delay increases clock-network power and can violate SDC-declared latency constraints used by upstream STA budgeting. *Validation:* per-sink latency distribution check.
7. **Slew-controlled buffering.** Clock-net transition time (slew) at every net segment of the tree must remain within the configured slew bound at every buffering stage. *Rationale:* excessive slew degrades downstream flip-flop setup/hold characterization validity and increases short-circuit power. *Validation:* per-net slew check via incremental STA at each construction stage.
8. **Fanout-bounded buffering.** No clock-net segment may exceed the configured maximum fanout before a buffer/inverter is inserted. *Rationale:* uncontrolled fanout degrades slew and skew simultaneously and is the primary driver of buffer-insertion decisions. *Validation:* per-segment fanout count check.
9. **Buffer legality.** 100% of inserted clock buffers/inverters must be placed on legal sites with zero overlap, consistent with Phase 14.7's legality definition. *Rationale:* an illegally placed buffer invalidates downstream routing exactly as an illegally placed standard cell would. *Validation:* automated legality checker identical in mechanism to Phase 14.7 Stage H/J.
10. **QoR completeness.** Every run must emit the full metric set defined in Part 10 with no missing fields. *Rationale:* incomplete QoR breaks downstream ML pipelines that consume this data as feature vectors. *Validation:* schema validation against the fixed CTS QoR JSON schema.

**Engineering rationale (aggregate).** These ten objectives are jointly necessary and mutually constraining in the same manner established in Phase 14.7 Part 2: connectivity without legality yields a functionally complete but physically unrealizable tree; skew-bounding without determinism yields non-reproducible research claims. The objective set is evaluated as a conjunction; any single failure marks the run FAIL.

**Validation.** A CTS run is marked PASS only if all ten objectives independently pass their respective gates (Part 5, Stage J); any single failure routes to Part 12 failure handling.

**Industrial notes.** These objectives correspond directly to the acceptance criteria used in OpenROAD-derived industrial flows (TritonCTS 2.0 skew/slew/fanout targets, OpenDP-based buffer legalization) and are not project-specific inventions.

**Future scalability.** Objective thresholds (skew bound, latency budget, slew bound, fanout limit) are externalized to the CTS configuration manifest (Part 3) so that objective *definitions* remain fixed while objective *thresholds* can be swept for ML dataset diversity generation, mirroring the utilization-sweep pattern established in Phase 14.7 Part 6.

---

## PART 3 — INPUTS

| Input | Description | Format | Source |
|---|---|---|---|
| Validated Placed DEF | Legalized standard-cell placement, all instance positions final | DEF 5.8 | Phase 14.7 output |
| Placed ODB | Binary OpenDB database mirroring the placed DEF | `.odb` | Phase 14.7 output |
| Placement QoR | Pre-CTS slack estimate, congestion estimate, displacement statistics | JSON | Phase 14.7 output |
| Liberty | Timing/power views for standard cells and clock-buffer/inverter cells | `.lib`/`.lib.gz` | PDK |
| SDC | Clock definitions, clock uncertainty, clock latency constraints, generated clocks | SDC | Upstream constraint phase |
| Clock buffer library metadata | Enumerated clock-capable buffer/inverter cells with drive strength, input capacitance, characterized slew/delay tables | JSON/LEF+Liberty derived | PDK, curated by this phase |
| CTS configuration | Target skew, target latency, target slew, max fanout, topology preference (H-tree/X-tree/spine), useful-skew policy | YAML/JSON | This phase, user/manifest-supplied |
| Benchmark metadata | Design name, benchmark suite ID, technology node ID | JSON | Project-level manifest |
| Manifest | Run identifier, timestamp, tool versions, seed | JSON | Auto-generated |
| Configuration snapshots | Frozen copy of all config files used in the run | Directory snapshot | Auto-generated |

**Engineering rationale.** As in Phase 14.7 Part 3, every input is versioned and hashed at ingestion time so the manifest can later prove exactly which artifact set produced a given clock tree, satisfying both determinism (Part 2, Objective 1) and Artifact Evaluation requirements (Part 16). The clock buffer library metadata is treated as a distinct, explicitly curated input (rather than an implicit subset of the technology Liberty) because CTS-specific characterization data (drive-strength ladder, clock-cell-only slew tables) must be unambiguous and versioned independently of the general standard-cell library.

**Validation.** Input ingestion performs: (a) DEF/Liberty/SDC syntactic validation via OpenDB/OpenSTA parser round-trip, (b) placement-legality re-confirmation (re-checking the Phase 14.7 Stage J PASS record has not been invalidated by any intervening manual edit), (c) SDC clock-definition completeness check (every declared clock has a resolvable source pin and a non-empty sink set), (d) hash verification against manifest-recorded hashes for any resumed/rerun job.

**Failure conditions.** Missing or unparsable DEF/Liberty/SDC; a placed DEF whose Phase 14.7 legality record cannot be reconfirmed; an SDC clock definition with an unresolvable source or empty sink set; missing or malformed CTS configuration; hash mismatch on resume. All input-validation failures are logged as `STAGE_A_INPUT_FAILURE` and halt before any tree-construction computation begins.

---

## PART 4 — CTS ENVIRONMENT

**OpenROAD.** Provides the core CTS engine used in this specification: TritonCTS 2.0 (`cts` command), which performs clustering-based clock-tree topology construction, buffer insertion/sizing, and skew balancing directly against the OpenDB database inherited from Phase 14.7.

**OpenLane2.** Supplies the orchestration layer (`Odb.CTS` step) that sequences CTS as a manifest-driven, resumable step following `Odb.DetailedPlacement`, with per-step artifact snapshotting consistent with the pattern established in Phase 14.6 and Phase 14.7.

**OpenDB.** The shared physical database used as the canonical intermediate representation for reading the placed design and writing the buffered clock network, avoiding lossy DEF round-trips between internal CTS stages, exactly as in Phase 14.7 Part 4.

**OpenSTA.** The static timing analysis engine invoked incrementally throughout CTS construction (not merely at the end) to provide slew, latency, and skew feedback that drives buffer insertion and sizing decisions; OpenSTA is also the tool used for the final post-CTS timing-estimate QoR extraction (Part 10).

**TritonCTS 2.0.** The specific clustering-and-balancing algorithm underlying OpenROAD's `cts` command: sinks are recursively clustered (typically via a bottom-up, capacitance- and slew-aware clustering procedure), buffers are inserted at cluster centroids, and the resulting topology is iteratively balanced to meet skew targets.

**Coordinate system.** Cartesian, origin at core-area lower-left corner, units in Database Units (DBU) — inherited unchanged from Phase 14.7's placement, consistent with the coordinate-system continuity principle established across all phases of this project.

**Database Units.** Fixed at the PDK-declared DBU-per-micron, inherited unchanged from the placed design; no re-scaling occurs at CTS.

**Placement Grid / Sites / Rows.** Inherited unchanged from Phase 14.7; newly inserted clock buffers/inverters must be legalized onto this same grid using the identical site/row/legality definitions established in Phase 14.7 Part 4, ensuring buffer legalization (Part 8) is mechanically consistent with standard-cell legalization.

**Clock Root.** The design's clock source pin as declared in the SDC `create_clock` command (typically a top-level clock port or a PLL/clock-generator macro output pin), treated as a fixed, immovable coordinate for tree-construction purposes.

**Clock Sinks.** The complete set of clock pins on sequential elements (flip-flops, latches, integrated clock gating cells) and any explicitly declared generated-clock sink points, as enumerated from the SDC clock definition intersected with the placed netlist's sequential-cell clock-pin set.

**Clock Nets.** The set of nets belonging to the clock SDC definition (the root net and every net introduced by subsequent buffer/inverter insertion), tracked distinctly from signal nets throughout this phase and explicitly excluded from any signal-routing consideration (out of scope, Phase 14.9+).

**Placement Constraints.** Fence regions, keepout margins, and macro halos inherited from Phase 14.7 apply identically to inserted clock-buffer legalization; no clock-specific placement constraint relaxation is permitted.

**Technology Constraints.** Minimum spacing, site definitions, and any PDK-specific clock-buffer-adjacent DRC rules (e.g., required clock-buffer-to-clock-buffer spacing for shielding provisions, discussed in Part 8) as declared in the technology LEF and clock buffer library metadata.

**Engineering rationale.** Reusing Phase 14.7's OpenDB-based coordinate system, grid, and legality mechanism without modification is a deliberate architectural choice: it guarantees that buffer legalization in this phase is not a parallel, potentially inconsistent re-implementation of placement legality, but the identical mechanism applied to a larger instance set (original standard cells plus newly inserted clock buffers).

**Industrial notes.** This environment definition mirrors OpenLane2's default CTS configuration, deviating only in explicit configuration exposure (Part 3) needed for ML-corpus parameter sweeps, consistent with the Phase 14.7 environment specification pattern.

**Future scalability.** Because the CTS engine boundary is OpenDB-based rather than file-based, swapping in an alternative clock-tree synthesis engine (e.g., a learned/ML-guided topology selector) in a future phase requires only that it read/write the same OpenDB schema — the staged architecture (Part 5) does not need to change, mirroring the extensibility argument made in Phase 14.7 Part 4.

---

## PART 5 — CTS ARCHITECTURE

The CTS stage is a deterministic ten-stage pipeline (Stage A–J). Each stage consumes the OpenDB state emitted by the prior stage and emits an updated OpenDB state plus a stage-local log/QoR fragment, in direct structural parallel with Phase 14.7 Part 5.

### Stage A — Database Initialization
**Purpose.** Load placed ODB, Liberty (standard cell + clock buffer), SDC, and clock buffer library metadata into a single consistent OpenDB/OpenSTA session.
**Theory.** Establishes the shared in-memory representation all subsequent stages operate on, identical in role to Phase 14.7 Stage A.
**Engineering rationale.** A single initialization point guarantees every stage sees an identical starting database, required for determinism.
**Inputs.** All Part 3 inputs.
**Outputs.** Initialized OpenDB/OpenSTA session; input-validation report.
**Dependencies.** None (first stage).
**Runtime.** Seconds to low tens of seconds depending on netlist and clock-buffer-library size.
**Memory.** Proportional to design size; dominated by Liberty timing-arc data for the combined standard-cell and clock-buffer libraries.
**Failure conditions.** Parse errors, unresolved clock source/sink pins, missing clock-buffer characterization data.
**Validation.** Sink count cross-checked against SDC clock-definition-derived expectation; every declared clock resolves to exactly one source pin.
**Industrial notes.** Mirrors OpenLane2's `Odb.CTS` initialization sub-step.
**Reviewer expectations.** Exact tool/library versions logged, including clock-buffer library revision.
**Future scalability.** Supports multi-clock-domain initialization (multiple independent `create_clock` definitions processed as parallel sink sets within the same session) without structural change.

### Stage B — Clock Root and Sink Enumeration
**Purpose.** Formally enumerate the clock root coordinate and the complete, deduplicated clock-sink coordinate set for each declared clock domain.
**Theory.** Treats root/sink enumeration as a distinct, auditable step separate from topology construction, so that connectivity validation (Stage J) has a fixed ground-truth sink set to check against.
**Engineering rationale.** Explicit enumeration catches SDC/netlist mismatches (e.g., a sequential cell whose clock pin is not actually reachable from the declared clock source due to an upstream gating structure) before expensive tree construction is attempted.
**Inputs.** Initialized OpenDB/OpenSTA session, SDC clock definitions.
**Outputs.** Per-clock-domain root coordinate; per-clock-domain deduplicated sink coordinate list; sink-count QoR fragment.
**Dependencies.** Stage A.
**Runtime.** Sub-second to a few seconds.
**Memory.** Negligible relative to other stages.
**Failure conditions.** Zero-sink clock domain; unresolvable root; sink pin not electrically connected to the declared clock net.
**Validation.** 100% of enumerated sinks trace back to the declared clock root through the pre-CTS (unbuffered) netlist connectivity graph.
**Industrial notes.** Corresponds to TritonCTS 2.0's internal sink-collection pre-pass.
**Reviewer expectations.** Sink list hash recorded for reproducibility.
**Future scalability.** Extensible to generated-clock and multi-source clock-domain enumeration without structural change.

### Stage C — Sink Clustering
**Purpose.** Recursively partition the enumerated sink set into geometrically and electrically coherent clusters that will become the leaf-level fanout groups of the clock tree.
**Theory.** Bottom-up clustering (TritonCTS 2.0's default clustering procedure) groups sinks by proximity subject to a maximum-capacitance and maximum-fanout-per-cluster constraint derived from the clock buffer library's drive-strength characteristics and the Part 2 fanout objective.
**Engineering rationale.** Clustering is performed as an explicit, isolable stage (rather than implicit within buffer insertion) so that the resulting cluster structure can be independently validated and re-tuned (e.g., re-clustered with a tighter fanout cap) without re-running topology synthesis from scratch.
**Inputs.** Stage B sink coordinates; clock buffer library metadata; CTS configuration (max fanout, max capacitance per cluster).
**Outputs.** Hierarchical cluster tree (leaf clusters up through intermediate groupings).
**Dependencies.** Stage B.
**Runtime.** Seconds to a couple of minutes depending on sink count.
**Memory.** Proportional to sink count; clustering data structures dominate.
**Failure conditions.** Clustering non-termination (pathological sink distribution preventing convergence within configured iteration bound); a cluster whose capacitance cannot be satisfied by any available buffer drive strength.
**Validation.** Every leaf cluster satisfies the configured max-fanout and max-capacitance bound.
**Industrial notes.** Directly corresponds to TritonCTS 2.0's internal clustering pass invoked ahead of buffer insertion.
**Reviewer expectations.** Cluster-count and cluster-size distribution archived.
**Future scalability.** Clustering granularity (max fanout/capacitance per cluster) is manifest-driven, enabling dataset-diversity sweeps between deep, buffer-heavy trees and shallow, buffer-sparse trees.

### Stage D — Topology Selection
**Purpose.** Select and instantiate the clock-tree topology (H-tree, X-tree, spine, or hybrid) most appropriate to the die aspect ratio, sink distribution, and CTS configuration's topology preference.
**Theory.** Topology is selected from a fixed, enumerable set rather than synthesized ad hoc: H-tree for regular, roughly-square sink distributions targeting minimal global skew by construction symmetry; X-tree as a diagonal-symmetry variant for certain macro-heavy floorplans; spine topology for elongated or macro-segmented dies where symmetric quadrant recursion is not geometrically efficient.
**Engineering rationale.** Constraining topology selection to a fixed enumerable set (rather than a fully general Steiner-tree search) preserves determinism and reviewer-interpretability: a reviewer can verify, from the manifest alone, which topology class was used and why, rather than needing to re-derive an opaque search result.
**Inputs.** Stage C cluster tree; die geometry from Phase 14.6 floorplan record; CTS configuration topology preference.
**Outputs.** Instantiated topology skeleton (levels, branch points, per-level fanout targets) prior to buffer sizing.
**Dependencies.** Stage C.
**Runtime.** Seconds.
**Failure conditions.** No configured topology is geometrically feasible for the given die aspect ratio and blockage layout (e.g., a large central macro blockage prevents a symmetric H-tree center tap).
**Validation.** Topology skeleton's per-level branch count matches the cluster tree's hierarchy depth.
**Industrial notes.** Corresponds to TritonCTS 2.0's topology-construction configuration flags (`-sink_clustering_levels`, topology-shape-influencing parameters); mesh topology is explicitly reserved as future work (Part 8) and is not selectable in this phase.
**Reviewer expectations.** Selected topology and the geometric rationale for its selection are logged verbatim in the stage report.
**Future scalability.** The enumerable topology set is designed to be extended (e.g., adding mesh, Part 8) by adding a new topology-construction module without altering Stages A–C or E–J.

### Stage E — Buffer and Inverter Insertion
**Purpose.** Insert clock buffers/inverters at each topology branch point and at each leaf-cluster centroid, selecting drive strength from the clock buffer library to satisfy the downstream fanout/capacitance load.
**Theory.** Drive-strength selection is a discrete sizing problem solved greedily per branch point: the smallest library drive strength satisfying the branch's capacitance/slew requirement is selected first, escalating to larger drive strengths only when required, to minimize clock-network dynamic power (a secondary objective, Part 9).
**Engineering rationale.** Greedy, library-driven discrete sizing is chosen over continuous buffer sizing (unavailable in standard-cell libraries) because industrial clock-buffer libraries are inherently discrete (fixed drive-strength ladder); the greedy minimal-sufficient-strength rule is the standard industrial power-minimization heuristic and keeps sizing decisions deterministic and auditable.
**Inputs.** Stage D topology skeleton; clock buffer library metadata; per-branch capacitance load from Stage C.
**Outputs.** Fully buffered clock network (buffer/inverter instances inserted, not yet legalized); per-instance drive-strength assignment record.
**Dependencies.** Stage D.
**Runtime.** Seconds to tens of seconds.
**Failure conditions.** A branch load exceeds the maximum available drive strength in the clock buffer library even after escalation (indicating a cluster-capacitance misconfiguration from Stage C).
**Validation.** Every inserted buffer's assigned drive strength satisfies its branch's capacitance/slew requirement per Liberty characterization data.
**Industrial notes.** Directly corresponds to TritonCTS 2.0's buffer-insertion and library-based sizing pass.
**Reviewer expectations.** Full buffer-instance list with drive-strength assignment archived for reproducibility audit.
**Future scalability.** Inverter-pair (rather than buffer-pair) insertion policy is a manifest-exposed alternative for future duty-cycle-sensitivity studies without altering the surrounding stage structure.

### Stage F — Skew Balancing
**Purpose.** Iteratively adjust buffer placement/sizing and topology-level wire-length matching to bring global and local skew within the Part 2 configured bounds.
**Theory.** Skew balancing operates by equalizing root-to-sink delay across symmetric topology branches (delay-matching via wirelength/buffer-count equalization for H-tree/X-tree symmetry, or explicit buffer re-sizing for spine topology asymmetries), using incremental OpenSTA delay calculation as the feedback signal at each iteration.
**Engineering rationale.** Skew balancing is performed as a distinct post-insertion stage (rather than folded into Stage E) so that the useful-skew policy (Part 8) — which deliberately introduces *bounded, intentional* skew to favor specific timing paths — has a well-defined, isolated stage to apply its adjustments against an already-connected, already-sized baseline tree.
**Inputs.** Stage E buffered network; incremental STA session; CTS configuration skew targets and useful-skew policy.
**Outputs.** Skew-balanced buffered network (buffer positions/sizes may be locally adjusted); skew convergence trace.
**Dependencies.** Stage E.
**Runtime.** Tens of seconds to a few minutes, dominated by incremental STA re-evaluation per balancing iteration.
**Failure conditions.** Non-convergence (skew fails to decrease within a rolling window across the configured maximum iteration count).
**Validation.** Final global skew and local skew both below configured thresholds.
**Industrial notes.** Corresponds to TritonCTS 2.0's balancing pass, typically invoked with `-balance_levels` and skew-target configuration flags.
**Reviewer expectations.** Full skew convergence trace (iteration vs. global skew vs. local skew) archived.
**Future scalability.** Useful-skew target vectors (per-register-pair intentional skew biasing) are manifest-exposed for future timing-closure-research sweeps.

### Stage G — Slew and Latency Optimization
**Purpose.** Verify and correct, via bounded re-buffering, any clock-net segment whose slew exceeds the configured bound, and confirm root-to-sink latency remains within the configured budget.
**Theory.** Slew violations are resolved by local buffer re-sizing (escalating drive strength) or, where re-sizing is insufficient, by inserting an additional buffer stage on the offending segment; latency is re-computed after any such correction and checked against budget.
**Engineering rationale.** Slew and latency are optimized jointly in a single stage (rather than two separate stages) because slew correction (adding buffer stages) directly perturbs latency, and resolving them independently would risk a correction loop between two stages re-undoing each other's work; a single joint stage with a fixed correction order (slew first, then latency re-check) keeps the process deterministic and terminating.
**Inputs.** Stage F skew-balanced network; incremental STA session; CTS configuration slew bound and latency budget.
**Outputs.** Slew-corrected, latency-verified buffered network.
**Dependencies.** Stage F.
**Runtime.** Seconds to tens of seconds.
**Failure conditions.** Slew violation persists after maximum re-buffering iterations; latency exceeds budget after all slew corrections are applied and cannot be reduced without reintroducing a slew violation (a documented tradeoff conflict, escalated per Part 12).
**Validation.** Zero slew violations across all clock-net segments; root-to-sink latency within configured budget for every sink.
**Industrial notes.** Corresponds to TritonCTS 2.0's post-balancing slew-repair pass combined with OpenSTA-driven latency verification.
**Reviewer expectations.** Slew histogram and latency distribution archived.
**Future scalability.** Slew/latency bound tightness is a manifest-exposed sweep parameter for dataset-diversity generation, mirroring Phase 14.7's density-band sweep pattern.

### Stage H — Buffer Legalization
**Purpose.** Snap all inserted clock buffers/inverters to legal sites/rows with zero residual overlap against both pre-existing standard cells and other newly inserted clock buffers, using the identical minimum-displacement legalization mechanism established in Phase 14.7 Stage H.
**Theory.** Formulated as the same assignment problem as Phase 14.7 Stage H, extended to include the newly inserted buffer instance set as additional movable instances against the already-legal standard-cell background.
**Engineering rationale.** Reusing the identical legalizer (rather than a CTS-specific legalization routine) guarantees that post-CTS legality is checked by the same mechanism as post-placement legality, eliminating any risk of a legality-definition mismatch between phases.
**Inputs.** Stage G buffered network; legal-site bitmap (re-derived to exclude sites now occupied by pre-existing standard cells).
**Outputs.** Fully legal post-CTS DEF/ODB.
**Dependencies.** Stage G.
**Runtime.** Seconds to a couple of minutes depending on buffer count and required displacement.
**Failure conditions.** Legalization failure (insufficient legal sites near a required buffer location, typically in high-utilization regions where Phase 14.7 whitespace planning did not reserve adequate CTS headroom).
**Validation.** Zero overlap; 100% site/row legality; orientation legality — identical validation predicate to Phase 14.7 Stage H.
**Industrial notes.** Directly reuses OpenDP's `dpl` legalizer as integrated in OpenROAD/OpenLane2, now operating on the combined standard-cell-plus-clock-buffer instance set.
**Reviewer expectations.** Buffer displacement statistics (mean/max) archived as primary legalization-cost evidence, in direct parallel with Phase 14.7's displacement metric.
**Future scalability.** Because legalization is mechanism-shared with Phase 14.7, any future legalizer upgrade automatically benefits both phases without duplicated maintenance.

### Stage I — QoR Extraction
**Purpose.** Compute and serialize the complete CTS QoR metric set (Part 10) from the final legal post-CTS network.
**Theory.** Post-hoc, read-only computation over the legalized OpenDB/OpenSTA state; no tree modification occurs in this stage, in direct parallel with Phase 14.7 Stage I.
**Engineering rationale.** Isolating QoR extraction as a distinct, side-effect-free stage guarantees that QoR numbers reflect the exact legalized state validated in Stage H/J, with no possibility of measurement-induced drift, preserving the identical rationale established in Phase 14.7.
**Inputs.** Legalized OpenDB/DEF; final incremental STA session.
**Outputs.** CTS QoR JSON (Part 10 schema).
**Dependencies.** Stage H.
**Runtime.** Seconds to tens of seconds (dominated by final full-tree STA re-evaluation).
**Failure conditions.** Schema validation failure; missing metric computation.
**Validation.** JSON schema conformance check.
**Industrial notes.** Corresponds to OpenLane2's post-step metrics aggregation, extended with CTS-specific fields.
**Reviewer expectations.** QoR JSON is the primary artifact reviewers will inspect for reproducibility claims, exactly as in Phase 14.7.
**Future scalability.** Schema is versioned to allow additive metric extension without breaking existing ML-consumer pipelines.

### Stage J — CTS Validation
**Purpose.** Final automated gate-check confirming the clock tree satisfies every objective in Part 2 before the pipeline is marked complete.
**Theory.** A deterministic checklist evaluator over the QoR JSON, connectivity report, and legality report, in direct structural parallel with Phase 14.7 Stage J.
**Engineering rationale.** Centralizing all pass/fail logic in one final stage gives a single, auditable PASS/FAIL record per run, which is the unit Part 16's Artifact Evaluation claims are built on, exactly as established in Phase 14.7.
**Inputs.** QoR JSON, connectivity report, legality report, all stage logs.
**Outputs.** PASS/FAIL verdict; validation report.
**Dependencies.** Stage I.
**Runtime.** Sub-second.
**Failure conditions.** Any Part 2 objective gate failing.
**Validation.** This *is* the validation stage; its own output is the validation record.
**Industrial notes.** Equivalent to OpenLane2's step-level `Metric` assertion checks aggregated into a single go/no-go, mirroring Phase 14.7 Stage J.
**Reviewer expectations.** Validation report is what reviewers cite when confirming a design "passed CTS" in the dataset.
**Future scalability.** Gate thresholds are manifest-driven, allowing stricter/looser corpora to be generated from the same codebase, exactly as in Phase 14.7.

---

## PART 6 — CLOCK PLANNING

- **Clock root definition.** The clock root is fixed at the SDC-declared `create_clock` source pin coordinate; for hierarchical designs with a clock-generator macro, the root is the macro's clock output pin as placed in Phase 14.6/14.7 — never a synthesized virtual coordinate.
- **Clock domain enumeration.** Each independently declared SDC clock is planned as an independent tree-construction problem within the same Stage A–J pipeline invocation; cross-domain skew is explicitly out of scope for this phase (deferred to sign-off-stage cross-domain analysis in a later phase) since it depends on routing-stage parasitics not yet available.
- **Sink budget planning.** The expected sink count per clock domain is cross-checked against the clock buffer library's maximum practical fanout-per-level to estimate the minimum required tree depth before Stage C clustering is attempted, allowing early detection of a clearly infeasible configuration.
- **Whitespace/headroom interaction with Phase 14.7.** Because clock buffers must legalize into whitespace reserved during placement, this phase's planning step cross-references the Phase 14.7 utilization/whitespace QoR record to flag configurations where Phase 14.7's utilization was set high enough to risk Stage H legalization failure, surfacing this as a WARN before Stage C begins rather than allowing a late-stage legalization failure.
- **Fence-region interaction.** Clock buffers inserted within a Phase 14.7-declared fence region must themselves respect that fence's constraints; clock planning does not override placement-stage fencing.
- **Macro interaction.** Clock-buffer insertion points falling within a macro halo margin are redirected to the nearest legal exterior point during Stage E/H, consistent with the macro-interaction handling established in Phase 14.7 Part 6.
- **Engineering tradeoffs.** Deeper trees (more buffer levels) reduce per-buffer fanout and improve slew/skew control but increase buffer count, dynamic power, and legalization displacement risk; the CTS configuration manifest exposes tree-depth-influencing parameters (max fanout per cluster, max capacitance per cluster) as first-class sweep parameters specifically so the downstream ML corpus can capture this tradeoff empirically, mirroring the utilization-tradeoff philosophy of Phase 14.7 Part 6.

---

## PART 7 — CLOCK BUFFER LIBRARY AND CELL SELECTION

**Clock buffer cell enumeration.** The clock buffer library metadata (Part 3) enumerates every clock-capable buffer and inverter cell available in the technology library, tagged with drive strength, input capacitance, intrinsic delay, and characterized output-slew-vs-load tables extracted directly from Liberty.

**Buffer vs. inverter selection policy.** Buffer-pair insertion (non-inverting) is the default policy to preserve clock polarity through the tree without requiring downstream polarity tracking; inverter-pair insertion is available as a manifest-exposed alternative for duty-cycle-correction or intentional-polarity-inversion research scenarios, consistent with the Stage E future-scalability note in Part 5.

**Drive-strength ladder.** Cells are ordered by drive strength (input capacitance ascending) to support the greedy minimal-sufficient-strength sizing rule established in Stage E; the ladder must contain sufficient granularity (project convention: at least four drive-strength steps) to avoid large power-inefficient over-sizing jumps.

**Cell selection engineering rationale.** Restricting buffer selection to library cells explicitly tagged as clock-capable (rather than reusing arbitrary combinational buffers) is required because clock-network cells typically carry tighter transition-time characterization, higher electromigration-relevant current ratings, and (in industrial libraries) dedicated clock-cell physical construction (e.g., balanced pull-up/pull-down for duty-cycle preservation) — using a non-clock-tagged buffer would be technically valid but industrially non-representative, undermining the paper's DTCO realism claims.

**Slew-table-driven sizing.** Stage E's drive-strength escalation decision is made by direct lookup against the Liberty-characterized output-slew-vs-load table for each candidate cell, not by a simplified capacitance-only heuristic, to keep sizing decisions faithful to real silicon characterization data.

**Technology independence.** The clock buffer library metadata schema is technology-agnostic (drive strength expressed in relative ladder position plus absolute characterized values, rather than technology-specific cell-name pattern matching), satisfying Part 2 Objective 2.

**Validation.** At Stage A, every buffer/inverter cell referenced in the clock buffer library metadata is cross-checked against the loaded Liberty to confirm characterization data actually exists for that cell; a metadata entry with no corresponding Liberty data is a Stage A input failure.

**Industrial notes.** This directly mirrors how OpenROAD's TritonCTS 2.0 is configured via `-buf_list` (or equivalent clock-buffer cell-list configuration), which explicitly requires the user/flow to declare which library cells are eligible for clock-tree insertion.

**Future scalability.** The drive-strength ladder and buffer/inverter policy are both manifest parameters, allowing future research into alternative clock-cell topologies (e.g., dedicated low-skew clock buffers if characterized separately in a given PDK) without altering Stage E's algorithmic structure.

---

## PART 8 — CLOCK TREE CONSTRUCTION STRATEGY

**H-tree.** The default topology for regular, roughly-square core areas with a centrally reachable clock root: recursive quadrant subdivision with a buffer at each subdivision center, producing inherently symmetric root-to-sink path lengths and therefore low global skew by geometric construction before any active balancing (Stage F) is applied.

**X-tree.** A diagonal-symmetry variant of the H-tree, preferred when the sink distribution or macro layout exhibits diagonal rather than orthogonal symmetry (e.g., certain datapath-heavy floorplans); selected in Stage D when the topology-selection geometric feasibility check favors diagonal branch alignment over orthogonal.

**Spine topology.** A linear (or piecewise-linear) trunk-and-branch topology preferred for elongated dies or floorplans segmented by large macro rows, where a symmetric quadrant-recursive tree is not geometrically efficient; skew control in a spine topology relies more heavily on Stage F active balancing (explicit delay matching per branch) than on geometric symmetry.

**Mesh topology — future work only.** A fully-connected or partially-connected clock mesh (multiple redundant drive points feeding a shorted grid) is explicitly reserved as future work and is **not implemented, selectable, or validated in this phase**. Mesh topology fundamentally changes the QoR model (skew becomes a function of mesh short-circuit currents and requires SPICE-level or specialized mesh-analysis tooling rather than tree-based STA), and its inclusion would violate this phase's tree/DAG problem formulation stated in Part 1. Mesh support is documented here only to establish the architectural boundary for a future phase.

**Clock shielding discussion.** Physical shielding of clock nets (dedicated ground/power shield wires alongside clock routes) is a routing-stage concern and is explicitly out of scope for this phase's tree-construction and buffer-insertion activities; however, this phase's CTS configuration manifest reserves a shielding-intent flag per clock domain so that the downstream routing phase (Phase 14.9+) can consume a documented shielding requirement without needing to re-derive it from the SDC. No shielding geometry is created, planned, or validated in this phase.

**Clock balancing / useful skew philosophy.** Two balancing philosophies are supported, selected via CTS configuration: (a) **zero-skew philosophy** — Stage F drives global and local skew toward the minimum achievable value uniformly across all sinks, the default and recommended policy for general-purpose benchmark corpus generation; (b) **useful-skew philosophy** — Stage F deliberately introduces bounded, directionally-biased skew at specific register pairs identified (via the Phase 14.7-carried-forward pre-CTS slack estimate) as having asymmetric setup/hold margin, borrowing time from a non-critical path's clock arrival to relax a critical path's effective timing requirement. Useful skew is applied only within the hard bound established by Part 2 Objective 5 and is never permitted to push any sink's local skew outside that bound merely to benefit another sink — it is a bounded reallocation, not an unbounded optimization.

**Fanout control.** Enforced structurally at Stage C (cluster-level max fanout) and re-verified at Stage E/G (per-buffer fanout at insertion and after any slew-driven re-buffering); no stage is permitted to exceed the configured maximum fanout even transiently in its committed output.

**Slew control.** Enforced at Stage G as the primary corrective stage, but monitored continuously from Stage E onward via incremental STA so that a slew violation is caught as close as possible to its point of introduction rather than only at the final Stage G check.

**Clock latency.** Root-to-sink insertion delay, tracked per-sink from Stage E onward and finalized at Stage G; latency budget compliance is a hard Part 2 objective (Objective 6) but latency *minimization* beyond the budget is explicitly not pursued as an objective, since industrial practice treats "within budget" as sufficient and further minimization trades against buffer count/power for no QoR benefit.

**Local/global skew.** Global skew is defined as the max-minus-min root-to-sink latency across the entire sink set of a clock domain; local skew is defined as the max root-to-sink latency difference restricted to register pairs with a direct combinational timing path between them (as identified from the netlist), which is the skew metric most directly relevant to setup/hold margin consumption and is therefore weighted more heavily in the Stage F balancing objective than global skew.

**Buffer legalization.** As established in Part 5 Stage H, buffer legalization reuses the Phase 14.7 legalization mechanism unmodified, applied to the combined standard-cell-plus-buffer instance set.

**Engineering rationale (aggregate).** Constraining this phase to a fixed, enumerable topology set (H-tree, X-tree, spine) plus a clearly bounded useful-skew policy — while explicitly fencing off mesh topology and shielding geometry as later-phase or future-work concerns — keeps the phase's QoR model fully STA-tractable (no SPICE-level mesh analysis required) and keeps the phase boundary with Phase 14.9 (routing) unambiguous.

---

## PART 9 — CTS OPTIMIZATION (INSERTION DELAY, SKEW, LATENCY, SLEW, FANOUT)

**Insertion delay optimization.** Insertion delay is monitored (not independently minimized beyond budget compliance) throughout Stages E–G; the only active correction applied to insertion delay is the latency-budget check in Stage G, consistent with Part 8's latency philosophy.

**Skew optimization.** The primary active optimization of this phase, performed in Stage F via iterative delay-matching (symmetric-topology branches) or explicit buffer re-sizing/re-positioning (spine topology), governed by either the zero-skew or useful-skew philosophy as configured (Part 8).

**Latency optimization.** Bounded, budget-compliance-only optimization performed in Stage G as a joint pass with slew correction; latency is never traded against skew — if a conflict arises (a skew-optimal buffer position would violate the latency budget), the latency budget takes precedence and the conflict is logged as a WARN-level QoR annotation rather than silently resolved in either direction.

**Slew optimization.** Performed continuously from Stage E (initial sizing) through Stage G (final correction pass), using direct Liberty slew-table lookups (Part 7) rather than simplified capacitance-based heuristics, ensuring slew correction decisions are grounded in real characterization data.

**Fanout optimization.** Structural, not iterative — fanout is controlled by construction (Stage C clustering caps) rather than by post-hoc correction, since allowing fanout violations to occur and then correcting them would require tree-topology rework rather than simple buffer re-sizing.

**Interaction ordering and engineering rationale.** The fixed correction order established across Stages F and G — skew first (Stage F), then slew, then latency (both within Stage G, slew taking precedence) — is a deliberate, documented design decision: skew is optimized first because it is the most topology-sensitive (best resolved while the tree structure is still only lightly perturbed by later stages), while slew and latency are resolved last because they are primarily buffer-sizing concerns that should not undo the just-achieved skew balance. This ordering is fixed and configuration-independent to preserve determinism (Part 2, Objective 1) — the manifest may change *thresholds* for each objective but never the *order* in which they are optimized.

**Buffer movement during optimization.** Any buffer repositioning performed during Stage F/G optimization remains within the continuous (pre-legalization) coordinate space; Stage H legalization is the sole point at which positions are made final and grid-legal, exactly mirroring the Phase 14.7 Stage G→H relationship between pre-legalization refinement and legalization.

**ECO friendliness.** Stage-boundary QoR snapshots are retained at every stage (not only Stage I), consistent with the ECO-friendliness rationale established in Phase 14.7 Part 9, so that a future ECO-style re-CTS (out of scope for this phase but anticipated future scalability) can resume from any intermediate stage.

**Power-awareness.** The greedy minimal-sufficient-drive-strength sizing rule (Stage E, Part 7) is the primary mechanism by which this phase controls clock-network dynamic power; no separate power-optimization pass exists in this phase, since clock-network power is dominated by buffer count and drive strength, both of which are already governed by the fanout/clustering and sizing rules above.

---

## PART 10 — CTS QUALITY METRICS

Each metric below is emitted in the Stage I QoR JSON with: definition, importance, engineering rationale, measurement method, and ML relevance.

1. **Sink connectivity (bool + unconnected-sink count).** *Definition:* fraction of declared clock sinks reachable from the clock root through the final tree. *Importance:* hard gating metric. *Rationale:* an unconnected sink is a functional failure. *Measurement:* exhaustive graph traversal from root. *ML relevance:* binary/near-binary filter feature for corpus validity.
2. **Buffer/inverter count.** *Definition:* total number of clock-tree buffer and inverter instances inserted. *Importance:* primary area/power proxy. *Rationale:* directly drives clock-network dynamic power and legalization displacement risk. *Measurement:* direct instance-count query. *ML relevance:* core regression target/feature for power-prediction models.
3. **Global skew.** *Definition:* max-minus-min root-to-sink latency across the full sink set per clock domain. *Importance:* primary timing-margin-consumption metric. *Rationale:* directly gates Part 2 Objective 5. *Measurement:* incremental STA latency query per sink. *ML relevance:* core regression target for skew-prediction research.
4. **Local skew.** *Definition:* max root-to-sink latency difference restricted to combinationally-connected register pairs. *Importance:* setup/hold-margin-relevant skew metric, more directly tied to timing closure than global skew. *Rationale:* per Part 8's local-skew weighting rationale. *Measurement:* incremental STA latency query restricted to identified register pairs. *ML relevance:* primary feature for timing-closure-prediction models.
5. **Insertion delay (root-to-sink latency) distribution.** *Definition:* mean/median/std/max root-to-sink latency across all sinks. *Importance:* latency-budget compliance evidence. *Rationale:* directly gates Part 2 Objective 6. *Measurement:* incremental STA latency query, distribution-reduced. *ML relevance:* regression feature for latency-budget-sensitivity studies.
6. **Slew distribution.** *Definition:* mean/median/std/max transition time across all clock-net segments. *Importance:* slew-bound compliance evidence. *Rationale:* directly gates Part 2 Objective 7. *Measurement:* incremental STA slew query per net segment. *ML relevance:* regression feature for slew-prediction models.
7. **Fanout distribution.** *Definition:* mean/median/std/max fanout across all clock-net segments. *Importance:* fanout-bound compliance evidence. *Rationale:* directly gates Part 2 Objective 8. *Measurement:* direct netlist fanout count per segment. *ML relevance:* structural feature for tree-topology-classification research.
8. **Tree depth.** *Definition:* number of buffer levels from root to the deepest sink. *Importance:* structural complexity indicator. *Rationale:* correlates with both insertion delay and buffer count. *Measurement:* graph-depth computation from root. *ML relevance:* structural feature for topology-comparison studies.
9. **Topology class.** *Definition:* categorical label (H-tree / X-tree / spine / hybrid) selected in Stage D. *Importance:* structural/categorical feature. *Rationale:* enables topology-conditioned QoR analysis. *Measurement:* direct Stage D decision record. *ML relevance:* categorical feature for topology-selection-prediction research.
10. **Buffer legality (bool + violation count).** *Definition:* fraction of inserted buffers satisfying site/row/orientation/non-overlap constraints. *Importance:* hard gating metric. *Rationale:* directly gates Part 2 Objective 9. *Measurement:* exhaustive geometric overlap/grid-alignment check, identical mechanism to Phase 14.7. *ML relevance:* binary/near-binary filter feature.
11. **Buffer displacement (legalization cost).** *Definition:* mean/max Euclidean/Manhattan distance between Stage G (pre-legalization) and Stage H (post-legalization) buffer positions. *Importance:* legalization-cost proxy specific to clock buffers. *Rationale:* directly parallels Phase 14.7's cell-displacement metric, isolated to the buffer subset. *Measurement:* direct coordinate delta on buffer instances only. *ML relevance:* feature for predicting CTS-stage legalization-induced QoR loss.
12. **Clock-network wirelength.** *Definition:* total HPWL (or Steiner estimate) of all clock nets post-legalization. *Importance:* clock-network routing-resource-consumption proxy. *Rationale:* clock wirelength directly consumes routing resources that would otherwise be available to signal nets in the downstream routing phase. *Measurement:* direct geometric computation on clock nets only. *ML relevance:* feature for routing-resource-contention-prediction research.
13. **Clock-network dynamic power estimate.** *Definition:* estimated switching power of the clock network derived from buffer count, drive strength, and toggle activity (assumed at clock frequency for the clock network itself). *Importance:* primary CTS-stage power proxy. *Rationale:* directly informs the Part 9 power-awareness sizing rationale. *Measurement:* Liberty-derived per-buffer switching power summed across the tree. *ML relevance:* core regression target for clock-network-power-prediction models.
14. **Useful-skew utilization (if enabled).** *Definition:* fraction of the configured skew bound actually consumed by intentional useful-skew biasing, per register pair where applied. *Importance:* diagnostic metric for the useful-skew philosophy. *Rationale:* documents how aggressively useful skew was applied relative to its hard bound. *Measurement:* direct comparison of biased vs. zero-skew-baseline latency per targeted register pair. *ML relevance:* feature for useful-skew-effectiveness research.
15. **CTS Runtime.** *Definition:* wall-clock time per stage and total. *Importance:* engineering/scalability metric. *Rationale:* required for the runtime-expectation claims in Part 1. *Measurement:* stage-boundary timestamps. *ML relevance:* auxiliary feature for runtime-prediction/scheduling research.
16. **Memory Usage.** *Definition:* peak RSS per stage and total. *Importance:* engineering/scalability metric. *Rationale:* required for the memory-expectation claims in Part 1. *Measurement:* periodic RSS sampling. *ML relevance:* auxiliary feature for resource-prediction research.
17. **Balancing convergence statistics.** *Definition:* iteration count and skew-reduction trace for Stage F. *Importance:* optimization-difficulty diagnostic. *Rationale:* isolates how much iterative effort was required to reach the skew target, useful for QoR-regression debugging. *Measurement:* per-iteration skew snapshot. *ML relevance:* feature for optimization-difficulty-prediction research.
18. **Slew/latency correction statistics.** *Definition:* count of buffer re-sizing and buffer-insertion corrections applied in Stage G. *Importance:* Stage G effort/diagnostic metric. *Rationale:* isolates how much of the final tree state resulted from initial sizing (Stage E) versus corrective action (Stage G). *Measurement:* per-correction event log, aggregated. *ML relevance:* stage-attribution feature set, mirroring Phase 14.7's cell-movement-statistics metric.
19. **Additional meaningful metrics** (reserved schema extension fields): per-clock-domain skew/latency breakdown for multi-clock-domain designs, clustering-level fanout-skew correlation, and configuration-echoed parameters (target skew, target slew, max fanout) for direct feature-label pairing in ML corpus construction.

---

## PART 11 — OUTPUTS

- **Post-CTS DEF.** Final legalized DEF, schema-identical in convention to the Phase 14.7 placed DEF plus fully-specified clock-buffer instances and clock-net topology records.
- **Post-CTS ODB.** Binary OpenDB snapshot of the same final state, used as the direct input to Phase 14.9 (routing) without requiring DEF re-parsing, mirroring the DEF+ODB dual-output rationale established in Phase 14.7 Part 11.
- **CTS reports.** Human-readable per-stage summary reports (text/log) mirroring the QoR JSON for manual review.
- **CTS QoR JSON.** Schema-validated, versioned JSON containing every metric in Part 10.
- **Visualization.** Clock-tree topology diagram, skew heatmap (per-sink latency deviation from target), and buffer-displacement overlay images (PNG/SVG), generated from Stage I data for both manual review and dataset documentation.
- **Metadata.** Design name, benchmark ID, technology node, clock buffer library revision, tool versions, seed, timestamps.
- **Logs.** Full stage-by-stage execution logs, retained unredacted for Artifact Evaluation.
- **Manifest updates.** CTS-stage completion status, output artifact hashes, and stage timing appended to the running project manifest.
- **Configuration snapshots.** Frozen copies of every configuration file consumed by this phase's run, including the resolved clock buffer library metadata.

**Engineering rationale.** Emitting both DEF and ODB, and explicitly including the clock buffer library revision in metadata, ensures that any downstream re-derivation of this phase's QoR is possible even if the technology library is later updated, preserving the Stage-to-Stage database-continuity and reproducibility principles established in Phase 14.7 Part 11.

**Validation.** All outputs are validated against their respective schemas/formats before the run is marked complete; a run producing a Stage J PASS verdict but failing output schema validation is itself marked FAIL and logged to the failure ledger, identical in mechanism to Phase 14.7 Part 11.

---

## PART 12 — FAILURE HANDLING

| Failure Mode | Detection Point | Recovery Strategy |
|---|---|---|
| Unconnected clock sink | Stage B/J connectivity check | Re-verify SDC/netlist consistency; if a genuine netlist defect, flag `SINK_UNREACHABLE` and halt (not auto-correctable) |
| Clustering non-termination | Stage C | Relax max-fanout-per-cluster bound and retry up to configured max attempts; else flag `CLUSTERING_INFEASIBLE` |
| Topology infeasibility | Stage D | Fall back to spine topology (most geometrically permissive) and retry; if still infeasible, flag `TOPOLOGY_INFEASIBLE` and halt |
| Branch load exceeds max drive strength | Stage E | Re-cluster with tighter capacitance bound (return to Stage C) up to configured max re-cluster attempts; else flag `SIZING_INFEASIBLE` |
| Skew non-convergence | Stage F | Increase balancing iteration budget and retry once; else flag `SKEW_NONCONVERGENT` and halt |
| Persistent slew violation | Stage G | Escalate drive strength one additional ladder step and retry up to configured max; else flag `SLEW_VIOLATION` |
| Latency budget exceeded | Stage G | Log WARN if within a configured tolerance margin of budget; hard flag `LATENCY_BUDGET_EXCEEDED` if beyond tolerance |
| Buffer legalization failure | Stage H | Attempt relaxed swap-radius legalization pass (identical strategy to Phase 14.7 Stage H); if still failing, escalate to `BUFFER_LEGALIZATION_FAILURE` and halt |
| Buffer site/orientation violation | Stage H/J | Immediate hard failure — indicates a legalizer or database defect; escalated as `DATABASE_INTEGRITY_FAILURE` |
| Database corruption | Any stage | Immediate halt; manifest marks run `CORRUPTED`; no partial artifacts are promoted to the deliverable corpus |
| Manifest handling | N/A (cross-cutting) | Every failure updates the manifest's failure ledger with stage, error class, and timestamp before halting |

**Engineering rationale.** As in Phase 14.7 Part 12, failures are stratified into *recoverable-via-bounded-retry* (clustering, sizing, skew, slew) and *hard/fatal* (unreachable sink, topology infeasibility after fallback, legalization failure after relaxed retry, database corruption), preserving the same conflation-avoidance rationale: bounded retries handle genuinely tunable optimization difficulty, while hard failures surface genuine structural or database defects immediately rather than masking them behind further retries.

**Logging.** Every failure emits a structured log entry (stage, error class, relevant metric values, retry count) to both the run-local log and the project-level failure ledger, which — as in Phase 14.7 — is treated as a first-class Part 15 deliverable providing negative (failed) examples for ML corpus researchers.

---

## PART 13 — AUTOMATION

- **`cts.py`** — top-level orchestrator invoking Stages A–J in order, reading the CTS configuration manifest and writing all Part 11 outputs.
- **`cluster_sinks.py`** — invokes Stage C (sink clustering) as an isolable sub-pipeline for standalone tuning of fanout/capacitance caps.
- **`build_topology.py`** — invokes Stage D (topology selection) as an isolable sub-pipeline, supporting forced-topology override runs for comparative dataset generation.
- **`insert_buffers.py`** — invokes Stage E (buffer/inverter insertion and sizing) as an isolable sub-pipeline against a fixed Stage D topology snapshot.
- **`balance_skew.py`** — invokes Stage F (skew balancing) standalone against a fixed Stage E snapshot, supporting rapid re-tuning of skew targets and useful-skew policy without re-running clustering/topology/insertion.
- **`fix_slew_latency.py`** — invokes Stage G standalone against a fixed Stage F snapshot, supporting rapid slew/latency-bound sweeps.
- **`legalize_buffers.py`** — invokes Stage H alone, supporting rapid legalizer-only re-runs against a previously computed Stage G snapshot, in direct parallel with Phase 14.7's `legalize.py`.
- **`validate_cts.py`** — invokes Stage I–J standalone against any previously produced post-CTS ODB, for post-hoc re-validation without re-running the full pipeline.

**Resume capability.** Every script checkpoints OpenDB state at its stage boundary; `cts.py` can resume from any completed stage's checkpoint rather than restarting from Stage A, keyed by the manifest's stage-completion record, identical in mechanism to Phase 14.7 Part 13.

**Parallel execution.** Independent designs (distinct placed-DEF/SDC pairs) are trivially parallelizable across processes/nodes; independent clock domains within a single design may also be parallelized at Stages B–G (per-domain sink sets are independent) before being merged for combined Stage H legalization and Stage I/J extraction/validation, since buffer legalization must consider all clock domains' buffers jointly against the shared placement fabric.

**Cluster execution.** The manifest-driven checkpoint scheme supports the same job-array submission model established in Phase 14.7 Part 13, with `cts.py` as the per-job entry point.

**Manifest-driven execution.** All scripts read their full parameter set from the frozen configuration snapshot, never from ad hoc CLI flags alone, exactly as in Phase 14.7.

**Dry-run mode.** All scripts support a `--dry-run` flag performing Stage A input validation and configuration echoing without executing any tree-construction computation, used for fast manifest-correctness checking across large sweep batches.

**Engineering rationale.** Exposing per-stage-group entry points in addition to the monolithic `cts.py` directly supports the ML-corpus-generation use case established in Phase 14.7 Part 13, where researchers frequently need to re-sweep only skew targets (`balance_skew.py`) or only slew/latency bounds (`fix_slew_latency.py`) without paying the full Stage A–E cost repeatedly.

---

## PART 14 — REPOSITORY STRUCTURE

```
phase14_8_clock_tree_synthesis/
├── configs/
│   ├── cts_default.yaml
│   ├── cts_skew_sweep/
│   │   ├── skew_tight.yaml
│   │   ├── skew_medium.yaml
│   │   └── skew_loose.yaml
│   ├── clock_buffer_libraries/
│   │   ├── sky130_clkbuf.json
│   │   └── gf180mcu_clkbuf.json
│   └── technology/
│       ├── sky130.yaml
│       └── gf180mcu.yaml
├── scripts/
│   ├── cts.py
│   ├── cluster_sinks.py
│   ├── build_topology.py
│   ├── insert_buffers.py
│   ├── balance_skew.py
│   ├── fix_slew_latency.py
│   ├── legalize_buffers.py
│   └── validate_cts.py
├── stages/
│   ├── stage_a_init.py
│   ├── stage_b_root_sink_enum.py
│   ├── stage_c_clustering.py
│   ├── stage_d_topology.py
│   ├── stage_e_buffer_insert.py
│   ├── stage_f_skew_balance.py
│   ├── stage_g_slew_latency.py
│   ├── stage_h_legalize.py
│   ├── stage_i_qor_extract.py
│   └── stage_j_validate.py
├── schema/
│   ├── cts_qor.schema.json
│   └── manifest.schema.json
├── runs/
│   └── <design>/<config_id>/<run_id>/
│       ├── post_cts.def
│       ├── post_cts.odb
│       ├── qor.json
│       ├── reports/
│       ├── logs/
│       ├── visualization/
│       │   ├── clock_tree_topology.svg
│       │   ├── skew_heatmap.png
│       │   └── buffer_displacement_overlay.svg
│       └── manifest_snapshot.json
├── failure_ledger/
│   └── <design>/<config_id>/<run_id>/failure.json
└── docs/
    └── phase14_8_specification.md
```

**Engineering rationale.** The `runs/<design>/<config_id>/<run_id>/` hierarchy is preserved unchanged from Phase 14.7 Part 14, maintaining the same design/configuration-sweep/seed indexing axes across phases so that a single project-level dataset loader can traverse both phases' corpora with identical indexing logic.

---

## PART 15 — DELIVERABLES

1. **CTS flow.** The full Stage A–J pipeline implementation (scripts + stage modules) as described in Parts 5 and 13.
2. **Post-CTS DEF corpus.** The complete set of legalized post-CTS DEF files across all design × configuration × seed combinations executed for this project.
3. **Post-CTS ODB corpus.** The corresponding binary OpenDB snapshots.
4. **QoR dataset.** The aggregate Part 10 metric set across the full corpus, in a single indexed dataset file (in addition to per-run JSON) suitable for direct ML consumption.
5. **Failure ledger.** The complete record of all failed runs (Part 12) with stage, error class, and metric context, retained as first-class negative-example data.
6. **Metadata.** Full manifest set across the corpus (design/config/seed/tool-version/clock-buffer-library indexing).
7. **Visualization corpus.** All clock-tree topology/skew-heatmap/displacement visualizations across the full run set.
8. **Configuration snapshots.** All frozen configuration files across the full sweep space, including resolved clock buffer library metadata per run.

**Engineering rationale.** As in Phase 14.7 Part 15, the failure ledger is treated as a formal deliverable rather than discarded data, since CTS-stage failure modes (clustering infeasibility, skew non-convergence, legalization failure under high placement utilization) are themselves valuable labeled examples for failure-prediction research directly tied to this project's DTCO/ML objective.

---

## PART 16 — PUBLICATION READINESS

**IEEE reproducibility.** Every deliverable in Part 15 is produced under the determinism guarantees of Part 2 Objective 1, satisfying IEEE's expectation that reported skew/latency/buffer-count numbers be independently regenerable from the released artifact set, exactly as established in Phase 14.7 Part 16.

**Artifact Evaluation.** The repository structure (Part 14), manifest schema, and dry-run mode (Part 13) are specifically designed to satisfy typical AE-track requirements: a reviewer can execute `validate_cts.py` against any released post-CTS ODB to independently re-derive and confirm the published QoR JSON without re-running the full multi-minute pipeline.

**Industrial deployment.** Because the pipeline is built directly on OpenROAD (TritonCTS 2.0) and OpenLane2 primitives with no proprietary substitutions, the specification is directly portable to industrial open-source-EDA-based flows without translation, mirroring Phase 14.7's industrial-deployment claim.

**Zenodo compatibility.** The `runs/` and `failure_ledger/` hierarchies are structured as flat, self-describing directory trees suitable for direct Zenodo archival with manifest-derived checksums as the integrity-verification mechanism, identical in structure to Phase 14.7 Part 16.

**Reviewer expectations.** Reviewers should expect, and this specification provides: explicit tool/version and clock-buffer-library pinning, explicit skew/latency/slew/fanout target provenance from SDC, a versioned QoR schema, and an explicit, auditable PASS/FAIL gate (Stage J) rather than qualitative claims of clock-tree quality.

**Future scalability.** This phase's manifest-driven, stage-checkpointed architecture is designed to scale unmodified from single-clock-domain debugging to full corpus-scale, multi-clock-domain generation runs, and hands off cleanly — via the post-CTS ODB/DEF and QoR JSON — to Phase 14.9 (Routing), which will consume this phase's legalized clock tree as its own validated starting state without needing to re-derive any clock-network topology, skew, or latency information.

---

*End of Phase 14.8 — Clock Tree Synthesis Specification. This document establishes the validated legal post-CTS clock tree and complete CTS QoR record that Phase 14.9 (Routing) will consume as its starting input, consistent with the phase-boundary discipline established in Phase 14.5, Phase 14.6, and Phase 14.7.*
