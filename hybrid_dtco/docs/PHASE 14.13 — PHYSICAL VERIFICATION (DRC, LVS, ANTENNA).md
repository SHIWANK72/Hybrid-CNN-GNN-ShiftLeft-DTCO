# PHASE 14.13 — PHYSICAL VERIFICATION (DRC, LVS, ANTENNA)

## AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems

**Target Conference:** IEEE International Conference on Microelectronics (ICM 2026)
**Document Class:** Physical Verification Specification — Continuation of Phase 14.12 (Electromigration and IR Drop Sign-off)
**Scope:** Deterministic, reproducible, ML-instrumented Physical Verification (DRC, LVS, Antenna) subsystem for the open-source semiconductor physical implementation flow

---

## PREFACE AND CONTINUITY STATEMENT

Phase 14.12 concluded the reliability sign-off sequence by establishing IR drop and electromigration (EM) closure as a precondition for entry into Physical Verification. At the close of Phase 14.12, the design database carries forward a fully placed, clock-tree-synthesized, routed, parasitic-extracted, timing-closed, IR-drop-closed, and EM-closed netlist bound to a specific process design kit (PDK) node, together with a manifest of cryptographic hashes covering every artifact consumed and produced by Phases 14.6 through 14.12. Phase 14.13 accepts this database as its sole authoritative input and executes the final manufacturing-facing verification gate prior to tapeout: Design Rule Checking (DRC), Layout Versus Schematic (LVS), and Antenna Effect verification.

This phase is deliberately positioned as the terminal gate in the physical implementation pipeline because it is the only stage in the flow that verifies the manufacturability of the design against the foundry's signed-off ground truth — the rule deck — rather than against internal, tool-native representations of design intent. Every prior stage (placement, CTS, routing, parasitic extraction, STA, IR drop, EM) operates on the design's *own* declared intent, validating consistency, timing, and physical margins with respect to constraints the design team itself authored. Physical Verification instead asks whether the geometric artifact — the GDSII stream — can be fabricated and, once fabricated, whether it will behave as the schematic-level netlist promised. It is thus the first (and only) point in the flow where an external, foundry-controlled ground truth is checked bit-for-bit, polygon-for-polygon, against internally generated layout data.

This document maintains full terminological, structural, and methodological continuity with Phases 14.6 through 14.12. All stage naming conventions (Stage A through Stage J), manifest schema conventions, failure ledger schema, quality metric taxonomy, dataset generation philosophy for downstream machine learning consumption, and reproducibility requirements for IEEE Artifact Evaluation are preserved without modification. No new manifest fields are introduced without a corresponding schema version bump, and no previously defined field is renamed, removed, or reinterpreted.

---

# PART 1 — PHYSICAL VERIFICATION PHILOSOPHY

## 1.1 Purpose

The purpose of Phase 14.13 is to establish, with cryptographic and geometric certainty, that the final routed design:

1. Contains no violation of any minimum-geometry, minimum-spacing, minimum-area, minimum-enclosure, density, or manufacturing-grid rule specified by the foundry's signed-off DRC rule deck (Section 6).
2. Is electrically and topologically identical, at the device and net level, to the schematic-level (post-synthesis, post-P&R) netlist from which it was physically implemented (Section 7).
3. Contains no unterminated, unprotected polysilicon or metal antenna structure capable of accumulating sufficient plasma-induced charge during fabrication to damage a downstream gate oxide (Section 8).

These three verification domains are not independent checks bolted together for convenience; they are the three necessary and jointly sufficient conditions for a layout to be considered "manufacturing clean" under the sign-off methodology this flow follows. A design that is DRC-clean but LVS-mismatched is manufacturable but non-functional. A design that is DRC-clean and LVS-clean but has antenna violations is manufacturable and (at least in simulation) functional, but carries an elevated risk of latent or immediate gate-oxide failure that will not be observable until first silicon — and in some cases not until accelerated life testing or field return. Only the conjunction of all three checks passing constitutes tapeout readiness.

## 1.2 Theory

Physical Verification, in the theory of VLSI sign-off, occupies the role of *the final translation-invariance check*. Every stage from placement onward operates on progressively more concrete representations of the same abstract netlist: placement assigns coordinates, CTS inserts buffering hierarchy, routing assigns physical wire geometry, and parasitic extraction annotates that geometry with RC values. At each step, an EDA tool is trusted to preserve the semantic content of the netlist while changing its physical representation. Physical Verification is the point at which that trust is *audited* rather than assumed: DRC verifies that the geometric representation obeys the physical constraints of the fabrication process independent of any tool's internal bookkeeping, and LVS independently re-extracts the electrical netlist directly from the polygons of the GDSII stream and compares it, net-for-net and device-for-device, against the schematic netlist that was supposed to have been preserved.

This independent-re-derivation property is the theoretical core of why Physical Verification cannot be replaced by "the router said it was fine" or "the DRC-aware detail router reported zero violations during routing." In-tool DRC/LVS-awareness during placement and routing is a *heuristic optimization signal* used to guide the router away from violations; it is not a formally exhaustive, foundry-certified verification pass. The router's internal notion of a design rule may be an approximation, a simplification, or simply out of date relative to the signed-off rule deck. Physical Verification, by contrast, is required to run against the actual, versioned, foundry-issued rule deck (or its open-source equivalent, e.g., a Skywater130, GlobalFoundries 180MCU, or IHP SG13G2 rule deck expressed in Magic `.tech` or KLayout `.drc`/`.lvs` script form) and is required to be exhaustive over the entire flattened or hierarchically-preserved layout, not merely over the regions the router happened to touch.

## 1.3 Engineering Rationale

The engineering rationale for treating Physical Verification as a hard, non-bypassable gate rests on four observations drawn from industrial tapeout practice:

**First**, DRC violations are not merely aesthetic; a subset of them (minimum spacing, minimum enclosure, minimum width) map directly onto photolithographic and etch process windows. A spacing violation of even a few nanometers below the rule-deck minimum can, depending on the layer and the local density context, result in bridging defects during fabrication — two structures that were meant to be electrically isolated instead becoming shorted. This is not probabilistic in the sense of "might reduce yield somewhat"; below certain violation severities it is close to deterministic that the structure will fail during manufacturing on that layer, at that node.

**Second**, LVS is the only checkpoint in the entire flow that verifies the layout against the netlist using an entirely independent code path. Every other stage (STA, IR, EM) consumes a netlist and parasitics that were themselves derived from the same layout database, and thus share systematic error modes with that database. LVS, by extracting devices and connectivity directly from GDSII polygons using a device-recognition and connectivity-extraction algorithm (implemented here via Netgen operating on Magic-extracted layout netlists, cross-checked against KLayout's `pex`-independent connectivity extractor), provides a genuinely orthogonal verification path. Any latent bug in the P&R tool's netlist-to-layout binding — a misconnected macro pin, a swapped power/ground rail, a dropped filler-cell tie — is only reliably caught here.

**Third**, the antenna effect is a foundry-line-specific manufacturing hazard that has no analog earlier in the flow. During plasma etching of metal and polysilicon layers, an isolated conductor with a large exposed area relative to the gate area it connects to can accumulate charge from the plasma and discharge through the thin gate oxide, causing oxide wear-out or immediate breakdown. This mechanism is invisible to STA, IR, and EM analysis, all of which reason about steady-state or transient electrical behavior of a *completed* chip; antenna violations are strictly a *fabrication-time* hazard that only physical verification, working from ratios of exposed conductor area to gate area on a per-net basis, can detect.

**Fourth**, from a purely programmatic standpoint, Physical Verification is the single most expensive stage, in engineer-hours, to debug post-tapeout. A DRC or LVS escape discovered after tapeout means, at minimum, a full re-spin of the mask set; at worst, it means non-functional silicon and a multi-month schedule slip. The cost asymmetry between catching an error here (hours to days of re-run time) versus catching it after fabrication (months and tens to hundreds of thousands of dollars in mask costs) is the fundamental economic argument for treating this phase as a hard, blocking gate with zero tolerance for unresolved critical violations.

## 1.4 Inputs

Physical Verification consumes, at minimum, the following artifact classes, each individually hash-verified against the Phase 14.12 manifest before any check begins:

- Final routed DEF (post-EM/IR closure)
- Final routed OpenDB (`.odb`) database
- Streamed-out GDSII (generated as the first sub-step of Stage A, described below)
- Cell-level and macro-level LEF (abstract views)
- Technology LEF (`.tlef`)
- Liberty timing views (`.lib`) for device recognition cross-reference
- Gate-level, post-P&R Verilog netlist
- SPEF (parasitics, used only for cross-referential sanity, not for DRC/LVS itself)
- Prior-phase timing, IR, and EM reports (used for manifest lineage, not re-analyzed)
- PDK distribution (complete, version-pinned)
- Technology DRC rule deck (Magic `.tech`, KLayout `.lydrc`)
- Technology LVS rule deck (Netgen `.lvs`, KLayout `.lylvs`)
- OpenROAD-generated outputs (routing guides, via reports, congestion maps — used for annotation only)
- Phase 14.12 manifest, including all prior hashes
- Configuration snapshots (tool versions, environment lockfile, random seeds where applicable)

## 1.5 Outputs

- A hash-sealed, verified GDSII stream (identical bytes to the input GDSII if verification passes; the GDSII is never modified as part of verification — verification is read-only with respect to the layout database)
- DRC violation report (structured, layer-by-layer, rule-by-rule)
- LVS comparison report (net binding, device binding, mismatch list)
- Antenna violation report (net-by-net ratio table)
- Machine-readable JSON/CSV/XML exports of all three report classes
- Violation heatmaps and violation-density maps (visualization artifacts)
- Updated manifest (Phase 14.13 section appended, not overwritten)
- Updated configuration snapshot
- Updated failure ledger (if any recoverable failures occurred during the run)

## 1.6 Dependencies

Phase 14.13 has a hard dependency on the successful, hash-verified completion of Phase 14.12. It additionally has soft (informational, non-blocking) dependencies on the timing (Phase 14.10), IR drop, and EM (Phase 14.12) reports, which are consulted during Stage F (Error Classification) to help distinguish, for example, an antenna violation on a non-critical net from one on a timing-critical net, and to prioritize repair ordering in Stage G accordingly.

## 1.7 Runtime Expectations

Runtime for Physical Verification scales differently from every prior phase in the flow: where placement, CTS, and routing runtime scale primarily with cell count and net count, DRC and LVS runtime scale with layout *area* and *polygon count*, and are strongly affected by whether the rule deck can be evaluated hierarchically (cell-by-cell, exploiting layout reuse) or must be flattened first. For a design in the 50k–500k standard-cell range on a mature open PDK (e.g., Skywater130), full-chip flat DRC typically requires 15 minutes to 3 hours depending on core area and rule deck complexity; hierarchical DRC exploiting standard-cell and macro reuse can reduce this by 3–8×. LVS runtime is dominated by device and net extraction time, typically 10–90 minutes for the same design class, with comparison (graph-isomorphism-based net/device matching) usually contributing under 10% of total LVS wall-clock time except in pathological cases involving large symmetric structures (e.g., memory arrays, PLLs) where the isomorphism search can dominate. Antenna checking is comparatively cheap, typically 2–15 minutes, since it is a per-net area-ratio computation rather than a geometric or graph-matching problem.

## 1.8 Memory Expectations

Flat DRC and LVS on full-chip layouts are the most memory-intensive operations in the entire flow to this point, frequently exceeding the peak memory usage of global and detailed routing. Magic and KLayout's polygon databases held in memory for a flattened, full-reticle design can reach 8–32 GB for designs in the multi-million-instance range; Netgen's netlist comparison graphs are typically far lighter (under 4 GB even for million-device designs) since they operate on the extracted device/net graph rather than raw polygon data. The automation harness (Part 13) is required to query available system memory before selecting flat-versus-hierarchical execution mode and to fail fast, with a clear diagnostic, rather than allow an out-of-memory condition to silently truncate a verification run.

## 1.9 Failure Conditions

A Physical Verification run is considered to have failed — as distinct from having found violations, which is a *result*, not a *failure* — under any of the following conditions: rule deck hash mismatch against the manifest-pinned version; GDSII streamout failure or corruption; LVS extraction crash (device or net extractor terminates abnormally); DRC engine crash or timeout without producing a complete report; manifest hash mismatch on any consumed input; or configuration snapshot mismatch indicating the verification environment has drifted from the environment used in Phase 14.12. These are distinguished sharply, throughout this document and in the failure ledger schema (Part 12), from *violation conditions*, in which the tools ran to completion and correctly reported that the design contains DRC errors, LVS mismatches, or antenna violations. Violation conditions are expected, common, and are the entire reason this phase exists; failure conditions are infrastructure or environment faults that invalidate the run and must trigger the retry/resume policy of Part 12/13 rather than being interpreted as design defects.

## 1.10 Validation Philosophy

Consistent with Phases 14.6–14.12, this phase adopts a strict **zero-trust-in-the-previous-stage** validation posture: no report, hash, or intermediate artifact produced by any earlier phase is taken on faith. Every input is re-hashed and compared against the manifest at Stage A before any downstream computation proceeds. In addition, this phase introduces a **dual-tool cross-validation** requirement not previously mandatory in earlier phases: because DRC and LVS results are tapeout-blocking and effectively irreversible once a mask is committed, both DRC and LVS are run through two independently implemented engines (Magic + KLayout for DRC; Netgen + KLayout for LVS), and a design is only considered clean if *both* engines agree. Any divergence between the two engines' results — for example, one engine reporting a rule as clean and the other reporting a violation — is treated as a Stage F escalation requiring manual engineering review, and is never silently resolved by preferring one tool's output over the other's.

## 1.11 Industrial Notes

In industrial ASIC and full-custom flows, this stage is typically executed using commercial signoff-grade tools (e.g., Calibre DRC/LVS/xACT for antenna, or Synopsys IC Validator), which maintain foundry-certified accuracy guarantees that open-source tools like Magic, Netgen, and KLayout do not carry with the same level of formal foundry certification. This flow's use of open-source verification tooling is appropriate and standard practice for the open PDK ecosystem (Skywater130, GlobalFoundries 180MCU, IHP SG13G2) this research targets, where the PDK-provided rule decks are themselves authored for and validated against these specific open-source tools. When this methodology is adapted to a commercial, closed PDK, the rule decks referenced throughout this document should be understood as being replaced by the foundry's certified Calibre or IC Validator decks, and the dual-tool cross-validation requirement of Section 1.10 should be replaced with cross-validation between the signoff tool and a foundry-approved secondary tool where one is available, or relaxed to single-tool signoff where the foundry's certification is itself the industry-accepted ground truth.

## 1.12 Reviewer Expectations

A reviewer evaluating this phase for IEEE ICM, TCAD, TVLSI, DAC, ICCAD, or DATE submission is expected to scrutinize four properties in particular: (1) whether the rule deck used is explicitly versioned and hash-pinned, since DRC/LVS results are meaningless without a fixed rule-deck version; (2) whether the dual-tool cross-validation methodology is actually exercised in the reported results, or merely described; (3) whether the reported violation counts are broken down by severity and by whether they were subsequently repaired, since an aggregate "zero violations at tapeout" claim without an intermediate violation history is a weaker reproducibility claim than a documented violation-discovery-and-repair trajectory; and (4) whether antenna violations are analyzed with technology-specific antenna ratio thresholds rather than generic placeholder values, since antenna rules are among the most technology-node-specific rules in any PDK.

## 1.13 Future Scalability

The architecture defined here is designed to scale along three axes without structural modification: (1) **process node scalability** — the stage pipeline (Part 5) and manifest schema are technology-agnostic, with all node-specific behavior isolated to the rule deck and PDK configuration layer, such that porting to a new open or commercial PDK requires only a configuration change, never a pipeline code change; (2) **hierarchy scalability** — the pipeline supports both flat and hierarchical DRC/LVS execution modes selectable per-run, allowing the same codebase to scale from small test chips to full-reticle multi-project wafer designs; and (3) **dataset scalability** — every violation, at every stage, is emitted in a schema-stable structured format specifically designed for accumulation across many tapeouts into a training corpus for the downstream ML models this overall research program is building (Phase 15 and beyond), a design decision elaborated further in Part 10.

---

# PART 2 — OBJECTIVES

## Objective 1 — Technology Independence

**Definition.** The Physical Verification pipeline must produce correct, consistent results across any PDK expressed in the supported rule-deck formats (Magic `.tech`, KLayout `.lydrc`/`.lylvs`, Netgen `.lvs`), without requiring modification to pipeline code.

**Engineering Rationale.** DRC and LVS logic is inherently technology-specific at the rule level but technology-agnostic at the algorithmic level (spacing checks, area checks, connectivity extraction are the same *kind* of operation regardless of node). Encoding this separation cleanly is what allows the same verification harness to be validated once and reused indefinitely across PDK ports.

**Validation.** The pipeline is run, unmodified except for configuration, against at least two distinct open PDKs (e.g., Skywater130 and GlobalFoundries 180MCU) and produces schema-identical report structures for both.

**Industrial Notes.** Commercial signoff flows achieve this same property via Calibre's SVRF or ICV's rule-deck abstraction; this flow's configuration-driven rule-deck binding is the open-source analog.

## Objective 2 — Determinism

**Definition.** Given identical inputs (layout, rule deck, tool versions), the pipeline must produce byte-identical or semantically identical violation reports on every re-run.

**Engineering Rationale.** Non-determinism in a tapeout-blocking gate is unacceptable: if a re-run of an identical design under identical conditions can produce a different violation count, no downstream decision (including ML training on violation datasets) can be trusted.

**Validation.** Triplicate re-runs of the identical input set are diffed at the JSON report level; any non-whitespace, non-timestamp diff is treated as a determinism failure requiring root-cause investigation.

**Industrial Notes.** Determinism failures in industrial DRC most often trace to unpinned threading in multi-threaded rule evaluation engines producing order-dependent floating-point rounding on area/perimeter computations; this pipeline pins thread counts and evaluation order wherever the underlying tool exposes a control for doing so.

## Objective 3 — Reproducibility

**Definition.** Any third party, given the manifest, configuration snapshot, and PDK version referenced therein, must be able to regenerate identical Physical Verification results independent of the original execution environment (subject only to tool-version pinning).

**Engineering Rationale.** This is the IEEE Artifact Evaluation bar; without it, the phase's results are not scientifically defensible as reproducible research artifacts.

**Validation.** A clean-room re-execution (fresh container, no cached intermediate state) from the manifest reproduces all reported violation counts exactly.

**Industrial Notes.** Industrial signoff similarly ties results to a locked EDA tool version and rule-deck revision, typically enforced through internal license-server version pinning rather than open manifest files.

## Objective 4 — Complete DRC Compliance

**Definition.** Zero unresolved DRC violations of any severity at the point of Stage J final validation.

**Engineering Rationale.** As established in Section 1.3, DRC violations map to concrete manufacturing defect mechanisms; "complete" compliance, not "acceptable" compliance, is the only sign-off-grade bar.

**Validation.** Stage J re-runs the full DRC deck after any repair cycle and requires a report with zero entries across all rule categories.

**Industrial Notes.** Some industrial flows tolerate a small number of explicitly waived violations (e.g., known false positives against dummy fill) via a formal waiver mechanism; this flow supports an equivalent waiver ledger, described in Part 12, but treats waivers as exceptional, auditable, and individually justified rather than default practice.

## Objective 5 — Complete LVS Equivalence

**Definition.** Full net-for-net and device-for-device topological equivalence between the extracted layout netlist and the schematic (post-P&R gate-level) netlist, including power and ground connectivity.

**Engineering Rationale.** LVS equivalence is the only guarantee that the fabricated chip will implement the intended logic function; a design can be perfectly DRC-clean and still be functionally dead if LVS fails.

**Validation.** Netgen and KLayout LVS comparisons both report "MATCH" (zero net mismatches, zero device mismatches, zero pin mismatches) as a precondition for Stage J pass.

**Industrial Notes.** Power/ground LVS is frequently under-emphasized in academic flows relative to signal-net LVS; this pipeline explicitly elevates PG-network LVS to first-class status given its outsized impact on catastrophic (rather than merely functional) failure modes.

## Objective 6 — Zero Antenna Violations

**Definition.** No net in the design may exceed the technology-specific antenna ratio threshold for any routing or polysilicon layer without either a qualifying protection structure (diode, jumper) or an explicit, ratio-computed exemption.

**Engineering Rationale.** As discussed in Section 1.3, antenna violations are a fabrication-time gate-oxide reliability hazard invisible to all earlier-stage electrical analysis.

**Validation.** Antenna ratio computed per net, per layer, cross-checked against the technology antenna rule table; any net exceeding threshold without a qualifying protection structure is flagged.

**Industrial Notes.** Antenna repair strategy (diode insertion vs. jumper insertion vs. router-driven net splitting) is technology- and even foundry-line-specific; this flow's repair stage (Stage G) implements both strategies and selects based on rule-deck-declared preference.

## Objective 7 — Manufacturing Compliance

**Definition.** The final GDSII stream must be directly acceptable for tapeout submission without requiring any foundry-side manual correction.

**Engineering Rationale.** This is the ultimate practical objective of the entire phase; all preceding objectives are decomposed sub-goals of this single outcome.

**Validation.** Successful completion of all DRC, LVS, and antenna checks under Objectives 4–6, combined with a successful GDSII streamout validation (Stage A) and merge-conflict-free layer mapping (Part 4).

**Industrial Notes.** Foundries frequently run their own confirmatory DRC/LVS pass on submitted GDSII even after a designer's own signoff; this flow's manifest and hash-pinning are designed to make any foundry-side discrepancy immediately traceable to either a rule-deck-version mismatch or a genuine tool-behavior divergence.

## Objective 8 — Rule Deck Consistency

**Definition.** The exact rule-deck version, hash, and configuration used for DRC, LVS, and antenna checking must be identical to the version referenced in the PDK manifest entry, with no local, undocumented modification.

**Engineering Rationale.** A locally patched rule deck, however well-intentioned, invalidates the sign-off guarantee the rule deck exists to provide.

**Validation.** SHA-256 hash comparison of the in-use rule deck files against the manifest-recorded hash, performed at Stage A before any check executes.

**Industrial Notes.** Industrial teams occasionally maintain "engineering change order" rule deck patches ahead of official foundry rule-deck releases; this flow requires any such patch to be captured as an explicit, hash-tracked configuration variant rather than an untracked file-level edit.

## Objective 9 — Database Integrity

**Definition.** The OpenDB, DEF, and GDSII representations of the design must be mutually consistent (identical net topology, identical cell placement, identical routing geometry) at the point Physical Verification begins.

**Engineering Rationale.** Physical Verification operates across multiple database representations (OpenDB for LVS cross-reference, GDSII for DRC and LVS layout extraction); any silent divergence between these representations would invalidate the meaning of a "pass" result.

**Validation.** Stage B (Database Integrity) performs a full cross-representation consistency check prior to any rule evaluation.

**Industrial Notes.** GDSII streamout bugs (e.g., cell array flattening errors, layer-mapping table mistakes) are a well-known source of "false" DRC/LVS failures in industrial flows; Stage B is specifically designed to catch these before they are misattributed to genuine design errors.

## Objective 10 — Artifact Reproducibility

**Definition.** Every artifact emitted by this phase (reports, visualizations, GDSII) must be regenerable byte-for-byte (or, where floating-point non-determinism in visualization rendering is unavoidable, content-for-content) from the manifest.

**Engineering Rationale.** This is the artifact-level instantiation of Objective 3, scoped specifically to phase outputs rather than the full end-to-end flow.

**Validation.** Re-running Stage I (Report Generation) from a fixed set of Stage C/D/E results reproduces identical report files.

**Industrial Notes.** Visualization artifacts (heatmaps, violation maps) are explicitly exempted from byte-identical reproducibility (due to font rendering and image-library non-determinism) but are required to be content-identical at the underlying data level.

## Objective 11 — Output Completeness

**Definition.** Every category of output enumerated in Part 11 must be present, non-empty (where non-emptiness is semantically expected), and schema-valid at the conclusion of a successful run.

**Engineering Rationale.** A partial output set silently degrades the usefulness of the phase for both human sign-off review and downstream ML dataset construction.

**Validation.** Stage J performs an output manifest completeness check against a fixed schema of expected output files and fails the run if any expected artifact is missing.

**Industrial Notes.** Analogous to industrial "deliverable checklists" used at tapeout readiness reviews, formalized here as a machine-checked gate rather than a human checklist.

## Objective 12 — Dataset Completeness

**Definition.** Every violation instance detected during the run (whether ultimately repaired or not) must be captured in the structured violation dataset with full feature annotation (location, layer, rule, severity, net, repair status).

**Engineering Rationale.** This research program's overarching goal is to train ML models to predict and mitigate manufacturing and reliability challenges; a Physical Verification phase that discards intermediate (pre-repair) violation data would materially degrade the training corpus this program depends on.

**Validation.** Violation counts logged at Stage C/D/E (pre-repair) are cross-checked against the cumulative dataset row count to ensure no violation instance is dropped during Stage G repair processing.

**Industrial Notes.** Industrial flows typically discard intermediate violation data once repaired, retaining only final signoff reports; this flow deliberately deviates from that practice for ML dataset construction purposes, a design decision explicitly called out for reviewers in Part 16.

## Objective 13 — Industrial Compatibility

**Definition.** Report formats and repository structure must be translatable, with a documented and ideally scriptable mapping, to and from industrial signoff tool formats (Calibre RVE databases, ICV result databases).

**Engineering Rationale.** Research value is substantially higher if the methodology can be validated against, or migrated to, industrial-grade tools without a ground-up reimplementation.

**Validation.** A documented format-mapping specification (Part 14/16) exists and is exercised at least once against a representative violation report.

**Industrial Notes.** Full bit-compatibility with Calibre RVE/ICV formats is explicitly out of scope; semantic (not binary) compatibility is the target.

## Objective 14 — Scalability

**Definition.** The pipeline must execute correctly, within the runtime/memory envelopes of Sections 1.7/1.8, across design sizes ranging from small test chips (under 10k instances) to large SoC-class designs (multi-million instances), using the hierarchical execution mode where flat execution would exceed resource budgets.

**Engineering Rationale.** A pipeline validated only on small test designs provides limited evidence of the flow's suitability for realistic industrial-scale tapeouts.

**Validation.** The pipeline is benchmarked across at least three design-size tiers (small/medium/large), with runtime and memory scaling curves reported in Part 10's metrics.

**Industrial Notes.** Hierarchical DRC/LVS is standard industrial practice for large designs precisely because flat verification does not scale; this flow's support for both modes mirrors that practice.

## Objective 15 — Future Extensibility

**Definition.** The stage architecture (Part 5) must accommodate the future addition of further verification checks (e.g., electrical rule checking (ERC), fill/density verification as a standalone stage, reliability-aware DRC extensions such as electromigration-aware width rules) without requiring restructuring of the existing Stage A–J pipeline.

**Engineering Rationale.** Physical Verification methodology continues to evolve (e.g., increasing adoption of machine-learning-assisted hotspot detection as a pre-DRC filtering stage); a rigid pipeline would require costly rearchitecture to absorb such advances.

**Validation.** A worked example (Part 16) demonstrates insertion of a new stage (e.g., Stage K — ML-Assisted Hotspot Pre-Screening) without modification to Stages A–J.

**Industrial Notes.** Several commercial signoff flows have, in the last product generation, added ML-based hotspot prediction as a pre-DRC accelerant; this flow's extensibility objective is explicitly informed by that industry trend.

*(Objectives 16–20, addressing Configuration Snapshot Fidelity, Manifest Backward Compatibility, Failure Ledger Auditability, Cross-Tool Report Normalization, and Waiver Governance, follow the identical definition/rationale/validation/industrial-notes structure and are elaborated in the extended appendix referenced in Part 16.)*

---

# PART 3 — INPUTS

## 3.1 Final Routed DEF

The Stage A entry point re-reads the final routed DEF produced at the close of Phase 14.12, re-verifying its hash against the manifest before any parsing occurs. The DEF is used in this phase primarily as the source of net-to-pin connectivity cross-reference for LVS pre-processing (Stage D) and as the geometric source for antenna-net identification (Stage E), since DEF retains routing-segment-level net identity that can simplify per-net antenna area accumulation relative to working from GDSII polygons alone.

**Validation.** DEF header version string checked against expected LEF/DEF version; net count and pin count cross-checked against the OpenDB-recorded values; hash checked against manifest.

**Failure Handling.** Hash mismatch is treated as a fatal Stage A failure (Part 12), aborting the run and requiring manual investigation of why the Phase 14.12 output has diverged from its recorded manifest hash — a condition that should never occur in a correctly operating pipeline and is treated as a canary for upstream tooling or storage corruption.

## 3.2 Final Routed ODB

The OpenDB database is the primary working representation for Stage B's cross-representation consistency check and for annotation of violation locations back onto a browsable database for Stage I visualization.

**Validation.** OpenDB schema version check; instance count, net count, and via count cross-checked against DEF-derived counts.

## 3.3 GDSII

GDSII is streamed out fresh at the start of Stage A from the verified OpenDB/DEF pair (rather than consumed as a pre-existing artifact from Phase 14.12, since GDSII streamout is itself considered part of Physical Verification's responsibility, not a Phase 14.12 deliverable). This design decision — generating rather than merely consuming GDSII — is deliberate: it ensures that the GDSII actually verified by DRC/LVS is guaranteed fresh and internally consistent with the DEF/ODB at verification time, eliminating an entire class of "stale GDSII" false-pass risk.

**Validation.** Streamout log checked for zero errors/warnings; layer-mapping table hash checked against the manifest-pinned technology layer map; cell count and top-level bounding box cross-checked against DEF.

## 3.4 LEF and Technology LEF

Standard-cell and macro abstract views (LEF) and the technology LEF (`.tlef`) are consumed to resolve layer stack, via definitions, and pin-shape abstractions used during Stage C rule evaluation and Stage D pin-matching.

**Validation.** LEF/DEF version compatibility check; hash comparison against manifest.

## 3.5 Liberty

Liberty (`.lib`) views are consumed by Stage D as a secondary source of expected pin directionality and cell-terminal naming, used to disambiguate device recognition in cases where the extracted layout netlist's automatically-inferred pin names do not directly match schematic pin names (a common occurrence with certain standard-cell layout styles).

## 3.6 Netlist / Verilog

The gate-level, post-P&R Verilog netlist is the schematic-side reference for LVS (Stage D). It is parsed into an internal device/net graph representation using the same graph schema as the layout-extracted netlist, enabling direct graph-isomorphism-based comparison in Netgen and KLayout.

**Validation.** Netlist parse-clean check (zero syntax errors); module hierarchy cross-checked against DEF-declared top module and macro instances; hash comparison against manifest.

## 3.7 SPEF

Parasitics are not used for any DRC/LVS/antenna computation directly but are retained in the Stage A input set purely for manifest lineage completeness and for optional cross-referential sanity checks (e.g., verifying that every net present in the SPEF is also present in both the layout-extracted and schematic netlists, catching certain classes of extraction-tool net-naming bugs early).

## 3.8 Timing / IR / EM Reports

Phase 14.10 (timing) and Phase 14.12 (IR/EM) reports are consumed read-only by Stage F (Error Classification) solely to annotate violation severity/priority; they are never used to gate or suppress any DRC/LVS/antenna check itself.

## 3.9 PDK

The complete, version-pinned PDK distribution is required in full (not merely the rule-deck subset) because LVS device recognition requires access to the PDK's device model definitions (transistor types, well/tap rules) in addition to the geometric rule deck.

**Validation.** PDK version manifest hash checked against Phase 14.6's originally recorded PDK binding, ensuring the same PDK version has been used consistently across the entire flow from floorplanning through Physical Verification.

## 3.10 Technology Rule Deck (Magic)

Magic `.tech` file defining layer definitions, DRC rules expressed in Magic's native rule language, and extraction rules used for Magic-based LVS netlist extraction.

## 3.11 Technology Rule Deck (KLayout)

KLayout `.lydrc` (DRC) and `.lylvs` (LVS) scripts, used as the second, independent verification engine per the dual-tool cross-validation requirement of Section 1.10.

## 3.12 Netgen Rule Deck

Netgen `.lvs` setup file defining device recognition and comparison rules used for the Magic-side LVS extraction-and-compare path.

## 3.13 OpenROAD Outputs

Routing guides, via reports, and congestion maps from Phase 14.9/14.12 are consumed read-only, used exclusively to annotate Stage I visualizations with routing-context overlays (e.g., showing whether a DRC violation coincides with a previously-flagged high-congestion region) and are never used as a source of ground truth for any check.

## 3.14 Manifest

The full Phase 14.6–14.12 manifest chain, consumed at Stage A to validate every other input's hash before use.

## 3.15 Configuration Snapshots

Tool version pins, environment lockfiles, and any random seeds (used, e.g., in KLayout's parallel rule evaluation thread scheduling where applicable) required for deterministic re-execution.

## 3.16 Hashes

SHA-256 hashes for every artifact listed above, recorded in the manifest and independently re-computed and compared at Stage A.

## 3.17 Metadata

Timestamps, tool invocation command lines, host environment descriptors (OS version, CPU architecture, available memory at time of run) captured for full provenance.

## 3.18 Tool Versions

Exact version strings (including git commit hash for tools built from source, e.g., OpenROAD, Magic, Netgen, KLayout) recorded and checked against the configuration snapshot.

## 3.19 Validation (Cross-Cutting)

All eighteen input categories above are hash-checked, schema-checked, and cross-representation-consistency-checked (Stage B) before Stage C (the first actual rule-evaluation stage) begins. No partial input set is permitted to proceed; Stage A is an all-or-nothing gate.

## 3.20 Failure Handling (Cross-Cutting)

Any input validation failure at Stage A is logged to the failure ledger with full diagnostic context (which input, which check, expected vs. actual hash/schema value) and the run is aborted before any compute-intensive rule evaluation begins, in keeping with the "fail fast, fail cheap" philosophy established in earlier phases.

---

# PART 4 — PHYSICAL VERIFICATION ENVIRONMENT

## 4.1 OpenROAD

Within Physical Verification, OpenROAD's role is limited relative to its central role in Phases 14.7–14.12: it is consulted only as the source of the final DEF/ODB and of routing-context metadata used for visualization annotation (Section 3.13). OpenROAD is not invoked to perform any DRC, LVS, or antenna computation itself in this pipeline; those responsibilities belong entirely to Magic, Netgen, and KLayout, described below.

## 4.2 OpenLane2

OpenLane2 serves as the orchestration layer binding OpenROAD's outputs to the Magic/Netgen/KLayout verification toolchain, providing the PDK-aware configuration binding (SCL selection, rule-deck path resolution) that this phase's automation harness (Part 13) wraps with the additional manifest/hash-checking, dual-tool cross-validation, and dataset-generation logic specific to this research program.

## 4.3 Magic

Magic serves as the primary DRC engine (Stage C, primary path) and as the layout-side netlist extractor for Netgen-based LVS (Stage D, primary path). Magic's native `.tech` rule-deck format and its mature, well-validated extraction engine for open PDKs (particularly Skywater130, for which Magic's rule deck is the reference implementation) make it the natural primary tool for this flow.

**Engineering Rationale.** Magic's extraction engine directly encodes device recognition (e.g., recognizing a polysilicon-over-diffusion overlap as a transistor gate) as part of its layer-interaction rules, providing a well-understood, auditable extraction methodology.

**Industrial Notes.** Magic is not a foundry-certified signoff tool for commercial tapeouts but is the de facto reference tool for open PDK verification and is explicitly endorsed as such by the Skywater130 and IHP SG13G2 PDK maintainers.

## 4.4 Netgen

Netgen performs the graph-isomorphism-based comparison between the Magic-extracted layout netlist and the schematic (Verilog-derived) netlist, implementing the primary-path LVS comparison (Stage D).

**Engineering Rationale.** Netgen's comparison algorithm is specifically designed to handle the common "acceptable difference" cases in LVS (e.g., series/parallel transistor merging, different net names representing the same electrical node) via a well-documented set of comparison directives, reducing false-mismatch noise relative to a naive netlist-diff approach.

## 4.5 KLayout

KLayout serves as the secondary, independent DRC engine (via its DRC scripting language, `.lydrc`) and secondary LVS engine (via its LVS scripting language, `.lylvs`), fulfilling the dual-tool cross-validation requirement of Section 1.10. KLayout additionally provides the visualization backend for Stage I (violation heatmaps and violation-density maps), given its mature GDSII rendering and layer-styling capabilities.

**Engineering Rationale.** KLayout's DRC/LVS engines are implemented via an entirely independent codebase from Magic/Netgen, with a different underlying polygon-processing library, making genuine independence (rather than merely nominal independence) of the dual-tool cross-validation credible.

## 4.6 OpenDB

OpenDB is consulted (read-only, via OpenROAD's Python API) at Stage B for cross-representation consistency checking against DEF and GDSII-derived data, and again in Stage I for violation-location annotation onto a browsable design database.

## 4.7 Technology Database

The unified technology database (layer stack, via stack, design rules encoded in tool-native formats) is loaded once at Stage A and held in memory for the duration of the run to avoid redundant rule-deck parsing overhead across Stages C/D/E.

## 4.8 Layer Mapping

GDSII layer-number-to-name mapping is resolved via the PDK-provided layer map file, hash-checked against the manifest at Stage A (Section 3.3), and cross-validated at Stage B by confirming that every layer present in the streamed-out GDSII resolves to a known technology layer with no "unmapped layer" warnings.

## 4.9 Coordinate Systems

All geometric data is normalized to the technology's manufacturing grid coordinate system (Section 4.10) prior to any rule evaluation; DEF-native microns are converted to database units (DBU) using the technology's declared DBU-per-micron scale factor, with rounding behavior explicitly pinned (round-half-to-even) to preserve determinism (Objective 2).

## 4.10 Manufacturing Grid

Every coordinate in the final GDSII is validated, as part of Stage C, against the technology's manufacturing grid quantum (e.g., 0.005 μm for Skywater130); any off-grid vertex is reported as a manufacturing-grid violation, a DRC violation category with its own severity classification (Part 6).

## 4.11 Rule Deck Loading

Rule decks for both engines (Magic `.tech`/Netgen `.lvs`, and KLayout `.lydrc`/`.lylvs`) are loaded once at Stage A initialization and validated for internal consistency (e.g., confirming that every layer referenced in the DRC rule deck exists in the layer mapping table) before Stage C begins.

## 4.12 Database Consistency

Stage B's cross-representation consistency check spans OpenDB, DEF, and GDSII, verifying that instance counts, net counts, and pin counts agree across all three representations to within an explicitly zero tolerance (any discrepancy is a Stage B failure, not merely a warning).

## 4.13 Engineering Rationale (Environment)

The environment architecture's guiding principle is that every tool consulted in this phase serves a single, non-overlapping responsibility: OpenROAD/OpenLane2 for database provisioning and orchestration context; Magic for primary DRC and layout extraction; Netgen for primary LVS comparison; KLayout for secondary DRC, secondary LVS, and visualization. No tool's output is used to override or "smooth over" a disagreement produced by another; disagreements are surfaced, not resolved silently.

## 4.14 Industrial Notes (Environment)

This multi-tool environment architecture mirrors, in open-source form, the common industrial practice of running signoff DRC/LVS through a primary tool (e.g., Calibre) with a secondary spot-check tool (e.g., ICV or an in-house verification utility) reserved for high-risk designs or as a qualification exercise when adopting a new PDK revision.

## 4.15 Future Scalability (Environment)

The environment's tool-abstraction layer (implemented in the automation harness, Part 13) is designed so that a third DRC/LVS engine (e.g., a future open-source or academic tool) could be added as an additional cross-validation path without modifying Stages A–J, by registering it against the same abstract "DRC engine" / "LVS engine" interface Magic/KLayout and Netgen/KLayout currently implement.

---

# PART 5 — PHYSICAL VERIFICATION ARCHITECTURE

The Physical Verification pipeline is structured as a deterministic, checkpointed ten-stage pipeline, Stage A through Stage J, consistent with the Stage-lettering convention used throughout Phases 14.6–14.12. Each stage is a discrete, independently resumable unit of work with its own manifest section, its own failure-ledger namespace, and its own explicit input/output contract with adjacent stages.

## Stage A — Initialization

**Purpose.** Establish a validated, hash-verified, freshly-streamed working database (GDSII, rule decks, netlist) from which all subsequent stages operate.

**Theory.** Initialization is the boundary at which external trust (Phase 14.12's manifest) is converted into internal trust (this phase's own re-verified working set); everything downstream of Stage A operates only on locally re-validated data.

**Engineering Rationale.** Concentrating all input validation into a single stage, rather than scattering ad hoc checks throughout the pipeline, makes the trust boundary auditable and testable in isolation.

**Inputs.** All artifacts enumerated in Part 3.

**Outputs.** Freshly streamed GDSII; loaded, validated rule decks (both engines); parsed schematic netlist graph; Stage A manifest section recording all hash checks performed and their results.

**Dependencies.** Phase 14.12 manifest.

**Runtime.** Dominated by GDSII streamout time; typically 2–20 minutes depending on design size.

**Memory.** Modest; typically under 4 GB except for very large designs where GDSII streamout itself becomes memory-intensive.

**Failure Conditions.** Any hash mismatch, schema violation, or streamout error (Section 1.9).

**Validation.** All eighteen input categories of Part 3 individually confirmed.

**Industrial Notes.** Equivalent to the "data prep" phase of a commercial signoff flow, in which GDSII, LVS netlist, and rule decks are gathered and version-locked before a Calibre run is submitted to a batch queue.

**Reviewer Expectations.** Reviewers should expect an explicit list of every hash check performed at this stage, not a generic "inputs validated" statement.

**Future Scalability.** Additional input categories (e.g., a future fourth verification tool's rule deck) can be added to Stage A's validation set without restructuring the stage.

## Stage B — Database Integrity

**Purpose.** Confirm cross-representation consistency (OpenDB, DEF, GDSII) prior to any rule evaluation.

**Theory.** A rule-evaluation result is only meaningful if all representations of the design agree; Stage B is the formal instantiation of Objective 9.

**Engineering Rationale.** Catching a representation-consistency bug here, before Stage C/D/E run, avoids the far more expensive failure mode of debugging a "false" DRC or LVS violation that turns out to be a database inconsistency rather than a genuine design defect.

**Inputs.** Stage A's validated GDSII, OpenDB, and DEF.

**Outputs.** Cross-representation consistency report; Stage B manifest section.

**Dependencies.** Stage A.

**Runtime.** Typically under 5 minutes.

**Memory.** Light; under 2 GB.

**Failure Conditions.** Any instance-count, net-count, or pin-count mismatch across representations.

**Validation.** Zero-tolerance count comparison across all three representations.

**Industrial Notes.** This check has no single standard industrial name but is functionally equivalent to the "database sanity check" step some commercial flows run as an implicit precondition inside their DRC/LVS batch scripts; this pipeline makes it explicit and independently auditable.

**Reviewer Expectations.** Reviewers should expect explicit counts reported (not merely "consistent"/"inconsistent") to allow independent verification of the check's rigor.

**Future Scalability.** Extensible to additional representations (e.g., a future LEF/DEF abstraction layer for hierarchical block reuse) without restructuring.

## Stage C — DRC Verification

**Purpose.** Execute the full design rule check, via both Magic (primary) and KLayout (secondary), across the entire rule deck.

**Theory.** Elaborated fully in Part 6.

**Engineering Rationale.** Elaborated fully in Part 6.

**Inputs.** Stage B-validated GDSII; Stage A-loaded DRC rule decks (both engines).

**Outputs.** Magic DRC report; KLayout DRC report; cross-tool agreement/divergence report; Stage C manifest section.

**Dependencies.** Stage B.

**Runtime.** Section 1.7.

**Memory.** Section 1.8.

**Failure Conditions.** Engine crash, timeout, or rule-deck load failure (as distinct from a clean report containing violations, which is a valid, non-failing result).

**Validation.** Every rule in the loaded rule deck confirmed to have been evaluated (no silently skipped rules); cross-tool divergence explicitly flagged.

**Industrial Notes.** Equivalent to a standard Calibre DRC batch run, here executed twice (Magic + KLayout) per Objective 1.10's dual-tool requirement.

**Reviewer Expectations.** Full per-rule violation counts, not merely an aggregate total, are expected in the published results.

**Future Scalability.** New rule categories (e.g., a future reliability-aware DRC extension) can be added to the rule deck without pipeline restructuring, since Stage C treats the rule deck as an opaque, fully data-driven input.

## Stage D — LVS Verification

**Purpose.** Execute layout-versus-schematic comparison via Netgen (primary) and KLayout (secondary).

**Theory.** Elaborated fully in Part 7.

**Engineering Rationale.** Elaborated fully in Part 7.

**Inputs.** Stage B-validated GDSII (for layout-side extraction); Stage A-parsed schematic netlist; Stage A-loaded LVS rule decks (both engines).

**Outputs.** Netgen LVS report; KLayout LVS report; cross-tool agreement/divergence report; Stage D manifest section.

**Dependencies.** Stage B, Stage A (netlist parsing).

**Runtime.** Section 1.7.

**Memory.** Section 1.8.

**Failure Conditions.** Extraction crash, comparison-engine crash or timeout.

**Validation.** Both engines confirmed to have completed a full comparison pass (not a partial/aborted comparison); cross-tool divergence explicitly flagged.

**Industrial Notes.** Equivalent to a standard Calibre LVS run with an RVE-equivalent mismatch database, here executed twice per the dual-tool requirement.

**Reviewer Expectations.** Full mismatch categorization (net vs. device vs. pin) expected, not an aggregate "match/no match" boolean alone.

**Future Scalability.** New device recognition rules (e.g., for a future process node introducing new transistor architectures) accommodated purely through rule-deck configuration.

## Stage E — Antenna Verification

**Purpose.** Compute per-net, per-layer antenna ratios and compare against technology-specific thresholds.

**Theory.** Elaborated fully in Part 8.

**Engineering Rationale.** Elaborated fully in Part 8.

**Inputs.** Stage B-validated GDSII/DEF; technology antenna rule table (part of the DRC rule deck).

**Outputs.** Antenna violation report (per net, per layer); Stage E manifest section.

**Dependencies.** Stage B.

**Runtime.** Section 1.7.

**Memory.** Light relative to Stage C/D.

**Failure Conditions.** Antenna rule table load failure; per-net area accumulation crash on pathological net topologies (e.g., nets with disconnected floating shapes — itself also flagged as a Stage D LVS "open" condition).

**Validation.** Every net in the design confirmed to have been evaluated for antenna ratio (no silently skipped nets).

**Industrial Notes.** Equivalent to Calibre's `xACT` or ICV's antenna-checking module.

**Reviewer Expectations.** Reviewers should expect the actual antenna ratio values reported for violating nets, not merely a pass/fail flag, to allow assessment of violation severity.

**Future Scalability.** Extensible to accommodate future antenna-rule refinements (e.g., cumulative multi-layer antenna ratio rules) via rule-deck configuration.

## Stage F — Error Classification

**Purpose.** Classify every violation from Stages C/D/E by severity, criticality (cross-referenced against timing/IR/EM reports per Section 3.8), and repair priority.

**Theory.** Not all violations carry equal manufacturing or reliability risk; classification enables rational repair-effort allocation in Stage G.

**Engineering Rationale.** A flat, unprioritized violation list is operationally unusable on any design with more than a handful of violations; classification is what converts a raw violation list into an actionable repair plan.

**Inputs.** Stage C/D/E reports; Phase 14.10/14.12 timing/IR/EM reports (read-only, informational).

**Outputs.** Classified, prioritized violation dataset; Stage F manifest section.

**Dependencies.** Stage C, D, E.

**Runtime.** Typically under 10 minutes; dominated by cross-referencing violation locations against timing-critical-path and IR/EM-critical-net lists.

**Memory.** Light.

**Failure Conditions.** Classification-rule load failure; cross-reference lookup failure (e.g., a violation net not found in the timing/IR/EM report net list, itself logged as a data-consistency warning rather than a fatal error).

**Validation.** Every violation from Stage C/D/E confirmed present in the classified dataset (Objective 12, dataset completeness).

**Industrial Notes.** Equivalent to the manual "waiver triage" meetings common in industrial tapeout readiness reviews, here formalized as a deterministic, rule-driven classification step.

**Reviewer Expectations.** The classification rule set itself (what makes a violation "critical" vs. "minor") should be explicitly documented and justified, not left implicit.

**Future Scalability.** New classification dimensions (e.g., a future ML-predicted yield-impact score) can be added as additional dataset columns without restructuring the stage.

## Stage G — Incremental Repair Validation

**Purpose.** Apply and validate repairs (antenna diode/jumper insertion, DRC-driven local re-routing, LVS-driven connectivity fixes) incrementally, re-verifying only the affected region rather than the full design, where hierarchical/incremental verification is supported.

**Theory.** Incremental verification exploits locality: a repair applied to a small region of the layout should only require re-verification of that region (plus a bounded halo) rather than a full-chip re-run, provided the verification engine supports region-scoped rule evaluation.

**Engineering Rationale.** Full-chip re-verification after every individual repair would make iterative violation cleanup computationally prohibitive on large designs; incremental verification is what makes iterative cleanup tractable at scale.

**Inputs.** Stage F's classified violation dataset; repair-candidate generation logic (diode/jumper library cells, local re-route directives).

**Outputs.** Repaired GDSII/DEF/ODB; incremental re-verification report per repair; Stage G manifest section.

**Dependencies.** Stage F.

**Runtime.** Highly variable, dependent on violation count and repair complexity; typically 1–5 minutes per repair cycle for region-scoped re-verification.

**Memory.** Bounded by the region-scoped verification window, typically much lighter than full-chip Stage C/D/E memory usage.

**Failure Conditions.** Repair application failure (e.g., insufficient free space for diode insertion); incremental re-verification engine crash.

**Validation.** Every applied repair confirmed, via region-scoped re-verification, to have resolved its target violation without introducing a new violation in the affected halo region.

**Industrial Notes.** Equivalent to the "ECO (Engineering Change Order) DRC/LVS" flows common in industrial back-end sign-off, in which small late-stage layout modifications are verified incrementally rather than via full-chip re-run.

**Reviewer Expectations.** The incremental verification methodology's soundness (i.e., that a repair validated only in a local region cannot have introduced an undetected violation outside the halo) should be explicitly justified, typically via a halo-sizing argument tied to the rule deck's maximum interaction distance.

**Future Scalability.** The halo-sizing logic and repair-candidate library are both configuration-driven, allowing new repair strategies or larger/smaller halo policies to be introduced without pipeline restructuring.

## Stage H — QoR Extraction

**Purpose.** Extract quality-of-results metrics (Part 10) from the full violation history (pre- and post-repair) for both human sign-off review and ML dataset construction.

**Theory.** QoR extraction is the bridge between raw verification output and the structured, schema-stable dataset this research program's downstream ML phases depend on.

**Engineering Rationale.** Concentrating metric extraction into a single, dedicated stage (rather than computing metrics ad hoc within Stage C/D/E/F/G) ensures a single, auditable, versioned metric-computation code path.

**Inputs.** Full Stage C through G history.

**Outputs.** QoR metrics dataset (Part 10); Stage H manifest section.

**Dependencies.** Stage C, D, E, F, G.

**Runtime.** Typically under 5 minutes.

**Memory.** Light.

**Failure Conditions.** Metric computation crash on malformed intermediate data (itself indicative of an upstream stage bug, escalated accordingly).

**Validation.** Every metric in Part 10's 25+-metric taxonomy confirmed present in the output dataset.

**Industrial Notes.** Analogous to the "QoR report" generation step in commercial signoff flows, extended here with explicit ML-feature-relevance annotation per metric.

**Reviewer Expectations.** Reviewers should expect the full metric taxonomy (Part 10) to be populated with actual measured values in the reported results, not a subset.

**Future Scalability.** New metrics can be appended to the schema (with a version bump) without breaking backward compatibility with previously generated datasets.

## Stage I — Report Generation

**Purpose.** Produce all human-readable and machine-readable output artifacts (Part 11), including violation heatmaps and violation-density maps.

**Theory.** Report generation is a pure, side-effect-free transformation of Stage H's dataset into the various output formats and visualizations required by Part 11.

**Engineering Rationale.** Isolating report generation as a distinct, dataset-driven stage (rather than generating reports piecemeal within earlier stages) guarantees that all report formats are generated from a single, internally consistent source of truth.

**Inputs.** Stage H's QoR dataset; Stage C/D/E raw reports (for detailed drill-down content).

**Outputs.** All Part 11 output artifacts.

**Dependencies.** Stage H.

**Runtime.** Typically 2–10 minutes, dominated by heatmap rendering for large designs.

**Memory.** Moderate, dominated by KLayout's rendering engine for large-design heatmap generation.

**Failure Conditions.** Rendering engine crash; output-schema validation failure.

**Validation.** Every output artifact schema-validated against its declared format specification before being written to the reports directory.

**Industrial Notes.** Equivalent to Calibre RVE report export or ICV's result-database export functionality.

**Reviewer Expectations.** Visualization artifacts should be checked for correct violation-location-to-layout correspondence (i.e., a spot check that a heatmap "hot" region actually corresponds to a real reported violation cluster).

**Future Scalability.** New output formats (e.g., a future GDS-II-embedded annotation layer for violations) can be added as additional export targets without restructuring the stage.

## Stage J — Final Validation

**Purpose.** Perform the terminal, all-or-nothing sign-off gate: confirm zero unresolved critical violations across DRC, LVS, and antenna domains, confirm output completeness (Objective 11), and seal the phase's manifest section.

**Theory.** Stage J is the formal instantiation of the "tapeout readiness" decision; it is the single point in the pipeline where a binary pass/fail sign-off determination is made.

**Engineering Rationale.** Concentrating the sign-off decision into a single, explicit, auditable final stage (rather than an implicit "if no earlier stage crashed, we're done" assumption) makes the sign-off criterion itself a first-class, reviewable artifact.

**Inputs.** Stage G's final (post-repair) violation state; Stage I's output artifact set.

**Outputs.** Final Stage J sign-off record (pass/fail with full justification); sealed Phase 14.13 manifest section.

**Dependencies.** All prior stages (A–I).

**Runtime.** Under 2 minutes.

**Memory.** Light.

**Failure Conditions.** Any unresolved critical violation in DRC, LVS, or antenna domains (Objective 4/5/6); any missing required output artifact (Objective 11).

**Validation.** Explicit re-check of zero-violation state (not merely trusting Stage G's self-reported repair success); explicit re-check of output completeness.

**Industrial Notes.** Equivalent to the final "tapeout readiness review" gate in industrial practice, here made fully automated and machine-checkable rather than a manual sign-off meeting.

**Reviewer Expectations.** The Stage J pass/fail record and its full justification (violation counts by domain, output completeness checklist) should be included verbatim or near-verbatim in any publication reporting this phase's results.

**Future Scalability.** Additional sign-off criteria (e.g., a future ML-predicted-yield threshold) can be added to Stage J's gating logic as additional, independently toggleable checks.

---

# PART 6 — DESIGN RULE CHECK (DRC)

## 6.1 Minimum Width

Minimum width rules specify the smallest permissible dimension of a drawn shape on a given layer in the direction perpendicular to its length, reflecting the smallest feature the lithography and etch process can reliably resolve on that layer. A width violation indicates a shape narrower than this threshold, which risks incomplete pattern transfer during etch, resulting in an open circuit or a resistance far higher than the design intended.

**Engineering Rationale.** Width rules are typically the most conservative (least node-dependent variability) of all DRC categories because they map almost directly onto the resolution limit of the lithography tool used for that layer; violations here carry a near-certain manufacturing failure risk rather than a probabilistic yield-reduction risk.

**Industrial Notes.** Minimum width rules frequently differ between "normal" and "wide" metal definitions on the same layer (with different subsequent density or antenna rule implications), a distinction this pipeline's rule-deck parser preserves explicitly rather than collapsing into a single width threshold per layer.

## 6.2 Minimum Spacing

Minimum spacing rules specify the smallest permissible gap between two shapes on the same layer (or, for some rule categories, between shapes on different but interacting layers), reflecting the smallest gap the lithography/etch process can reliably resolve without bridging.

**Engineering Rationale.** As discussed in Section 1.3, spacing violations map directly onto bridging-defect risk; unlike width violations (which primarily risk opens), spacing violations primarily risk shorts, a failure mode that is often harder to detect in downstream electrical test since a marginal short may only manifest under specific voltage/temperature conditions.

**Industrial Notes.** Spacing rules are frequently density- or context-dependent (e.g., tighter spacing permitted in low-density regions, looser spacing required in high-density regions to control etch loading effects); this pipeline's rule-deck parser must correctly resolve context-dependent spacing rules rather than applying a single flat spacing threshold.

## 6.3 Minimum Area

Minimum area rules specify the smallest permissible total area of an isolated shape on a given layer, addressing the observation that very small isolated shapes can be etched away entirely or can lift off during chemical-mechanical polishing (CMP), even if their width and spacing individually satisfy the corresponding rules.

**Engineering Rationale.** Area violations most commonly arise from small via-adjacent metal fragments or from filler/tie-cell remnants left over from placement optimization; this pipeline's Stage C explicitly cross-references area violations against the placement database (via the DEF consumed in Stage A) to help distinguish "genuine design defect" area violations from "leftover filler artifact" area violations during Stage F classification.

## 6.4 Minimum Enclosure

Minimum enclosure rules specify the smallest permissible margin by which one layer's shape must surround an overlapping shape on another layer (most commonly, the margin by which a metal layer must surround an underlying via), addressing alignment tolerance in the lithography stack between layers.

**Engineering Rationale.** Enclosure violations reflect a risk that layer-to-layer misalignment during fabrication (an inherent, statistically distributed process variation) could result in a via not being fully landed on its intended metal shape, producing a high-resistance or open via contact.

## 6.5 Minimum Extension

Minimum extension rules specify the smallest permissible distance by which a shape on one layer must extend beyond the edge of an interacting shape on another layer (e.g., polysilicon extension beyond a diffusion edge, ensuring the transistor gate fully spans the active region with adequate margin for alignment tolerance).

**Engineering Rationale.** Extension violations most directly threaten transistor-level functionality (an under-extended gate can result in a transistor with an effectively shorter or malformed channel than the schematic-level device model assumes), making this rule category one of the few DRC categories with a direct, first-order impact on device electrical behavior rather than purely on interconnect manufacturability.

## 6.6 Via Rules

Via rules encompass minimum via size, minimum via spacing (both via-to-via and via-to-adjacent-shape), and via enclosure (Section 6.4) as a coherent sub-category, reflecting the unique manufacturing sensitivity of vias as the layers with the smallest, most alignment-sensitive features in the entire metal stack.

**Engineering Rationale.** Via-related violations are disproportionately represented in industrial yield-loss data relative to their proportion of total layout area, motivating this pipeline's explicit sub-classification of via violations as a distinct severity tier within the DRC violation taxonomy (Part 10) rather than folding them into generic width/spacing/enclosure categories.

## 6.7 Cut Rules

Cut rules govern the geometry of the via "cut" shape itself (as distinct from the surrounding metal enclosure), including minimum cut size, cut spacing, and cut array rules governing multi-cut via arrays used to reduce via resistance and improve electromigration robustness.

**Engineering Rationale.** Cut array rules interact directly with the EM analysis performed in Phase 14.12; a cut-array violation discovered here that forces a reduction in via-array redundancy can, in principle, feed back into an EM margin re-check, a cross-phase interaction this pipeline flags (via Stage F's cross-referencing against Phase 14.12 EM reports) rather than silently ignoring.

## 6.8 Density Rules

Density rules specify minimum and maximum permissible fill density of a given layer within a specified window (a sliding-window density computation across the layout), addressing chemical-mechanical polishing (CMP) planarity requirements: regions of insufficient density risk dishing during CMP, while regions of excessive density risk erosion.

**Engineering Rationale.** Density violations are commonly resolved via automated filler-cell or metal-fill insertion rather than via functional design changes, making this rule category's repair strategy (Stage G) distinct from most other DRC categories in that it typically does not require any change to functional connectivity.

**Industrial Notes.** Density-driven fill insertion, if performed carelessly, can itself introduce new antenna violations (Part 8) by creating large isolated fill shapes connected, however incidentally, to signal nets; this pipeline's fill-insertion repair logic in Stage G explicitly re-checks antenna impact of any inserted fill.

## 6.9 Parallel Run Length

Parallel run length rules specify spacing requirements that become progressively tighter or looser as a function of how far two parallel-running shapes extend alongside one another, reflecting the observation that longer parallel runs accumulate greater capacitive coupling risk and greater cumulative lithographic interaction than short parallel runs at the same nominal spacing.

**Engineering Rationale.** Parallel-run-length-dependent spacing rules are among the more algorithmically complex DRC checks to implement correctly, since they require the rule engine to track cumulative parallel overlap length rather than evaluating spacing at isolated points; this pipeline relies on Magic's and KLayout's native, independently implemented parallel-run-length rule evaluation engines specifically because a custom re-implementation would risk subtle correctness bugs in this particularly intricate rule category.

## 6.10 End-of-Line Rules

End-of-line (EOL) spacing rules specify a distinct (typically tighter) spacing requirement specifically at the terminating end of a shape, reflecting the distinct lithographic behavior (line-end shortening, corner rounding) at shape endpoints relative to the sidewall behavior parallel-run-length rules address.

## 6.11 Notch Rules

Notch rules specify minimum permissible width of a concave ("notch") indentation into a shape, addressing the risk that very narrow notches can print incorrectly (either filling in entirely, effectively merging what was meant to be two separate features, or over-etching and creating an unintended gap).

## 6.12 Cell Boundary Rules

Cell boundary rules govern the geometric relationship between a standard cell's internal shapes and its cell-boundary abstraction (LEF), ensuring that cell abutment during placement does not, by construction, create a downstream spacing or enclosure violation at the cell-to-cell boundary.

**Engineering Rationale.** Cell boundary rule violations are a strong signal of either a standard-cell library authoring defect or, more commonly in this flow's context, a placement-legalization bug that has permitted an illegal cell overlap or an insufficient cell-to-cell gap; Stage F classification cross-references any cell boundary violation against the Phase 14.7 (placement) legalization report to help triage root cause.

## 6.13 Power Rail Rules

Power rail rules govern minimum width, spacing, and via requirements specific to the power distribution network (PDN) rails, typically differing from generic signal-metal rules due to the substantially higher current density power rails are expected to carry.

**Engineering Rationale.** Power rail DRC violations carry compounded risk beyond ordinary DRC violations, since a power-rail manufacturing defect can propagate into an IR-drop or EM failure across the entire fan-out of the affected rail segment, making this rule category one where Stage F classification automatically assigns maximum severity regardless of the raw geometric violation magnitude.

## 6.14 Routing Layer Rules

Routing layer rules encompass the full complement of width/spacing/via/density rules described above, applied per-layer across the full metal stack, with each layer typically carrying its own distinct rule table reflecting that layer's specific lithographic and process characteristics (lower metal layers typically carry the tightest rules; upper, thicker metal layers typically carry looser geometric rules but tighter current-density-driven width rules).

## 6.15 Macro Rules

Macro rules govern the DRC relationship between hard macro boundaries (memory arrays, analog IP, PLLs) and the surrounding standard-cell fabric, including macro-to-macro spacing, macro halo/keepout rules, and macro-boundary pin-access rules.

**Engineering Rationale.** Macro rule violations are frequently a symptom of a floorplanning-stage (Phase 14.6/14.7) keepout-region configuration error rather than a routing-stage defect; Stage F classification cross-references macro rule violations against the Phase 14.6 floorplan manifest to aid root-cause attribution.

## 6.16 Manufacturing Grid

As introduced in Section 4.10, manufacturing grid violations occur when any layout vertex falls off the technology's declared manufacturing grid quantum; while conceptually simple, this rule category is disproportionately valuable as an early diagnostic since a widespread manufacturing-grid violation pattern is a strong signal of a systemic tool-configuration bug (e.g., an incorrect DBU-per-micron scale factor) rather than isolated genuine design defects, and is treated by this pipeline as a Stage B-adjacent sanity check performed early in Stage C specifically to catch such systemic issues before the bulk of rule evaluation proceeds.

## 6.17 Hierarchical DRC

Hierarchical DRC exploits layout reuse (identical standard-cell instances, identical macro instances) by verifying each distinct cell/macro definition exactly once and applying an incremental, boundary-only check at each instantiation site, rather than re-verifying every polygon at every instance.

**Engineering Rationale.** For designs with substantial cell reuse (essentially all standard-cell-based designs), hierarchical DRC provides substantial runtime and memory savings (Objective 14) at the cost of additional implementation complexity in correctly handling boundary-interaction rules (parallel run length, EOL) that can span a hierarchy boundary.

## 6.18 Incremental DRC

Incremental DRC, distinct from hierarchical DRC, re-verifies only a specified region of the layout (typically following a Stage G repair) rather than either the full flat layout or the full cell/macro-definition hierarchy, and is the verification mode used within Stage G's incremental repair validation loop.

## 6.19 Flat DRC

Flat DRC verifies every polygon in the fully-flattened layout without exploiting any reuse structure, providing the most conservative, unambiguous verification mode at the cost of the highest runtime and memory usage (Section 1.7/1.8), and is the mode used for the final Stage J sign-off check specifically because its lack of any reuse-exploiting assumption provides the strongest possible correctness guarantee for the terminal gate.

**Engineering Rationale.** This pipeline's policy of using hierarchical or incremental DRC for iterative Stage C/G work but mandating a final flat DRC pass at Stage J reflects a deliberate trade-off: exploit reuse structure for iteration speed, but never allow the final sign-off determination to depend on an assumption (correct hierarchy boundary handling) that, however well-tested, is strictly weaker than full flat verification.

**Industrial Notes.** This hierarchical-for-iteration, flat-for-final-signoff policy directly mirrors standard industrial signoff practice, in which hierarchical DRC is used throughout the design cycle for turnaround-time reasons but a final flat "clean" run is mandatory before tapeout submission.

---

# PART 7 — LAYOUT VS SCHEMATIC (LVS)

## 7.1 Theory

LVS theory rests on representing both the layout (as extracted from GDSII polygons) and the schematic (as parsed from the gate-level Verilog netlist) as directed graphs whose nodes are devices (transistors, and for this flow, standard-cell instances treated as black-box devices at the appropriate hierarchy level) and whose edges are nets connecting device terminals. LVS comparison is then, at its core, a graph-isomorphism problem: determine whether the layout graph and the schematic graph are isomorphic, accounting for well-understood equivalence transformations (series/parallel device merging, net-name-invariant comparison) that do not represent genuine electrical differences.

## 7.2 Connectivity Checking

Connectivity checking verifies that every net's constituent shapes (across all layers and vias that electrically connect them) form a single, electrically continuous region in the layout-extracted graph, distinguishing genuinely connected nets from nets that merely appear adjacent in the geometric sense without an actual electrical connection (e.g., two metal shapes on the same layer that are geometrically close but not touching, versus two metal shapes on different layers connected through a via).

## 7.3 Net Equivalence

Net equivalence determines whether a given layout-extracted net corresponds, under the graph-isomorphism mapping, to a specific schematic net, independent of naming (since layout-extracted nets frequently lack the human-readable names present in the schematic netlist, particularly for nets not brought out to any top-level or macro-boundary pin).

**Engineering Rationale.** Net equivalence checking, rather than a naive name-based comparison, is what makes LVS robust to the inevitable loss of net-naming information that occurs during synthesis, placement, and routing, none of which are obligated to preserve human-readable net names for purely internal nets.

## 7.4 Device Equivalence

Device equivalence determines whether a layout-extracted device (transistor or cell instance) corresponds to a specific schematic device, verifying not only topological correspondence (same terminal connectivity pattern) but also device-parameter correspondence (transistor width/length, or for cell-level LVS, cell type identity) where the rule deck specifies parameter-sensitive comparison.

## 7.5 Pin Matching

Pin matching verifies that each schematic-declared top-level (or macro-boundary) pin corresponds to exactly one layout-extracted pin at the geometrically and electrically correct location, catching a specific and historically common class of P&R tool bug in which a pin is placed correctly but bound to the wrong net, or bound correctly but placed on the wrong layer/location relative to the LEF abstract view's declared pin shape.

## 7.6 Power Network Verification

Power network verification specifically isolates the VDD-connected net set and verifies its full connectivity and correct binding to every power-consuming device's power terminal, treated by this pipeline as a distinct, first-class LVS sub-check (per Objective 5's explicit elevation of PG-network LVS) rather than folded indiscriminately into generic signal-net LVS.

**Engineering Rationale.** A power network connectivity defect (e.g., a macro instance whose power pin is inadvertently left floating due to a P&R abutment error) can result in catastrophic, whole-macro non-functionality that is qualitatively different from, and typically more severe than, an ordinary signal-net LVS mismatch, justifying its distinct treatment.

## 7.7 Ground Verification

Ground (VSS) network verification mirrors Section 7.6's power network verification methodology, applied to the ground net set, with equivalent severity classification in Stage F.

## 7.8 Short Detection

Short detection identifies layout regions where two schematically-distinct nets are found to be electrically connected in the extracted layout graph (i.e., the layout-extracted netlist has merged two nets the schematic keeps distinct), typically arising from a DRC-adjacent spacing violation (Section 6.2) that has actually resulted in unintended electrical bridging, or from a genuine P&R tool routing bug.

**Engineering Rationale.** This pipeline's Stage F explicitly cross-references every LVS short against the corresponding Stage C DRC spacing-violation report at the same physical location, since a large fraction of genuine (as opposed to tool-artifact) LVS shorts are directly explained by, and physically co-located with, a DRC spacing violation.

## 7.9 Open Detection

Open detection identifies layout regions where a single schematic net has been extracted, in the layout graph, as two or more electrically disconnected fragments, typically arising from a routing completion failure (an unrouted or partially-routed net that should have triggered a Phase 14.9 routing-completion failure, but is re-verified independently here as a defense-in-depth check) or from a via/contact enclosure violation severe enough to have actually resulted in electrical discontinuity rather than merely a manufacturing-margin risk.

## 7.10 Hierarchy Preservation

Hierarchy preservation refers to LVS's ability to perform comparison at a specified level of the design hierarchy (e.g., comparing macro-internal netlists against macro-internal schematics independently of the top-level netlist comparison) rather than requiring the entire design to be flattened for comparison, mirroring the hierarchical DRC benefits of Section 6.17 for LVS runtime and memory (Objective 14).

## 7.11 Black-Box Handling

Black-box handling refers to LVS's treatment of hard macros (memory arrays, analog IP, PLLs) whose internal layout is not verified as part of this phase's LVS pass (having presumably been separately signed off at the macro's own point of origin) but whose boundary-pin connectivity to the surrounding design must still be verified.

**Engineering Rationale.** Black-box LVS handling is what allows this pipeline to scale to designs incorporating third-party or previously-signed-off hard macros without requiring redundant re-verification of macro-internal layout on every top-level tapeout, a critical practical requirement for any realistic SoC-class design.

## 7.12 Parasitic Consistency

Parasitic consistency, while not a primary LVS function, is checked as a secondary Stage D validation: every net present in the SPEF (Section 3.7) is confirmed to correspond to exactly one net in both the layout-extracted and schematic netlist graphs, catching a specific class of extraction-tool net-naming inconsistency that could otherwise silently propagate incorrect parasitics into the Phase 14.10/14.12 timing and reliability analyses without ever being flagged as an LVS mismatch per se.

## 7.13 Engineering Rationale (LVS, Overall)

The overall engineering rationale for this pipeline's LVS methodology is that LVS is treated not merely as a binary "pass/fail" gate but as a rich, structured diagnostic output: every mismatch category (net, device, pin, power, ground, short, open) is independently tracked, classified, and fed into both the human-readable Stage I report and the machine-readable Stage H/Part-10 QoR dataset, reflecting this research program's broader objective of building a comprehensive violation dataset for downstream ML training (Objective 12) rather than a minimal pass/fail signoff record.

## 7.14 Validation (LVS, Overall)

Full LVS validation requires zero mismatches across every category enumerated in Sections 7.3 through 7.9, confirmed independently by both Netgen and KLayout per the dual-tool cross-validation requirement (Section 1.10), with any cross-tool divergence escalated to manual review rather than resolved automatically.

## 7.15 Industrial Notes (LVS, Overall)

Industrial LVS signoff typically relies on Calibre's RVE (Results Viewing Environment) for interactive mismatch debugging; this pipeline's Stage I visualization outputs are designed to provide a functionally analogous (though not format-compatible, per Objective 13's semantic-rather-than-binary-compatibility scoping) interactive debugging capability via KLayout's mismatch-highlighting features.

---

# PART 8 — ANTENNA CHECK

## 8.1 Theory

During plasma-based etching of metal and polysilicon layers, the wafer surface is exposed to a charged plasma environment. A conductor that is electrically isolated from any protective diode or from the substrate (e.g., a metal wire connected only to a transistor gate, with no other electrical path to ground during the specific fabrication step in question) can accumulate charge from the plasma across its exposed surface area. If this accumulated charge subsequently discharges through a thin gate oxide connected to the same net, the resulting current density through the oxide can exceed the oxide's breakdown or wear-out threshold, causing either immediate gate-oxide rupture (a catastrophic, immediately-detectable failure) or sub-catastrophic oxide damage that manifests later as an accelerated wear-out failure during the product's field lifetime (a latent, reliability-critical failure mode that is far more costly to detect and attribute after the fact).

## 8.2 Plasma Charging

Plasma charging magnitude is a function of the specific plasma etch process parameters (a property of the foundry's process, not something the design can control) combined with the total exposed conductor area on the layer being etched at that process step; this pipeline treats plasma charging behavior as fully encapsulated within the technology-specific antenna ratio threshold values provided in the rule deck, rather than attempting to model plasma physics directly.

## 8.3 Gate Oxide Damage

Gate oxide damage risk scales with the ratio of accumulated charge (proportional to exposed conductor area) to the gate oxide area the charge ultimately discharges through; this is the physical basis for the "antenna ratio" metric (exposed conductor area divided by connected gate area) that all antenna rule decks are built around.

## 8.4 Antenna Ratio

The antenna ratio for a given net, on a given layer, at a given point in the fabrication sequence (since a net's exposed conductor area accumulates progressively as successive metal layers are added, meaning the antenna ratio must be evaluated cumulatively at each metal layer's own fabrication step, not merely once at the final metal layer) is computed as the total conductor area of that net exposed at that fabrication step divided by the total gate area of transistors connected to that net.

**Engineering Rationale.** The requirement to evaluate antenna ratio cumulatively, layer-by-layer, rather than only at the topmost metal layer, is one of the more commonly under-implemented aspects of antenna checking in less rigorous verification flows; this pipeline's Stage E explicitly performs the full cumulative, per-layer evaluation rather than a topmost-layer-only approximation.

## 8.5 Antenna Rules

Antenna rule thresholds are provided per-layer, and in some technology rule decks, per-layer-combination (accounting for the fact that a net routed partly on one layer and partly on another accumulates antenna risk from both), in the technology's antenna rule table, itself part of the DRC rule deck loaded at Stage A.

## 8.6 Diode Insertion

Diode insertion is the most common antenna repair strategy: a protective diode, connected to the violating net and to the substrate/well, is inserted to provide a controlled discharge path for accumulated plasma charge, preventing that charge from instead discharging through the connected gate oxide.

**Engineering Rationale.** Diode insertion is generally preferred as a repair strategy when free layout area exists adjacent to the violating net's route, since it requires no change to the net's routing topology and thus carries minimal risk of introducing a new DRC or timing regression; Stage G's repair-candidate generation logic attempts diode insertion first, falling back to jumper insertion (Section 8.7) only where diode insertion is infeasible due to local area constraints.

## 8.7 Jumper Insertion

Jumper insertion resolves an antenna violation by routing the violating net's segment up to a higher metal layer and back down through a via jumper at a later point in the routing sequence, effectively resetting the cumulative exposed-area accumulation described in Section 8.4 by breaking the net's continuous exposure at the violating layer into two separately-fabricated segments.

**Engineering Rationale.** Jumper insertion is preferred over diode insertion specifically in cases where no free diode-insertion area exists locally, or where the violating net is timing-critical and the design team wishes to avoid the additional capacitive loading a diode insertion would introduce; this trade-off (diode capacitive loading vs. jumper routing-resource consumption) is explicitly surfaced in Stage F's classification of antenna violations by repair-strategy feasibility.

## 8.8 Router Interaction

Antenna-aware routing (a router feature invoked, where available, during Phase 14.9's detail routing) can proactively avoid creating antenna violations in the first place by tracking cumulative net exposure during route construction and preemptively inserting jumpers; this pipeline's Stage E antenna check is retained as a mandatory independent verification regardless of whether antenna-aware routing was enabled during Phase 14.9, precisely because router-internal antenna avoidance is a heuristic optimization (as discussed generally in Section 1.2), not a certified verification guarantee.

## 8.9 Technology Dependence

Antenna rule thresholds are among the most technology-node- and even foundry-fab-line-specific rules in any PDK, since they depend on the specific plasma etch equipment and process recipe used at a given foundry, meaning this pipeline's antenna rule table must never be assumed portable across PDKs even within the same nominal process node, and Stage A's rule-deck hash-pinning (Objective 8) applies with particular force to the antenna rule sub-table.

## 8.10 Validation (Antenna)

Full antenna validation requires every net in the design to have been evaluated (Objective per Stage E's validation criterion in Part 5) with a computed antenna ratio at every layer that net occupies, with zero nets exceeding threshold without a qualifying protective structure (diode or jumper) confirmed present and correctly connected.

## 8.11 Engineering Rationale (Antenna, Overall)

The overall antenna-checking methodology in this pipeline treats antenna violations with the same rigor as DRC and LVS violations (contrary to some less rigorous flows that treat antenna checking as an afterthought relative to DRC/LVS), reflecting this phase's Objective 6 status as one of the three necessary and jointly sufficient tapeout-readiness conditions established in Section 1.1.

## 8.12 Industrial Notes (Antenna)

Industrial antenna checking (via Calibre `xACT` or ICV's antenna module) is universally treated as a mandatory signoff check with zero-tolerance policy at every foundry this research program is aware of; this pipeline's equivalent zero-tolerance Objective 6 policy is a direct reflection of that universal industrial practice rather than a research-specific stringency choice.

---

# PART 9 — PHYSICAL VERIFICATION OPTIMIZATION

## 9.1 Incremental Verification

Incremental verification (Section 6.18, Stage G) is the primary optimization lever for iterative repair-cycle turnaround time, re-verifying only the region affected by a given repair (plus a rule-deck-derived interaction halo) rather than the full design, reducing per-iteration verification time from the full Stage C/D/E runtime envelope (Section 1.7) to a small fraction thereof.

## 9.2 Parallel Execution

Both Magic and KLayout support multi-threaded rule evaluation, and this pipeline's automation harness (Part 13) explicitly configures thread-count pinning (per Objective 2's determinism requirement) rather than allowing an unpinned, system-dependent default thread count that could introduce non-deterministic evaluation-order effects on floating-point area/perimeter accumulation.

## 9.3 Hierarchical Verification

Hierarchical DRC/LVS (Sections 6.17, 7.10) is the primary optimization lever for full-run (non-incremental) verification on large, reuse-heavy designs, and is the default execution mode for Stage C/D on any design exceeding a configurable instance-count threshold, with flat verification reserved for the final Stage J signoff pass (Section 6.19) and for designs below that threshold where the flat/hierarchical runtime difference is immaterial.

## 9.4 Database Caching

Rule-deck parsing and technology database loading (Section 4.7) are performed once per run and cached in memory for the duration of that run, avoiding redundant parsing overhead across Stage C, D, and E, each of which would otherwise independently reload the same rule deck.

## 9.5 Rule Partitioning

For very large rule decks (particularly on advanced nodes with thousands of individual DRC rules), this pipeline supports rule partitioning — dividing the rule deck into independently-evaluable subsets that can be dispatched to separate parallel worker processes — as an additional parallelism dimension beyond Magic/KLayout's own internal multi-threading, used selectively for designs where rule-deck size, rather than layout size, is the dominant runtime driver.

## 9.6 Runtime Optimization

Beyond the structural optimizations above, this pipeline applies targeted runtime optimizations including: pre-filtering the layout to the bounding region actually modified since the last verification pass (for Stage G incremental runs); caching GDSII streamout results between Stage A and any subsequent re-verification that does not require a fresh streamout; and short-circuiting Stage E antenna evaluation for nets with no connected gate terminals (nets that are purely internal to a black-boxed macro, per Section 7.11, and thus carry no antenna risk evaluable at the top level).

## 9.7 Memory Optimization

Memory optimization strategies include preferring hierarchical verification modes wherever design size and the Objective 14 scalability requirement make flat verification's memory footprint (Section 1.8) impractical, and explicit memory-budget pre-checking (Section 1.8) before selecting flat-versus-hierarchical mode, avoiding an out-of-memory failure mode that would otherwise only be discovered after a substantial, wasted runtime investment.

## 9.8 Engineering Rationale (Optimization, Overall)

Every optimization described in this Part is applied only insofar as it does not compromise the correctness or determinism guarantees established in Objectives 1–15; in particular, no optimization in this Part is permitted to substitute for, or weaken, the mandatory flat, full-rule-deck Stage J final verification pass (Section 6.19), which remains the unconditional terminal gate regardless of what optimizations were applied during iterative Stage C through G work.

---

# PART 10 — QUALITY METRICS

Each metric below is reported with Definition, Importance, Engineering Rationale, Measurement methodology, and ML Relevance, consistent with the metric-documentation convention established in Phases 14.6–14.12.

**1. Total DRC Violations.** *Definition:* Count of all DRC rule violations reported across both engines' union set at a given pipeline checkpoint. *Importance:* Primary top-line indicator of manufacturing readiness. *Engineering Rationale:* Aggregates across all rule categories to give a single-glance health indicator, while per-category breakdowns (below) preserve diagnostic granularity. *Measurement:* Direct count from Stage C's cross-tool union report. *ML Relevance:* Primary target/feature for violation-count prediction models.

**2. Critical DRC Violations.** *Definition:* Subset of total DRC violations classified as "critical" by Stage F (typically spacing/width violations on power rails or timing-critical nets). *Importance:* Distinguishes tapeout-blocking severity from cosmetic/marginal severity. *Engineering Rationale:* A flat total-violation count without severity weighting misrepresents true tapeout risk. *Measurement:* Stage F classification output. *ML Relevance:* Higher-priority training label for hotspot-prediction models than the unweighted total.

**3. Spacing Violations.** *Definition:* Count of Section 6.2 minimum-spacing rule violations. *Importance:* Direct bridging-defect risk indicator. *Engineering Rationale:* The single most common DRC violation category in dense-routed designs. *Measurement:* Per-rule-category count from Stage C. *ML Relevance:* Strong correlate of local routing congestion, useful as a congestion-model training feature.

**4. Width Violations.** *Definition:* Count of Section 6.1 minimum-width rule violations. *Importance:* Direct open-circuit risk indicator. *Engineering Rationale:* Frequently indicative of a router-generated narrow-neck routing artifact. *Measurement:* Per-rule-category count from Stage C. *ML Relevance:* Feature for router-quality assessment models.

**5. Area Violations.** *Definition:* Count of Section 6.3 minimum-area violations. *Importance:* CMP/etch-loss risk indicator. *Engineering Rationale:* Frequently traceable to filler-cell placement artifacts. *Measurement:* Stage C count, cross-referenced against Phase 14.6/14.7 placement database per Section 6.3. *ML Relevance:* Feature for fill-strategy optimization models.

**6. Enclosure Violations.** *Definition:* Count of Section 6.4 minimum-enclosure violations. *Importance:* Via-landing/alignment-tolerance risk indicator. *Engineering Rationale:* Concentrated at via locations, making this metric a useful proxy for overall via-quality across the design. *Measurement:* Stage C count. *ML Relevance:* Feature for via-placement-quality prediction models.

**7. Density Violations.** *Definition:* Count of Section 6.8 density rule violations. *Importance:* CMP planarity risk indicator. *Engineering Rationale:* Typically resolved via automated fill rather than functional design change, making this metric largely decoupled from functional-design-quality assessment. *Measurement:* Stage C count, pre- and post-fill-insertion. *ML Relevance:* Feature for fill-insertion-strategy training.

**8. LVS Mismatches (Total).** *Definition:* Sum of net, device, and pin mismatches from Stage D. *Importance:* Primary functional-correctness indicator. *Engineering Rationale:* Directly gates Objective 5. *Measurement:* Stage D cross-tool union report. *ML Relevance:* Primary label for P&R-tool-defect-prediction models.

**9. Open Nets.** *Definition:* Count of Section 7.9 open-net conditions. *Importance:* Catastrophic functional-failure risk indicator. *Engineering Rationale:* Typically indicates a routing-completion defect that should have been caught in Phase 14.9 but is independently re-verified here. *Measurement:* Stage D count. *ML Relevance:* Cross-phase-consistency feature (correlating Phase 14.9 routing-completion claims against Stage D findings).

**10. Short Circuits.** *Definition:* Count of Section 7.8 short conditions. *Importance:* Catastrophic functional-failure risk indicator. *Engineering Rationale:* Frequently co-located with a DRC spacing violation (Section 7.8's cross-reference). *Measurement:* Stage D count, cross-referenced against Stage C spacing violations. *ML Relevance:* Feature for joint DRC/LVS root-cause-attribution models.

**11. Missing Devices.** *Definition:* Count of schematic devices with no corresponding layout-extracted device. *Importance:* Indicates an incomplete or corrupted layout extraction, or a genuine P&R omission. *Engineering Rationale:* A non-zero count here almost always indicates a Stage A/B database-integrity issue rather than a genuine design defect, given Stage B's cross-representation consistency check. *Measurement:* Stage D device-comparison report. *ML Relevance:* Diagnostic feature for pipeline-health (rather than design-quality) monitoring.

**12. Extra Devices.** *Definition:* Count of layout-extracted devices with no corresponding schematic device. *Importance:* Indicates spurious layout content (e.g., mis-extracted parasitic transistor structures). *Engineering Rationale:* Frequently traceable to Netgen/Magic device-recognition rule miscalibration rather than genuine design defects. *Measurement:* Stage D device-comparison report. *ML Relevance:* Feature for extraction-rule-quality assessment.

**13. Pin Mismatches.** *Definition:* Count of Section 7.5 pin-matching failures. *Importance:* Top-level/macro-boundary connectivity-correctness indicator. *Engineering Rationale:* Disproportionately impactful per-instance relative to internal-net mismatches, given macro-boundary pins' typically high fan-out. *Measurement:* Stage D pin-comparison report. *ML Relevance:* Feature for macro-integration-quality models.

**14. Antenna Violations (Total).** *Definition:* Count of Section 8.4 antenna-ratio threshold exceedances, pre-repair. *Importance:* Primary reliability/yield-risk indicator specific to fabrication-time gate-oxide damage. *Engineering Rationale:* Directly gates Objective 6. *Measurement:* Stage E per-net, per-layer count. *ML Relevance:* Primary label for antenna-risk-prediction models intended to guide proactive, antenna-aware routing in future flow iterations.

**15. Fixed Antenna Violations.** *Definition:* Subset of Metric 14 successfully resolved by Stage G repair. *Importance:* Repair-effectiveness indicator. *Engineering Rationale:* Distinguishes "detected and resolved" from "detected and unresolved" for accurate final-signoff reporting. *Measurement:* Stage G repair-validation report. *ML Relevance:* Feature for repair-strategy-effectiveness models (diode vs. jumper success-rate comparison).

**16. Runtime (Per Stage).** *Definition:* Wall-clock execution time for each of Stage A through J. *Importance:* Primary scalability/practicality indicator (Objective 14). *Engineering Rationale:* Enables per-stage bottleneck identification. *Measurement:* Direct timing instrumentation in the automation harness (Part 13). *ML Relevance:* Feature for runtime-prediction models used in future flow-scheduling optimization.

**17. Memory (Peak, Per Stage).** *Definition:* Peak resident memory usage for each stage. *Importance:* Primary scalability/practicality indicator (Objective 14). *Engineering Rationale:* Directly informs the flat-vs-hierarchical mode-selection logic (Section 9.7). *Measurement:* OS-level resource monitoring during stage execution. *ML Relevance:* Feature for memory-budget-prediction models.

**18. Verification Coverage.** *Definition:* Fraction of the design (by area, for DRC; by net count, for LVS/antenna) actually subjected to rule evaluation, as distinct from rules or regions silently skipped due to a configuration error. *Importance:* Directly addresses the "silently skipped rule/region" failure mode flagged throughout Part 5's stage validation criteria. *Engineering Rationale:* A "zero violations" result is meaningless without a corresponding coverage guarantee. *Measurement:* Stage C/D/E internal coverage-accounting logic. *ML Relevance:* Data-quality gating feature; datasets with sub-100% coverage should be flagged as such before ML training use.

**19. Hierarchy Coverage.** *Definition:* Fraction of the design hierarchy verified under hierarchical mode versus flagged for flat-mode fallback due to hierarchy-boundary rule complexity. *Importance:* Diagnostic for hierarchical-mode soundness (Section 6.17's boundary-interaction caveat). *Engineering Rationale:* Directly informs confidence in hierarchical-mode results relative to the mandatory Stage J flat re-verification. *Measurement:* Stage C/D internal hierarchy-accounting logic. *ML Relevance:* Feature for hierarchical-mode-soundness-prediction models.

**20. Rule Coverage.** *Definition:* Fraction of the loaded rule deck's total rule count actually evaluated during a given Stage C/D/E run. *Importance:* Directly addresses Stage C/D/E's validation criterion (Part 5) that no rule be silently skipped. *Engineering Rationale:* Complementary to Metric 18 (area/net coverage) at the rule-table level rather than the layout level. *Measurement:* Rule-deck-parser accounting of rules loaded versus rules invoked during evaluation. *ML Relevance:* Data-quality gating feature.

**21. Database Integrity.** *Definition:* Binary/graded pass status of Stage B's cross-representation consistency check. *Importance:* Foundational precondition for the meaningfulness of every downstream metric. *Engineering Rationale:* Directly instantiates Objective 9. *Measurement:* Stage B report. *ML Relevance:* Data-quality gating feature; a Stage B failure should exclude the entire run from any downstream training corpus.

**22. Manifest Integrity.** *Definition:* Binary pass status of Stage A's full hash-verification sweep across all Part 3 input categories. *Importance:* Foundational precondition for reproducibility (Objective 3). *Engineering Rationale:* Directly instantiates Objectives 2, 3, and 8. *Measurement:* Stage A report. *ML Relevance:* Data-quality gating feature.

**23. Pass/Fail.** *Definition:* Stage J's final, binary sign-off determination. *Importance:* The single most consequential metric in the entire phase, directly gating tapeout submission. *Engineering Rationale:* Directly instantiates Objective 7. *Measurement:* Stage J final validation record. *ML Relevance:* Ultimate target label for any end-to-end tapeout-readiness-prediction model this research program might eventually train.

**24. Artifact Completeness.** *Definition:* Fraction of Part 11's expected output artifact set actually present and schema-valid at run completion. *Importance:* Directly instantiates Objective 11. *Engineering Rationale:* A run with a "pass" Stage J result but incomplete outputs is not usable for downstream review or dataset construction. *Measurement:* Stage J's output-completeness check. *ML Relevance:* Data-quality gating feature for dataset-ingestion pipelines.

**25. ML Feature Relevance.** *Definition:* A per-metric, analyst-assigned qualitative/quantitative score (documented in each metric's own "ML Relevance" field above) indicating that metric's expected utility as a training feature or label for the downstream ML models this broader research program is developing. *Importance:* Provides explicit, documented justification for why each metric is retained in the dataset schema, rather than an ad hoc or unmotivated metric list. *Engineering Rationale:* Directly instantiates Objective 12's dataset-completeness requirement, extended to require not merely completeness but documented relevance. *Measurement:* Qualitative analyst assessment, recorded in the schema documentation (Part 14/16). *ML Relevance:* Meta-metric; itself a piece of documentation metadata for the overall training corpus this phase contributes to.

*(Metrics 26–30 — Waiver Count, Cross-Tool Divergence Count, Repair Cycle Count, Halo-Region Re-Verification Overhead, and Configuration Drift Incidents — follow the identical five-field structure and are documented in full in the extended metrics appendix referenced in Part 16.)*

---

# PART 11 — OUTPUTS

## 11.1 Final Verified GDSII

The GDSII stream generated fresh at Stage A (Section 3.3) and confirmed, at Stage J, to have accumulated zero unresolved critical violations across DRC, LVS, and antenna domains; this artifact is byte-identical to the Stage A output unless Stage G repairs were applied, in which case it reflects the fully-repaired, re-verified layout.

## 11.2 Verified DEF

The DEF representation corresponding to the final verified GDSII, updated to reflect any Stage G repair-driven routing changes (diode/jumper insertion, local re-route).

## 11.3 Verified ODB

The OpenDB representation corresponding to the final verified GDSII/DEF, retained for downstream browsability and for potential future-phase consumption.

## 11.4 DRC Reports

Full Stage C reports from both Magic and KLayout, plus the cross-tool agreement/divergence summary, broken down per rule category per Part 6.

## 11.5 LVS Reports

Full Stage D reports from both Netgen and KLayout, plus the cross-tool agreement/divergence summary, broken down per mismatch category per Part 7.

## 11.6 Antenna Reports

Full Stage E per-net, per-layer antenna ratio report, including both violating and non-violating nets (for dataset completeness, Objective 12), per Part 8.

## 11.7 JSON

Machine-readable JSON export of every report category above, plus the Stage H QoR metrics dataset (Part 10), structured per a versioned schema documented in Part 14/16.

## 11.8 CSV

Tabular CSV export of the same violation and metrics data, optimized for direct ingestion into standard ML data-loading pipelines (pandas, etc.) without requiring JSON parsing.

## 11.9 XML

XML export of the same data, retained specifically to support Objective 13's industrial-compatibility goal, given XML's continued prevalence as an interchange format in some commercial EDA tool ecosystems.

## 11.10 Visualization

Rendered visual artifacts (Stage I, via KLayout's rendering backend) providing a human-browsable overview of violation distribution across the layout.

## 11.11 Heatmaps

Layer-by-layer and aggregate violation-density heatmaps, overlaying violation counts onto the physical layout to allow rapid visual identification of violation-clustered regions.

## 11.12 Violation Maps

Discrete, per-violation-instance markers overlaid on the layout (as distinct from the continuous-density heatmaps of Section 11.11), enabling direct navigation from a specific reported violation to its exact physical location.

## 11.13 Manifest Updates

The Phase 14.13 manifest section, appended (never overwriting) to the cumulative Phase 14.6–14.13 manifest chain, recording every hash check, stage completion, and sign-off determination made during this phase's execution.

## 11.14 Configuration Snapshots

Updated configuration snapshot recording the exact tool versions, thread-count pins, and environment descriptors used for this phase's execution, appended to the cumulative configuration-snapshot history.

## 11.15 Metadata

Full provenance metadata (timestamps, invocation command lines, host environment descriptors) for this phase's execution, appended to the manifest.

## 11.16 Engineering Rationale (Outputs, Overall)

The output artifact taxonomy above is deliberately redundant across formats (JSON/CSV/XML all encoding substantially the same underlying data) specifically to serve the differing consumption needs of human sign-off reviewers (who benefit most from visualization and structured reports), downstream ML pipelines (which benefit most from CSV/JSON), and industrial-compatibility validation exercises (which benefit most from XML per Objective 13), rather than reflecting any redundancy in the underlying verification computation itself.

---

# PART 12 — FAILURE HANDLING

## 12.1 Failure Table

| Failure Mode | Detection Stage | Recovery Strategy | Logging | Retry Policy | Fatal vs. Recoverable |
|---|---|---|---|---|---|
| Rule deck hash mismatch | Stage A | Abort run; require manual re-validation of rule deck provenance against Phase 14.6 PDK binding | Full diagnostic: expected vs. actual hash, file path | No automatic retry | Fatal |
| Database corruption (OpenDB/DEF/GDSII cross-inconsistency) | Stage B | Abort run; require manual investigation of Phase 14.12 output integrity | Full cross-representation count diff | No automatic retry | Fatal |
| LVS mismatch (net/device/pin) | Stage D | Route to Stage F classification and Stage G repair pipeline | Full mismatch record (net names, device names, locations) | N/A — this is a violation, not an infrastructure failure | Recoverable (design-level) |
| Open circuit | Stage D | Route to Stage F/G; cross-reference Phase 14.9 routing-completion report | Full net-fragment record | N/A — violation, not infrastructure failure | Recoverable (design-level), escalate to Phase 14.9 review if root cause is a routing-completion regression |
| Short circuit | Stage D | Route to Stage F/G; cross-reference Stage C spacing violations at same location | Full net-pair and location record | N/A — violation | Recoverable (design-level) |
| Critical DRC violation | Stage C/F | Route to Stage G repair pipeline with maximum priority | Full rule/location/severity record | N/A — violation | Recoverable (design-level), blocks Stage J until resolved |
| Antenna violation | Stage E/F | Route to Stage G diode/jumper repair pipeline | Full net/layer/ratio record | N/A — violation | Recoverable (design-level), blocks Stage J until resolved |
| Manifest mismatch (any input) | Stage A | Abort run | Full hash diff | No automatic retry | Fatal |
| Tool crash (Magic/Netgen/KLayout) | Any of C/D/E | Automated retry with verbose logging enabled, up to a configured retry limit; escalate to manual review on repeated failure | Full crash log, stack trace where available | Up to 2 automatic retries, then escalate | Fatal if retries exhausted |
| Configuration corruption/drift | Stage A | Abort run; require environment re-validation against Phase 14.12 configuration snapshot | Full configuration diff | No automatic retry | Fatal |
| Cross-tool divergence (DRC or LVS) | Stage C/D | Escalate to manual engineering review; never auto-resolved | Full per-check divergence record | N/A — requires manual resolution | Fatal for automated signoff (Stage J blocked) until manually resolved |
| Incremental repair introduces new violation in halo region | Stage G | Revert repair; escalate to alternate repair strategy or manual review | Full before/after violation diff for the halo region | Up to 1 automatic alternate-strategy retry per violation, then escalate | Recoverable (design-level) |
| Output artifact missing/schema-invalid | Stage I/J | Abort Stage J signoff; re-run Stage I report generation | Full missing/invalid artifact list | Up to 1 automatic Stage I retry | Fatal if retry does not resolve |

## 12.2 Engineering Rationale (Failure Handling, Overall)

The failure table above maintains the sharp distinction, established in Section 1.9, between infrastructure/environment failures (rule-deck mismatch, database corruption, tool crashes, configuration drift — all fatal, non-design conditions requiring investigation before any re-run is meaningful) and design-level violation conditions (LVS mismatches, DRC violations, antenna violations — expected, recoverable-by-design-repair conditions that are the entire purpose of this phase to discover). This distinction is critical for correct automation harness behavior (Part 13): an infrastructure failure should halt the pipeline and alert an engineer, while a design-level violation should route into the Stage F/G classification-and-repair loop without halting the overall pipeline.

## 12.3 Waiver Ledger

Consistent with Objective 4's acknowledgment that some industrial flows tolerate explicitly waived violations, this pipeline maintains a separate, append-only waiver ledger distinct from the failure ledger: any violation a design team elects not to repair (e.g., a known false-positive DRC flag against an intentionally non-standard dummy-fill pattern) must be recorded in the waiver ledger with an explicit justification, a reviewing engineer's identifier, and a timestamp, before Stage J will treat that specific violation instance as non-blocking. Waivers are never silent; every waived violation remains visible in the full violation dataset (Objective 12) with its waiver status explicitly flagged, never removed from the dataset.

## 12.4 Industrial Notes (Failure Handling, Overall)

This failure-handling architecture's separation of infrastructure failures from design violations, and its explicit, auditable waiver mechanism, directly mirrors the two-track failure taxonomy (tool/flow failures vs. design failures) and formal waiver-approval processes used in industrial tapeout-readiness review boards.

---

# PART 13 — AUTOMATION

## 13.1 Architecture Overview

The automation harness is implemented as a set of Python-based orchestration scripts, each corresponding to one or more pipeline stages, coordinated by a top-level driver (`physical_verification.py`) that reads a manifest-driven configuration, dispatches to the appropriate stage scripts in sequence, and enforces the checkpointing and resume-capability requirements described below.

## 13.2 `physical_verification.py`

The top-level orchestration script, responsible for: reading the Phase 14.12 manifest and this phase's configuration; invoking Stage A through Stage J in sequence (or resuming from the last successfully completed and checkpointed stage); enforcing the fail-fast behavior of Section 1.9/Part 12 for infrastructure failures; and sealing the final Phase 14.13 manifest section upon successful Stage J completion.

## 13.3 `run_drc.py`

Invoked by the top-level driver during Stage C, this script wraps both Magic's DRC invocation and KLayout's `.lydrc` invocation, normalizes both tools' native report formats into this pipeline's internal violation-record schema, and produces the cross-tool agreement/divergence summary described in Part 5's Stage C outputs.

## 13.4 `run_lvs.py`

Invoked during Stage D, this script wraps Netgen's LVS invocation (itself dependent on a prior Magic-based layout extraction sub-step) and KLayout's `.lylvs` invocation, normalizes both tools' native comparison output formats into the internal mismatch-record schema, and produces the cross-tool agreement/divergence summary for Stage D.

## 13.5 `run_antenna.py`

Invoked during Stage E, this script computes per-net, per-layer antenna ratios (Section 8.4) from the Stage B-validated GDSII/DEF, cross-referencing the technology antenna rule table, and produces the Stage E antenna violation report.

## 13.6 `collect_reports.py`

Invoked during Stage H, this script aggregates the raw Stage C/D/E reports (as classified and prioritized by an intermediate Stage F classification sub-routine invoked internally) into the unified QoR metrics dataset described in Part 10.

## 13.7 `generate_visualization.py`

Invoked during Stage I, this script wraps KLayout's rendering API to produce the heatmap and violation-map visualization artifacts described in Sections 11.11 and 11.12, reading directly from the Stage H QoR dataset and the raw Stage C/D/E location data.

## 13.8 `validate_results.py`

Invoked during Stage J, this script performs the final, all-or-nothing sign-off check described in Part 5's Stage J specification: confirming zero unresolved critical violations (cross-checked against the waiver ledger of Section 12.3 for any explicitly waived exceptions), confirming output artifact completeness (Objective 11), and sealing the final manifest section.

## 13.9 Resume Capability

Every stage script writes a checkpoint record (stage identifier, completion status, output artifact hashes) to the manifest immediately upon successful completion, before the top-level driver proceeds to the next stage. If the pipeline is interrupted (infrastructure crash, manual halt) and re-invoked, the top-level driver reads the manifest's checkpoint history and resumes from the first stage lacking a valid completion record, re-validating (via hash comparison) any artifacts produced by prior stages before trusting them, rather than blindly assuming a checkpointed stage's outputs remain valid.

## 13.10 Checkpointing

Checkpointing is implemented at stage granularity (not sub-stage granularity), consistent with the checkpointing granularity established in Phases 14.6–14.12, on the rationale that stage-level atomicity provides the correct balance between resume-efficiency (avoiding needless re-computation of already-completed work) and checkpoint-logic complexity (finer-grained checkpointing would require substantially more intricate partial-stage-state serialization for limited additional benefit given typical stage runtimes).

## 13.11 Manifest-Driven Execution

Every stage script's behavior (which rule deck to load, which tool versions to invoke, which thread-count pins to apply) is driven entirely by the manifest and configuration snapshot rather than by any hard-coded default, ensuring that a re-execution from a given manifest state is fully reproducible (Objective 3) regardless of the executing environment's own local defaults.

## 13.12 Parallel Execution

The top-level driver supports invoking Stage C, D, and E concurrently (as independent, non-interdependent verification domains operating on the same Stage B-validated database) where sufficient system resources are available, subject to the memory-budget pre-check of Section 9.7 confirming that concurrent execution will not exceed available system memory.

## 13.13 Dry-Run Mode

The top-level driver supports a dry-run mode that performs all Stage A/B validation (hash checks, cross-representation consistency checks) and reports the design's readiness for a full verification run (e.g., confirming rule-deck availability, confirming sufficient estimated memory for the design's size at the selected flat/hierarchical mode) without executing any actual Stage C/D/E rule evaluation, useful for rapid pre-flight sanity checking before committing to a potentially multi-hour full verification run.

---

# PART 14 — REPOSITORY STRUCTURE

```
phase_14_13_physical_verification/
├── configs/
│   ├── pdk_binding.yaml
│   ├── rule_deck_paths.yaml
│   ├── tool_versions.yaml
│   └── thread_pinning.yaml
├── scripts/
│   ├── physical_verification.py
│   ├── run_drc.py
│   ├── run_lvs.py
│   ├── run_antenna.py
│   ├── collect_reports.py
│   ├── generate_visualization.py
│   └── validate_results.py
├── stages/
│   ├── stage_a_initialization/
│   ├── stage_b_database_integrity/
│   ├── stage_c_drc/
│   ├── stage_d_lvs/
│   ├── stage_e_antenna/
│   ├── stage_f_classification/
│   ├── stage_g_repair/
│   ├── stage_h_qor/
│   ├── stage_i_reports/
│   └── stage_j_final_validation/
├── reports/
│   ├── drc/
│   │   ├── magic/
│   │   └── klayout/
│   ├── lvs/
│   │   ├── netgen/
│   │   └── klayout/
│   ├── antenna/
│   └── qor/
├── schema/
│   ├── violation_record_schema.json
│   ├── qor_metrics_schema.json
│   └── manifest_schema.json
├── runs/
│   └── <run_id>/
│       ├── gdsii/
│       ├── def/
│       ├── odb/
│       └── logs/
├── failure_ledger/
│   ├── infrastructure_failures.jsonl
│   ├── design_violations.jsonl
│   └── waiver_ledger.jsonl
├── visualization/
│   ├── heatmaps/
│   └── violation_maps/
├── docs/
│   ├── rule_deck_provenance.md
│   ├── repair_strategy_reference.md
│   └── industrial_compatibility_mapping.md
├── logs/
│   └── <run_id>_execution.log
└── manifest/
    └── phase_14_13_manifest.json
```

**Engineering Rationale.** This structure preserves the top-level directory taxonomy (`configs/`, `scripts/`, `reports/`, `manifest/`, etc.) established in Phases 14.6–14.12, extended with phase-specific subdirectories (`stages/` reflecting the ten-stage architecture of Part 5; `failure_ledger/` explicitly split into infrastructure-failure, design-violation, and waiver sub-ledgers per Part 12's taxonomy) to maintain cross-phase repository navigability for both human engineers and any future automated tooling traversing the full Phase 14.6–14.13 (and beyond) repository tree.

---

# PART 15 — DELIVERABLES

## 15.1 Implementation

The complete automation harness (Part 13) and stage implementation code (Part 5), version-controlled and tagged corresponding to the exact tool versions recorded in the configuration snapshot (Section 3.18).

## 15.2 Reports

The full DRC, LVS, and antenna report set (Part 11.4–11.6), in both native per-tool format and normalized internal schema.

## 15.3 Violation Datasets

The structured, schema-stable JSON/CSV/XML violation datasets (Part 11.7–11.9), retaining full pre-repair and post-repair violation history per Objective 12.

## 15.4 Visualization

Heatmap and violation-map artifacts (Part 11.10–11.12).

## 15.5 Verified Layouts

The final verified GDSII/DEF/ODB artifact set (Part 11.1–11.3).

## 15.6 Metadata

Full provenance metadata (Part 11.15).

## 15.7 Failure Ledger

The complete infrastructure-failure, design-violation, and waiver ledgers (Section 12.3, Part 14).

## 15.8 Configuration Snapshots

The complete tool-version and environment configuration snapshot history (Part 11.14).

## 15.9 Engineering Rationale (Deliverables, Overall)

This deliverable set is designed to satisfy simultaneously: (1) the immediate practical need for a tapeout-ready, signed-off GDSII; (2) the IEEE Artifact Evaluation reproducibility bar (Objective 3); and (3) this broader research program's need for a comprehensive, well-documented violation dataset (Objective 12) suitable for training the downstream ML models this multi-phase research program is ultimately building toward.

---

# PART 16 — PUBLICATION READINESS

## 16.1 IEEE Reproducibility

This phase's manifest-driven, hash-pinned architecture (Objectives 2, 3, 8) is designed to satisfy the IEEE reproducibility badge criteria applied by ICM, TCAD, TVLSI, DAC, ICCAD, and DATE artifact evaluation committees: every reported result traces to a specific, hash-identified rule deck version, tool version, and input artifact set, all recoverable from the manifest without recourse to any undocumented local state.

## 16.2 Artifact Evaluation

For formal Artifact Evaluation submission, the repository structure of Part 14, combined with the dry-run mode of Section 13.13 (allowing an evaluator to rapidly confirm environment readiness before committing to a full multi-hour verification run) and the clean-room re-execution validation described in Objective 3, together constitute the evidence package an Artifact Evaluation committee would expect: a documented environment specification, a fixed random-seed/thread-pinning policy (Objective 2), and a worked reproduction of at least one full Stage A–J run from the published manifest.

## 16.3 Industrial Deployment

Section 4.15's tool-abstraction layer and Objective 13's semantic (rather than binary) industrial-format-compatibility scoping together provide a documented, if partial, pathway toward industrial deployment: a team wishing to adopt this methodology against a commercial PDK and Calibre/ICV toolchain would replace the Magic/Netgen/KLayout tool bindings with equivalent Calibre/ICV bindings behind the same abstract stage interfaces, without needing to re-architect Stages A through J.

## 16.4 Zenodo Compatibility

The manifest, configuration snapshot, and full violation dataset (Part 11.7–11.9) are structured as flat, self-contained, schema-documented files suitable for direct archival deposit in a Zenodo (or equivalent long-term research-data-archival) record, with the schema files themselves (Part 14's `schema/` directory) included in the archival package to ensure the dataset remains interpretable independent of this document's continued availability.

## 16.5 Reviewer Expectations (Publication, Overall)

A reviewer assessing this phase's contribution for publication at IEEE ICM or a comparable venue should expect: explicit, quantified results for each of Part 10's 25+ metrics on at least one non-trivial benchmark design; an explicit accounting of any cross-tool divergence encountered (Section 1.10) and how it was resolved; and an explicit statement of which objectives (Part 2) were fully validated versus partially validated in the reported experimental campaign, rather than a blanket claim of full compliance without corresponding evidence.

## 16.6 Future Scalability (Publication, Overall)

This document's Objective 15 (future extensibility) is directly exercised by this research program's planned Phase 14.14 and beyond, in which the structured violation datasets produced by this phase are intended to feed a machine-learning hotspot-prediction and antenna-risk-prediction model whose outputs, in a future flow iteration, would feed back as an additional pre-Stage-C filtering pass — the "Stage K" extension referenced in Objective 15 — narrowing the region of the layout requiring full rule-deck evaluation and thereby further improving the runtime scalability characteristics established in Part 9.

---

## CONTINUITY CONFIRMATION

Phase 14.13 is now complete and its manifest section sealed at Stage J, contingent on a zero-unresolved-critical-violation result across DRC, LVS, and antenna domains (Objectives 4, 5, 6) and full output completeness (Objective 11). The design database, now carrying a complete, hash-verified manifest chain from Phase 14.6 through Phase 14.13, is ready for consumption by Phase 14.14, which — consistent with the established phase-numbering convention — is expected to address either final tapeout packaging and foundry submission formatting, or the initial construction of the ML training corpus and hotspot-prediction model referenced in Section 16.6, depending on this research program's next-phase scope determination.

*(End of Phase 14.13 specification. Continuity with Phase 14.14 to be established in the subsequent document.)*
