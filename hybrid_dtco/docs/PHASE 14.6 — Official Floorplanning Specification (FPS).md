# PHASE 14.6 — Official Floorplanning Specification (FPS)

**Paper:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target:** IEEE International Conference on Microelectronics (ICM 2026)
**Document Class:** Industrial Engineering Specification (continues directly after Phase 14.5 — Logic Synthesis & Technology Mapping Specification)

---

## PART 1 — Floorplanning Philosophy

### Purpose
Phase 14.6 defines the authoritative methodology by which a technology-mapped gate-level netlist (Phase 14.5 output) is converted into a validated, physically-realizable floorplan: a fixed die and core geometry, placed macros, planned I/O, and a provisioned power delivery skeleton, upon which all later placement, clock-tree synthesis, and routing phases will build.

### Theory
Floorplanning is the first stage at which a design acquires physical coordinates. It is fundamentally a resource-allocation problem: given a netlist's cell area, macro inventory, and pin count, determine a die/core geometry and a macro/IO arrangement that simultaneously satisfies utilization targets, timing-relevant proximity constraints, and power-delivery feasibility, while leaving sufficient whitespace and routing resource for the stages that follow. Unlike synthesis (Phase 14.5), whose transformations are Boolean-equivalence-preserving, floorplanning transformations are *geometry-defining*: they do not change logical function but they irreversibly constrain every subsequent physical decision.

### Engineering Rationale
Because floorplan-stage geometric decisions (die size, macro placement, power grid density) are strongly correlated with downstream manufacturing and packaging outcomes — congestion-induced yield loss, IR-drop-induced timing failures, macro-boundary-induced routing blockages — this phase is treated with the same reproducibility discipline as Phase 14.5. Every geometric decision must be derivable from a documented rule, not an unrecorded tool heuristic, so that floorplan-stage features can be used as trustworthy, explainable inputs to the paper's downstream manufacturing/reliability prediction models.

### Inputs
Technology-mapped netlist and QoR record (Phase 14.5), LEF library set, timing constraints, design/benchmark metadata, and configuration/manifest records (Part 3).

### Outputs
A validated floorplan expressed in DEF/ODB form, together with the full floorplan QoR schema (Part 10) and associated reports, logs, and metadata (Part 11).

### Dependencies
OpenROAD and the OpenLane2 flow orchestration layer (Part 4), the technology LEF/standard-cell LEF/macro LEF set, and the Phase 14.5 netlist corpus.

### Runtime Expectations
Small designs (≤50k instances, no macros): under 5 minutes. Macro-heavy designs (multiple SRAM/IP macros): 15–45 minutes, dominated by macro placement legalization (Stage E) and floorplan validation (Stage I).

### Memory Expectations
Typically 1–6 GB for standard-cell-only designs; macro-heavy designs may require 6–12 GB due to the physical database (ODB) holding full geometric and connectivity information simultaneously.

### Failure Conditions
Infeasible utilization targets, macro overlap that cannot be legalized, insufficient die area for the declared IO count, or power-grid infeasibility under the declared current budget (Part 12).

### Validation
Every floorplan is passed through a dedicated validation stage (Stage I) checking geometric legality, macro/IO/power consistency, and manufacturing-grid alignment before being admitted to the corpus.

### Industrial Notes
This philosophy mirrors the "floorplan sign-off" discipline used in industrial physical design, where a floorplan is not considered complete until it has independently passed a DRC-lite geometric legality check, separate from the interactive floorplanning session that produced it.

### Reviewer Expectations
Reviewers should expect every die/core/macro/power decision to be traceable to an explicit rule in this document, not to an unexplained tool default.

### Future Scalability
The floorplanning methodology is technology-node-agnostic by construction (Part 4's coordinate/units abstraction), allowing the same rule set to apply across Sky130, GF180, and ASAP7 (Phase 14.5's library set) without modification.

---

## PART 2 — Objectives

### Purpose
To enumerate the measurable, testable objectives that every generated floorplan must satisfy prior to corpus admission.

### O1 — Deterministic Floorplan Generation
Identical netlist + identical configuration + identical library ⇒ bit-identical DEF output across repeated runs. This requires fixing every stochastic element of macro placement (Stage E) to a recorded seed and disabling any non-deterministic multi-threaded geometry solving.

### O2 — Technology Independence
The floorplanning rule set (die-margin policy, aspect-ratio bounds, macro-halo policy) must be expressible without reference to a specific technology node's numeric constants; all node-specific values (manufacturing grid, minimum spacing) are read from the technology LEF (Part 4), never hardcoded in flow scripts.

### O3 — Reproducibility
Every floorplan must be regenerable from its recorded configuration snapshot (Part 11) alone, without requiring the original interactive session or undocumented manual edits.

### O4 — Macro Placement Consistency
For a given design synthesized against multiple libraries (Phase 14.5's multi-library objective O3), the *relative* macro placement strategy (clustering, orientation policy, channel allocation — Part 7) must follow identical rules across libraries, even though absolute coordinates will differ due to differing macro footprints.

### O5 — IO Planning Consistency
Pin ordering and side-assignment rules (Part 8) must be applied identically regardless of design size, so that IO-density QoR features (Part 10) are comparable across the corpus.

### O6 — Physical Constraint Completeness
Every floorplan must carry a complete, non-null record of die/core geometry, macro placement, IO assignment, and power-grid parameters (Part 10/11) before being marked complete in the manifest; partial floorplans are never silently admitted.

### Engineering Rationale
These six objectives collectively ensure that floorplan-stage QoR features are as trustworthy a label source for the paper's ML models as the Phase 14.5 synthesis QoR features, preserving the end-to-end reproducibility chain established since Phase 14.1.

### Inputs / Outputs
Inputs: none beyond the general Phase 14.6 input set. Outputs: an objectives-compliance checklist attached to each floorplan's metadata record, verified by `validate_floorplan.py` (Part 13).

### Dependencies
O1 depends on OpenROAD's deterministic-mode configuration (Part 13); O4/O5 depend on the macro/IO rule sets fixed in Parts 7–8.

### Runtime / Memory Expectations
Objective verification is a lightweight post-processing check, typically under 10 seconds per floorplan.

### Failure Conditions
Failure of O1 on a sampled re-run (a subset audit, consistent with the Phase 14.5 sampling methodology) triggers a full re-audit of that configuration/library combination.

### Validation
`verify_objectives.py` (extended from its Phase 14.5 form) checks O1–O6 automatically per floorplan.

### Industrial Notes
Mirrors floorplan QA checklists used before a floorplan is released to the placement team in industrial physical design sign-off.

### Reviewer Expectations
Reviewers should be able to map each objective directly to a specific validation check in Part 12/13.

### Future Scalability
Additional objectives (e.g., O7 — thermal-aware macro placement) can be appended without restructuring this document.

---

## PART 3 — Inputs

### Purpose
To precisely define every artifact consumed by the floorplanning stage.

### Technology-Mapped Netlist (Phase 14.5)
The structural gate-level Verilog netlist, per (design, library, corner), forming the connectivity backbone onto which physical coordinates are assigned.

### LEF Files

**Technology LEF.** Defines the fabrication process's routing layers, manufacturing grid, layer directions, and minimum-width/spacing design rules; consumed to establish the coordinate system and legal placement grid (Part 4).

**Standard Cell LEF.** Provides the abstract physical footprint (cell outline, pin locations, blockage shapes) for every standard cell used by the mapped netlist; required for legal cell-row and site definition even though standard cells are not individually placed until Phase 14.7.

**Macro LEF.** Provides the abstract footprint, pin locations, and blockage/halo geometry for every hard macro (e.g., SRAM compilers, hard IP) instantiated in the netlist; the primary geometric input to Stage E (Macro Placement).

### Timing Constraints
The SDC constraint set carried forward from Phase 14.5 (Part 7 of that phase); floorplanning does not re-author constraints but uses clock definitions to inform macro proximity heuristics (Part 7) relevant to later CTS feasibility.

### Library Information
The `.lib` timing/power data (Phase 14.5, Part 6), consulted only for cell-count-to-area estimation during die-size estimation (Stage B); no timing optimization occurs in this phase.

### Benchmark Metadata
The Phase 14.2/14.3 benchmark manifest entry, providing design-family classification used to select an appropriate default aspect-ratio and utilization policy (Part 6) where the design itself provides no explicit target.

### Design Metadata
The per-design metadata record (Phase 14.5, Part 3), extended in this phase with the design's macro inventory (count, type, footprint) extracted from the netlist and macro LEF.

### Configuration Files
A per-design floorplan configuration (utilization target, aspect-ratio bound, IO-side assignment policy, power-grid density class) authored under the rules fixed in Parts 6–9, and version-controlled alongside the design.

### Manifest
The master ledger, extended with a floorplan-status field per (design, library, corner) triple, consistent with the resume-capability model established in Phase 14.5, Part 13.

### Engineering Rationale
As in Phase 14.5, separating these input classes allows independent versioning: a macro LEF can be updated without re-authoring floorplan configuration, and a new aspect-ratio policy can be applied without touching the netlist.

### Dependencies
Depends on the successful, locked completion of Phase 14.5 for the netlist and library inputs.

### Runtime / Memory Expectations
Input validation is O(1) per design, negligible runtime (<1 second).

### Failure Conditions
Missing macro LEF for an instantiated macro, hash-mismatched netlist, or malformed configuration file abort the job before any floorplanning compute is spent.

### Validation
A pre-flight checker (extended `preflight_check.py`, Part 13) enforces presence and integrity of all input classes.

### Industrial Notes
Mirrors the "floorplan kickoff checklist" used before a floorplanning engineer begins work in an industrial physical design flow.

### Reviewer Expectations
Reviewers should see this six-class input schema as the concrete answer to "what exactly goes into your floorplanning experiment."

### Future Scalability
Additional input classes (e.g., thermal maps for future thermal-aware floorplanning) can be appended as a seventh class without disrupting existing jobs.

---

## PART 4 — Physical Design Environment

### Purpose
To define the physical database environment and coordinate conventions within which all floorplanning operations occur.

### Theory
A physical design database must establish an unambiguous, technology-consistent coordinate system before any geometric object (die boundary, macro, pin) can be placed. OpenROAD's internal database (OpenDB / ODB) provides this environment, backed by the industry-standard LEF/DEF interchange formats.

### OpenROAD
The open-source physical design tool suite used as the floorplanning engine; selected for consistency with the open-source, reproducibility-first methodology established in Phase 14.5 (Yosys/OpenSTA), and for its native ODB database model.

### OpenLane2
The flow-orchestration layer wrapping OpenROAD (and other tools) into a scripted, configuration-driven pipeline; used in this phase specifically for its floorplan-stage orchestration (`Floorplan` stage family), while later stages (placement, CTS, routing) remain out of scope per this document's boundary.

### Floorplanning Database (ODB)
The in-memory/on-disk physical database populated at Stage A, holding: die/core geometry, the complete cell instance list (unplaced at this stage, aside from macros), macro placement, IO pin locations, and power/ground net geometry — the single authoritative physical representation carried forward into Phase 14.7.

### DEF
Design Exchange Format — the industry-standard text format used to serialize the floorplan's physical geometry (die area, macro locations, IO pins, PDN geometry) for interchange between tools and for archival as a Part 11 deliverable.

### LEF
Library Exchange Format — the format of the technology/standard-cell/macro LEF inputs (Part 3), defining abstract cell/macro footprints and technology design rules consumed to populate the ODB.

### Coordinate System
All floorplanning geometry is expressed in a single Cartesian coordinate system with the origin fixed at the die's lower-left corner (Die Origin, below), X increasing rightward and Y increasing upward, consistent with LEF/DEF convention.

### Units
Physical dimensions are expressed in database units (DBU), an integer micron-subdivision fixed by the technology LEF's `UNITS DISTANCE` statement (commonly 1000 or 2000 DBU per micron); all floorplanning computation is performed in DBU internally to avoid floating-point rounding drift, with micron values used only for human-readable reporting.

### Die Origin
Fixed at DEF coordinate (0,0) by convention for every design in this corpus, ensuring that cross-design geometric comparisons (Part 10 metrics) are computed from a consistent reference point.

### Database Units
As above; recorded explicitly in every design's metadata record so that downstream tooling never assumes a fixed DBU-per-micron ratio across libraries (Sky130, GF180, and ASAP7 may declare different UNITS values).

### Layer Definitions
Routing layer names, directions (horizontal/vertical preferred routing direction), and pitch, as declared in the technology LEF; consumed at this phase only to inform power-strap layer selection (Part 9) and macro-halo sizing (Part 7), since detailed routing itself is out of scope.

### Manufacturing Grid
The minimum-resolution grid (from the technology LEF's `MANUFACTURINGGRID` statement) to which every placed object's coordinates must snap; floorplanning enforces grid alignment for die/core boundaries, macro origins, and IO pin locations as a hard legality rule (Part 12).

### Technology Constraints
Minimum spacing, minimum width, and site geometry (standard-cell row height/width) declared in the technology and standard-cell LEF, consumed to compute legal core-area boundaries (Part 6) and row-based placement legality.

### Power Domains (Introduction Only)
This phase introduces the concept of a single default power domain per design (multi-voltage/multi-domain floorplanning is explicitly deferred to a later phase); the power-planning stage (Stage G) and PDN discussion (Part 9) therefore assume one core voltage domain and one (optional) always-on domain boundary at most, with no domain-crossing level-shifter planning performed here.

### Engineering Rationale
Fixing the coordinate system, units, and origin convention identically across every design in the corpus is essential for Part 10's cross-design QoR comparisons (e.g., estimated wirelength, macro distance) to be meaningful.

### Inputs / Outputs
Input: technology/standard-cell/macro LEF. Output: an initialized, empty (pre-floorplan) ODB instance ready for Stage B.

### Dependencies
OpenROAD's ODB library, OpenLane2's LEF-reading utilities.

### Runtime / Memory Expectations
Database initialization is lightweight, typically under 10 seconds regardless of design size.

### Failure Conditions
Malformed LEF, missing `MANUFACTURINGGRID` or `UNITS` declarations, layer-definition inconsistency between technology and macro LEF.

### Validation
A LEF-conformance linter (extended from Phase 14.5's library linter) checks every LEF file against the format grammar before first use.

### Industrial Notes
Mirrors the "tech file / LEF sanity check" step universally required before any floorplanning session in industrial physical design tools (Cadence Innovus, Synopsys IC Compiler II).

### Reviewer Expectations
Reviewers should expect explicit DBU and origin convention disclosure wherever floorplan geometry is reported in the eventual paper.

### Future Scalability
The single-domain assumption is explicitly scoped to be revisited in a later multi-voltage-domain floorplanning phase, without altering this phase's locked content.

---

## PART 5 — Floorplanning Architecture

### Purpose
To define the nine-stage pipeline (A–I) constituting the floorplanning engine.

### Stage A — Physical Database Initialization
**Purpose:** Instantiate the ODB from the Phase 14.5 netlist and Part 3/4 LEF inputs.
**Theory/Rationale:** Must occur before any geometric computation; establishes the coordinate system (Part 4).
**Inputs:** Netlist, technology/standard-cell/macro LEF. **Outputs:** Initialized, unplaced ODB.
**Dependencies:** OpenROAD `read_lef`/`read_verilog` (via OpenLane2 orchestration). **Runtime:** seconds. **Memory:** proportional to instance/pin count, typically <500 MB. **Failure conditions:** LEF/netlist mismatch (undeclared cell type), corrupt LEF. **Validation:** instance-count cross-check against Phase 14.5's cell-count QoR field. **Industrial notes:** equivalent to the "init_design" step in Innovus. **Reviewer expectations:** a clean initialization log with zero unresolved-cell warnings. **Future scalability:** database format is OpenROAD-native but export-compatible with any LEF/DEF-consuming tool.

### Stage B — Die Size Estimation
**Purpose:** Compute an initial die-size estimate from total cell area, macro area, and the configured utilization target.
**Theory/Rationale:** Die size is estimated as `(total_std_cell_area / target_utilization) + total_macro_area + margin_area`, a standard area-budgeting formula; treated as an *estimate* subject to refinement in Stage C once macro placement constraints are known.
**Inputs:** Cell/macro area (from LEF footprints), target utilization (Part 6). **Outputs:** Initial die-size estimate (width × height, DBU).
**Dependencies:** Stage A's populated ODB. **Runtime:** low. **Memory:** low. **Failure conditions:** target utilization >100% (infeasible by construction), macro area exceeding a configured maximum die-area bound. **Validation:** estimate cross-checked against a conservative sanity bound derived from Phase 14.5's area QoR. **Industrial notes:** matches the "die size estimation spreadsheet" step commonly performed manually in early industrial floorplanning; here fully automated and deterministic. **Reviewer expectations:** the estimation formula disclosed explicitly, not left as an opaque tool computation. **Future scalability:** formula is parameterized (margin factor, utilization target) for easy tuning per design class.

### Stage C — Core Area Calculation
**Purpose:** Derive the final core area (the placeable region within the die, excluding die-to-core margins) from the Stage B die estimate and the configured core-offset policy (Part 6).
**Theory/Rationale:** Core area must leave adequate margin for the I/O ring (Part 8) and power ring (Part 9); margin values are computed from the pad/pin pitch declared in the macro/pad LEF, not fixed constants.
**Inputs:** Die-size estimate, pad-ring pitch data. **Outputs:** Final core-area boundary (DBU coordinates), snapped to the manufacturing grid.
**Dependencies:** Stage B output, Part 4's grid-snapping rule. **Runtime:** low. **Memory:** low. **Failure conditions:** core area computed as non-positive (die too small for required margins). **Validation:** core-to-die margin ratio checked against a documented acceptable range. **Industrial notes:** equivalent to `initialize_floorplan -core_space` conventions in industrial tools. **Reviewer expectations:** explicit die/core margin values reported for every design. **Future scalability:** margin policy is a versioned configuration parameter, adjustable per package-interface requirement (relevant to future ATMP integration, Part 8).

### Stage D — Aspect Ratio Optimization
**Purpose:** Adjust die/core width-to-height ratio to satisfy the configured aspect-ratio bound (Part 6) while preserving the Stage C core area.
**Theory/Rationale:** Aspect ratio affects macro-placement feasibility, IO-side pin density, and eventual package-substrate compatibility; this stage solves for a width/height pair satisfying `area = width × height` subject to `aspect_min ≤ width/height ≤ aspect_max`, preferring the aspect ratio closest to 1.0 (square) as the default tie-break, since near-square floorplans generally minimize average wirelength for a fixed area.
**Inputs:** Core area (Stage C), aspect-ratio bound (configuration). **Outputs:** Finalized width/height pair.
**Dependencies:** Stage C. **Runtime:** low (closed-form solve). **Memory:** low. **Failure conditions:** no width/height pair within the aspect-ratio bound satisfies the required area (Part 12). **Validation:** resulting aspect ratio re-checked against the bound post-solve. **Industrial notes:** mirrors the interactive "try different aspect ratios" step in manual floorplanning, here fully deterministic. **Reviewer expectations:** the chosen aspect ratio and its tie-break rationale disclosed per design. **Future scalability:** tie-break rule (prefer-square) is swappable for a package-driven aspect-ratio target in future ATMP-aware floorplanning.

### Stage E — Macro Placement
**Purpose:** Place all hard macros within the finalized die/core boundary according to the Part 7 macro placement strategy.
**Theory/Rationale:** Macro placement is treated as a constrained legalization problem: candidate positions are generated by a clustering/channel heuristic (Part 7), then legalized against overlap, halo, and boundary constraints via OpenROAD's macro placer (a simulated-annealing-based engine), run in fixed-seed deterministic mode (Objective O1).
**Inputs:** Macro LEF footprints, macro count/type (Part 3 metadata), Part 7 rule set. **Outputs:** Legalized macro placement (position + orientation per macro instance).
**Dependencies:** Stage D's finalized die/core geometry, OpenROAD's macro placer (`macro_place.py`, Part 13). **Runtime:** the largest time consumer in this phase for macro-heavy designs; low for standard-cell-only designs (no-op). **Memory:** scales with macro count × candidate-position search space. **Failure conditions:** unresolvable macro overlap, macro footprint exceeding available core area (Part 12). **Validation:** post-placement overlap and halo-clearance check (Part 10's macro-overlap metric). **Industrial notes:** equivalent to macro placement stages in Innovus/IC Compiler II, typically the most manually-intensive step in industrial floorplanning, here scripted deterministically. **Reviewer expectations:** a documented, reproducible macro-placement seed and rule set, not a "manually adjusted" floorplan. **Future scalability:** the clustering heuristic is swappable for a learned (ML-assisted) macro placer in a future phase, since Stage E's I/O contract (macro list in, legal placement out) is stable.

### Stage F — IO Planning
**Purpose:** Assign all primary I/O pins to physical locations along the die/core boundary per the Part 8 rule set.
**Theory/Rationale:** IO placement is modeled as a boundary-assignment problem: pins are grouped by function (clock, reset, power/ground, signal, differential pair) and assigned to sides/positions minimizing average pin-to-macro or pin-to-core-boundary distance, subject to a fixed pin-pitch derived from the pad LEF.
**Inputs:** Primary port list (from netlist), pad/pin LEF, Part 8 rule set. **Outputs:** Placed IO pin geometry.
**Dependencies:** Stage E's macro placement (for proximity-aware signal-pin assignment), pad LEF. **Runtime:** low to moderate. **Memory:** low. **Failure conditions:** insufficient boundary length for the declared pin count at the configured pitch (Part 12). **Validation:** pin-pitch and side-capacity check. **Industrial notes:** equivalent to `place_pins` in OpenROAD/Innovus terminology. **Reviewer expectations:** explicit side-assignment policy disclosed (Part 8). **Future scalability:** IO planning rules are extensible to flip-chip/bump-based interfaces relevant to future ATMP-aware packaging phases (Part 8's "Future ATMP compatibility" discussion).

### Stage G — Power Planning
**Purpose:** Generate the power delivery network (PDN) skeleton: power/ground rings and straps, per the Part 9 rule set.
**Theory/Rationale:** PDN geometry is generated as a regular grid of power/ground straps at a pitch and width derived from an IR-drop budget estimate (a first-order current-density calculation using total estimated dynamic power from Phase 14.5's power QoR field divided by supply voltage), overlaid with a peripheral power/ground ring connecting to the (future) package interface.
**Inputs:** Core geometry (Stage D), estimated power draw (Phase 14.5 QoR), Part 9 rule set. **Outputs:** PDN ring/strap geometry, added to the ODB.
**Dependencies:** Stage D, F (ring must clear IO pin locations). **Runtime:** low to moderate. **Memory:** low. **Failure conditions:** insufficient routing-layer resource for the required strap density at the estimated current budget (Part 12). **Validation:** coarse IR-drop estimate checked against a documented acceptable threshold. **Industrial notes:** equivalent to `pdngen`-style PDN generation in OpenROAD/Innovus. **Reviewer expectations:** the IR-drop budgeting formula disclosed explicitly. **Future scalability:** single-domain PDN generation here is extensible to multi-domain PDN in a future phase (Part 4's power-domain introduction).

### Stage H — Keep-out Region Generation
**Purpose:** Mark all regions where standard-cell placement (Phase 14.7) is prohibited: macro halos, IO-ring clearance, and PDN-strap clearance.
**Theory/Rationale:** Keep-out regions are the geometric union of the Part 7 macro-halo policy, the Part 8 IO-ring clearance, and any PDN-strap-adjacent clearance required by the technology LEF's routing-layer spacing rules; generated as explicit placement-blockage geometry in the ODB so that Phase 14.7's placer has an unambiguous, pre-computed legality map rather than needing to re-derive it.
**Inputs:** Stage E/F/G outputs, technology LEF spacing rules. **Outputs:** Placement-blockage geometry.
**Dependencies:** Stages E, F, G. **Runtime:** low. **Memory:** low. **Failure conditions:** keep-out regions covering the entire core area (over-constrained floorplan, Part 12). **Validation:** keep-out area ratio checked against a documented maximum acceptable fraction of core area. **Industrial notes:** equivalent to `create_blockage`/halo-generation steps in Innovus. **Reviewer expectations:** keep-out area disclosed as a distinct Part 10 metric (via whitespace/utilization interaction). **Future scalability:** keep-out generation logic is directly reusable by Phase 14.7's placement legality checker.

### Stage I — Floorplan Validation
**Purpose:** Perform final, independent legality and completeness verification of the entire floorplan before corpus admission.
**Theory/Rationale:** Independent from Stages A–H; acts as an acceptance gate, mirroring Phase 14.5 Stage G's validation-as-acceptance-gate philosophy.
**Inputs:** Fully populated ODB (all prior stages' outputs). **Outputs:** Pass/fail verdict plus the Part 10 QoR record.
**Dependencies:** `validate_floorplan.py` (Part 13). **Runtime:** low to moderate. **Memory:** low. **Failure conditions:** any geometric illegality (overlap, off-grid coordinates, boundary violation) or QoR-schema incompleteness (Part 12). **Validation:** this stage *is* the pipeline's validation step. **Industrial notes:** mirrors floorplan DRC-lite sign-off checks performed before a floorplan is released to placement in industrial flows. **Reviewer expectations:** a documented, automated validation methodology, not a bare assertion of floorplan correctness. **Future scalability:** validation rule set is directly extensible with additional geometric checks as later phases identify new failure modes.

---

## PART 6 — Die and Core Planning

### Purpose
To define the detailed rules governing die and core geometry beyond the stage-level summary in Part 5.

### Die Size
The outer physical boundary of the design, computed per Stage B/D as the smallest area (subject to the aspect-ratio bound) that accommodates the core area plus die-to-core margins; die size is always reported in both DBU and microns in metadata for human readability.

### Core Size
The inner placeable boundary within the die, offset from the die boundary by the core-offset margins (below); this is the region within which macros (Stage E), and later (Phase 14.7) standard cells, may legally be placed.

### Utilization
Defined as `total_cell_area / core_area`, expressed as a percentage; the primary lever controlling die size for a fixed netlist. This phase adopts a conservative default utilization target (typically 45–60% for standard-cell-only regions, deliberately left below the 70–85% range often used in production tapeouts) to preserve routing headroom given that no routing-congestion feedback loop exists yet at this phase — a documented, deliberate conservatism rather than an arbitrary choice.

### Margins
Die-to-core margins (top/bottom/left/right, individually configurable but defaulted to equal) sized to accommodate the IO-ring and power-ring geometry (Parts 8–9); computed as a function of pad pitch and ring width rather than a fixed constant, ensuring margin scales correctly across libraries with different pad/macro footprints.

### Core Offsets
The explicit (x, y) offset of the core boundary's lower-left corner from the die origin, recorded per design in metadata since Part 10's macro-distance and wirelength-estimate metrics are computed relative to the core boundary, not the die boundary.

### Aspect Ratio
Bounded, per Part 2's Objective O2-consistent policy, to a default range of 0.5–2.0 (i.e., no more than 2:1 elongation in either dimension) unless a design's benchmark metadata (Part 3) documents a specific package-driven aspect-ratio requirement.

### Whitespace Allocation
The core area not occupied by cell/macro footprints, deliberately budgeted (via the utilization target) to absorb placement-stage cell spreading, local congestion relief, and any future ECO (engineering change order) headroom; tracked explicitly as a Part 10 QoR metric since insufficient whitespace is a leading predictor of downstream routing congestion.

### Future Expansion Space
A configurable, optional additional whitespace reserve (distinct from ordinary utilization-driven whitespace) settable per design for benchmark families known to require post-floorplan ECO insertion; defaulted to zero for this corpus's benchmark set unless documented otherwise in metadata.

### Core Density
A secondary, macro-region-specific density measure — cell area occupied within the *non-macro* portion of the core — reported separately from overall utilization since macro-dense designs would otherwise show misleadingly low utilization figures when macro area dominates the core.

### Engineering Tradeoffs
Smaller die size reduces cost-relevant area and wirelength but increases congestion and IR-drop risk; larger die size relaxes both but increases cost and wire delay. This phase's conservative-utilization default explicitly favors congestion/IR-drop safety over area minimality, a tradeoff documented here so that the eventual paper can correctly characterize the corpus's floorplan QoR distribution as representative of a conservative, dataset-generation-oriented flow rather than a cost-optimized production tapeout.

---

## PART 7 — Macro Placement Strategy

### Macro Classification
Macros are classified at Stage E into three functional classes derived from netlist/metadata inspection: memory macros (SRAM/register-file compilers), analog/mixed-signal macros (PLLs, ADC/DAC blocks, if present in a given benchmark), and hard-IP macros (pre-hardened digital blocks); classification determines the default clustering and halo policy applied below.

### Macro Orientation
Each macro is assigned one of the eight legal LEF orientations (N, S, E, W, FN, FS, FE, FW); the placer defaults to the orientation minimizing pin-to-nearest-boundary distance for that macro's dominant signal-pin cluster, always constrained to orientations the macro LEF declares as legal (some macros restrict legal orientations to preserve internal routing assumptions).

### Legal Rotation
Only orientations explicitly permitted by the macro LEF's `SYMMETRY` statement are considered; a macro lacking any declared symmetry is treated as orientation-fixed (N only), a conservative default preventing illegal-rotation failures (Part 12).

### Macro Alignment
Macros are aligned to the manufacturing grid (Part 4) and, where multiple macros of identical type are present (e.g., multiple SRAM instances), aligned to a shared coordinate axis (common top or common left edge) to simplify later power-strap alignment (Stage G) and to reduce routing-channel irregularity.

### Boundary Constraints
Macros are kept at least one macro-halo width (below) away from the core boundary, and additionally constrained to leave a documented minimum-width straight channel along at least one core edge for macro-to-IO or macro-to-macro routing feasibility in the following phase.

### Macro Channels
Corridors of unobstructed core area deliberately preserved between macro clusters, sized to a configurable multiple of the technology's minimum routing pitch (Part 4), providing routing headroom for signals crossing between macro-adjacent logic regions — directly informing Part 10's channel-width metric.

### Macro Halo
A mandatory placement-keep-out margin around every macro (Stage H), sized from the macro LEF's own declared halo/blockage geometry where present, or else a configurable default (a documented multiple of standard-cell row height) where the LEF declares none; the halo prevents standard-cell placement (Phase 14.7) directly adjacent to macro boundaries, avoiding pin-access and routing-blockage conflicts.

### Keep-out Margins
The union of macro halo, IO-ring clearance, and PDN-strap clearance, generated at Stage H and stored as explicit ODB blockage geometry (Part 5).

### Macro Clustering
Macros of the same functional class (Macro Classification, above) are, by default, clustered together rather than scattered, since co-located same-type macros typically share power-strap alignment and reduce total power-ring perimeter; clustering is relaxed only where the netlist's connectivity structure (fan-out proximity to widely separated logic regions) makes clustering counterproductive, a decision made via a lightweight connectivity-proximity heuristic rather than manual judgment.

### Macro Pin Accessibility
Every macro's pin-bearing edge must retain a documented minimum clearance to any neighboring macro or core boundary, verified at Stage I, since insufficient pin-access clearance is a common, otherwise-late-discovered routing-blockage failure mode in industrial physical design.

### Macro Ordering
Macros are placed in a deterministic order (largest-area-first) during Stage E's legalization search, ensuring Objective O1's determinism guarantee holds regardless of the order macros appear in the source netlist.

### Hierarchy Preservation
Where the Phase 14.5 netlist retains RTL module hierarchy (per that phase's hierarchy-preservation QoR field), macro placement preserves hierarchical grouping where feasible — i.e., macros instantiated within the same RTL sub-hierarchy are preferentially clustered — supporting later GNN-based structural feature extraction that relies on hierarchy-consistent physical grouping.

### Engineering Rationale
Every rule above is chosen to make macro placement a fully rule-driven, auditable process rather than the interactive, engineer-judgment-driven process typical of industrial floorplanning, which is essential for Objective O1 (determinism) and O4 (macro placement consistency) to hold at corpus scale.

---

## PART 8 — IO Planning Strategy

### IO Pads
This corpus's floorplanning stage treats IO as abstract pin geometry rather than fully instantiated physical pad cells (pad-cell instantiation is a package-interface-specific step deferred to a later, explicitly ATMP-focused phase); pin locations are nonetheless planned at a pad-realistic pitch derived from the technology's documented pad-pitch convention, so that later pad-ring insertion is geometrically consistent with this phase's IO plan.

### Pin Assignment
Primary ports are assigned to core-boundary sides using a deterministic function-based rule: clock and reset pins to the side nearest the design's dominant sequential-logic centroid (estimated from Phase 14.5's netlist structure), power/ground pins evenly distributed across all four sides for PDN symmetry (Part 9), and signal pins assigned to the side nearest their principal fan-out/fan-in macro or logic cluster (Stage F/Stage E interaction).

### Pin Ordering
Within a given side, pins are ordered to minimize crossing among same-bus signals (e.g., a multi-bit data bus is kept contiguous and ordered by bit index), reducing unnecessary routing-layer jogs in the following phase.

### Clock Pins
Assigned first, before any other pin class, and placed at the side/position minimizing worst-case estimated clock-insertion distance to the sequential-logic centroid, since clock-pin placement has outsized influence on the feasibility of the (later, out-of-scope) clock-tree synthesis phase.

### Reset Pins
Placed adjacent to their associated clock pin by default, consistent with common package-interface convention and simplifying later reset-tree planning.

### Power Pins
Distributed evenly across all four sides at a pitch derived from the Stage G current-budget estimate, ensuring no single side must carry a disproportionate share of supply current.

### Ground Pins
Interleaved with power pins at a fixed power-to-ground pin ratio (default 1:1, adjustable per current-budget analysis), maintaining symmetric return-current paths.

### Signal Pins
Assigned per the Pin Assignment rule above; differential and single-ended signal pins are handled by separate sub-rules (below).

### Differential Pairs
Where metadata identifies a differential signal pair, both pins of the pair are placed immediately adjacent on the same side with matched distance-to-core-boundary, preserving the matched-length intent that differential signaling requires, even though detailed length-matching routing itself is out of scope for this phase.

### Pad Ring Concept
The IO plan is generated consistent with an eventual peripheral pad-ring assumption (as opposed to an area-array/flip-chip bump assumption), matching this corpus's benchmark set's wire-bond-oriented packaging assumptions (Part 8, Future ATMP compatibility, below); this assumption is recorded explicitly in metadata so the eventual paper does not overgeneralize its IO-planning findings to bump-based interfaces without qualification.

### ESD Considerations
While full ESD (electrostatic discharge) protection-cell insertion is out of scope for this phase, IO-pin placement reserves a documented minimum boundary-adjacent keep-out sized to accommodate a future ESD-cell insertion step, preventing a downstream phase from encountering an infeasibly tight IO pitch.

### Package Interface
IO planning records, per design, the assumed package-interface class (wire-bond peripheral, per Pad Ring Concept above) as a metadata field, explicitly flagged as a placeholder assumption pending the paper's dedicated packaging-phase treatment (outside this document's scope).

### Future ATMP Compatibility
Because this paper's central thesis concerns early prediction of packaging and reliability challenges, the IO plan's pin-class metadata (clock/reset/power/ground/signal/differential) and package-interface assumption are retained as first-class, explicitly-labeled fields specifically so that a future ATMP-focused phase can consume them directly as packaging-co-design features, without needing to re-derive pin classification from raw netlist inspection.

---

## PART 9 — Power Planning

### Power Rings
A peripheral power and ground ring is generated around the core boundary (Stage G), sized in width and layer per the current-budget estimate (below); the ring provides the primary current-collection path from the (future) package interface into the core's power straps.

### Power Straps
A regular grid of vertical and horizontal power/ground straps overlaid across the core area at a pitch derived from the IR-drop budgeting formula (Part 5, Stage G); strap layers are selected from the upper routing layers (per the technology LEF's layer stack) to minimize interference with the standard-cell and macro routing layers reserved for later phases.

### Power Grid Philosophy
The default philosophy is a conservative, uniform-density grid (rather than a congestion-aware, non-uniform grid), consistent with this phase's overall conservative-utilization stance (Part 6): uniform straps are simpler to reason about, fully deterministic, and avoid coupling power-grid density to a placement-stage congestion estimate that does not yet exist at floorplan time.

### IR Drop Considerations
A first-order IR-drop estimate is computed as `estimated_current × (strap_resistance_per_unit_length × average_current_path_length)`, using the estimated dynamic power (Phase 14.5 QoR) divided by supply voltage as the current term; this estimate is a coarse feasibility check (Part 12's power-planning-failure condition), not a sign-off-grade IR-drop analysis, which is explicitly deferred to a later, dedicated power-integrity phase.

### Voltage Domains
As established in Part 4, this phase assumes a single core voltage domain; the PDN is generated with no domain-crossing structures, with multi-domain PDN generation explicitly reserved for future work.

### Power Integrity
Beyond the coarse IR-drop estimate above, no dynamic power-integrity simulation (e.g., simultaneous-switching-noise analysis) is performed at this phase; the PDN is sized with a documented conservative margin (over-provisioned strap width relative to the coarse estimate) specifically to compensate for the absence of detailed power-integrity analysis at this stage.

### Ground Integrity
Symmetric ground-strap density to power-strap density is maintained by default (matching the 1:1 power-to-ground pin ratio from Part 8), avoiding asymmetric return-path resistance.

### Current Density
Strap width is additionally checked against the technology LEF's declared per-layer maximum current-density (electromigration-relevant) limit, ensuring the coarse current-budget estimate does not produce an EM-illegal strap width.

### EM Awareness
While full electromigration (EM) sign-off analysis is out of scope, this phase's current-density check (above) constitutes a first-order EM-awareness gate, flagged explicitly in metadata as a coarse check rather than a sign-off guarantee.

### Decoupling Concept
Decoupling capacitor (decap) insertion is not performed at this phase (decap cells are standard-cell-row-based and are more appropriately inserted during Phase 14.7 placement); however, this phase's whitespace budgeting (Part 6) deliberately reserves headroom sufficient for typical decap insertion ratios, a cross-phase consistency decision documented here for the benefit of the later phase.

### PDN Planning
The complete Stage G output — rings, straps, and their layer/width/pitch parameters — is recorded as explicit, versioned configuration (Part 11) alongside the geometry itself, so that the PDN's design rationale (not just its resulting geometry) is auditable.

### Engineering Rationale
Every power-planning decision in this phase favors conservative, auditable feasibility estimation over sign-off-grade precision, consistent with this document's floorplanning-only scope boundary; detailed power-integrity and EM sign-off are explicitly and repeatedly flagged as deferred to later phases to avoid any reviewer misreading this phase as providing production-grade power sign-off.

---

## PART 10 — Floorplan Quality Metrics

Each metric below includes its definition, importance, engineering rationale, measurement method, and future ML relevance, consistent with the Phase 14.5 QoR schema philosophy (Objective O4/O6).

### Die Area
**Definition:** Total die width × height (µm²). **Importance:** primary cost- and packaging-relevant size metric. **Rationale:** directly derived from Stage B/D. **Measurement:** read from final DEF geometry. **ML relevance:** a baseline scale feature against which all other metrics are normalized.

### Core Area
**Definition:** Placeable area within die margins (µm²). **Importance:** the true resource-constrained region for all placed objects. **Rationale:** distinguishes usable area from margin overhead. **Measurement:** Stage C output. **ML relevance:** denominator for utilization and density features.

### Utilization
**Definition:** Total cell area / core area (%). **Importance:** primary congestion-risk proxy. **Rationale:** Part 6's core lever. **Measurement:** computed post Stage E. **ML relevance:** a leading-indicator feature for manufacturing yield/congestion risk prediction, the paper's central concern.

### Aspect Ratio
**Definition:** Die width / die height. **Importance:** affects wirelength, macro feasibility, and package compatibility. **Rationale:** Stage D's solved output. **Measurement:** direct geometric ratio. **ML relevance:** a structural feature correlating with routing difficulty in prior DTCO literature.

### Whitespace
**Definition:** Core area minus total (cell + macro) area (µm² and %). **Importance:** congestion/ECO headroom indicator. **Rationale:** Part 6. **Measurement:** arithmetic from utilization and macro-area data. **ML relevance:** inversely correlated with congestion risk; a key predictive feature.

### Macro Density
**Definition:** Total macro area / core area (%). **Importance:** distinguishes macro-dominated from standard-cell-dominated designs. **Rationale:** Part 6's core-density discussion. **Measurement:** sum of placed macro footprints / core area. **ML relevance:** macro-heavy designs are known to exhibit distinct congestion/IR-drop signatures, an important stratification feature.

### Macro Overlap
**Definition:** Total overlapping area between any two macro footprints (µm²); must be zero in a legal floorplan. **Importance:** a hard legality indicator. **Rationale:** Stage E/I. **Measurement:** geometric intersection test over all macro pairs. **ML relevance:** used only as a corpus-admission gate (must be zero), not as a graded ML feature.

### Channel Width
**Definition:** Minimum observed corridor width between macro clusters (µm). **Importance:** routing-feasibility proxy. **Rationale:** Part 7's Macro Channels discussion. **Measurement:** geometric minimum-gap computation between macro-halo boundaries. **ML relevance:** correlates with routing-congestion risk in macro-adjacent regions.

### IO Density
**Definition:** Total IO pin count / core-boundary perimeter length (pins/µm). **Importance:** package-interface feasibility proxy. **Rationale:** Part 8. **Measurement:** pin count from netlist / perimeter from Stage D geometry. **ML relevance:** a packaging-co-design feature directly relevant to the paper's ATMP-prediction thesis.

### Power Grid Coverage
**Definition:** Fraction of core area within a documented maximum distance of a power/ground strap (%). **Importance:** IR-drop-risk proxy. **Rationale:** Part 9. **Measurement:** geometric distance-transform over the strap grid. **ML relevance:** a leading indicator for IR-drop-related reliability risk, directly serving the paper's reliability-prediction thesis.

### Estimated Congestion
**Definition:** A coarse, floorplan-stage congestion proxy computed as local (grid-cell) pin-density weighted by estimated net count crossing each grid cell (derived from netlist connectivity, not actual routing). **Importance:** earliest-available congestion signal in the entire flow. **Rationale:** provides a Phase-14.6-native congestion feature without waiting for Phase 14.7/later routing data. **Measurement:** a grid-based analytical estimate, explicitly labeled as an estimate, not a routed value. **ML relevance:** intended as the paper's primary early-prediction feature for congestion-driven yield risk.

### Estimated Wirelength
**Definition:** Sum of half-perimeter wirelength (HPWL) over all nets, computed from macro/IO placement and each net's (currently unplaced) standard-cell endpoints approximated at their parent macro or core centroid. **Importance:** classical PPA proxy. **Rationale:** the standard, tool-independent wirelength estimator used before detailed placement exists. **Measurement:** HPWL formula over net bounding boxes. **ML relevance:** a baseline feature for later comparison against Phase 14.7's post-placement wirelength, quantifying floorplan-stage prediction accuracy.

### Pin Accessibility
**Definition:** Minimum clearance observed at every macro pin location to the nearest obstruction (µm). **Importance:** routing-blockage risk proxy. **Rationale:** Part 7's Macro Pin Accessibility rule. **Measurement:** geometric clearance check per pin. **ML relevance:** correlates with local routing failure risk in later phases.

### Macro Distance
**Definition:** Pairwise Euclidean/Manhattan distance between all macro centroids (µm), and specifically the minimum inter-macro distance and the maximum macro-to-core-centroid distance. **Importance:** proximity-driven timing/power feasibility proxy. **Rationale:** Part 7's clustering rationale. **Measurement:** direct geometric computation post Stage E. **ML relevance:** a structural feature for GNN-based graph representations linking physical distance to timing/reliability outcomes.

### Routing Resource Estimation
**Definition:** A coarse per-grid-cell available-routing-track estimate, computed from the technology LEF's layer pitch and the keep-out geometry from Stage H (i.e., total tracks minus tracks consumed by blockages). **Importance:** the floorplan-stage proxy most directly linked to eventual routing/manufacturing feasibility. **Rationale:** synthesizes Parts 4, 7, and 9's geometric outputs into a single feasibility indicator. **Measurement:** analytical track-counting per grid cell. **ML relevance:** intended as a key input feature for the paper's manufacturing-yield-risk prediction model, bridging floorplan-stage geometry directly to the paper's central research question.

---

## PART 11 — Outputs

### Purpose
To enumerate every artifact the floorplanning stage is responsible for producing and persisting, consistent with the Phase 14.5 outputs philosophy (Part 11 of that phase).

### Floorplan DEF
The finalized physical geometry (die, core, macros, IO pins, PDN) serialized in DEF format, one file per (design, library, corner) triple, named per the convention `{design_name}_{library}_{corner}_floorplan.def`.

### ODB
The full OpenROAD database snapshot at the conclusion of Stage I, retained as the authoritative binary handoff artifact for Phase 14.7 (placement), avoiding any DEF-round-trip information loss.

### Reports
Human-readable summaries of die/core geometry, macro placement, IO assignment, and PDN parameters, generated per (design, library, corner) triple.

### Metrics
The full Part 10 QoR schema record, in JSON, one per (design, library, corner) triple.

### Logs
Full tool logs (OpenROAD, OpenLane2 orchestration) retained for every run, supporting forensic debugging.

### Metadata
The per-design metadata record (carried forward from Phase 14.5) updated with floorplan provenance: tool versions, flow-script hash, timestamp, macro inventory, package-interface assumption (Part 8), and Objective O1–O6 compliance flags.

### Updated Manifest
The benchmark manifest, updated to mark each design's floorplan status (pending/complete/failed) per (library, corner) triple, extending the resume-capability model from Phase 14.5.

### Configuration Snapshots
The exact floorplan configuration (utilization target, aspect-ratio bound, IO/power policy parameters) used for the run, archived verbatim to satisfy Objective O3 (reproducibility).

### Visualization Images
A rendered raster/vector image of the final floorplan (die outline, macros, IO pins, power rings) generated for every design, supporting rapid human QA review and, potentially, future image-based ML feature extraction.

### Engineering Rationale
As in Phase 14.5, treating configuration snapshots and manifest updates as first-class outputs — not an afterthought — is what keeps the multi-phase pipeline resumable and auditable at corpus scale.

### Dependencies
File-system layout defined in Part 14.

### Runtime / Memory Expectations
Output serialization is lightweight, typically under 30 seconds per design including visualization rendering.

### Failure Conditions
Disk write failures, schema-validation failures on the QoR record (Part 10).

### Validation
An output-completeness checker confirms all nine output classes exist for every successfully completed run before the manifest is marked complete.

### Industrial Notes
Mirrors the "floorplan release package" deliverables checklist used to hand off a floorplan from the floorplanning team to the placement team in industrial flows.

### Reviewer Expectations
Reviewers/Artifact Evaluators should be able to locate every one of these nine output classes for any given design in the released corpus.

### Future Scalability
New output classes (e.g., a thermal-map overlay) can be added as a tenth class without disrupting the existing nine.

---

## PART 12 — Failure Handling

### Purpose
To define detection, classification, logging, and recovery for every category of floorplanning failure, consistent with the fail-forward-per-design philosophy established in Phase 14.5, Part 12.

### Macro Overlap
Detected at Stage E/I via pairwise geometric intersection; logged as `failed:macro_overlap` with the specific offending macro pair identified; the design is excluded from that (library, corner) run without blocking other designs.

### Insufficient Whitespace
Detected when Stage B/C's computed utilization exceeds a documented maximum feasible bound (typically >85%, beyond which legalization is expected to fail); logged as `failed:insufficient_whitespace` before macro placement is even attempted, avoiding wasted compute.

### Illegal Orientation
Detected at Stage E when the placer's candidate orientation for a macro is not among the LEF-declared legal symmetries (Part 7); logged as `failed:illegal_orientation`.

### Invalid LEF
Detected at Stage A/Part 4's LEF-conformance linter; logged as `failed:invalid_lef` with the specific malformed statement identified.

### Broken DEF
Detected at Stage I's final consistency re-parse of the emitted DEF (a self-check analogous to Phase 14.5's netlist re-parse self-check); logged as `failed:broken_def`.

### Power Planning Failure
Detected at Stage G when the coarse IR-drop or current-density check (Part 9) fails against the documented threshold; logged as `failed:power_planning` with the specific violating strap/region identified.

### IO Conflicts
Detected at Stage F when the required pin count exceeds available boundary capacity at the configured pitch (Part 8); logged as `failed:io_conflict`.

### Density Overflow
Detected when post-macro-placement local density (a grid-cell-level check, distinct from the global utilization check) exceeds a documented maximum in any single region; logged as `failed:density_overflow`.

### Aspect Ratio Failure
Detected at Stage D when no legal width/height pair satisfies both the area and aspect-ratio-bound requirements (Part 5, Stage D); logged as `failed:aspect_ratio`.

### Database Corruption
Detected via ODB internal consistency checks (e.g., dangling pin references, orphaned geometry) at Stage I; logged as `failed:db_corruption` and treated as a high-priority infrastructure incident (potentially indicating an OpenROAD version regression) rather than an ordinary per-design failure, escalated for manual review per Phase 14.5's infrastructure-incident precedent (Part 12 of that phase).

### Recovery Strategy
Consistent with Phase 14.5: fail-forward-per-design. A failure on one (design, library, corner) triple never blocks any other triple; the batch orchestrator continues processing the remaining queue.

### Logging
Every failure is logged to the same structured failure ledger (JSON lines) format established in Phase 14.5, extended with floorplan-specific failure classes above.

### Validation
Weekly aggregate failure-rate review, consistent with Phase 14.5's monitoring cadence, with anomalous spikes triggering a flow-script or LEF-set audit.

### Engineering Rationale
Extending, rather than replacing, the Phase 14.5 failure-ledger schema and fail-forward philosophy ensures a single, uniform failure-analysis methodology spans the entire multi-phase pipeline.

### Industrial Notes
Mirrors floorplan QA failure-triage practices in industrial physical design regression infrastructure, directly analogous to the synthesis-regression triage precedent cited in Phase 14.5.

### Reviewer Expectations
Reviewers should expect an explicit floorplan failure-rate disclosure per library (e.g., "X% of designs failed macro legalization against library Y"), consistent with the transparency standard set in Phase 14.5.

### Future Scalability
The failure taxonomy is an open enum, extensible as the flow is applied to new macro types or package-interface assumptions.

---

## PART 13 — Automation

### Purpose
To specify the concrete automation scripts implementing Parts 1–12 as a repeatable, unattended batch pipeline, extending the Phase 14.5 automation model.

### floorplan.py
The top-level per-design driver for this phase: consumes the Part 3 input classes for a single (design, library, corner) triple, invokes Stages A–I via OpenROAD/OpenLane2, and produces the Stage I DEF/ODB plus intermediate logs. Fixed OpenROAD/OpenLane2 version pinned in the repository's environment lock file (Phase 13 — Repository Engineering).

### generate_floorplan.py
Implements Stages A–D (database initialization through aspect-ratio optimization), producing the finalized die/core geometry as an intermediate artifact consumable independently (e.g., for die-size-only studies without full macro/IO/power planning).

### powerplan.py
Implements Stage G in isolation, consuming a finalized die/core geometry and emitting PDN geometry; separated from `generate_floorplan.py` so that power-planning-policy experiments (e.g., alternate strap-pitch studies) can be re-run without repeating Stages A–F.

### macro_place.py
Implements Stage E in isolation, wrapping OpenROAD's macro placer with the Part 7 rule set and a fixed deterministic seed (Objective O1); exposes the seed and clustering-policy parameters as explicit, logged configuration.

### io_place.py
Implements Stage F in isolation, wrapping OpenROAD's `place_pins`-equivalent functionality with the Part 8 rule set.

### validate_floorplan.py
Implements Stage I: performs the complete legality/completeness check set (Part 12's failure conditions) and, on success, emits the Part 10 QoR record.

### Resume Capability
The manifest's per-(design, library, corner) floorplan-status field (Part 11) allows the batch orchestrator to skip already-`complete` triples, consistent with the resume model established in Phase 14.5.

### Parallel Execution
Independent (design, library, corner) triples are dispatched to a bounded worker pool, respecting Part 12's density/memory-related failure-avoidance considerations, identical in structure to Phase 14.5's worker-pool model.

### Cluster Execution
Extended to a job-scheduler-backed cluster identically to Phase 14.5, with the single-design driver (`floorplan.py`) kept identical between local and cluster execution.

### Manifest-Driven Execution
The batch orchestrator's sole source of work is the benchmark manifest's floorplan-pending entries, consistent with the single-source-of-truth principle established in Phase 14.5.

### Dry-Run Mode
A `--dry-run` flag on `floorplan.py` validates the full Part 3 input set for an entire pending batch (including LEF conformance and configuration completeness) without consuming floorplanning compute, catching manifest/LEF/configuration errors early, directly analogous to Phase 14.5's dry-run mode.

### Engineering Rationale
Fixing script boundaries (one driver, four stage-specific sub-scripts, one validator) mirrors Phase 14.5's discipline of preventing undocumented, mutually-inconsistent flow variants from accumulating across a long-running research project.

### Dependencies
OpenROAD, OpenLane2, the Phase 13 repository's environment lock file.

### Runtime / Memory Expectations
Aggregate batch runtime scales linearly with (design count × library count × corner count) divided by available parallelism, per the per-stage expectations in Part 5.

### Failure Conditions
Orchestrator-level failures are distinguished from per-design failures (Part 12) and escalated separately.

### Validation
Consistent with Phase 14.5: the dry-run mode is the primary pre-batch validation mechanism.

### Industrial Notes
Mirrors the regression-infrastructure conventions cited in Phase 14.5, Part 13.

### Reviewer Expectations
Reviewers/Artifact Evaluators should be able to re-run `floorplan.py --dry-run` against the released manifest and confirm zero input-validation errors.

### Future Scalability
The driver/sub-script/validator boundary is stable under future tool substitution (e.g., a commercial floorplanning engine), since each script's I/O contract is the specified interface, not its internal implementation.

---

## PART 14 — Repository Structure

```
floorplan/
├── flow/
│   ├── floorplan.py
│   ├── generate_floorplan.py
│   ├── powerplan.py
│   ├── macro_place.py
│   ├── io_place.py
│   └── validate_floorplan.py
├── lefs/
│   ├── sky130/
│   ├── gf180/
│   └── asap7/
├── configs/
│   └── {design_name}/{library}/{corner}.json
├── outputs/
│   └── {design_name}/{library}/{corner}/
│       ├── floorplan.def
│       ├── floorplan.odb
│       ├── qor.json
│       ├── report.txt
│       ├── visualization.png
│       └── logs/
├── failure_ledger.jsonl
└── manifest_status.json
```

### Engineering Rationale
This layout mirrors the modular structure established in Phase 14.5, Part 14, keeping flow scripts, technology inputs, per-design configuration, and outputs in clearly separated, independently-versionable trees.

### Dependencies
Consistent with repository conventions locked in Phase 13.

### Validation
A repository-structure linter confirms presence of all required directories before any batch run starts.

### Industrial Notes
Comparable to standard `flow/`, `lef/`, `config/`, `reports/` directory conventions in industrial floorplanning project workspaces.

### Reviewer Expectations
Reviewers should be able to locate any artifact referenced elsewhere in this specification using only this directory map.

### Future Scalability
Additional library or corner subtrees slot into the existing pattern without restructuring.

---

## PART 15 — Deliverables

1. The complete, version-controlled floorplanning flow (Parts 13/14).
2. The full validated floorplan corpus (DEF/ODB) across all designs × compatible libraries × corners.
3. The full floorplan QoR record corpus (Part 10 schema) — a second-stage ground-truth label set complementing Phase 14.5's synthesis QoR for later ML phases.
4. The failure ledger (Part 12), disclosed as a first-class research artifact.
5. Updated per-design metadata and benchmark manifest (Part 11), including macro inventory and package-interface assumptions.
6. Floorplan visualization images for the full corpus, supporting both human QA and potential future image-based ML feature extraction.
7. This specification document itself, serving as the methodology section basis for the eventual paper's floorplanning discussion.

### Engineering Rationale
As in Phase 14.5, treating the failure ledger and flow scripts as deliverables — not just the "successful" floorplans — is essential for IEEE Artifact Evaluation's transparency expectations.

### Dependencies
All prior parts of this phase.

### Validation
A deliverables-completeness checklist is run before the phase is declared closed.

### Industrial Notes
Matches the standard "phase exit criteria" checklist used in staged industrial engineering programs, consistent with Phase 14.5's precedent.

### Reviewer Expectations
Reviewers should be able to check off each of the seven deliverables independently against the released repository.

### Future Scalability
Additional deliverables (e.g., a cross-library floorplan-QoR-variance report) can be appended in a future phase.

---

## PART 16 — Publication Readiness

### IEEE Reproducibility
Every floorplanning decision in this document is stated as a fixed, versioned rule rather than a tool default, satisfying IEEE's reproducibility expectations; the flow-script hash, tool version pinning (Part 13), and configuration-snapshot archival (Part 11) provide the concrete reproducibility anchor.

### Artifact Evaluation
The dry-run validation mode (Part 13), the failure ledger (Part 12), and the fixed repository structure (Part 14) collectively satisfy the standard Artifact Evaluation criteria of *available*, *functional*, and *reusable*, consistent with Phase 14.5's precedent.

### Industrial Deployment
The strict input/output contracts (Part 3/Part 11), the deterministic macro/IO/power planning rules (Parts 7–9), and the fail-forward batch model (Part 12) make this flow directly adoptable as an internal floorplan-generation pipeline by an industrial EDA or foundry design-enablement team.

### Zenodo Compatibility
The Part 14 repository structure, combined with checksum-pinned LEF sets, versioned configuration snapshots, and a versioned flow-script set (Part 13), is directly packageable as a Zenodo-archived, DOI-citable artifact accompanying the paper.

### Reviewer Expectations
Reviewers should conclude this phase is self-contained, falsifiable, and directly extensible, consistent with the standard IEEE Artifact Evaluation committee criteria cited in Phase 14.5, Part 16.

### Future Scalability
This phase's technology-independent coordinate abstraction (Part 4), extensible failure taxonomy (Part 12), and modular script boundaries (Part 13) are explicitly designed so that later phases (placement, CTS, routing, congestion prediction — all explicitly out of scope here) can be appended as new phases without any retroactive modification to Phase 14.6's locked content.

---

**END OF PHASE 14.6**

*This document continues seamlessly from the locked Phase 14.5 (Logic Synthesis & Technology Mapping Specification) and is itself locked upon completion at validated floorplanning outputs (Stage I). The next phase (14.7, if defined) should address only standard-cell placement, per the explicit scope boundary established in this document's task definition.*
