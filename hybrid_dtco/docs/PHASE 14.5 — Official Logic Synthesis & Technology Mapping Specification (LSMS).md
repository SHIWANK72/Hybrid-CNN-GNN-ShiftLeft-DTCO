# PHASE 14.5 — Official Logic Synthesis & Technology Mapping Specification (LSMS)

**Paper:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target:** IEEE International Conference on Microelectronics (ICM 2026)
**Document Class:** Industrial Engineering Specification (continues directly after Phase 14.4 — RTL Standardization & Normalization Specification)

---

## PART 1 — Synthesis Philosophy

### Purpose
Phase 14.5 defines the authoritative specification governing how normalized RTL, produced under Phase 14.4, is converted into a technology-mapped gate-level netlist suitable for downstream QoR-driven machine learning ingestion (later phases) and for conventional physical design entry. This phase exists as the single point of truth for every synthesis decision made across the dataset generation pipeline, ensuring that every design instance in the corpus is synthesized under an identical, auditable, and reproducible methodology.

### Theory
Logic synthesis is the transformation of a technology-independent behavioral or structural RTL description into a technology-dependent gate-level netlist composed exclusively of cells drawn from a target standard-cell library, subject to a declared set of timing, area, and power constraints. The transformation is formally a sequence of semantics-preserving rewrites: RTL → generic Boolean network → optimized Boolean network → technology-mapped netlist. Each rewrite stage must preserve functional equivalence while progressively binding the design to physical implementation choices (cell selection, drive strength, threshold voltage class).

### Engineering Rationale
Because this pipeline feeds a machine learning system that predicts manufacturing, packaging, and reliability outcomes from synthesis-stage features, synthesis quality-of-results (QoR) variance must originate only from genuine design differences — never from methodology drift, tool nondeterminism, or undocumented flag changes. Phase 14.5 therefore treats the synthesis run as a controlled experiment: fixed tool version, fixed optimization script, fixed library set, and a manifest-recorded seed and configuration hash for every run.

### Inputs
Normalized RTL corpus (Phase 14.4 output), per-design metadata records, benchmark manifest (Phase 14.2/14.3), constraint files, technology library set (Part 6).

### Outputs
A synthesized, technology-mapped gate-level netlist per design, accompanied by structural and timing QoR reports (Part 10–11).

### Dependencies
Yosys (open-source synthesis engine, pinned version — see Part 13), OpenSTA (for post-synthesis static timing sign-off), the normalized RTL corpus, and the technology library set.

### Runtime Expectations
Single small-to-medium design (≤50k standard cells post-mapping): 2–15 minutes on a single compute node. Large designs (>200k cells): up to several hours, driving the parallel/cluster execution model in Part 13.

### Memory Expectations
Typical peak RSS 1–4 GB for designs under 100k gates; designs exceeding 500k gates may require 8–16 GB, motivating the memory-overflow handling in Part 12.

### Failure Conditions
Non-convergence of technology mapping, library incompatibility, unresolved black boxes, or parser rejection of unsupported RTL constructs (Part 4).

### Validation
Every synthesized netlist is validated for functional equivalence against the source RTL (formal equivalence checking where feasible, simulation-based checking otherwise) prior to acceptance into the corpus.

### Industrial Notes
This philosophy mirrors the "golden reference flow" discipline used in production ASIC synthesis sign-off at merchant EDA vendors (Synopsys Design Compiler, Cadence Genus), where a locked flow script and locked library set are mandated before any QoR number is considered comparable across designs.

### Reviewer Expectations
Reviewers evaluating this specification for IEEE Artifact Evaluation should expect: (a) a fully deterministic, scripted flow; (b) explicit documentation of every optimization knob; (c) traceability from raw RTL to final QoR number.

### Future Scalability
The philosophy is library-agnostic and tool-agnostic by design; Part 6's extensibility clause allows commercial PDKs (e.g., TSMC, GlobalFoundries advanced nodes) to be substituted without altering the flow architecture.

---

## PART 2 — Objectives

### Purpose
To enumerate the concrete, testable objectives that the synthesis stage must satisfy before its output is considered acceptable for inclusion in the dataset.

### Theory
An engineering specification is only falsifiable if its objectives are stated as measurable acceptance criteria rather than aspirational goals. Phase 14.5 adopts six binding objectives:

1. **O1 — Determinism:** Identical RTL + identical constraints + identical library ⇒ bit-identical netlist across repeated runs.
2. **O2 — Functional Equivalence:** The mapped netlist must be provably equivalent to the normalized RTL.
3. **O3 — Multi-Library Portability:** Every design must be synthesizable, without RTL modification, against at least two of the three supported libraries (Sky130, GF180, ASAP7).
4. **O4 — QoR Completeness:** Every run must emit the full QoR schema defined in Part 10, with no missing fields.
5. **O5 — Constraint Fidelity:** Reported timing must reflect the constraint set exactly as authored (Part 7), with no silent constraint relaxation.
6. **O6 — Failure Traceability:** Any non-converging run must produce a structured failure record (Part 12), never a silent skip.

### Engineering Rationale
These objectives exist because the downstream ML models (CNN/GNN, Phases 5–7) are only as trustworthy as the QoR labels they are trained on. Non-deterministic or silently degraded synthesis runs would inject label noise indistinguishable from genuine manufacturing risk signal.

### Inputs / Outputs
Inputs: none beyond the general Phase 14.5 input set. Outputs: an objectives-compliance checklist attached to each run's metadata record.

### Dependencies
Objective O1 depends on Yosys running in single-threaded, fixed-seed mode (Part 13). Objective O3 depends on the library abstraction layer described in Part 6.

### Runtime / Memory Expectations
Objective verification (equivalence checking, determinism re-run) roughly doubles per-design runtime but is performed on a sampled subset (10% of the corpus) rather than exhaustively, per the statistical research plan (Phase 9).

### Failure Conditions
Failure to meet O1 or O2 on a sampled design triggers a full-corpus re-audit of that library/flow combination.

### Validation
A dedicated `verify_objectives.py` utility (Part 13) checks O1–O6 automatically and emits a pass/fail record per design.

### Industrial Notes
This objective-driven structure parallels IEEE 1500/1149.1 style conformance clauses, where compliance is demonstrated against enumerated, testable requirements rather than narrative description.

### Reviewer Expectations
Reviewers should be able to map each objective directly to a section of the results/validation portion of the eventual paper.

### Future Scalability
Additional objectives (e.g., O7 — power-signoff fidelity) can be appended without restructuring the document, since each objective is independently verifiable.

---

## PART 3 — Inputs

### Purpose
To precisely define every artifact consumed by the synthesis stage, eliminating ambiguity about what constitutes a valid synthesis job.

### Theory
A synthesis job is fully specified only when five independent input classes are simultaneously fixed: (1) design RTL, (2) design metadata, (3) benchmark manifest entry, (4) constraints, (5) technology library. Any missing class renders the job under-specified and therefore non-reproducible.

### Detailed Input Classes

**Normalized RTL.** The exact output artifact of Phase 14.4: lint-clean, structurally normalized Verilog/SystemVerilog with a canonical module hierarchy and no residual vendor-specific pragmas outside the whitelist established in Phase 14.4.

**Metadata.** A per-design JSON record carrying: design name, source benchmark family, RTL line count, declared top module, target library list, expected clock domains, and a content hash of the RTL used for provenance.

**Benchmark manifest.** The master ledger (Phase 14.2/14.3) mapping every design instance to its acquisition source, license terms, and annotation status; synthesis reads this manifest to confirm a design is licensed and annotated before consuming compute resources on it.

**Constraints.** SDC-format constraint files (Part 7), one per design per operating corner, authored or auto-derived under rules fixed in this phase.

**Technology libraries.** The `.lib`/LEF pairs for Sky130, GF180, and ASAP7 (Part 6), version-pinned and checksum-verified before use.

### Engineering Rationale
Separating these five classes allows independent versioning: RTL can be re-normalized without re-authoring constraints, and a new library can be added without touching any RTL.

### Inputs/Outputs Table Note
This part is itself the formal definition of "Inputs" referenced by every other part; no separate outputs are produced here — Part 3 is a schema, not a transform.

### Dependencies
Depends entirely on the successful, locked completion of Phases 14.1–14.4.

### Runtime / Memory Expectations
Input validation (hash checking, manifest cross-reference) is O(1) per design and adds negligible runtime (<1 second).

### Failure Conditions
Missing or hash-mismatched RTL, absent manifest entry, or malformed constraint files immediately abort the job with a Part-12 failure record before any synthesis compute is spent.

### Validation
A pre-flight checker (`preflight_check.py`, Part 13) enforces presence and integrity of all five input classes prior to invoking Yosys.

### Industrial Notes
This mirrors the "design kit checklist" gating step used before RTL is admitted to a production synthesis run in industrial ASIC flows.

### Reviewer Expectations
Reviewers should see the five-input schema as the concrete answer to "what exactly goes into your synthesis experiment."

### Future Scalability
Additional input classes (e.g., power intent in UPF format) can be appended as a sixth class in a future phase without disrupting existing five-class jobs.

---

## PART 4 — Supported RTL Languages

### Purpose
To bound the syntactic and semantic scope of RTL the synthesis stage guarantees to process correctly.

### Theory
Synthesizability is not a property of a language but of a *subset* of a language — the "synthesizable subset." Phase 14.5 explicitly enumerates the accepted subset rather than relying on tool-default behavior, since undocumented subset boundaries are a primary source of irreproducibility in synthesis research.

### Supported Constructs

**Verilog-2001.** Full structural and RTL-level synthesizable subset: always blocks with blocking/non-blocking assignment disciplines matching combinational/sequential intent, parameterized modules, generate blocks, and standard operators.

**SystemVerilog (IEEE 1800, synthesizable subset).** `always_comb`, `always_ff`, `always_latch`, packed structs/unions used in a synthesizable manner, interfaces resolved at elaboration time, and enumerated types. Assertions (SVA) are accepted but stripped to synthesis-inert form (moved to a sidecar file) rather than synthesized as logic.

**Generated Verilog.** Output of HLS tools or generator scripts (Chisel/FIRRTL-to-Verilog, PyRTL, etc.) is accepted provided it passes the same Phase 14.4 normalization gate as hand-written RTL; no special-casing is applied at the synthesis stage.

**Gate-level netlists.** Pre-mapped netlists (e.g., delivered as a benchmark in already-mapped form) are accepted as a pass-through input class, routed directly to Stage F (QoR Collection) after a library-consistency check, bypassing Stages A–D.

### Unsupported Constructs
Explicitly rejected at the Phase 14.4 gate (and re-checked defensively at Stage A of this phase): testbench-only constructs (`initial` blocks used for stimulus, `$display`, file I/O system tasks), real/time datatypes in synthesizable logic, dynamic process control (`fork`/`join` outside verification code), unbounded dynamic arrays, and class-based SystemVerilog OOP constructs. Any of these encountered at Stage A triggers immediate rejection with a Part-12 "unsupported construct" failure record rather than a best-effort partial synthesis.

### Engineering Rationale
A hard rejection policy (rather than silent tool-specific workarounds) guarantees that every design admitted to the QoR corpus was synthesized under identical semantic assumptions, which is essential for the ML labels to be comparable across the dataset.

### Inputs / Outputs
Input: RTL file set. Output: an accept/reject decision plus, on rejection, a construct-level diagnostic.

### Dependencies
Depends on the Yosys frontend's language support boundary for the pinned tool version (Part 13).

### Runtime / Memory Expectations
Language-conformance scanning is a lightweight static pass, typically under 5 seconds per design regardless of design size.

### Failure Conditions
Any unsupported construct is a hard failure, not a warning.

### Validation
A construct whitelist/blacklist table is maintained under version control and checked programmatically at Stage A.

### Industrial Notes
This construct-boundary discipline matches the "RTL coding guidelines for synthesis" documents published by major EDA vendors, which similarly enumerate accepted and forbidden constructs rather than relying on tool heuristics.

### Reviewer Expectations
Reviewers should be able to independently verify that no design in the corpus relies on an unsupported construct, by consulting this table.

### Future Scalability
The construct table is designed to be extended (e.g., to admit a restricted class-based subset) as tool support matures, without invalidating previously synthesized designs.

---

## PART 5 — Synthesis Architecture

### Purpose
To define the internal seven-stage pipeline (A–G) that constitutes the synthesis engine, giving each stage a single, well-defined responsibility.

### Theory
Decomposing synthesis into discrete, independently-inspectable stages allows QoR degradation or failure to be attributed to a specific transformation, rather than treating the synthesizer as an opaque black box — a requirement for any research claiming synthesis-stage feature attribution.

### Stage A — RTL Parsing
**Purpose:** Convert accepted RTL text into an internal abstract syntax representation.
**Theory/Rationale:** Parsing must be strict; any parse ambiguity is treated as a Part-4 unsupported-construct rejection rather than a best-guess recovery.
**Inputs:** Normalized RTL files. **Outputs:** Internal AST / RTLIL (Yosys's intermediate representation).
**Dependencies:** Yosys `read_verilog`/`read_systemverilog` frontends. **Runtime:** seconds to low minutes depending on file count. **Memory:** proportional to RTL token count, typically small (<500 MB). **Failure conditions:** syntax errors, unsupported constructs. **Validation:** parser exit code plus line-accurate error logging. **Industrial notes:** equivalent to the "elaboration read" step in Design Compiler/Genus. **Reviewer expectations:** a clean parse log with zero warnings for every accepted design. **Future scalability:** frontend swappable for a commercial parser without changing downstream stages.

### Stage B — Hierarchy Elaboration
**Purpose:** Resolve module instantiation hierarchy, parameters, generate-block expansion, and bind the design's top module.
**Theory/Rationale:** Elaboration must fully resolve all parameters to constants; any residual unresolved parameter is a hard error, since it would make QoR non-deterministic.
**Inputs:** RTLIL from Stage A, top-module declaration from metadata. **Outputs:** Fully elaborated, flattened-parameter hierarchical netlist (`hierarchy`, `proc` passes in Yosys terms).
**Dependencies:** Stage A output; metadata top-module field. **Runtime:** low, typically under a minute. **Memory:** scales with hierarchy depth × instance count. **Failure conditions:** unresolved parameters, missing top module, combinational loops detected at elaboration. **Validation:** hierarchy report cross-checked against metadata's expected module count. **Industrial notes:** mirrors "elaborate" step in industrial flows, where a hierarchy report is a standard sign-off artifact. **Reviewer expectations:** hierarchy report attached to every run. **Future scalability:** supports future multi-top (hard-macro) elaboration.

### Stage C — Optimization
**Purpose:** Perform technology-independent logic optimization (Part 8) on the elaborated netlist.
**Theory/Rationale:** Boolean simplification, constant propagation, and dead-logic removal are performed before technology binding so that the optimization search space is not constrained by cell-library artifacts.
**Inputs:** Elaborated netlist. **Outputs:** Optimized generic (technology-independent) netlist.
**Dependencies:** Yosys `opt`, `fsm`, `memory` passes. **Runtime:** moderate; the largest time consumer for large designs. **Memory:** can spike during Boolean restructuring (ABC integration). **Failure conditions:** optimizer non-termination (bounded by a hard iteration cap; see Part 12). **Validation:** cell-count and depth deltas logged before/after. **Industrial notes:** equivalent to "compile -only_hold_time false" style generic optimization phases in commercial tools. **Reviewer expectations:** optimization pass log with iteration counts. **Future scalability:** optimization recipe is a versioned script (Part 13), independently upgradable.

### Stage D — Technology Mapping
**Purpose:** Bind the generic optimized netlist to the target standard-cell library (Part 9).
**Theory/Rationale:** Technology mapping is modeled as a covering problem over the technology-independent Boolean network, solved via ABC's structural/Boolean matching under the library's cell timing/area models.
**Inputs:** Optimized generic netlist, `.lib` file for target library. **Outputs:** Technology-mapped gate-level netlist.
**Dependencies:** ABC (bundled with Yosys), target `.lib`. **Runtime:** moderate to high for large designs. **Memory:** proportional to netlist size × library cell count. **Failure conditions:** no legal cell covering found for a sub-network (Part 12). **Validation:** post-mapping cell list checked against library cell whitelist. **Industrial notes:** functionally equivalent to Genus/Design Compiler's "map_optimize" phase. **Reviewer expectations:** confirmation that 100% of instantiated cells belong to the declared library. **Future scalability:** mapping stage is the primary extension point for multi-Vt and multi-library experiments (Part 6).

### Stage E — Netlist Generation
**Purpose:** Emit the final structural gate-level netlist in a standard, tool-agnostic format.
**Theory/Rationale:** Output format (structural Verilog) is chosen for maximum downstream compatibility (STA tools, physical design tools, GNN graph extraction in later phases).
**Inputs:** Mapped netlist. **Outputs:** Structural Verilog netlist file, per-design. **Dependencies:** Yosys `write_verilog`. **Runtime:** low. **Memory:** low. **Failure conditions:** write errors, disk quota. **Validation:** output file re-parsed as a self-check. **Industrial notes:** equivalent to a "write netlist" sign-off deliverable. **Reviewer expectations:** netlist openly readable, not obfuscated. **Future scalability:** additional output formats (e.g., structural VHDL) can be added as alternate Stage E emitters.

### Stage F — QoR Collection
**Purpose:** Extract and record the full quality-of-results metric set (Part 10).
**Theory/Rationale:** QoR must be collected from the mapped netlist plus a dedicated static timing analysis pass (OpenSTA), not estimated from synthesis-internal heuristics alone, to ensure sign-off-grade accuracy.
**Inputs:** Mapped netlist, constraints, `.lib`. **Outputs:** QoR report (Part 10 schema). **Dependencies:** OpenSTA. **Runtime:** low to moderate. **Memory:** low. **Failure conditions:** STA non-convergence, constraint parse failure. **Validation:** QoR schema completeness check. **Industrial notes:** matches the "STA sign-off" deliverable pattern. **Reviewer expectations:** every field in Part 10 populated, non-null. **Future scalability:** additional QoR fields (e.g., leakage power) can be appended to the schema.

### Stage G — Validation
**Purpose:** Confirm functional equivalence and constraint fidelity of the final artifact before corpus admission.
**Theory/Rationale:** Independent from Stages A–F; acts as an acceptance gate rather than a transformation.
**Inputs:** Original normalized RTL, mapped netlist. **Outputs:** Pass/fail equivalence verdict, appended to metadata. **Dependencies:** equivalence-checking flow (formal where tractable, simulation-based fallback). **Runtime:** variable, bounded by a per-design timeout. **Memory:** variable. **Failure conditions:** equivalence mismatch, timeout without conclusive verdict (treated as fail-closed). **Validation:** this stage *is* the validation step for the whole pipeline. **Industrial notes:** mirrors LEC (logical equivalence checking) sign-off. **Reviewer expectations:** a documented equivalence-checking methodology, not a bare assertion of correctness. **Future scalability:** formal equivalence coverage can be expanded as tooling matures.

---

## PART 6 — Technology Libraries

### Purpose
To define the exact set of technology libraries against which every design is synthesized, and the abstraction layer that keeps the flow library-agnostic.

### Theory
A standard-cell library is the joint specification of (a) a `.lib` liberty timing/power model per cell per corner, and (b) a LEF abstract physical footprint per cell. Synthesis consumes only the `.lib` view; the LEF view becomes relevant starting in the physical-design phase (explicitly out of scope here per the task boundary).

### Sky130
Open-source SkyWater 130nm PDK standard-cell library (`sky130_fd_sc_hd` family used as primary). Chosen as the primary library because of its complete open liberty characterization across multiple corners and its established use in the OpenLane/OpenROAD reference flow, giving strong reproducibility guarantees.

### GF180
GlobalFoundries 180nm open PDK standard-cell library, used as the secondary library to test cross-library portability (Objective O3) and to provide a second, independent process node for QoR variance analysis.

### ASAP7
The ASAP7 predictive 7nm FinFET library (academic, non-manufacturable, calibrated to represent an advanced-node regime), used to extend the QoR distribution toward advanced-node design points that neither Sky130 nor GF180 can represent, broadening the training distribution for the downstream ML models.

### Future Extensibility
The library abstraction layer treats every library as a tuple `(name, lib_path, corner_set, cell_naming_convention)`. Adding a new library — including a commercial PDK under NDA, used only in a private, non-published run — requires populating this tuple and adding no other code changes.

### .lib and LEF Interaction
Only `.lib` is consumed at this phase; LEF is recorded in the library tuple for forward compatibility with later physical-design phases but is not read by Stage D.

### Timing Models
Each `.lib` provides non-linear delay models (NLDM) or, where available, current-source models (CCS); Stage D and Stage F use whichever model class the library provides, recorded per-run in metadata so QoR comparisons account for model-class differences.

### Operating Corners
Each library exposes at minimum a slow (worst-case, high temperature/low voltage), typical, and fast (best-case) corner. Synthesis timing optimization (Part 8) targets the slow corner by default; QoR reports (Part 10) additionally record typical and fast-corner numbers where the library provides them.

### Drive Strengths and Cell Variants
Each logical cell (e.g., NAND2) is available in multiple drive-strength variants (X1, X2, X4, etc.); the mapper (Stage D) selects among these based on the optimization objective (Part 8), and the selected variant distribution is itself recorded as a QoR feature (Part 10) since it correlates with downstream routability and reliability risk.

### Multi-Vt Discussion
Where a library provides multiple threshold-voltage (Vt) cell families (e.g., high-Vt for leakage reduction, low-Vt for speed), the mapper is permitted to mix Vt families under the power-optimization objective (Part 8); the resulting Vt-mix ratio is recorded as a QoR feature, since Vt mixing is a known contributor to reliability and manufacturing variation risk — directly relevant to this paper's central thesis.

### Engineering Rationale
Supporting three structurally different libraries (open 130nm, open 180nm, predictive 7nm) is deliberate: it prevents the downstream ML model from overfitting to a single process node's QoR distribution, directly supporting the paper's claim of cross-technology generalization.

### Dependencies
Library files are checksum-pinned in the manifest (Part 3); a mismatch aborts the run before Stage D.

### Runtime / Memory Expectations
Library loading is a one-time cost per synthesis batch (cached across designs within the same batch), typically under 10 seconds.

### Failure Conditions
Missing corner data, malformed `.lib` syntax, or checksum mismatch.

### Validation
A library-conformance linter checks every `.lib` file against the liberty format grammar before first use.

### Industrial Notes
This tri-library strategy mirrors how industrial DTCO (design-technology co-optimization) studies deliberately synthesize the same design across multiple foundry nodes to isolate technology-driven QoR variance from design-driven variance.

### Reviewer Expectations
Reviewers should expect explicit corner and Vt disclosure for every reported QoR number, not an unqualified single figure.

### Future Scalability
The tuple-based abstraction supports adding advanced-node FinFET/GAA libraries as they become available in open or academic form.

---

## PART 7 — Constraints

### Purpose
To define the complete SDC constraint methodology governing every synthesis run, ensuring timing results are meaningful and comparable.

### Theory
Constraints translate a design's intended operating environment into the mathematical bounds (arrival/required times) that drive both optimization (Part 8) and QoR measurement (Part 10). Under-constraining silently permits invalid designs to appear to "pass"; over-constraining wastes area/power chasing unnecessary margin. Phase 14.5 fixes a constraint-authoring methodology to avoid both failure modes.

### Clock
Each design's primary clock(s) are declared via `create_clock`, with period derived either from the benchmark's documented target frequency (where available) or, absent documentation, a conservative default derived from the design's estimated logic depth (a heuristic bootstrap constraint that is then iteratively tightened — see Part 8's timing-optimization tradeoff philosophy).

### Generated Clocks
Divided or gated derivative clocks are declared via `create_generated_clock`, referencing their master clock explicitly, to avoid the mapper incorrectly treating a divided clock as an independent free-running clock.

### False Paths
Paths crossing genuinely asynchronous domains, or paths through configuration registers not intended for timing closure, are declared via `set_false_path`, always with an explicit textual justification recorded in the constraint file's header comment (never a blanket false-path-everything policy).

### Multicycle Paths
Declared via `set_multicycle_path` only where the RTL's control logic demonstrably guarantees a multi-cycle data-valid window (verified against the RTL's FSM structure, not assumed).

### Input/Output Delays
`set_input_delay`/`set_output_delay` are applied at every primary I/O, defaulting to a fraction (typically 20–30%) of the clock period when the benchmark provides no explicit I/O timing budget, documented per design in the constraint file.

### Reset Handling
Asynchronous reset paths are constrained via `set_false_path -from [get_ports rst]` only when the reset is documented as asynchronous in the metadata; synchronous resets are left fully timed.

### Clock Uncertainty and Transition
`set_clock_uncertainty` and `set_clock_transition` are applied using library-recommended defaults for the target corner, ensuring margin assumptions are library-consistent rather than arbitrary.

### Max Fanout / Max Transition / Load
`set_max_fanout`, `set_max_transition`, and `set_load` are derived directly from the target library's recommended operating conditions, never left at tool defaults, since tool defaults are frequently library-agnostic and can silently produce unrealistic QoR.

### Engineering Rationale
A fully documented, per-design constraint provenance (why each constraint was chosen) is essential because the ML models trained on this corpus must not learn spurious correlations between arbitrary constraint choices and manufacturing/reliability labels.

### Inputs / Outputs
Input: benchmark documentation, library operating conditions, RTL FSM structure. Output: one `.sdc` file per design per corner.

### Dependencies
Depends on Part 6 library operating-condition data and Part 4's accepted RTL structure for multicycle justification.

### Runtime / Memory Expectations
Constraint authoring/derivation is a lightweight, largely one-time cost per design (seconds), with re-use across corners.

### Failure Conditions
Missing or self-contradictory constraints (e.g., a false path also covered by a multicycle declaration) are rejected by a constraint linter before Stage F.

### Validation
`check_setup`/`check_timing`-equivalent SDC linting is run before every synthesis job.

### Industrial Notes
This constraint discipline mirrors the "constraint sign-off" methodology mandated before any tapeout-bound synthesis run in industrial ASIC design.

### Reviewer Expectations
Reviewers should expect a justification comment for every non-default constraint, not bare SDC syntax.

### Future Scalability
The constraint methodology is corner-parameterized so that additional operating corners can be added without restructuring constraint files.

---

## PART 8 — Optimization Strategy

### Purpose
To define the technology-independent and technology-aware optimization strategy applied during Stages C and D.

### Theory
Synthesis optimization is a multi-objective search over area, timing, and power, subject to the constraint set (Part 7). Because these objectives are frequently in tension (e.g., aggressive buffering improves timing at an area/power cost), Phase 14.5 fixes an explicit, documented tradeoff policy rather than leaving the balance to opaque tool defaults.

### Area Optimization
Achieved primarily through Boolean factoring and common sub-expression sharing during Stage C, and through minimum-drive-strength cell selection during Stage D wherever timing slack permits.

### Timing Optimization
Achieved through critical-path-aware resynthesis (ABC's `dch`/`resyn2`-class scripts), drive-strength upsizing on the reported critical path, and structural logic restructuring (Part 8, Logic Restructuring) targeted only at paths within a documented slack threshold of the critical path — avoiding "polishing" don't-care paths at unnecessary area cost.

### Power Optimization
Addressed primarily through Multi-Vt cell selection (Part 6) on non-critical paths and through clock-gating-aware structural preservation (ensuring any RTL-level clock-gating structures from Phase 14.4 normalization are not accidentally optimized away).

### Buffer Insertion
Applied only where max-transition or max-fanout constraints (Part 7) are violated, or where timing optimization identifies a genuine long-wire/high-fanout critical path; buffer count is tracked as a QoR feature (Part 10) precisely because excess buffering is itself a known proxy signal for downstream routing congestion and reliability risk.

### Logic Restructuring
Boolean restructuring (associativity/commutativity-preserving rewrites) is bounded by an iteration cap to guarantee termination (feeding Part 12's failure handling for non-convergent cases).

### Constant Propagation and Dead Logic Removal
Applied exhaustively during Stage C as a correctness-preserving simplification, prior to any timing/power-driven optimization, since removing genuinely dead logic can never worsen any objective.

### Boolean Optimization
Two-level and multi-level Boolean minimization (via ABC) is applied to the generic netlist prior to technology binding, so that the technology mapper operates on an already-minimized Boolean network.

### Technology-Aware Optimization
After initial technology mapping (Stage D), a technology-aware re-optimization pass adjusts cell selection using the actual library timing/area/power data, since generic-network optimization cannot fully anticipate library-specific effects (e.g., library cells that do not follow a simple gate-count-proportional area model).

### Tradeoff Philosophy
The default optimization objective is **timing-first, area-second, power-third**, matching the conservative industrial default for exploratory/dataset-generation flows (as opposed to a production tapeout flow, which would be tuned per-project). This choice is documented explicitly in every run's metadata so the ML models can, if desired, later be trained on runs using an alternate objective ordering as an ablation study.

### Engineering Rationale
Fixing and documenting the objective ordering, rather than leaving it as an undocumented tool default, is essential to the paper's reproducibility claims, since QoR is materially different under different objective orderings for the same RTL and library.

### Inputs / Outputs
Input: optimized/mapped netlist candidates. Output: final selected netlist per the fixed objective ordering, plus a per-design log of every optimization decision.

### Dependencies
ABC optimization scripts (version-pinned, Part 13), library timing/power data (Part 6), constraint set (Part 7).

### Runtime / Memory Expectations
Optimization is typically the single largest runtime contributor within Stages C–D; large designs may require the parallel execution model (Part 13).

### Failure Conditions
Non-convergent restructuring (bounded by iteration cap), infeasible constraint set (no legal solution within max fanout/transition bounds).

### Validation
Before/after cell-count, depth, and estimated-slack deltas are logged at every optimization sub-pass for auditability.

### Industrial Notes
This objective-ordering discipline mirrors "compile strategy" documentation required in industrial synthesis sign-off packages.

### Reviewer Expectations
Reviewers should expect the objective ordering to be explicitly stated wherever QoR numbers are reported in the eventual paper.

### Future Scalability
The objective ordering is a configurable parameter recorded per run, enabling future ablation experiments (e.g., power-first ordering) without any flow restructuring.

---

## PART 9 — Technology Mapping

### Purpose
To specify precisely how each generic Boolean/RTL construct is bound to library cells during Stage D.

### Theory
Technology mapping is a covering problem: partition the technology-independent Boolean network into sub-networks, each exactly matched (structurally or functionally) to an available library cell, minimizing the chosen cost function (Part 8's objective ordering) subject to legality constraints (fan-in limits, supported cell functions).

### Standard Cell Mapping
Combinational logic (AND/OR/XOR/MUX networks) is mapped to the library's standard combinational cells (NAND, NOR, AOI, OAI, XOR, MUX primitives) via ABC's structural/Boolean matching, preferring compound gates (e.g., AOI22) over discrete gate chains wherever the library provides them, since compound-gate mapping typically improves both area and timing.

### Arithmetic Mapping
Adders, comparators, and multipliers surviving Stage C's generic optimization are mapped either to dedicated library arithmetic macros (where the library provides them) or synthesized from the standard cell set using the library's carry-chain-friendly cell variants where available; multiplier mapping defaults to a generic multi-level synthesis rather than assuming a hard macro, since none of the three target libraries (Part 6) provide characterized multiplier macros.

### Sequential Mapping
Flip-flops and latches are mapped to the library's sequential cells matching the RTL's declared reset/set polarity and synchronicity exactly; any RTL sequential element whose reset semantics cannot be exactly matched by an available library cell is treated as an unsupported-cell condition (Part 12), not silently approximated.

### Memory Handling
RTL-inferred memories (register-file-style arrays) are, at this phase, kept as flip-flop-array-mapped structures rather than routed to memory compiler macros, since Phase 14.5 is explicitly bounded to logic synthesis (memory compilation and hard-macro integration are reserved for a later phase per the task's stated scope boundary).

### Black Boxes
Any module explicitly declared as a black box in metadata (e.g., a hard IP stub) is preserved as an unmapped, opaque instance in the final netlist, with its interface checked for consistency but its internal logic untouched by Stages C–D.

### Library Compatibility
A design is only accepted for mapping against a given library after a compatibility pre-check confirms the library provides every required cell function (sequential polarity variants, arithmetic primitives) needed by that design's elaborated netlist.

### Unsupported Cells
Where a required functional cell genuinely has no library equivalent (e.g., a specific latch polarity absent from a given library), the run against that library is aborted with a Part-12 "library mismatch" record, while the same design continues normally against the other compatible libraries (Objective O3 only requires two-of-three compatibility, not universal compatibility).

### Multi-Library Support
The mapper is invoked once per (design, library) pair; there is no cross-library sharing of mapping decisions, ensuring each library's QoR is measured independently and fairly.

### Engineering Rationale
Explicit, documented mapping rules for each RTL construct class prevent the common research pitfall of silently inconsistent mapping behavior across designs, which would otherwise inject unexplained variance into the QoR-label distribution used for ML training.

### Inputs / Outputs
Input: optimized generic netlist, target `.lib`. Output: fully technology-mapped netlist, or a documented Part-12 failure record.

### Dependencies
ABC technology mapper, library cell function inventory (Part 6).

### Runtime / Memory Expectations
Scales with the product of netlist size and library cell-function count; typically the second-largest runtime contributor after Stage C optimization.

### Failure Conditions
Uncoverable sub-networks, unsupported sequential polarity, incompatible library/design pairing.

### Validation
Post-mapping cell-list audit confirming 100% of instances belong to the declared library's cell set (Part 5, Stage D validation, re-stated here for mapping-specific completeness).

### Industrial Notes
This mapping-rule specificity matches the "technology mapping guidelines" appendices found in Cadence Genus and Synopsys Design Compiler user manuals.

### Reviewer Expectations
Reviewers should expect a clear statement, per design, of which of the three libraries it was successfully mapped against and why any exclusions occurred.

### Future Scalability
Memory-macro and hard-IP mapping is explicitly deferred to a later, clearly separated phase, keeping this phase's scope stable as the flow is extended.

---

## PART 10 — Quality Metrics

### Purpose
To define the exact, complete QoR schema emitted by Stage F for every synthesized design, forming the ground-truth label set consumed by later ML phases.

### Theory
QoR completeness (Objective O4) requires a fixed schema so that every design contributes a directly comparable feature vector; partial or inconsistently-named QoR fields would silently corrupt downstream model training.

### Schema Fields

- **Area:** total cell area (µm²), reported directly from the library's cell area data summed over the mapped netlist.
- **Cell count:** total instance count, and a breakdown by cell class (combinational/sequential/buffer).
- **Timing:** worst-case arrival time at every timing endpoint, summarized into...
- **Worst Negative Slack (WNS):** the single most negative slack value across all timing paths under the applicable corner.
- **Total Negative Slack (TNS):** the sum of all negative slack values across all violating endpoints, capturing the *breadth* of timing violation, not just its worst point.
- **Critical path:** the specific start-point/end-point pair and its full logic-cell sequence corresponding to WNS, retained for later GNN-based structural feature extraction.
- **Power:** dynamic switching power (at the constraint-declared clock activity assumption) and static leakage power, both from the `.lib` power model.
- **Logic depth:** maximum combinational logic-level count between any two sequential elements or I/O boundary.
- **Buffer count:** count of cells inserted purely for buffering (Part 8), tracked separately from functional logic cells, as a congestion/reliability-risk proxy.
- **Utilization estimate:** a coarse area-based utilization proxy computed as total cell area divided by an assumed core-area bound (a lightweight stand-in, since true placement utilization is a later-phase concern).
- **Hierarchy preservation:** a boolean/percentage indicator of how much of the original RTL module hierarchy survives flattening-free optimization, relevant to later GNN graph construction which relies on hierarchy-aware graph structure.

### Engineering Rationale
Each field is chosen because it either (a) directly reflects a classical PPA (power-performance-area) concern, or (b) has documented literature linkage to manufacturing/packaging/reliability risk (e.g., excessive buffer count correlating with routing congestion and hence yield risk) — directly serving the paper's central DTCO thesis.

### Inputs / Outputs
Input: mapped netlist, STA results. Output: a single structured (JSON) QoR record per design per library per corner.

### Dependencies
OpenSTA for timing/power extraction; library `.lib` data for area/power.

### Runtime / Memory Expectations
Lightweight; QoR extraction typically completes in well under a minute per design.

### Failure Conditions
Any null/missing field is treated as a Stage F failure (Objective O4), not silently tolerated.

### Validation
A schema validator checks every emitted QoR record against the fixed field list before corpus admission.

### Industrial Notes
This schema mirrors the structure of a standard "QoR summary report" emitted by commercial synthesis tools, deliberately kept vendor-neutral in field naming.

### Reviewer Expectations
Reviewers should expect the exact schema (field names, units) reproduced in the eventual paper's dataset-description section.

### Future Scalability
Additional fields (e.g., a formal congestion estimate) can be appended to the schema as later phases mature, without breaking existing records (schema versioned, Part 11).

---

## PART 11 — Outputs

### Purpose
To enumerate every artifact the synthesis stage is responsible for producing and persisting.

### Theory
A reproducible pipeline must treat its outputs as a versioned, self-describing artifact set, not merely a working directory of files.

### Mapped Netlist
The Stage E structural Verilog netlist, one file per (design, library) pair, named per a fixed convention: `{design_name}_{library}_{corner}.v`.

### Reports
Human-readable synthesis reports covering area, timing, and power summaries, generated per (design, library, corner) triple.

### Statistics
Machine-readable statistics (cell histograms, optimization-pass deltas) supporting later meta-analysis of the synthesis process itself.

### Logs
Full tool logs (Yosys, ABC, OpenSTA) retained for every run, enabling forensic debugging of any anomalous QoR result.

### QoR Summary
The Part 10 schema record, in JSON, one per (design, library, corner) triple.

### Metadata Update
The per-design metadata record (Part 3) is updated in place with synthesis provenance: tool versions, flow-script hash, timestamp, and Objective O1–O6 compliance flags.

### Manifest Update
The benchmark manifest (Phase 14.2/14.3) is updated to mark each design's synthesis status (pending/complete/failed) per library, feeding the resume capability described in Part 13.

### Engineering Rationale
Treating metadata and manifest updates as first-class synthesis outputs — not an afterthought — is what makes the overall multi-phase pipeline resumable and auditable at corpus scale.

### Inputs / Outputs
This part is itself the formal definition of "Outputs"; inputs are the completed Stage A–G artifacts of Part 5.

### Dependencies
File-system layout defined in Part 14.

### Runtime / Memory Expectations
Output serialization is lightweight, typically a few seconds per design.

### Failure Conditions
Disk write failures, schema-validation failures on the QoR record (Part 10).

### Validation
An output-completeness checker confirms all seven output classes exist for every successfully completed run before the manifest is marked complete.

### Industrial Notes
Mirrors the "deliverables checklist" used to close out a synthesis milestone in an industrial project plan.

### Reviewer Expectations
Reviewers/Artifact Evaluators should be able to locate every one of these seven output classes for any given design in the released corpus.

### Future Scalability
New output classes (e.g., a power-intent-aware report) can be added as an eighth class without disrupting the existing seven.

---

## PART 12 — Failure Handling

### Purpose
To define how every category of synthesis failure is detected, classified, logged, and — where applicable — recovered from, ensuring the pipeline degrades gracefully at corpus scale rather than halting on a single bad design.

### Theory
At corpus scale (thousands of designs × three libraries × multiple corners), some non-zero failure rate is expected and must be treated as data, not as an exceptional event requiring manual intervention for every occurrence.

### Syntax Failures
Detected at Stage A; logged with exact file/line diagnostics; design is marked `failed:syntax` in the manifest and excluded from that run, without blocking other designs.

### Unsupported RTL
Detected at Stage A/B against the Part 4 construct table; logged as `failed:unsupported_construct` with the specific construct identified.

### Library Mismatch
Detected at Stage D's pre-mapping compatibility check (Part 9); logged as `failed:library_mismatch`, with the design still eligible for the remaining compatible libraries.

### Mapping Failures
Detected when ABC cannot find a legal cell covering for some sub-network; logged as `failed:mapping` with the specific uncoverable sub-network identified where possible.

### Timing Failures
Distinguished carefully from a *synthesis* failure: a design with negative WNS (Part 10) is **not** a pipeline failure — it is a valid, informative QoR data point (indeed, timing-violating designs are valuable negative examples for the downstream ML models). Only STA *non-convergence* (the tool failing to produce any timing verdict) is logged as `failed:timing_analysis`.

### Memory Overflow
Detected via a per-job memory ceiling (Part 13's cluster-execution resource limits); a design exceeding the ceiling is logged as `failed:oom` and automatically re-queued once, at a reduced parallelism level, before being marked permanently failed.

### Recovery Strategy
The governing recovery principle is **fail-forward-per-design**: a failure on one (design, library, corner) triple never blocks any other triple. The batch orchestrator (Part 13) continues processing the remaining queue and reports an aggregate failure-rate statistic at batch completion.

### Logging
Every failure is logged to a structured, machine-parseable failure ledger (JSON lines) with: design ID, library, corner, failure class, tool exit code, and a link to the full tool log (Part 11).

### Engineering Rationale
Explicit failure taxonomy prevents the common research error of conflating "the design is genuinely bad" (a valid QoR data point) with "the tool could not process the design" (a genuine pipeline defect requiring investigation).

### Inputs / Outputs
Input: any Stage A–G exception/non-zero-exit condition. Output: a structured failure ledger entry, plus the manifest status update (Part 11).

### Dependencies
The batch orchestrator (Part 13).

### Runtime / Memory Expectations
Failure detection itself is lightweight; the memory-overflow recovery re-queue adds one additional run at reduced parallelism for affected designs only.

### Failure Conditions
(This section is itself about failure conditions; a "failure of failure-handling" — e.g., the orchestrator itself crashing — is treated as a Part-13 infrastructure incident, escalated for manual review.)

### Validation
Weekly aggregate failure-rate review against a documented acceptable-failure-rate threshold (informed by the statistical research plan, Phase 9); an anomalous spike triggers a flow-script audit.

### Industrial Notes
This fail-forward, ledger-driven approach mirrors regression-farm failure triage practices used in large-scale industrial verification and synthesis regression infrastructure.

### Reviewer Expectations
Reviewers should expect an explicit failure-rate disclosure per library in the eventual paper (i.e., "X% of designs failed to map against library Y, for reason Z"), not a corpus presented as uniformly successful.

### Future Scalability
The failure taxonomy is an open enum; new failure classes can be added as the flow is extended to new libraries or RTL sources.

---

## PART 13 — Automation

### Purpose
To specify the concrete automation scripts that implement Parts 1–12 as a repeatable, unattended batch pipeline.

### Theory
A specification is only as reproducible as its executable realization; Phase 14.5 therefore fixes not just the methodology but the exact script boundaries and responsibilities.

### synthesis.py
The top-level per-design driver: consumes the five Part 3 input classes for a single (design, library, corner) triple, invokes Stages A–E via Yosys, and produces the Stage E netlist plus intermediate logs. Fixed tool version pinned (Yosys, exact release tag recorded in the repository's environment lock file, per Phase 13 — Repository Engineering).

### run_yosys.py
A thin, deterministic wrapper around the Yosys invocation itself: fixes the random seed (where Yosys/ABC exposes one), disables multi-threaded non-determinism, and captures the full command-line and environment for provenance (supporting Objective O1).

### collect_qor.py
Implements Stage F: invokes OpenSTA against the mapped netlist and constraints, parses its reports into the Part 10 schema, and validates schema completeness before writing the QoR record.

### generate_reports.py
Produces the human-readable report artifacts (Part 11) from the same underlying QoR record used by `collect_qor.py`, ensuring reports and machine-readable records never diverge.

### Resume Capability
The manifest's per-(design, library, corner) status field (Part 11) allows the batch orchestrator to skip already-`complete` triples on re-invocation, making the entire corpus generation process safely interruptible and restartable.

### Parallel Execution
Independent (design, library, corner) triples are embarrassingly parallel; the orchestrator dispatches a bounded worker pool (sized to available cores/memory) rather than a single global thread count, to respect Part 12's memory-overflow avoidance.

### Cluster Execution
For corpus-scale batches, the same worker-pool model is extended to a job-scheduler-backed cluster (e.g., Slurm-style array jobs), with each array task processing one manifest-assigned triple, keeping the single-design driver (`synthesis.py`) identical between local and cluster execution.

### Manifest-Driven Execution
The batch orchestrator's sole source of work is the benchmark manifest's pending-status entries (Part 3/Part 11); there is no separate, undocumented job list, ensuring the manifest remains the single source of truth for corpus completeness.

### Engineering Rationale
Fixing script boundaries (one driver, one wrapper, one QoR collector, one report generator) prevents the common failure mode where ad hoc scripts accumulate undocumented, mutually-inconsistent flow variants across a long-running research project.

### Inputs / Outputs
Input: manifest pending-queue. Output: updated manifest, full Part 11 output set per completed triple.

### Dependencies
Yosys, ABC, OpenSTA, the Phase 13 repository's environment lock file.

### Runtime / Memory Expectations
Aggregate batch runtime scales linearly with (design count × library count × corner count) divided by available parallelism; per-triple expectations as stated in Parts 5, 8, 9.

### Failure Conditions
Orchestrator-level failures (scheduler errors, environment drift) are distinguished from per-design failures (Part 12) and escalated separately.

### Validation
A dry-run mode (`--dry-run` flag on `synthesis.py`) validates the full input set (Part 3) for an entire pending batch without consuming synthesis compute, catching manifest/library/constraint errors early.

### Industrial Notes
This automation structure mirrors the regression-infrastructure conventions of large EDA-tool user sites, where a single canonical driver script is mandated precisely to prevent flow drift across a large design portfolio.

### Reviewer Expectations
Reviewers/Artifact Evaluators should be able to re-run `synthesis.py --dry-run` against the released manifest and confirm zero input-validation errors.

### Future Scalability
The driver/wrapper/collector/report-generator boundary is stable under future tool substitution (e.g., swapping Yosys for a commercial synthesis engine) since each script's I/O contract, not its internal implementation, is the specified interface.

---

## PART 14 — Repository Structure

### Purpose
To define the on-disk layout produced and consumed by this phase, consistent with the Phase 13 Repository Engineering specification.

### Structure

```
synthesis/
├── flow/
│   ├── synthesis.py
│   ├── run_yosys.py
│   ├── collect_qor.py
│   ├── generate_reports.py
│   └── preflight_check.py
├── libs/
│   ├── sky130/
│   ├── gf180/
│   └── asap7/
├── constraints/
│   └── {design_name}/{corner}.sdc
├── outputs/
│   └── {design_name}/{library}/{corner}/
│       ├── netlist.v
│       ├── qor.json
│       ├── report.txt
│       └── logs/
├── failure_ledger.jsonl
└── manifest_status.json
```

### Engineering Rationale
This layout keeps flow scripts, libraries, constraints, and per-design outputs in clearly separated, independently-versionable trees, matching the modular input classes defined in Part 3.

### Dependencies
Consistent with the repository conventions locked in Phase 13.

### Validation
A repository-structure linter confirms the presence of all required directories before any batch run is permitted to start.

### Industrial Notes
Comparable to the standard `work/`, `lib/`, `constraints/`, `reports/` directory conventions used in industrial synthesis project workspaces.

### Reviewer Expectations
Reviewers should be able to locate any artifact referenced elsewhere in this specification using only this directory map.

### Future Scalability
Additional library or corner subtrees slot into the existing pattern without restructuring.

---

## PART 15 — Deliverables

### Purpose
To enumerate the concrete deliverables Phase 14.5 contributes to the overall research artifact package.

### Deliverables
1. The complete, version-controlled synthesis flow (Part 13/14).
2. The full technology-mapped netlist corpus across all designs × compatible libraries × corners.
3. The full QoR record corpus (Part 10 schema) — the primary ground-truth label set for later ML phases.
4. The failure ledger (Part 12), disclosed as a first-class research artifact, not omitted.
5. Updated per-design metadata and benchmark manifest (Part 11).
6. This specification document itself, serving as the methodology section basis for the eventual paper.

### Engineering Rationale
Treating the failure ledger and the flow scripts as deliverables — not just the "successful" netlists — is essential for IEEE Artifact Evaluation, which rewards transparency about a pipeline's limitations.

### Dependencies
All prior parts of this phase.

### Validation
A deliverables-completeness checklist is run before the phase is declared closed.

### Industrial Notes
Matches a standard "phase exit criteria" checklist used in staged industrial engineering programs.

### Reviewer Expectations
Reviewers should be able to check off each of the six deliverables independently against the released repository.

### Future Scalability
Additional deliverables (e.g., a cross-library QoR-variance report) can be appended in a future phase.

---

## PART 16 — Publication Readiness

### Purpose
To assess and document this phase's readiness for IEEE submission, artifact evaluation, and long-term reproducibility.

### IEEE Reproducibility
Every synthesis decision in this document is stated as a fixed, versioned rule rather than a tool default, satisfying IEEE's reproducibility expectations for methodology sections; the flow-script hash and tool version pinning (Part 13) provide the concrete reproducibility anchor.

### Artifact Evaluation
The dry-run validation mode (Part 13), the failure ledger (Part 12), and the fixed repository structure (Part 14) collectively satisfy the standard Artifact Evaluation criteria of *available*, *functional*, and *reusable*.

### Industrial Deployment
The strict input/output contracts (Part 3/Part 11) and the fail-forward batch model (Part 12) make this flow directly adoptable as an internal DTCO dataset-generation pipeline by an industrial EDA or foundry design-enablement team, beyond its research use.

### Zenodo Compatibility
The Part 14 repository structure, combined with checksum-pinned libraries (Part 6) and a versioned flow-script set (Part 13), is directly packageable as a Zenodo-archived, DOI-citable artifact accompanying the paper.

### Future Scalability
This phase's library abstraction (Part 6), extensible failure taxonomy (Part 12), and modular script boundaries (Part 13) are explicitly designed so that later phases (floorplanning, placement, CTS, routing, congestion prediction — all explicitly out of scope here) can be appended as new phases without any retroactive modification to Phase 14.5's locked content.

### Engineering Rationale
Publication readiness is treated as a design requirement of the specification itself, not an afterthought applied at paper-writing time.

### Reviewer Expectations
Reviewers should conclude this phase is self-contained, falsifiable, and directly extensible — the three properties IEEE Artifact Evaluation committees most commonly cite as differentiating strong versus weak systems papers.

---

**END OF PHASE 14.5**

*This document continues seamlessly from the locked Phase 14.4 (RTL Standardization & Normalization Specification) and is itself locked upon completion. The next phase (14.6, if defined) should address only floorplanning and physical-design entry, per the explicit scope boundary established in this document's task definition.*
