# PHASE 14.12 — IR Drop & Power Integrity Analysis Specification (IPIAS)

**Paper:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target:** IEEE International Conference on Microelectronics (ICM 2026)
**Document Class:** Industrial Engineering Specification (continues directly after Phase 14.11 — Post-Route Static Timing Analysis & Timing Closure; precedes Phase 14.13 — Physical Verification: DRC/LVS/Antenna)

---

## PART 1 — IR Drop & Power Integrity Philosophy

### Purpose
Phase 14.12 defines the authoritative methodology by which a fully routed, timing-closed design (Phase 14.11 output) is analyzed for power-delivery integrity: the degree to which the power distribution network (PDN) built up progressively since floorplanning (Phase 14.6) and refined through placement (Phase 14.7), CTS (Phase 14.8), and routing (Phase 14.9) actually delivers a stable, in-tolerance supply voltage to every standard cell and macro instance under both static and dynamic operating conditions. This phase closes the loop between the *geometric* power-delivery decisions made early in the flow and the *electrical* consequences of those decisions, producing the IR-drop and power-integrity QoR record that is one of the paper's most direct manufacturing/reliability-risk signals.

### Theory
Power integrity analysis is fundamentally a resistive (and, for the dynamic case, resistive-inductive-capacitive) network solve. The PDN — package, rings, straps, rails, and vias — together with every standard-cell and macro instance's current draw, forms a large sparse linear system whose solution yields the voltage at every node of the network. Departures of this solved voltage from the nominal supply value constitute *IR drop* (a naming convention retained from Ohm's Law, `V = IR`, even though the dynamic case is more accurately an impedance-drop phenomenon incorporating parasitic inductance and capacitance).

### Static IR Drop
The voltage drop observed under a fixed, time-invariant current draw assumption (typically the design's average or a documented worst-case-average current per instance, derived from Phase 14.5's synthesis-stage power QoR and refined using post-route parasitic data from Phase 14.10). Static IR drop characterizes the PDN's baseline adequacy independent of any specific switching pattern and is the more tractable, faster-converging analysis of the two, making it the first-line, always-run check in this phase's pipeline (Stage E).

### Dynamic IR Drop
The voltage drop observed under a time-varying current draw reflecting realistic or worst-case switching activity, most severely manifesting as a transient sag immediately following a clock edge when a large fraction of sequential and downstream combinational logic switches simultaneously. Dynamic IR drop is materially more severe than static IR drop in any design with meaningful clock-synchronous activity concentration and is the more physically realistic predictor of functional and timing failures induced by supply-voltage sag; it is addressed in Stage F using the clock-tree structure (Phase 14.8) and switching-activity assumptions (Part 8) as its primary drivers.

### Voltage Drop
The generic term for the difference between the nominal supply voltage (VDD) as delivered at the package interface and the actual voltage observed at a given internal PDN node or cell instance; voltage drop degrades a cell's effective drive strength and timing margin, and — if severe enough — can cause functional failure (a flip-flop failing to capture correctly) rather than merely a timing degradation, which is why this phase treats voltage-drop analysis as a first-class, mandatory closure gate rather than an optional refinement.

### Power Distribution Network Behavior
The PDN behaves as a distributed resistive mesh (for static analysis) or resistive-capacitive mesh with current-source-modeled cell instances (for dynamic analysis); its behavior is governed by the interaction of ring/strap/rail geometry (established in Phase 14.6 and refined through Phase 14.9's routing) with the actual per-instance current draw determined by the final placed-and-routed netlist.

### Current Flow
Current is modeled as flowing from the package/board-level voltage source, through the PDN's rings and straps (upper metal layers), down through vias to the standard-cell rail layer, and into each cell instance's power pin, with the return (ground) path modeled symmetrically; this phase's resistance-network construction (Stage D) explicitly represents both the power and ground networks rather than assuming an ideal, zero-impedance ground return.

### Resistance Network
Every segment of every power/ground conductor (ring segment, strap segment, rail segment, via) is represented as a resistor in the network, with resistance values derived from the technology's metal sheet resistance and via resistance data (declared in the technology LEF/technology file and consumed identically to how Phase 14.10's parasitic extraction consumes the same technology data for signal-net RC extraction).

### Ohm's Law
The fundamental relation `V = I × R` governing every edge of the resistance network; the static IR-drop solve (Stage E) is, at its core, a large-scale sparse linear-system solution of Kirchhoff's current law applied at every network node combined with Ohm's law applied at every network edge, conceptually identical to (though decoupled from) the RC-network solves performed during Phase 14.10's parasitic extraction.

### Package Resistance
The resistance contributed by the package's power/ground bond wires, bumps, or leadframe between the board-level voltage regulator and the die's power pads; modeled in this phase as a documented, conservative lumped-resistance assumption (Part 4) rather than a detailed package-level extraction, since detailed package modeling is reserved for a dedicated packaging-co-design phase consistent with this paper's ATMP-focused but appropriately-scoped treatment of packaging concerns.

### Via Resistance
The resistance of each via connecting adjacent metal layers within the PDN, derived from the technology file's per-via-type resistance value; via resistance is a first-order contributor to the vertical voltage drop between the upper-metal strap layers and the standard-cell-rail layer, and is tracked explicitly as a Part 10 QoR feature (Via Count, Current Through Vias) because insufficient via redundancy is a well-documented contributor to localized IR hotspots.

### Metal Resistance
The sheet resistance of each routing layer, declared per-layer in the technology file, consumed identically across the entire PDN (rings, straps, rails) and applied uniformly to determine each resistive segment's value as `R = sheet_resistance × (length / width)`.

### Power Mesh
The regular grid structure of straps and rails established during floorplanning (Phase 14.6, Part 9) and preserved (subject to any routing-stage-necessitated local rerouting) through placement, CTS, and routing; the power mesh's density and redundancy are the PDN's primary architectural determinants of IR-drop robustness, and this phase's Stage B loads the *as-routed* mesh geometry rather than the *as-planned* Phase 14.6 geometry, since routing-stage obstacle avoidance can introduce mesh discontinuities not present in the original floorplan.

### Ground Mesh
The symmetric ground counterpart to the power mesh, analyzed with identical rigor (Objective O2, Part 2) since asymmetric power/ground network robustness is a common, easily-overlooked source of dynamic IR-drop-induced failures.

### Current Density
The current per unit cross-sectional area flowing through any given metal or via segment; tracked explicitly (Part 10) both for its direct IR-drop relevance and because excessive current density is the proximate cause of electromigration-driven reliability degradation, directly connecting this phase's analysis to the paper's reliability-prediction thesis, even though full EM lifetime sign-off remains a distinct, later concern (Part 9's EM-awareness discussion, consistent with Phase 14.6, Part 9's precedent of flagging EM as a coarse check rather than sign-off).

### Voltage Collapse
The severe-case condition in which IR drop at a given node exceeds a threshold beyond which the affected logic can no longer be guaranteed to operate correctly (as distinct from a milder in-tolerance drop that merely erodes timing margin); this phase's Stage H power-integrity validation explicitly distinguishes ordinary IR-drop violations (Part 12: `failed:ir_limit_exceeded`) from voltage-collapse-severity violations (`failed:voltage_collapse`), since the latter represents a functional, not merely a timing, risk.

### Local Hotspots
Spatially-concentrated regions of elevated IR drop, typically arising from a combination of high local current density (e.g., beneath a macro or within a dense clock-buffer cluster from Phase 14.8) and locally sparse PDN redundancy (e.g., a region where routing-stage congestion forced strap thinning); hotspot detection (Stage G) is a dedicated pipeline stage precisely because aggregate (chip-average) IR-drop statistics can mask severe, spatially-localized violations.

### Engineering Rationale
This phase exists as a dedicated, mandatory gate — rather than folding power-integrity checking into the routing or STA phases — because IR drop is a distinct physical phenomenon governed by the PDN's resistive network, not by the signal-net timing graph that Phase 14.11's STA analyzes; conflating the two would obscure the specific, actionable engineering lever (PDN strengthening, Part 9) needed to remediate a power-integrity violation.

### Industrial Motivation
Industrial ASIC sign-off universally treats power-integrity (IR-drop and, increasingly, dynamic voltage-drop) analysis as a mandatory tapeout gate alongside STA and physical verification; this phase's inclusion, positioned explicitly between Phase 14.11 (timing closure) and Phase 14.13 (DRC/LVS/antenna), mirrors the standard industrial sign-off ordering in which power integrity is verified after routing is final but before physical verification is run on the final GDSII.

### Reviewer Expectations
Reviewers should expect this phase to demonstrate that voltage-drop-induced timing degradation is explicitly re-incorporated into a documented view of the design's true operating margin, rather than allowing Phase 14.11's STA sign-off to be read as unconditionally final.

### Runtime Expectations
Static IR-drop analysis on a small-to-medium design: 5–20 minutes. Dynamic IR-drop analysis, being substantially more compute-intensive due to its time-domain or activity-weighted vectorless nature: 20 minutes to several hours depending on design size and the switching-activity model's resolution (Part 8).

### Memory Expectations
Static analysis: typically 2–8 GB, dominated by the sparse resistive-network matrix. Dynamic analysis: 8–24 GB for larger designs, due to the additional time-domain or multi-vector current-waveform data retained per instance.

### Failure Conditions
PDN disconnection (an unreachable network node), solver non-convergence, IR-drop or voltage-collapse threshold violations, or missing power/ground net declarations (Part 12).

### Validation Philosophy
Consistent with every prior Phase 14.x document, validation is treated as an independent, final acceptance gate (Stage J) rather than an implicit byproduct of the analysis stages themselves.

### Future Scalability
The static/dynamic separation and the technology-agnostic resistance-network construction (Part 4) allow this phase's methodology to extend unchanged to additional technology libraries or to a future multi-voltage-domain PDN (explicitly deferred since Phase 14.6, Part 4).

---

## PART 2 — Objectives

### O1 — Static IR Compliance
**Definition:** Every PDN node's static-analysis voltage drop must remain within a documented percentage (default 5%) of nominal VDD. **Rationale:** static IR drop is the baseline PDN-adequacy signal, unaffected by activity-model uncertainty. **Validation:** Stage E's per-node threshold check. **Industrial notes:** matches the conventional 5% static IR-drop sign-off criterion used broadly across industrial ASIC flows. **Future scalability:** the 5% threshold is a configurable parameter, not a hardcoded constant.

### O2 — Dynamic IR Compliance
**Definition:** Every PDN node's dynamic-analysis worst-case transient voltage drop must remain within a documented, typically looser (default 8–10%) percentage of nominal VDD. **Rationale:** transient sag is expected to be more severe than static drop and is tolerated to a looser bound reflecting its brief duration relative to a full clock period. **Validation:** Stage F's per-node, per-time-step (or per-vector) threshold check. **Industrial notes:** the static/dynamic threshold asymmetry mirrors standard industrial signoff practice. **Future scalability:** threshold pair is jointly configurable per technology/reliability-margin policy.

### O3 — Power Integrity Verification
**Definition:** The complete PDN (power and ground networks) must be verified electrically connected from every package-interface pad to every standard-cell/macro instance's power/ground pin, with no floating or disconnected sub-network. **Rationale:** a disconnected sub-network invalidates any IR-drop number computed downstream of the disconnection. **Validation:** Stage B/D connectivity check, prior to any numerical solve. **Industrial notes:** equivalent to a PDN "connectivity DRC" performed before any signoff-grade IR analysis. **Future scalability:** directly reusable for future multi-domain PDN connectivity checking.

### O4 — Voltage Margin Preservation
**Definition:** The margin between the worst-case analyzed voltage and the failure-relevant voltage-collapse threshold (Part 1) must remain positive by a documented guard-band. **Rationale:** ensures the design is not merely "passing" at the threshold boundary but retains genuine margin against process/model uncertainty. **Validation:** Stage H. **Industrial notes:** mirrors the general sign-off practice of requiring margin beyond a bare pass/fail threshold. **Future scalability:** guard-band is a tunable, technology-class-dependent parameter.

### O5 — PDN Validation
**Definition:** The as-routed PDN geometry (Stage B) must match the intended PDN architecture established in Phase 14.6 (and preserved, subject to documented routing-stage modification, through Phases 14.7–14.9) within a documented tolerance. **Rationale:** detects unintended PDN degradation introduced by routing-stage congestion avoidance. **Validation:** Stage B's as-planned-versus-as-routed geometric comparison. **Industrial notes:** equivalent to a PDN "final versus intent" reconciliation check performed before signoff in industrial flows. **Future scalability:** comparison logic is reusable for any future PDN-modification phase.

### O6 — Current Density Validation
**Definition:** No metal or via segment may exceed the technology's documented maximum current-density (electromigration-relevant) limit under either static or dynamic analysis. **Rationale:** connects this phase's electrical analysis directly to the reliability-risk concerns central to the paper's thesis. **Validation:** Stage E/F current-density check, cross-referenced against the technology file's per-layer/per-via-type limits. **Industrial notes:** a first-order EM-awareness check, explicitly not a substitute for dedicated EM lifetime signoff. **Future scalability:** extensible to a full EM lifetime model in a future phase.

### O7 — Power Hotspot Detection
**Definition:** Every spatially-localized region whose IR drop exceeds the Part 1 hotspot criteria must be identified, bounded, and ranked by severity. **Rationale:** aggregate statistics alone are insufficient for reliability risk characterization (Part 1's Local Hotspots discussion). **Validation:** Stage G's grid-based clustering algorithm, output cross-checked against Stage E/F's raw per-node data. **Industrial notes:** matches industrial "hotspot report" deliverables. **Future scalability:** hotspot geometry is directly consumable by future thermal or reliability co-analysis phases.

### O8 — IR Map Generation
**Definition:** A complete, full-chip spatial voltage map (a value per grid cell or per PDN node) must be generated and archived for both static and dynamic analyses. **Rationale:** supports both human visual QA and machine-consumable spatial feature extraction. **Validation:** Stage I's map-completeness check (no null grid cells). **Industrial notes:** equivalent to the "IR-drop heatmap" deliverable standard in industrial signoff packages. **Future scalability:** map resolution is a configurable parameter, tunable against runtime/memory budget.

### O9 — EM-Aware Preparation
**Definition:** All current-density data computed in this phase must be archived in a form directly consumable by a future, dedicated electromigration-signoff phase, without requiring re-derivation from raw netlist/parasitic data. **Rationale:** avoids duplicated analysis effort across phases. **Validation:** Stage I's schema check for EM-relevant fields (Part 10). **Industrial notes:** mirrors how industrial flows typically compute current density once and consume it in multiple downstream reliability checks. **Future scalability:** the schema is explicitly versioned to remain stable as a future EM-signoff phase is defined.

### O10 — Determinism
**Definition:** Identical routed design + identical activity assumptions + identical PDN ⇒ bit-identical (or numerically-identical within solver tolerance) voltage-map output across repeated runs. **Rationale:** consistent with every prior phase's Objective O1 precedent (Phase 14.5/14.6), essential for the corpus's QoR labels to be trustworthy. **Validation:** sampled re-run comparison (`verify_objectives.py`, extended). **Industrial notes:** requires fixing solver iteration order and disabling non-deterministic parallel reduction in the linear-system solve. **Future scalability:** determinism guarantee extends to any future solver substitution provided the same fixed-seed discipline is maintained.

### O11 — Technology Independence
**Definition:** The IR-drop/power-integrity methodology must be expressible without hardcoded technology-specific numeric constants; all resistance, current-density-limit, and via-resistance values are read from the technology file. **Rationale:** consistent with Objective O2 precedent from Phase 14.5/14.6. **Validation:** a configuration-audit check confirming no hardcoded technology constants appear in flow scripts. **Industrial notes:** essential for the tri-library (Sky130/GF180/ASAP7) corpus strategy established since Phase 14.5. **Future scalability:** directly supports future library additions.

### O12 — Reproducibility
**Definition:** Every IR-drop/power-integrity result must be regenerable from its archived configuration snapshot (Part 11) and the upstream Phase 14.9–14.11 artifacts alone. **Rationale:** consistent with the reproducibility discipline established across every prior Phase 14.x document. **Validation:** periodic full re-run audit against archived snapshots. **Industrial notes:** mirrors industrial signoff-package archival requirements. **Future scalability:** unaffected by future solver or activity-model upgrades provided snapshot schema versioning is maintained.

### O13 — Dataset Completeness
**Definition:** Every (design, library, corner) triple successfully reaching this phase must produce a fully populated Part 10 QoR record with no null/missing field. **Rationale:** consistent with the Objective O4/O6 precedent from Phase 14.5/14.6 (QoR completeness / physical constraint completeness). **Validation:** Stage I's schema-completeness check. **Industrial notes:** mirrors industrial QoR-report completeness requirements. **Future scalability:** schema is versioned and extensible (Part 10).

### O14 — ML Feature Extraction Readiness
**Definition:** All QoR fields, voltage maps, and hotspot records must be emitted in a directly machine-consumable (JSON/CSV plus raster/vector map) form requiring no further reformatting before ingestion into the paper's CNN/GNN models (Phases 5–7). **Rationale:** this phase's outputs are among the most directly reliability-relevant features in the entire pipeline, and unnecessary reformatting overhead would slow the paper's downstream experimentation. **Validation:** a schema-conformance linter checking output format against the ML-ingestion interface contract. **Industrial notes:** an explicitly research-oriented objective, distinguishing this corpus-generation flow from a pure industrial signoff flow whose reports need not be ML-ready. **Future scalability:** the ML-ingestion contract is versioned independently of the underlying analysis methodology, allowing either to evolve without breaking the other.

### O15 — Reviewer-Auditable Traceability
**Definition:** Every IR-drop or power-integrity number reported in the eventual paper must be traceable, via the archived configuration snapshot and logs, to the exact upstream design, library, corner, and activity-assumption combination that produced it. **Rationale:** prevents any ambiguity in how a headline QoR statistic (e.g., "worst-case dynamic IR drop across the corpus") was derived. **Validation:** a traceability audit tool cross-referencing any reported summary statistic against its constituent per-design records. **Industrial notes:** mirrors the auditability standard expected in IEEE Artifact Evaluation. **Future scalability:** directly reusable by any future phase reporting corpus-level aggregate statistics.

---

## PART 3 — Inputs

### GDSII
Not yet consumed at this phase (GDSII streamout occurs after Phase 14.13's physical verification); listed here only to clarify the phase boundary — this phase operates on the pre-GDSII routed database (DEF/ODB), not the final streamed layout.

### DEF
The final routed DEF from Phase 14.9/14.11, carrying complete metal-layer geometry for signal, power, and ground nets alike; the authoritative geometric source for Stage B's power-mesh loading.

### ODB
The OpenROAD physical database snapshot carried forward from Phase 14.9 through 14.11, providing the richest, most directly consumable representation of routed geometry and avoiding any DEF-round-trip precision loss, consistent with the ODB-as-authoritative-handoff philosophy established since Phase 14.6.

### LEF
Technology, standard-cell, and macro LEF (carried forward since Phase 14.6, Part 3), consumed here specifically for each cell/macro's power-pin location and the technology's per-layer sheet-resistance and per-via-type resistance data.

### Liberty
The `.lib` timing/power characterization data (Phase 14.5, Part 6), consumed for each cell's per-state leakage and switching power, forming the basis of the per-instance current-draw estimate used in both static (Stage C) and dynamic (Stage F) current estimation.

### SPEF
The Standard Parasitic Exchange Format file produced by Phase 14.10's parasitic extraction, providing signal-net RC data; while this phase's primary concern is the power/ground network rather than signal nets, SPEF data is consulted in Stage F to refine per-instance switching-current timing (i.e., *when* within a clock cycle a given instance's current draw peaks), improving dynamic IR-drop accuracy over a purely activity-count-based estimate.

### Timing Reports
Phase 14.11's post-route STA reports, consumed to identify the clock-domain structure and any already-flagged marginal-timing paths whose margin should be re-evaluated in light of this phase's voltage-drop findings (Part 9's power-aware DTCO discussion).

### Power Reports
Phase 14.5's synthesis-stage power QoR (dynamic switching and leakage power per cell), forming the initial, coarse current-budget estimate later refined by this phase's more geometrically-precise analysis.

### Clock Tree
The Phase 14.8 clock-tree structure (buffer locations, insertion delay, skew data), consumed in Stage F because clock-buffer switching is typically the single largest concentrated contributor to dynamic IR-drop transients, given the near-simultaneous switching of an entire clock-tree level.

### Routing Database
The complete routed-net geometry (Phase 14.9), consumed for two purposes: (a) confirming actual PDN strap/rail routing as physically realized (as opposed to as-planned), and (b) providing signal-net proximity data relevant to any future PDN-versus-signal-routing congestion co-analysis.

### Power Grid
The PDN geometry specifically (a subset of the full routing database), isolated by net-name/net-class filtering (power/ground nets) as the direct input to Stage B.

### Via Database
The complete via instance list (from ODB), providing the exact via count, location, and type needed for the resistance-network construction (Stage D) and the current-through-vias QoR metric (Part 10).

### Metal Layers
The technology's metal stack definition (layer count, thickness, sheet resistance, preferred routing direction), consumed identically to how Phase 14.6's Part 4 and Phase 14.10's parasitic-extraction phase consume the same underlying technology data.

### Technology Rules
Current-density limits, via-resistance tables, and manufacturing-grid data from the technology file, consumed across Stages D, E, and F.

### Manifest
The benchmark manifest, extended with a power-integrity-status field per (design, library, corner) triple, consistent with the resume-capability model established since Phase 14.5.

### Configuration Snapshots
The exact analysis configuration (activity-model parameters, IR-drop thresholds, hotspot-detection sensitivity) used for a given run, archived verbatim (Objective O12).

### Benchmark Metadata
The Phase 14.2/14.3 benchmark manifest entry, consulted for any benchmark-family-specific activity-profile hints (e.g., a benchmark documented as clock-gated versus free-running) relevant to Part 8's activity assumptions.

### Design Metadata
The per-design metadata record, extended in this phase with the design's power-grid topology summary (ring count, strap pitch, rail count) extracted from Stage B.

### Power Intent
Where declared, the design's power-intent specification (voltage domains, power switches, isolation/retention strategy); for this corpus's single-voltage-domain scope (Part 4), power intent is minimal but is still explicitly recorded to distinguish "no multi-domain intent exists" from "multi-domain intent exists but is not yet analyzed," avoiding ambiguity in future multi-domain extensions.

### UPF/CPF (If Applicable)
Unified/Common Power Format files are consumed only if present in a given benchmark's metadata; the majority of this corpus's benchmark set (consistent with the single-voltage-domain assumption carried since Phase 14.6, Part 4) will have no UPF/CPF file, and its absence is not treated as a Part 12 failure condition but as an expected, documented configuration state.

### Engineering Rationale
As in every prior Phase 14.x document, separating these input classes allows independent versioning: a technology file update (revised via-resistance data) can be applied without re-routing a design, and an activity-model refinement can be applied without re-extracting parasitics.

### Validation
A pre-flight checker (`preflight_check.py`, extended, Part 13) enforces presence and integrity of all required input classes before Stage A begins.

### Failure Conditions
Missing SPEF, hash-mismatched DEF/ODB relative to the Phase 14.11 record, or malformed technology current-density data abort the job before any solver compute is spent.

---

## PART 4 — Power Integrity Environment

### Purpose
To define the tool environment and internal representations within which power-integrity analysis is performed.

### OpenROAD
The physical-design tool suite continued from every prior physical-implementation phase (14.6–14.11), providing this phase's ODB access layer and orchestration continuity.

### PDNSim
OpenROAD's dedicated power-delivery-network analysis engine, used as the primary static and dynamic IR-drop solver; selected for direct ODB integration (avoiding a DEF round-trip) and for its native support of both static and vectorless/activity-weighted dynamic analysis modes, consistent with this phase's static/dynamic separation (Part 1).

### OpenRCX
OpenROAD's parasitic extraction engine, already established as the Phase 14.10 extraction tool; reused in this phase (in a power/ground-net-focused invocation) to extract precise PDN segment resistance values from as-routed geometry, rather than relying solely on nominal sheet-resistance-times-geometry estimates, improving accuracy over a purely analytical resistance model.

### OpenDB
The underlying physical database library (ODB's implementation), providing the geometric and connectivity query interface consumed by PDNSim and OpenRCX alike.

### OpenSTA
Consulted in this phase (Part 3, Timing Reports) for its already-computed clock-domain and switching-relevant timing-window data, reused rather than re-derived, consistent with the general principle (established since Phase 14.5) of never duplicating analysis effort already performed by an upstream phase's canonical tool.

### OpenLane2
The flow-orchestration layer wrapping this phase's stage sequence (Part 5) into a scripted, configuration-driven pipeline, consistent with its role in every prior physical-implementation phase.

### Power Grid Representation
The PDN is represented internally as a graph: nodes correspond to metal-segment endpoints and via locations, edges correspond to resistive segments (metal or via), each annotated with its resistance value (Part 1); this graph representation is the direct input to Stage D's resistance-network construction.

### Voltage Sources
The package-interface power pads are modeled as ideal (zero-impedance) voltage sources at the declared nominal VDD, with the package's own resistance (Part 1, Package Resistance) modeled as a discrete lumped resistor in series between the ideal source and the die's power pad, per the conservative package-resistance assumption documented in this phase's configuration.

### Current Sources
Every standard-cell and macro instance's power pin is modeled as a current sink (a current source in network-analysis convention, drawing current from the network) whose magnitude is derived in Stage C from Liberty power data and, for dynamic analysis, from the Part 8 activity model.

### Package Model Assumptions
Because detailed package-level modeling is out of scope (Part 1), this phase adopts a single, conservative, documented lumped package-resistance value per design class (derived from typical wire-bond peripheral package resistance data for the corpus's assumed package interface, consistent with Phase 14.6, Part 8's peripheral pad-ring assumption), explicitly flagged in metadata as a simplifying assumption rather than a package-vendor-specific extraction.

### Resistance Modeling
As established in Part 1: metal segment resistance from sheet resistance × geometry (or, where available, OpenRCX-extracted precise values), via resistance from technology-file per-via-type tables.

### Current Propagation
Current is propagated through the resistive network per Kirchhoff's current law at every node, solved as a sparse linear system (Stage E) or, for dynamic analysis, as a sequence of such solves across discretized time steps or activity-weighted vector cases (Stage F).

### Power Rails
The lowest-level PDN conductors, running at standard-cell-row pitch and connecting directly to individual cell power pins; the finest-granularity component of the resistance network and typically the dominant resistive contributor closest to any given cell instance.

### Ground Rails
The symmetric ground counterpart to power rails, modeled with identical rigor (Objective O2, Part 2 — Technology Independence, applied here to power/ground symmetry rather than library symmetry).

### Power Straps
The mid-level PDN conductors (established in Phase 14.6, Part 9, and refined through routing) connecting rails to rings; a primary lever for power-integrity optimization (Part 9's grid-strengthening discussion).

### Power Rings
The peripheral PDN conductors (Phase 14.6, Part 9) collecting current from straps and delivering it toward the package interface; modeled as the network's outermost resistive segments, directly adjacent to the Part 4 voltage-source nodes.

### Vias
Modeled as discrete resistive edges connecting nodes on adjacent metal layers, per Part 1's Via Resistance discussion.

### Metal Stack
The complete technology metal-layer stack (Phase 14.6, Part 4), consumed identically across this phase's resistance modeling and Phase 14.10's parasitic extraction, ensuring consistent technology-data provenance across phases.

### Coordinate System
Identical to the coordinate system, units, and die-origin convention established in Phase 14.6, Part 4, and preserved unchanged through every subsequent physical-implementation phase, ensuring this phase's voltage maps are spatially registered consistently with every prior phase's geometric outputs.

### Engineering Rationale
Reusing PDNSim/OpenRCX/OpenDB/OpenSTA — rather than introducing a new, phase-specific tool — maintains the single-toolchain-provenance discipline established since Phase 14.5, minimizing the risk of inter-tool data-representation drift.

### Industrial Notes
This tool selection and network-modeling approach mirrors the power-integrity signoff methodology of commercial tools (Cadence Voltus, Synopsys PrimePower/RedHawk), which likewise construct a resistive (and, for dynamic analysis, RLC) network from routed geometry and solve it against Liberty-derived current estimates.

### Future Scalability
The graph-based power-grid representation (Part 4) is directly extensible to a future multi-domain PDN or a future detailed package-model integration, since neither extension changes the fundamental node/edge resistive-network abstraction.

---

## PART 5 — Pipeline Architecture

### Stage A — Initialization
**Purpose:** Instantiate the power-integrity analysis session from the Phase 14.11 ODB and Part 3 inputs. **Theory/Rationale:** must occur before any network construction; establishes tool-session state and confirms input completeness. **Inputs:** ODB, LEF, Liberty, SPEF, technology rules. **Outputs:** an initialized PDNSim session bound to the routed design. **Dependencies:** OpenROAD/PDNSim session APIs. **Runtime:** seconds. **Memory:** proportional to design size, typically <1 GB. **Failure conditions:** ODB load failure, missing required input class (Part 3). **Validation:** input-completeness check identical in spirit to every prior phase's Stage A precedent. **Industrial notes:** equivalent to session initialization in Voltus/RedHawk. **Reviewer expectations:** a clean initialization log with zero missing-input warnings. **Future scalability:** session model is tool-agnostic in principle, bounded only by PDNSim's API surface.

### Stage B — Power Grid Loading
**Purpose:** Extract the as-routed PDN geometry (rings, straps, rails, vias) from the ODB and construct the initial power-grid graph (Part 4). **Theory/Rationale:** must use as-routed, not as-planned, geometry (Objective O5) to capture any routing-stage PDN modification. **Inputs:** ODB power/ground net geometry, LEF via/layer data. **Outputs:** power-grid graph (nodes + unweighted edges, prior to resistance annotation). **Dependencies:** Stage A, OpenDB net-class filtering. **Runtime:** low to moderate, scaling with PDN geometry complexity. **Memory:** proportional to via/segment count. **Failure conditions:** PDN disconnection detected during graph construction (Part 12: `failed:pdn_disconnected`), missing power or ground net declaration. **Validation:** graph connectivity check (Objective O3) — every leaf node (cell/macro power pin) must have a path to at least one voltage-source node. **Industrial notes:** equivalent to the "power grid extraction" step preceding any Voltus/RedHawk analysis. **Reviewer expectations:** a documented as-planned-versus-as-routed comparison (Objective O5) attached to every run. **Future scalability:** directly reusable for a future multi-domain PDN's per-domain graph construction.

### Stage C — Current Estimation
**Purpose:** Assign a per-instance current-draw value to every standard-cell and macro power-pin node, for both static (average) and dynamic (activity-weighted) analysis. **Theory/Rationale:** static current is estimated from Liberty leakage/average-switching power divided by nominal VDD; dynamic current is estimated per Part 8's activity model, weighted by clock-tree-derived switching timing (Part 3, Clock Tree). **Inputs:** Liberty power data, Phase 14.5 QoR power fields, clock-tree structure, activity-model configuration. **Outputs:** per-instance static current value; per-instance, per-time-step (or per-vector) dynamic current value. **Dependencies:** Stage B's graph (for node correspondence), Liberty data. **Runtime:** low for static; moderate to high for dynamic, scaling with activity-model resolution. **Memory:** low for static; moderate for dynamic (time-series or multi-vector storage). **Failure conditions:** missing Liberty power data for an instantiated cell, activity-model configuration inconsistency. **Validation:** aggregate current sum cross-checked against Phase 14.5's total dynamic/leakage power QoR fields for consistency. **Industrial notes:** mirrors the "current estimation" or "power state generation" step in commercial power-integrity tools. **Reviewer expectations:** the current-estimation formula and activity-model assumptions disclosed explicitly (Part 8), not left as an opaque tool default. **Future scalability:** current-estimation methodology is directly extensible to a future vectored (simulation-derived) activity model in place of the vectorless default.

### Stage D — Resistance Network Construction
**Purpose:** Annotate every Stage B graph edge with its resistance value (Part 1/Part 4). **Theory/Rationale:** combines technology-file sheet/via resistance data with OpenRCX-extracted precise values where available, defaulting to analytical (geometry × sheet resistance) values elsewhere. **Inputs:** Stage B graph, technology resistance data, OpenRCX extraction results. **Outputs:** fully resistance-annotated power-grid network, ready for solving. **Dependencies:** Stage B, OpenRCX. **Runtime:** moderate, scaling with segment/via count. **Memory:** proportional to network size. **Failure conditions:** missing resistance data for a declared metal layer or via type. **Validation:** resistance-value sanity check against documented technology-typical ranges. **Industrial notes:** equivalent to the "RC network build" step common to all resistive/RLC power-integrity solvers. **Reviewer expectations:** resistance-source provenance (analytical versus extracted) disclosed per network segment class. **Future scalability:** directly extensible to a future RLC (inductance-inclusive) network for higher-frequency dynamic analysis.

### Stage E — Static IR Analysis
**Purpose:** Solve the resistance network under the Stage C static current assignment, producing a full-chip static voltage map. **Theory/Rationale:** formulated as a sparse linear system (`G × V = I`, where `G` is the network conductance matrix) solved via a sparse direct or iterative solver; the fixed-point solution yields voltage at every network node. **Inputs:** Stage D network, Stage C static currents, Part 2 O1 threshold. **Outputs:** static voltage map (per-node voltage), Objective O1 pass/fail per node. **Dependencies:** Stage D, PDNSim's static solver. **Runtime:** the largest single runtime contributor for static analysis, scaling with network size; typically dominates over Stages A–D combined. **Memory:** proportional to the sparse matrix's non-zero count. **Failure conditions:** solver non-convergence, singular/ill-conditioned matrix (indicating a Stage B connectivity defect that escaped detection). **Validation:** solver-residual check against a documented convergence tolerance. **Industrial notes:** the direct analog of Voltus/RedHawk's static IR-drop solve. **Reviewer expectations:** solver iteration count and residual disclosed per run (Part 10's Solver Iterations metric). **Future scalability:** solver is swappable (direct versus iterative) without changing the network-construction stages upstream.

### Stage F — Dynamic IR Analysis
**Purpose:** Solve the resistance network under the Stage C dynamic (activity-weighted, time-varying) current assignment, producing a worst-case transient voltage map. **Theory/Rationale:** performed as either a discretized time-domain solve (a sequence of static-like solves at successive time steps following a clock edge) or a vectorless, statistically-weighted worst-case estimate combining the Part 8 activity model with clock-tree switching concentration; this phase defaults to the vectorless mode for tractable runtime across the full corpus, with the time-domain mode available as a configurable, more expensive alternative for designs specifically flagged for detailed dynamic study. **Inputs:** Stage D network, Stage C dynamic currents, clock-tree structure, Part 2 O2 threshold. **Outputs:** dynamic (worst-case transient) voltage map, Objective O2 pass/fail per node. **Dependencies:** Stage D, PDNSim's dynamic/vectorless analysis mode. **Runtime:** the largest single runtime contributor in this phase overall; substantially exceeds Stage E for the same design. **Memory:** the largest single memory contributor in this phase, particularly in time-domain mode. **Failure conditions:** solver non-convergence, activity-model configuration error, insufficient time-step resolution flagged by an internal accuracy heuristic. **Validation:** consistency check between vectorless and (where run) time-domain results on a sampled subset. **Industrial notes:** the direct analog of Voltus/RedHawk's dynamic voltage-drop (DVD) analysis. **Reviewer expectations:** the chosen analysis mode (vectorless versus time-domain) disclosed explicitly per design, along with its known accuracy tradeoff. **Future scalability:** the vectorless/time-domain duality allows future adoption of a fully vectored, simulation-derived activity profile without restructuring the stage's I/O contract.

### Stage G — Hotspot Detection
**Purpose:** Identify, bound, and rank spatially-localized IR-drop violation regions from the Stage E/F voltage maps. **Theory/Rationale:** applies a grid-based clustering algorithm (connected-component analysis over grid cells exceeding a documented severity threshold) to distinguish genuine spatial hotspots from isolated, non-clustered single-node violations, consistent with Part 1's Local Hotspots discussion and Objective O7. **Inputs:** Stage E/F voltage maps, hotspot-detection configuration (severity threshold, minimum cluster size). **Outputs:** ranked hotspot region list, each with bounding geometry, peak drop value, and affected-instance count. **Dependencies:** Stage E and/or F. **Runtime:** low to moderate, scaling with map resolution. **Memory:** low. **Failure conditions:** hotspot-detection configuration producing degenerate results (e.g., the entire chip flagged as one hotspot, indicating a miscalibrated threshold). **Validation:** cross-check that every detected hotspot's peak value matches the corresponding raw voltage-map value at that location. **Industrial notes:** equivalent to hotspot-report generation in commercial power-integrity signoff tools. **Reviewer expectations:** the clustering algorithm and threshold parameters disclosed explicitly (Part 2, Objective O7). **Future scalability:** hotspot geometry is directly consumable by a future thermal or reliability co-analysis phase.

### Stage H — Power Integrity Validation
**Purpose:** Apply the complete Objective O1–O9 compliance check set against the Stage E–G results. **Theory/Rationale:** acts as the phase's primary pass/fail decision point, distinct from Stage J's final artifact-level validation. **Inputs:** Stage E/F/G outputs, Part 2 objective thresholds. **Outputs:** per-objective pass/fail verdict, aggregated into an overall power-integrity-compliance record. **Dependencies:** Stages E, F, G. **Runtime:** low. **Memory:** low. **Failure conditions:** any objective threshold violation (Part 12's `failed:ir_limit_exceeded`, `failed:voltage_collapse`, `failed:current_density_overflow`). **Validation:** this stage *is* the phase's principal validation step alongside Stage J. **Industrial notes:** equivalent to the "power integrity signoff" gate in industrial tapeout checklists. **Reviewer expectations:** a documented, itemized objective-compliance record, not a bare aggregate pass/fail. **Future scalability:** directly extensible as new objectives (Part 2) are added.

### Stage I — QoR Extraction
**Purpose:** Populate the complete Part 10 QoR schema from the Stage E–H results. **Theory/Rationale:** consistent with the QoR-completeness discipline (Objective O13) established since Phase 14.5. **Inputs:** all prior stage outputs. **Outputs:** the full Part 10 QoR record, in JSON. **Dependencies:** Stages E–H. **Runtime:** low. **Memory:** low. **Failure conditions:** any null/missing schema field (a Stage I failure distinct from a Stage H objective violation — a design can be QoR-complete while still failing objectives, and vice versa a schema gap is always a hard failure regardless of objective compliance). **Validation:** schema-completeness linter. **Industrial notes:** equivalent to "QoR summary generation" in every prior Phase 14.x precedent. **Reviewer expectations:** exact schema reproduced in the eventual paper's dataset-description section. **Future scalability:** schema is versioned and extensible.

### Stage J — Final Validation
**Purpose:** Perform final, independent completeness and consistency verification of the entire phase's artifact set before corpus admission. **Theory/Rationale:** independent from Stages A–I, mirroring the validation-as-acceptance-gate philosophy established in Phase 14.5 Stage G and reused in every subsequent phase. **Inputs:** the complete Part 11 output set. **Outputs:** pass/fail verdict, manifest status update. **Dependencies:** `validate_power.py` (Part 13). **Runtime:** low. **Memory:** low. **Failure conditions:** any output-completeness gap (Part 11), any Objective O10 (determinism) sampled re-run mismatch. **Validation:** this stage *is* the pipeline's final validation step. **Industrial notes:** mirrors the final signoff-package completeness check performed before a design is released to the next flow stage in industrial tapeout processes. **Reviewer expectations:** a documented, automated final-validation methodology. **Future scalability:** validation rule set is directly extensible with additional checks as later phases (14.13 onward) identify new cross-phase consistency requirements.

---

## PART 6 — Power Grid Modeling

### Power Rings, Power Mesh, Straps, Rails
Modeled as the layered hierarchy established in Phase 14.6 (Part 9) and refined through routing (Phase 14.9): rings at the die periphery, straps forming the mid-density mesh across the core, and rails at standard-cell-row pitch delivering current to individual instances; this phase's Stage B loading step captures the *as-routed* realization of this hierarchy rather than assuming it matches the original floorplan-stage intent exactly.

### Via Ladders
Stacks of vias connecting a strap on one layer down through intermediate layers to the rail layer; via-ladder redundancy (multiple parallel via instances at each strap/rail intersection, rather than a single via) is a key PDN-robustness lever tracked explicitly via the Part 10 Via Count and Current Through Vias metrics, since a single-via connection is both a resistance concentration point and a single point of failure.

### Voltage Domains
Consistent with the single-domain assumption carried since Phase 14.6, Part 4; this phase's grid modeling assumes one core VDD/VSS pair, with the Part 3 Power Intent/UPF discussion documenting this as an explicit, revisitable simplification.

### Current Distribution
Current is not drawn uniformly across the chip; regions of high cell density (Phase 14.7 placement) or high switching concentration (Phase 14.8 clock-tree buffer clusters) draw disproportionately more current, a fact this phase's Stage C current-estimation step captures explicitly on a per-instance basis rather than assuming a uniform chip-average current density.

### Ground Return Paths
Modeled with equal rigor to power-current paths (Part 4), since asymmetric power/ground network robustness is a common source of underestimated dynamic IR-drop severity if the ground network is naively assumed ideal.

### Metal Layer Utilization
The fraction of each routing layer's total available track/area consumed by PDN geometry (as opposed to signal routing); tracked as a Part 10 metric since excessive PDN metal utilization on a given layer directly competes with signal-routing resource, a tension already anticipated in Phase 14.6's power-grid-philosophy discussion (Part 9 of that phase) and now empirically measurable against as-routed data.

### Grid Density
The strap/rail pitch actually realized post-routing; may differ locally from the Phase 14.6 floorplan-stage target where routing-stage congestion avoidance forced strap thinning or rerouting, directly motivating Objective O5's as-planned-versus-as-routed reconciliation check.

### Grid Redundancy
The degree to which any single PDN node has multiple independent current paths to the voltage source, as opposed to a single, non-redundant path; redundancy is the primary structural determinant of hotspot risk (Part 1) and is tracked, at the network-topology level, as an input to Stage G's hotspot-clustering sensitivity.

### Current Spreading
The tendency of current to distribute across multiple parallel resistive paths in proportion to their conductance; this phase's linear-network solve (Stage E/F) captures current spreading exactly (it is an inherent property of the Kirchhoff's-law solution), in contrast to simpler, non-solved current-density estimates that would need to assume idealized uniform spreading.

### Package Assumptions
As documented in Part 4, this phase's package-resistance modeling remains a conservative, lumped, non-vendor-specific assumption, explicitly flagged as such wherever package-adjacent QoR figures are reported.

### Engineering Tradeoffs
Denser power grids reduce IR drop and hotspot risk but consume routing resource competing with signal nets (a tension explicit since Phase 14.6); this phase's empirical, as-routed measurement of that tension — rather than Phase 14.6's earlier, purely analytical estimate — is one of this phase's principal contributions to the paper's DTCO thesis, since it closes the loop between an early geometric decision and its measured electrical consequence.

---

## PART 7 — Static IR Drop Analysis

### Ohm's Law and Current Estimation
As established in Parts 1 and 5 (Stage C/E): static analysis assumes a fixed, average per-instance current draw derived from Liberty leakage/average-switching power, and solves `V = IR` (in its network form, `G × V = I`) across the full resistive network.

### Resistive Network
The complete Stage D network, comprising rings, straps, rails, and vias, annotated with technology-derived or OpenRCX-extracted resistance values.

### Voltage Propagation
Voltage is not uniform across the PDN; nodes farther (in resistive-network terms, not merely geometric terms) from a voltage source exhibit progressively greater drop, a phenomenon this phase's full network solve captures precisely rather than approximating via a simple geometric-distance heuristic.

### Worst-Case Drop
The single node exhibiting the maximum static voltage drop across the entire chip, tracked as the primary Part 10 Maximum IR Drop metric and as the primary Objective O1 compliance criterion.

### Cell-Level IR
The voltage drop specifically at standard-cell power pins, the most numerous node class in the network and the class most directly relevant to timing-margin erosion (since Phase 14.11's STA assumes nominal VDD at every cell unless re-derated using this phase's findings).

### Macro-Level IR
The voltage drop at macro power pins, tracked separately from standard-cell IR since macros typically draw substantially higher per-instance current (particularly memory macros) and can locally dominate a chip's worst-case IR figure even when the surrounding standard-cell fabric is well within margin.

### Voltage Maps
The full-chip spatial record of every node's solved voltage, the primary Stage E output and a mandatory Part 11 deliverable (Objective O8).

### Solver
PDNSim's static linear-system solver (Part 4), configured in this phase's fixed, deterministic mode (Objective O10).

### Convergence
The solver's iterative or direct-factorization process is considered converged when its residual falls below a documented tolerance; non-convergence is a hard Stage E failure (Part 12), never silently accepted as an approximate result.

### Engineering Rationale
Static IR analysis is retained as a mandatory, always-run check (rather than being subsumed entirely by the more realistic dynamic analysis) because it is faster, more numerically stable, and provides a conservative baseline sanity check independent of any activity-model assumption uncertainty; a design failing static IR analysis is known to be inadequate regardless of any subsequent dynamic-analysis refinement.

### Validation
Cross-checked against a simplified, independent analytical estimate (average current × average resistive-path length) as a sanity bound, in addition to the solver's own residual-convergence check.

### Industrial Notes
Directly analogous to the static IR-drop signoff step universal across commercial power-integrity tools (Voltus, RedHawk, PrimePower), performed identically in position within the overall physical-implementation flow.

---

## PART 8 — Dynamic IR Drop Analysis

### Switching Activity
The fraction of clock cycles in which a given instance's output toggles; consumed from Phase 14.5's synthesis-stage activity assumptions (Part 7 of that phase's constraint methodology) where available, or from a documented conservative default activity factor otherwise.

### Clock Activity
The clock network itself (Phase 14.8) is treated as a 100%-activity-factor network by construction (every clock buffer switches every cycle), making it, cycle-for-cycle, the single most activity-dense sub-network in the design and consequently a dominant contributor to Stage F's peak-current estimate.

### Peak Current
The maximum instantaneous current draw across the analyzed time window (or, in vectorless mode, the maximum statistically-weighted current estimate), the primary driver of the worst-case transient voltage drop.

### Transient Current
The time-varying current waveform following a clock edge, rising sharply as clocked elements and their downstream logic switch and decaying as switching activity subsides within the remainder of the clock period; modeled explicitly in time-domain mode (Stage F) or statistically summarized in vectorless mode.

### Simultaneous Switching
The phenomenon whereby a large fraction of a design's sequential elements (and a correlated fraction of downstream combinational logic) switch within a narrow time window immediately following a clock edge, producing the characteristic sharp current spike that static analysis, by construction, cannot capture.

### Current Pulses
The discrete, per-switching-event current contribution of each instance, summed (with appropriate timing offset per Part 3's SPEF-informed switching-timing refinement) to produce the aggregate transient current waveform.

### Package Effects
The package's parasitic inductance (not modeled in this phase's resistive-only network, per Part 4's scope boundary) would, in a full RLC treatment, contribute additional transient voltage overshoot/undershoot ("di/dt noise") beyond the resistive IR-drop component analyzed here; this phase explicitly flags dynamic IR-drop results as a resistive-only lower bound on true transient voltage-drop severity, deferring full RLC/di-dt analysis to a documented future extension (Part 1's engineering-rationale precedent of flagging conservative simplifying assumptions explicitly rather than silently).

### Temporal Voltage Drop
The voltage-drop waveform's evolution across the analyzed time window, summarized (in time-domain mode) as a worst-case-instant snapshot for QoR reporting purposes, while the full waveform is retained in raw logs for any deeper post-hoc analysis.

### Activity Assumptions
This phase's default vectorless activity model assumes a documented, conservative worst-case correlated-switching fraction (rather than assuming fully independent, uncorrelated per-instance switching, which would understate peak current); the specific correlation-fraction parameter is archived in the configuration snapshot (Objective O12) for every run.

### Engineering Rationale
Dynamic IR-drop analysis is treated as materially more important than static analysis for genuine functional-risk characterization (Part 1), but is deliberately not made the *sole* mandatory check, since its vectorless statistical nature carries more inherent modeling uncertainty than the static solve's simpler, more directly verifiable current assumption.

### Future Scalability
The vectorless/time-domain duality (Stage F) and the explicit resistive-only scope flag (Package Effects, above) together define a clear, documented extension path toward a future full RLC, di/dt-aware dynamic analysis phase, without requiring any restructuring of this phase's Stage F I/O contract.

---

## PART 9 — Power Integrity Optimization

### Purpose
To document the remediation strategies available when Stage H validation identifies an objective violation, and the order in which they are applied.

### Grid Strengthening
The general strategy of increasing PDN conductance in a violating region, encompassing the more specific techniques below; the default first-line remediation strategy given its broad applicability across most violation types.

### Via Insertion
Adding additional parallel via instances at strap/rail intersections exhibiting high current-through-via values (Part 10), directly reducing local via resistance and via-current-density risk; typically the lowest-cost remediation (minimal additional routing-resource consumption) and therefore attempted before strap widening.

### Power Strap Widening
Increasing strap width in a hotspot-adjacent region, reducing that segment's resistance at the cost of additional routing-layer area consumption; applied where via insertion alone is insufficient to resolve a violation.

### Additional Stripes
Inserting entirely new strap/rail stripes in a locally under-provisioned region (most relevant where Stage B's as-routed grid-density measurement reveals routing-stage-induced strap thinning relative to the Phase 14.6 floorplan-stage intent); the most routing-resource-intensive remediation and therefore the last-attempted option in this phase's default remediation ordering.

### Current Redistribution
Where feasible, redistributing a portion of a hotspot region's current draw by re-examining placement-stage cell locality (a cross-phase remediation requiring, in the general case, a return to Phase 14.7); flagged in this phase's failure/remediation reporting as a documented option but not automated within this phase's own scope, since placement modification is outside this phase's stage boundary.

### Voltage Recovery
The general goal-state of any remediation: restoring the worst-case node's voltage to within the Objective O1/O2 threshold plus the Objective O4 guard-band.

### Hotspot Mitigation
The application of the above techniques specifically targeted at Stage G's ranked hotspot regions, addressed in severity-rank order (worst hotspot first) rather than uniformly across the entire chip, for remediation-effort efficiency.

### Engineering Tradeoffs
Every remediation technique above trades additional PDN metal-layer resource consumption against reduced signal-routing resource availability (Part 6's Engineering Tradeoffs precedent); this phase documents, but does not automatically resolve, this tradeoff, since a genuinely optimal resolution requires re-entering the routing phase (14.9) with updated PDN constraints — a documented, explicit hand-off point rather than an implicit assumption.

### Optimization Order
Consistent with the ordering implied above: via insertion, then strap widening, then additional stripes, then (as a cross-phase escalation) placement-stage current redistribution; this fixed default ordering ensures Objective O10's determinism guarantee extends to the remediation-recommendation process itself, not merely to the initial analysis.

### Power-Aware DTCO
This phase's remediation-ordering discipline and its explicit as-planned-versus-as-routed measurement (Objective O5) together constitute this phase's most direct contribution to the paper's design-technology co-optimization thesis: a measured, quantified feedback loop from early floorplan-stage PDN intent (Phase 14.6) through final routed-stage electrical reality (this phase), with a documented, ranked remediation path back into the flow where violations are found.

---

## PART 10 — Quality Metrics

### Maximum IR Drop
**Definition:** The single largest voltage drop (V or % of VDD) observed across the static voltage map. **Importance:** the primary Objective O1 compliance figure. **Rationale:** a single worst-case number is the most conservative, safety-relevant summary statistic. **Measurement:** direct maximum over Stage E's voltage map. **ML relevance:** a primary label for manufacturing/reliability-risk prediction models.

### Average IR Drop
**Definition:** The mean voltage drop across all analyzed nodes. **Importance:** a chip-wide PDN-adequacy indicator, complementing the worst-case figure. **Rationale:** distinguishes a chip with one severe localized hotspot from one with uniformly moderate drop. **Measurement:** arithmetic mean over Stage E's voltage map. **ML relevance:** a secondary, distribution-shape-informing feature.

### Minimum Voltage
**Definition:** The lowest absolute voltage (not drop percentage) observed at any node, under both static and dynamic analysis. **Importance:** the direct, non-normalized correlate of voltage-collapse risk (Part 1). **Rationale:** normalized (%) figures can obscure absolute-voltage-scale effects relevant across different supply-voltage technology classes (Sky130/GF180 versus ASAP7). **Measurement:** direct minimum over the voltage map. **ML relevance:** a technology-normalized-risk feature, particularly relevant for cross-library comparison.

### Voltage Margin
**Definition:** The difference between Minimum Voltage and the documented voltage-collapse threshold (Part 1, Objective O4). **Importance:** the direct Objective O4 compliance figure. **Rationale:** margin, not bare pass/fail, is the more informative risk-gradation feature. **Measurement:** arithmetic difference. **ML relevance:** a continuous-valued risk-gradation label, more useful for regression-style ML models than a binary pass/fail.

### Static IR
**Definition:** The complete Stage E result set (Maximum/Average IR Drop, Minimum Voltage), reported as a distinct labeled group from Dynamic IR. **Importance:** isolates the activity-model-independent baseline signal. **Rationale:** Part 1's static/dynamic distinction. **Measurement:** Stage E. **ML relevance:** a lower-variance, more reproducible feature subset than dynamic IR, useful as a stable baseline feature.

### Dynamic IR
**Definition:** The complete Stage F result set, reported distinctly from Static IR. **Importance:** the more physically realistic risk signal (Part 1). **Rationale:** as above. **Measurement:** Stage F. **ML relevance:** the paper's primary functional-risk-relevant feature subset, at the cost of higher activity-model-dependent variance, documented explicitly (Part 8).

### Power Density
**Definition:** Total power (W) divided by core area (Phase 14.6's core-area QoR field), per unit area (W/µm²). **Importance:** a normalized, cross-design-comparable power-intensity figure. **Rationale:** raw total power is not comparable across differently-sized designs. **Measurement:** Phase 14.5 total power QoR divided by Phase 14.6 core-area QoR. **ML relevance:** a normalized feature enabling cross-design comparison independent of absolute design scale.

### Current Density
**Definition:** Current per unit cross-sectional area for every metal/via segment, with the maximum value reported as a summary figure. **Importance:** directly connects to Objective O6 (current-density validation) and to electromigration-relevant reliability risk. **Rationale:** Part 1. **Measurement:** per-segment current (from Stage E/F) divided by segment cross-sectional area (from LEF geometry). **ML relevance:** a direct reliability-risk feature, central to the paper's thesis.

### Hotspot Count
**Definition:** The total number of distinct hotspot regions identified by Stage G. **Importance:** a breadth-of-risk indicator, complementing the single-worst-case figures above. **Rationale:** Objective O7. **Measurement:** Stage G's clustering output count. **ML relevance:** a count-valued feature informing risk-distribution-shape prediction.

### Worst Hotspot
**Definition:** The peak IR-drop value and affected-instance count of the single most severe Stage G hotspot region. **Importance:** the most safety-critical spatially-localized figure. **Rationale:** aggregate statistics alone (Average IR Drop) can mask this. **Measurement:** Stage G's top-ranked hotspot record. **ML relevance:** a high-signal feature for localized-failure-risk prediction.

### Metal Utilization
**Definition:** The fraction of each routing layer's area consumed by PDN geometry (Part 6). **Importance:** quantifies the PDN-versus-signal-routing resource tension. **Rationale:** Part 6's Engineering Tradeoffs discussion. **Measurement:** geometric area computation per layer from Stage B's as-routed PDN geometry. **ML relevance:** a resource-tension feature relevant to congestion-risk co-prediction alongside Phase 14.6's floorplan-stage congestion estimate.

### Power Grid Utilization
**Definition:** The overall PDN metal consumption relative to the total available routing resource across all layers (an aggregate of Metal Utilization above). **Importance:** a single-figure PDN-resource-intensity summary. **Rationale:** complements the per-layer breakdown with an easily-compared aggregate. **Measurement:** weighted aggregate over Metal Utilization. **ML relevance:** a compact summary feature for cross-design PDN-intensity comparison.

### Via Count
**Definition:** Total PDN via instance count, and specifically the count at each strap/rail intersection (informing redundancy, Part 6). **Importance:** a structural PDN-robustness indicator. **Rationale:** Part 6's Via Ladders discussion. **Measurement:** direct count from the Part 3 via database. **ML relevance:** a structural feature correlating with hotspot risk.

### Current Through Vias
**Definition:** The current flowing through each PDN via instance, with the maximum value reported as a summary figure. **Importance:** directly relevant to both IR-drop and electromigration risk at the via level, a well-documented failure-concentration point (Part 1). **Rationale:** vias are typically the highest-resistance, highest-current-density individual elements in the network. **Measurement:** Stage E/F's per-edge current solution restricted to via-type edges. **ML relevance:** a fine-grained reliability-risk feature.

### Voltage Histogram
**Definition:** A binned distribution of node voltages across the full chip (static and dynamic, separately). **Importance:** captures the full risk distribution shape, not merely its extremes or mean. **Rationale:** complements Maximum/Average/Minimum with distributional detail. **Measurement:** binning of the Stage E/F voltage map. **ML relevance:** a distribution-shape feature directly consumable as an input to CNN-based spatial models (Phase 5), analogous to how a wafer-map defect distribution is consumed.

### Power Map Statistics
**Definition:** Summary statistics (mean, standard deviation, skewness) of the per-instance current-draw distribution (Stage C). **Importance:** characterizes current-demand concentration independent of the PDN's resistive response. **Rationale:** distinguishes a "hard to deliver power to" design (concentrated current demand) from a "PDN inadequate" design (weak grid regardless of demand pattern) — an important causal distinction for remediation targeting (Part 9). **Measurement:** statistical computation over Stage C's current assignment. **ML relevance:** a causally-informative feature pair (paired with grid-topology features) for root-cause-aware ML modeling.

### Runtime
**Definition:** Wall-clock time consumed by each pipeline stage and the phase overall. **Importance:** an operational, engineering-management metric distinct from the design's electrical QoR. **Rationale:** essential for corpus-scale batch-planning (Part 13). **Measurement:** direct timing instrumentation per stage. **ML relevance:** not used as a design-quality feature but retained for pipeline-performance meta-analysis.

### Memory
**Definition:** Peak RSS consumed by each pipeline stage. **Importance:** as above, an operational metric. **Rationale:** informs cluster-execution resource allocation (Part 13). **Measurement:** direct process-memory instrumentation. **ML relevance:** pipeline-performance meta-analysis only.

### Solver Iterations
**Definition:** The iteration count (for iterative solvers) or factorization statistics (for direct solvers) consumed by Stage E/F's linear-system solve. **Importance:** a solver-health and reproducibility-relevant figure (Objective O10). **Rationale:** unexpected iteration-count variance across nominally-identical runs would indicate a determinism defect. **Measurement:** direct solver instrumentation. **ML relevance:** not a design-quality feature; a pipeline-integrity diagnostic.

### Additional ML-Ready Metrics
Beyond the above, this phase archives the complete raw voltage map (Objective O8, full spatial resolution) and the complete hotspot-region geometry list (Objective O7) as directly ML-consumable artifacts (Part 11), rather than only their summary statistics, so that future spatial-feature-extraction work (analogous to the paper's CNN wafer-map defect-detection methodology) is not constrained to the scalar metrics enumerated above.

---

## PART 11 — Outputs

### Reports
Human-readable summaries of static and dynamic IR-drop results, hotspot findings, and objective-compliance status, generated per (design, library, corner) triple.

### Voltage Maps
The complete, full-resolution static and dynamic voltage-map data (Objective O8), archived in a structured raster or grid-value format suitable for both visualization and direct ML ingestion.

### Heatmaps
Rendered raster visualizations of the voltage maps and current-density maps, supporting rapid human QA review, consistent with the visualization-deliverable precedent established in Phase 14.6, Part 11.

### CSV
Tabular per-node or per-grid-cell voltage and current-density data, provided as an alternative, spreadsheet-compatible format alongside the primary JSON schema.

### JSON
The complete Part 10 QoR schema record, the primary machine-consumable deliverable, one per (design, library, corner) triple.

### Power Integrity Reports
A consolidated report combining Stage H's objective-compliance record with Stage I's QoR schema, forming the single authoritative power-integrity-signoff document per design.

### Hotspot Maps
Stage G's ranked hotspot region geometry, archived both as structured data (for ML ingestion) and as an overlay visualization atop the base voltage-map heatmap.

### Manifest
The benchmark manifest, updated with this phase's power-integrity status (pending/complete/failed) per (library, corner) triple, extending the resume-capability model established since Phase 14.5.

### Visualization
Consolidated visualization artifacts (voltage-map heatmaps, hotspot overlays, current-density maps), archived per design.

### Logs
Full tool logs (PDNSim, OpenRCX, OpenDB, OpenLane2 orchestration) retained for every run, supporting forensic debugging, consistent with every prior Phase 14.x precedent.

### Configuration Snapshots
The exact analysis configuration (activity-model parameters, thresholds, hotspot-detection sensitivity) archived verbatim, satisfying Objective O12.

### Engineering Rationale
As in every prior Phase 14.x document, treating configuration snapshots and manifest updates as first-class outputs is what keeps the multi-phase pipeline resumable and auditable at corpus scale.

### Validation
An output-completeness checker confirms all eleven output classes exist for every successfully completed run before the manifest is marked complete, performed as part of Stage J.

---

## PART 12 — Failure Handling

### Power Grid Disconnected
Detected at Stage B; logged as `failed:pdn_disconnected` with the specific unreachable node/sub-network identified; the design is excluded from that (library, corner) run without blocking other designs, consistent with the fail-forward-per-design philosophy established since Phase 14.5.

### IR Limit Exceeded
Detected at Stage H when Objective O1 or O2's threshold is violated; logged as `failed:ir_limit_exceeded` with the specific violating node(s) and margin identified; distinguished explicitly from the more severe voltage-collapse condition below.

### Voltage Collapse
Detected at Stage H when a node's voltage falls below the more severe, functionally-critical threshold (Part 1); logged as `failed:voltage_collapse` and treated as a higher-priority finding than an ordinary IR-limit violation, warranting immediate remediation-path escalation (Part 9) rather than routine batch continuation.

### Solver Divergence
Detected at Stage E/F when the linear-system solver fails to converge within a documented iteration/time budget; logged as `failed:solver_divergence`, distinguished from an ill-conditioned-matrix failure (below) by checking whether the underlying network is well-formed before attributing the failure to solver behavior specifically.

### Missing Power Net
Detected at Stage A/B when a declared power net has no corresponding routed geometry; logged as `failed:missing_power_net`.

### Missing Ground
The symmetric counterpart, logged as `failed:missing_ground`, checked with equal rigor per Part 4's power/ground-symmetry discipline.

### Via Failures
Detected at Stage D/E when a via's resistance data is missing or its current (Stage E/F) exceeds a documented sanity bound indicating a likely modeling defect rather than a genuine design issue; logged as `failed:via_failure`.

### Current Density Overflow
Detected at Stage E/F/H when Objective O6's current-density limit is exceeded; logged as `failed:current_density_overflow` with the specific violating segment/via identified.

### Database Corruption
Detected via ODB internal consistency checks at Stage A/J; logged as `failed:db_corruption` and escalated as a high-priority infrastructure incident rather than an ordinary per-design failure, consistent with the Phase 14.6 Part 12 precedent for this failure class.

### Manifest Failures
Detected when the manifest's floorplan/routing-status prerequisite fields (from Phases 14.6–14.11) indicate an incomplete upstream state; logged as `failed:manifest_prerequisite`, preventing this phase from attempting analysis on a design that has not genuinely completed all required upstream phases.

### Recovery Strategy
Consistent with every prior Phase 14.x document: fail-forward-per-design. A failure on one (design, library, corner) triple never blocks any other triple; the batch orchestrator continues processing the remaining queue, with `failed:db_corruption` and `failed:voltage_collapse` findings additionally flagged for priority human review given their severity.

### Logging
Every failure is logged to the same structured failure-ledger (JSON lines) format established in Phase 14.5 and extended in every subsequent phase, with this phase's failure classes appended to the ledger schema.

### Validation
Weekly aggregate failure-rate review, consistent with the monitoring cadence established since Phase 14.5, with particular attention to any spike in `voltage_collapse` findings, which may indicate a systemic PDN-architecture inadequacy across a benchmark family rather than isolated per-design issues.

---

## PART 13 — Automation

### ir_drop.py
The top-level per-design driver for this phase: consumes the Part 3 input classes for a single (design, library, corner) triple, invokes Stages A–J via PDNSim/OpenRCX/OpenDB (orchestrated through OpenLane2), and produces the complete Part 11 output set. Fixed tool versions pinned in the repository's environment lock file (Phase 13 — Repository Engineering).

### pdn_solver.py
Implements Stages B–E (power grid loading through static IR analysis) as an independently invocable module, enabling static-only studies without incurring the substantially higher runtime/memory cost of dynamic analysis.

### dynamic_ir.py
Implements Stage F in isolation, wrapping PDNSim's dynamic/vectorless analysis mode with the Part 8 activity-model configuration exposed as explicit, logged parameters.

### hotspot_detector.py
Implements Stage G in isolation, consuming a previously-generated voltage map (from either `pdn_solver.py` or `dynamic_ir.py`) and applying the clustering algorithm independently, supporting rapid re-tuning of hotspot-detection sensitivity without re-running the underlying solve.

### power_qor.py
Implements Stage I, populating the Part 10 QoR schema from the outputs of the above scripts.

### validate_power.py
Implements Stage H and Stage J: applies the complete Objective compliance check set and the final output-completeness/determinism verification.

### Checkpointing
Given this phase's substantial dynamic-analysis runtime (Part 1), `ir_drop.py` checkpoints intermediate state after each stage (A through J), allowing a failure late in the pipeline (e.g., at Stage H) to resume from the last completed stage rather than re-running the expensive Stage E/F solves.

### Resume
The manifest's per-(design, library, corner) power-integrity-status field (Part 11) allows the batch orchestrator to skip already-`complete` triples, consistent with the resume model established since Phase 14.5, and to resume mid-pipeline via the checkpointing mechanism above for partially-completed triples.

### Parallel Execution
Independent (design, library, corner) triples are dispatched to a bounded worker pool, sized conservatively given this phase's substantial per-job memory footprint (Part 1), consistent with the worker-pool model established since Phase 14.5.

### Cluster Execution
Extended to a job-scheduler-backed cluster identically to every prior Phase 14.x precedent, with the single-design driver (`ir_drop.py`) kept identical between local and cluster execution; given this phase's runtime profile, cluster execution is expected to be the primary execution mode for full-corpus dynamic-analysis batches rather than an optional scale-out path.

### Manifest-Driven Execution
The batch orchestrator's sole source of work is the benchmark manifest's power-integrity-pending entries, consistent with the single-source-of-truth principle established since Phase 14.5.

### Dry-Run Mode
A `--dry-run` flag on `ir_drop.py` validates the full Part 3 input set for an entire pending batch (including manifest-prerequisite checks against Phases 14.6–14.11's completion status) without consuming solver compute, catching input errors before expensive dynamic-analysis runtime is spent, directly analogous to every prior phase's dry-run precedent.

---

## PART 14 — Repository Structure

```
power_integrity/
├── configs/
│   └── {design_name}/{library}/{corner}.json
├── scripts/
│   ├── ir_drop.py
│   ├── pdn_solver.py
│   ├── dynamic_ir.py
│   ├── hotspot_detector.py
│   ├── power_qor.py
│   └── validate_power.py
├── stages/
│   ├── stage_a_init/
│   ├── stage_b_grid_loading/
│   ├── stage_c_current_estimation/
│   ├── stage_d_resistance_network/
│   ├── stage_e_static_ir/
│   ├── stage_f_dynamic_ir/
│   ├── stage_g_hotspot/
│   ├── stage_h_validation/
│   ├── stage_i_qor/
│   └── stage_j_final_validation/
├── schema/
│   └── power_qor_schema.json
├── runs/
│   └── {design_name}/{library}/{corner}/
│       ├── checkpoints/
│       └── session_state.odb
├── reports/
│   └── {design_name}/{library}/{corner}/
│       ├── power_integrity_report.txt
│       ├── qor.json
│       └── qor.csv
├── visualization/
│   └── {design_name}/{library}/{corner}/
│       ├── static_voltage_heatmap.png
│       ├── dynamic_voltage_heatmap.png
│       └── hotspot_overlay.png
├── failure_ledger/
│   └── failure_ledger.jsonl
├── docs/
│   └── methodology.md
└── manifest_status.json
```

### Engineering Rationale
This layout mirrors the modular structure established since Phase 14.5/14.6, keeping configuration, scripts, per-stage intermediate state, schema, run artifacts, reports, visualization, and failure records in clearly separated, independently-versionable trees.

### Validation
A repository-structure linter confirms presence of all required directories before any batch run starts.

---

## PART 15 — Deliverables

1. The complete, version-controlled power-integrity analysis flow (Parts 13/14).
2. The full static and dynamic IR-drop QoR record corpus (Part 10 schema) across all designs × compatible libraries × corners — a third-stage ground-truth label set complementing Phase 14.5's synthesis QoR and Phase 14.6's floorplan QoR.
3. The complete voltage-map and hotspot-map corpus, archived at full spatial resolution for direct ML ingestion (Objective O14).
4. The failure ledger (Part 12), disclosed as a first-class research artifact, including explicit `voltage_collapse` and `pdn_disconnected` incident records.
5. Updated per-design metadata and benchmark manifest (Part 11), including power-grid topology summaries.
6. Heatmap and hotspot-overlay visualizations for the full corpus, supporting both human QA and future image-based ML feature extraction.
7. This specification document itself, serving as the methodology section basis for the eventual paper's power-integrity discussion.

### Engineering Rationale
Consistent with every prior Phase 14.x precedent, treating the failure ledger and flow scripts as deliverables — not just the "passing" designs — is essential for IEEE Artifact Evaluation's transparency expectations.

### Validation
A deliverables-completeness checklist is run before the phase is declared closed.

---

## PART 16 — Publication Readiness

### IEEE Reproducibility
Every power-integrity analysis decision in this document is stated as a fixed, versioned rule rather than a tool default, satisfying IEEE's reproducibility expectations; the flow-script hash, tool version pinning (Part 13), and configuration-snapshot archival (Part 11) provide the concrete reproducibility anchor, consistent with every prior Phase 14.x document.

### Artifact Evaluation
The dry-run validation mode, the failure ledger, and the fixed repository structure collectively satisfy the standard Artifact Evaluation criteria of *available*, *functional*, and *reusable*, consistent with the precedent established in Phase 14.5/14.6.

### Industrial Deployment
The strict input/output contracts, the deterministic static/dynamic analysis methodology (Parts 7–8), and the fail-forward batch model make this flow directly adoptable as an internal power-integrity-signoff pipeline by an industrial EDA or foundry design-enablement team, extending beyond its research use.

### Zenodo Compatibility
The Part 14 repository structure, combined with archived configuration snapshots and a versioned flow-script set, is directly packageable as a Zenodo-archived, DOI-citable artifact accompanying the paper.

### Reviewer Expectations
Reviewers should conclude this phase demonstrates a genuine, measured closure of the loop between early PDN-architecture decisions (Phase 14.6) and final, as-routed electrical reality — the central empirical contribution this phase makes to the paper's DTCO thesis — rather than treating power-integrity analysis as a perfunctory, late-stage checkbox.

### Dataset Generation
The complete voltage-map, hotspot, and QoR corpus produced by this phase constitutes one of the paper's most directly reliability-relevant ML training-label sources, given current density and IR-drop's well-established literature linkage to electromigration and functional-failure risk.

### Future Scalability
This phase's technology-independent resistance modeling (Part 4), extensible failure taxonomy (Part 12), and modular script boundaries (Part 13) are explicitly designed so that a future dedicated electromigration-lifetime-signoff phase, or a future full RLC/di-dt dynamic-analysis phase, can be appended without any retroactive modification to Phase 14.12's locked content.

### Connection to Phase 14.13
This phase's outputs — most directly the validated, as-routed PDN geometry and its confirmed electrical adequacy — form a necessary precondition for Phase 14.13's physical verification (DRC/LVS/antenna checking), since antenna-rule violations in particular are directly related to the same metal/via geometry this phase has already characterized electrically; Phase 14.13 is explicitly scoped to begin only after this phase's Stage J final validation has passed.

---

**END OF PHASE 14.12**

*This document continues seamlessly from the locked Phase 14.11 (Post-Route Static Timing Analysis & Timing Closure) and is itself locked upon completion at validated power-integrity outputs (Stage J). The next phase (14.13) addresses Physical Verification — DRC/LVS/Antenna, per the explicit scope boundary established in this document's task definition.*
