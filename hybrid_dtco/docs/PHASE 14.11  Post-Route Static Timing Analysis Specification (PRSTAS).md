# PHASE 14.11
## Post-Route Static Timing Analysis Specification (PRSTAS)

**Document Classification:** Industrial Post-Route Static Timing Analysis Engineering Specification
**Project:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target Conference:** IEEE International Conference on Microelectronics (ICM 2026)
**Long-Term Target Journals/Venues:** IEEE TCAD · IEEE TVLSI · DAC · ICCAD · DATE — Artifact Evaluation Ready
**Predecessor Document:** Phase 14.10 (Parasitic Extraction / SPEF Generation)
**Successor Document:** Phase 14.12 (Power Integrity Analysis — IR Drop & Electromigration)

**Boundary Statement:** This document governs the interval **after** Phase 14.10 delivers a validated, checksummed, routing-consistent SPEF corpus and **before** Phase 14.12 performs power-integrity analysis. Its sole function is to perform deterministic, technology-independent, graph-based static timing analysis on validated post-route physical design data, producing a complete, schema-conformant timing report and quality-of-results (QoR) corpus. This document performs **analysis only**: it does not perform timing ECO, buffer insertion, cell resizing, gate sizing, placement modification, routing modification, IR drop analysis, electromigration analysis, signal integrity or noise analysis, crosstalk fixing, DRC/LVS, or any tapeout-adjacent activity. Any reader looking for those topics should proceed to Phase 14.12 (power integrity) or later, not-yet-written phases (timing closure/ECO); this document ends precisely where a timing report becomes an input to a decision, not where that decision is made.

---

## PART 1 — Static Timing Analysis Philosophy

**Purpose:** Establish why post-route STA is treated, within this project, as an independently versioned, fully deterministic analytical subsystem rather than an incidental verification step appended to the physical-design flow, and to fix the theoretical vocabulary (arrival time, required arrival time, slack, timing arcs) that every subsequent Part in this document depends upon without redefinition.

**Theory:** Static timing analysis is, at its mathematical core, a longest-path and shortest-path problem defined over a directed acyclic timing graph, where nodes represent timing points (pins) and edges represent timing arcs (either combinational cell arcs, characterized by the pinned Liberty timing library, or interconnect arcs, characterized by the pinned Phase 14.10 SPEF parasitics). Two structurally symmetric but purpose-distinct analyses are performed over this graph: **setup analysis**, a longest-path problem bounding the maximum propagation delay a signal may experience before a capturing clock edge, and **hold analysis**, a shortest-path problem bounding the minimum propagation delay a signal must experience to avoid being captured prematurely by a subsequent clock edge. Every quantity this document reports — arrival time, required arrival time, slack, worst negative slack (WNS), total negative slack (TNS) — is a direct or aggregate consequence of this longest-path/shortest-path formulation applied over the same underlying timing graph, and this document treats that graph, not any single reported number, as the primary analytical artifact requiring validation.

**Engineering Rationale:** A downstream ML model trained to predict timing outcomes (this project's ultimate objective, though model architecture and training remain wholly out of scope for this document, consistent with the strict phase-boundary discipline established across every prior 14.x document) can only be as trustworthy as the ground-truth timing analysis it learns from. Any nondeterminism, technology-dependent assumption baked in unstated, or silently incomplete endpoint coverage in the underlying STA run becomes an unquantifiable confound in every downstream prediction claim — exactly the same reasoning Phase 14.3 Part 1 applied to ground-truth label generation generally, now specialized to the single highest-stakes label category in the entire project: timing.

**Industrial STA Philosophy:** Production sign-off STA in an industrial ASIC flow is characterized by three non-negotiable properties that this document adopts unmodified as its own governing philosophy: **completeness** (every timing endpoint reachable from every declared clock domain must be analyzed; a not-analyzed endpoint is a sign-off blocker, not a permissible gap), **conservatism under uncertainty** (where a modeling assumption is uncertain — on-chip variation, clock uncertainty, unmodeled parasitic effects — the analysis is required to bound the true behavior pessimistically rather than optimistically, since an optimistic timing error is safety-critical while a pessimistic one is merely a QoR cost), and **traceability** (every reported slack value must be traceable to a specific, reproducible timing path with a fully itemized delay breakdown). This document's remaining Parts operationalize these three properties as concrete, checkable engineering requirements rather than restating them as aspirations.

**Graph-Based Timing Analysis:** The primary analysis mode this document specifies is **graph-based analysis (GBA)** — arrival times are propagated through the timing graph using each timing arc's own characterized delay, without attempting to track which specific combination of arcs constitutes any one physical path until critical-path extraction (Part 5, Stage H) is explicitly invoked. GBA is computationally efficient (each arc is traversed once per propagation direction) and is the mode used for the corpus-wide, every-endpoint analysis this document's completeness requirement demands.

**Path-Based Timing Analysis:** A secondary, more precise analysis mode, **path-based analysis (PBA)**, is reserved for the worst-slack subset of endpoints identified by GBA — PBA re-evaluates a specific candidate path's delay accounting for path-specific effects (notably, common-path pessimism removal, discussed further in Part 8) that GBA's arc-local propagation cannot capture without full path enumeration. This document specifies GBA as the mandatory, corpus-wide analysis mode and PBA as an optional, configurable refinement applied only to a bounded worst-endpoint subset (Part 9), since full-corpus PBA is computationally prohibitive at this project's benchmark scale and, more importantly, GBA's inherent additional pessimism is a conservative bias consistent with the industrial STA philosophy stated above, not a correctness defect requiring universal correction.

**Timing Graph Formulation:** Formally, the timing graph $G = (V, E)$ has vertex set $V$ corresponding to every pin in the post-route netlist (both cell pins, characterized by Liberty, and interconnect-segment endpoints, characterized by SPEF), and edge set $E$ partitioned into **cell arcs** (intra-cell, Liberty-characterized, condition-dependent on input-pin timing sense and output-load) and **net arcs** (inter-cell, SPEF-characterized, condition-dependent on driver output resistance and the extracted RC network's own topology). Arrival time at a vertex $v$ is defined recursively as $AT(v) = \max_{u \to v \in E} \left( AT(u) + \delta(u, v) \right)$ for setup-relevant (maximum) analysis, and analogously with a minimum operator for hold-relevant (minimum) analysis, where $\delta(u,v)$ is the arc's delay under the analysis corner's operating conditions. This recursive formulation is what Part 5 Stages D and E operationalize as concrete pipeline stages.

**Arrival Time:** The time at which a signal transition actually reaches a given timing point, measured relative to a reference clock edge, propagated forward from primary inputs and clock sources through the timing graph as defined above.

**Required Arrival Time:** The latest (for setup) or earliest (for hold) time at which a signal transition is permitted to arrive at a given timing point without violating the design's timing intent, propagated backward from primary outputs and register data-input constraints through the timing graph.

**Slack:** The difference between required arrival time and arrival time — $\text{slack} = RAT - AT$ for setup analysis (positive slack indicates timing is met; negative slack indicates a violation) and $\text{slack} = AT - RAT$ for hold analysis (the sign convention is inverted because hold analysis bounds a minimum, not a maximum, delay). Every downstream metric in Part 10 (WNS, TNS, and their setup/hold-specific variants) is a direct aggregate function of the complete per-endpoint slack distribution this definition produces.

**Setup Analysis:** The maximum-delay analysis verifying that data launched by one clock edge arrives at a capturing register before the next relevant capturing clock edge, net of the register's own setup-time requirement; this is the analysis mode whose violation directly bounds a design's achievable maximum operating frequency.

**Hold Analysis:** The minimum-delay analysis verifying that data launched by one clock edge does not arrive at a capturing register so quickly that it is inadvertently captured by that same edge (rather than the intended subsequent edge), net of the register's own hold-time requirement; hold violations are frequency-independent and, if present, indicate a functional failure at any operating frequency, not merely a performance limitation — this distinction is a direct consequence of the setup/hold asymmetry already established in the arrival-time/required-arrival-time formulation above and is restated explicitly here because it is the single most common point of confusion this document's Parts 6–7 are designed to prevent.

**Clock Propagation:** The process by which clock-source waveforms are propagated through the design's actual clock network (as extracted from the post-route netlist and its Phase 14.10 SPEF parasitics), rather than assumed ideal, producing a per-register clock arrival time (clock latency) that directly feeds both setup and hold analysis; Part 8 is devoted entirely to this concern given its outsized influence on both analysis modes.

**Clock Uncertainty:** A configured margin subtracted from setup slack and added to hold slack to conservatively bound unmodeled clock-network variation (jitter, unaccounted-for on-chip variation between launch and capture clock paths) not otherwise captured by explicit clock-network extraction — this is one of the concrete mechanisms by which this document's stated conservatism-under-uncertainty philosophy is operationalized rather than left aspirational.

**Timing Arcs:** The atomic delay-characterized edges of the timing graph, as formally introduced above; this document distinguishes cell arcs (Liberty-sourced) from net arcs (SPEF-sourced) throughout, since the two have entirely distinct provenance, distinct failure modes (a missing Liberty cell model versus a missing/malformed SPEF net), and distinct validation requirements (Part 3, Part 12).

**Incremental STA:** The capability to re-propagate arrival/required-arrival times affecting only the timing graph region downstream of a localized netlist or parasitic change, without re-analyzing the entire graph — this document specifies full, non-incremental STA as its primary mode (consistent with the completeness requirement and with this phase's single-shot, post-route analysis scope, distinct from an ECO-iteration context where incremental STA is the dominant mode), while noting incremental STA as the natural mechanism a future timing-closure/ECO phase (explicitly out of scope here) would require, and ensuring this document's timing-graph construction (Part 5, Stage B) is structured in a form compatible with future incremental re-use even though this document itself never invokes that capability.

**OpenSTA Philosophy:** OpenSTA, the open-source STA engine this specification is built around (consistent with the OpenROAD-centric tool chain established across Phase 14.1–14.10), implements the graph-based analysis formulation above directly, using a discrete timing-graph data structure with explicit support for multi-corner, multi-mode analysis, SDC-based constraint and exception specification, and SPEF-based parasitic annotation — this document's Part 4 and Part 5 map this specification's stage-by-stage pipeline directly onto OpenSTA's own command and data-model vocabulary, rather than defining an abstract STA process independent of the actual tool that will execute it, consistent with the same tool-fidelity discipline Phase 14.4 Part 18 applied to elaboration validation.

**Determinism:** Every quantity this document produces is required to be a deterministic function of its inputs (routed DEF/OpenDB, SPEF, Liberty, SDC, and the pinned OpenSTA tool version) — re-running this phase's analysis against identical, unchanged inputs is expected to reproduce byte-identical timing reports, since OpenSTA's core graph-propagation algorithm contains no stochastic element, in direct contrast to certain upstream placement/routing stages (Phase 14.1 Part C) that do carry documented, bounded nondeterminism. Any observed non-reproducibility at this phase is therefore treated as a validation failure requiring root-cause investigation (Part 12), never as expected tool-level noise.

**Technology Independence:** This specification's stage structure, metric definitions, and validation methodology are defined independent of any specific PDK, consistent with the technology-independence principle established in Phase 14.2 Part 9 and Phase 14.4 Part 15 — every technology-specific quantity (Liberty timing arcs, SPEF parasitic values, operating-condition corners) enters this document's pipeline as a pinned, versioned input (Part 3), never as an assumption embedded in this document's own stage logic.

**ML Dataset Generation:** Although this document produces no model training code (explicitly out of scope, consistent with the boundary discipline established from Phase 14.1 onward), every artifact it produces — the complete per-endpoint slack distribution, the critical-path corpus, the full QoR metric set (Part 10) — is structured specifically to serve as a ground-truth timing label set for the project's eventual CNN/GNN prediction models, extending Phase 14.3's timing-label taxonomy (Phase 14.3 Parts 2.4, 2.13–2.15) from that document's dataset-generation-pipeline-level treatment into this document's fully detailed, post-route-specific, production-fidelity analysis.

**Inputs:** The complete Phase 14.10 deliverable set (validated routed DEF, validated routed OpenDB, validated SPEF, associated QoR/manifest artifacts), plus Liberty timing libraries and SDC constraints pinned at the benchmark's acquisition/standardization stage (Phase 14.2/14.4).
**Outputs:** The complete Part 11 output set — validated post-route STA reports, the timing QoR dataset, the timing-path and critical-path corpora, setup/hold/clock reports, and the associated manifest and validation-report updates.
**Dependencies:** OpenSTA at a pinned version, OpenROAD/OpenDB for physical-database interoperability, the pinned Liberty and SDC assets, and the full upstream artifact chain from Phase 14.1 through Phase 14.10.
**Runtime Expectations:** Governed in aggregate by Part 5's stage-by-stage figures; single-corner, single-mode analysis for the smallest corpus members (ISCAS/ITC-99-class) completes in well under a minute, while the largest corpus members (CVA6/OpenTitan-class, multi-corner) require tens of minutes, consistent with the scale-dependent figures established for comparable stages in Phase 14.1 and Phase 14.3.
**Memory Expectations:** Dominated by timing-graph size, itself proportional to pin count and net count; ranges from under 1 GB for the smallest benchmarks to several tens of GB for the largest multi-corner analyses, detailed per-stage in Part 5.
**Failure Conditions:** Detailed exhaustively in Part 12; at the philosophy level, any condition preventing a complete, every-endpoint analysis (a missing Liberty cell model, an unresolvable SDC clock definition, a corrupted SPEF net) is treated as a phase-blocking failure, never as a partial-result acceptance, consistent with this Part's stated completeness requirement.
**Validation:** The complete Part 5 Stage J validation methodology, itself informed by the determinism and technology-independence principles established here.
**Industrial Notes:** This document's philosophy section is deliberately more theory-dense than the corresponding introductory Parts of Phase 14.1–14.4, reflecting the fact that STA, unlike RTL standardization or benchmark acquisition, is a domain with an extensive, well-established formal theory that this specification is obligated to state precisely rather than merely gesture toward, since any imprecision here would propagate as ambiguity through every subsequent Part's engineering rationale.
**Reviewer Expectations:** IEEE TCAD/ICCAD/DAC reviewers with production STA backgrounds will scrutinize this Part specifically for correct, precise use of standard terminology (arrival time, required time, slack sign conventions, GBA versus PBA) — imprecision here is a fast, credibility-damaging reviewer objection, which is why this Part defines every term formally before any subsequent Part relies on it informally.
**Future Scalability:** The graph-based formulation established here generalizes without modification to future technology nodes, future clock-topology complexity, and — should a future phase require it — to the incremental-STA mode explicitly noted above as compatible-but-unused in this document's current scope.

---

## PART 2 — Objectives

Each objective below is stated with its definition, engineering rationale, validation mechanism, industrial notes, and future scalability, consistent with this document's governing philosophy (Part 1).

### 2.1 Deterministic Timing Analysis
**Definition:** Every reported timing quantity must be exactly reproducible from identical pinned inputs and tool version.
**Engineering Rationale:** Non-reproducible timing labels would silently corrupt any downstream ML training claim; this is the single most foundational objective this document must satisfy.
**Validation:** Deterministic-rerun comparison (Part 5, Stage J), following the same methodology Phase 14.3 Part 8 established for annotation labels generally, applied here with STA-specific tolerance (exact byte-for-byte match expected, given OpenSTA's non-stochastic core algorithm).
**Industrial Notes:** Mirrors the sign-off STA determinism requirement every production tapeout decision depends upon.
**Future Scalability:** Extends unmodified to any future technology node or tool-version upgrade, provided the upgrade itself is pinned and versioned consistent with this document's versioning scheme (Part 16).

### 2.2 Technology Independence
**Definition:** This document's stage structure and metric definitions must not embed any PDK-specific assumption.
**Engineering Rationale:** Consistent with Phase 14.2 Part 9 and Phase 14.4 Part 15's technology-independence principle, required to support the project's cross-PDK generalization claims (Phase 14.1 Part 3).
**Validation:** A structural review confirming every technology-specific value enters this document's pipeline as a Part 3 pinned input, never as an embedded constant in stage logic.
**Industrial Notes:** Directly supports reuse of this specification across Sky130, GF180, and ASAP7 without modification, as already established for physical-design stages in Phase 14.1.
**Future Scalability:** Extends to a future open FinFET-class PDK (Phase 14.2 Part 9's stated future-extensibility target) without structural revision.

### 2.3 Reproducibility Across Machines and Environments
**Definition:** Identical timing results must be obtainable on a distinct host machine or container environment given identical pinned inputs.
**Engineering Rationale:** Extends Phase 14.3 Part 8's cross-machine/cross-platform validation methodology to the timing-analysis layer specifically, where floating-point delay-calculation nondeterminism across CPU architectures is a documented, real risk requiring explicit checking rather than assumption.
**Validation:** Cross-machine validation subset, per Part 5 Stage J and Part 12.
**Industrial Notes:** A standard requirement for any AE-track submission whose central claim depends on quantitative timing data.
**Future Scalability:** Generalizes to any future compute environment (cloud, on-premises cluster) without new validation infrastructure.

### 2.4 Complete Timing Graph Construction
**Definition:** The timing graph constructed in Part 5 Stage B must include every pin, cell arc, and net arc reachable from the design's declared top module and clock sources.
**Engineering Rationale:** An incomplete timing graph silently produces an incomplete, and therefore misleading, timing report — this objective is the graph-level operationalization of Part 1's completeness principle.
**Validation:** A graph-completeness check cross-referencing the timing graph's pin count against the Phase 14.4-standardized netlist's structural pin count.
**Industrial Notes:** Mirrors the sign-off requirement that no timing arc be silently dropped due to a library-characterization or netlist-parsing gap.
**Future Scalability:** Scales without modification to arbitrarily large future benchmark additions, bounded only by Part 5 Stage B's stated runtime/memory figures.

### 2.5 100% Endpoint Analysis Coverage
**Definition:** Every valid timing endpoint (register data input, primary output, or other constrained pin per SDC) must receive both a setup and a hold analysis result, or an explicit, justified not-applicable disposition.
**Engineering Rationale:** A silently unanalyzed endpoint is functionally equivalent to reporting a false "timing met" result — this objective closes that specific risk.
**Validation:** An endpoint-coverage completeness check (Part 5 Stage J) comparing the analyzed-endpoint set against the SDC-derived expected-endpoint set.
**Industrial Notes:** Directly analogous to the sign-off requirement that 100% of a design's timing endpoints be covered before tapeout release.
**Future Scalability:** Extends to future multi-mode/multi-corner analysis expansion without new coverage-checking logic beyond parameterizing the existing check per corner/mode.

### 2.6 Setup Verification Completeness
**Definition:** Every clock-to-clock, input-to-register, register-to-output, and input-to-output setup timing check applicable to the design must be performed.
**Engineering Rationale:** Setup analysis directly bounds achievable operating frequency and is the single most commonly reported timing-closure metric (Phase 14.3 Part 2.14); incomplete setup coverage would compromise the primary timing-label category this project depends on.
**Validation:** Cross-check against the SDC-declared check-type set (Part 3).
**Industrial Notes:** Consistent with standard sign-off setup-check-type coverage requirements.
**Future Scalability:** Extends to future check types (e.g., a future recovery/removal-check requirement for asynchronous-reset-heavy designs) via Part 6's stated extensibility.

### 2.7 Hold Verification Completeness
**Definition:** Every hold-relevant check, at every valid launch/capture clock-edge relationship, must be performed.
**Engineering Rationale:** Hold violations are functional-correctness failures independent of operating frequency (Part 1); incomplete hold coverage risks silently missing a genuine functional defect.
**Validation:** Analogous cross-check against the SDC-declared check-type set, specialized to hold-relevant relationships.
**Industrial Notes:** Consistent with the standard sign-off principle that hold verification is never optional or frequency-conditional.
**Future Scalability:** Extends to future clock-domain-crossing-aware hold checking, foreshadowed as a future concern in Phase 14.4 Part 8.

### 2.8 Critical Path Identification and Extraction
**Definition:** The complete, itemized delay breakdown of the worst-slack path per endpoint-analysis category must be extractable and stored.
**Engineering Rationale:** A scalar slack value alone provides no diagnostic or ML-feature value regarding *why* a path is critical; the itemized path (Part 5 Stage H) is what makes this project's timing dataset genuinely useful beyond a bare pass/fail signal.
**Validation:** Cross-check that every reported WNS/TNS-contributing endpoint has a corresponding stored critical-path record.
**Industrial Notes:** Mirrors the standard sign-off deliverable of a critical-path timing report accompanying any WNS/TNS summary.
**Future Scalability:** Extends to a configurable top-N worst-paths-per-endpoint extraction depth without restructuring the extraction mechanism itself.

### 2.9 QoR Completeness
**Definition:** Every metric enumerated in Part 10 must be computed and populated for every analyzed benchmark, corner, and mode combination.
**Engineering Rationale:** Partial QoR population would silently bias any corpus-wide statistical analysis (a Phase 14.3-Part-9-style statistics report, extended here to the timing-QoR layer) toward whichever benchmarks happened to produce complete data.
**Validation:** A QoR-schema completeness check, consistent with the schema-validation discipline established across Phase 14.2/14.3/14.4.
**Industrial Notes:** Directly analogous to a production QoR-tracking dashboard's completeness requirement across a chip's full block portfolio.
**Future Scalability:** New QoR metrics are added via the same schema-versioning mechanism established in Part 10/16.

### 2.10 Manifest Completeness and Schema Compliance
**Definition:** Every artifact this document produces must be referenced in a schema-validated manifest, consistent with the manifest philosophy established in every predecessor 14.x document.
**Engineering Rationale:** An artifact absent from the manifest is, for reproducibility purposes, equivalent to a nonexistent artifact — this objective is the direct extension of Phase 14.2 Part 5/6's manifest discipline to the STA layer.
**Validation:** Full manifest schema validation as a CI gate (Part 13).
**Industrial Notes:** Consistent with the single-manifest-as-source-of-truth principle applied throughout this project.
**Future Scalability:** Extends to future artifact categories via the same additive-field, versioned-schema policy established in Phase 14.2 Part 6.

### 2.11 Multi-Corner Analysis Support
**Definition:** This document's pipeline must support analysis under multiple process/voltage/temperature (PVT) operating corners without structural modification per corner.
**Engineering Rationale:** Single-corner analysis alone cannot support a defensible claim regarding a design's true timing margin across manufacturing and operating variation, a concern directly relevant to this project's stated broader manufacturing-reliability research objective.
**Validation:** A corner-completeness check confirming every declared corner in the benchmark's configuration produced a complete analysis pass.
**Industrial Notes:** Mirrors the standard multi-corner sign-off methodology used throughout industrial ASIC timing closure.
**Future Scalability:** Extends to additional future corners (e.g., a future reliability-aging corner, directly relevant to this project's stated title) via the same per-corner pipeline parameterization.

### 2.12 Clock Network Fidelity
**Definition:** Clock propagation (Part 8) must be performed against the design's actual, post-route-extracted clock network, never an idealized zero-latency assumption.
**Engineering Rationale:** Idealized clock assumptions would systematically bias both setup and hold slack in a manner unrepresentative of true post-route timing behavior, directly undermining this phase's stated purpose as a post-route (not pre-CTS) analysis.
**Validation:** A cross-check confirming every register's clock arrival time reflects a nonzero, SPEF-derived clock-network delay rather than a default/idealized value.
**Industrial Notes:** Consistent with standard post-route sign-off methodology, which universally requires propagated (not ideal) clock analysis.
**Future Scalability:** Extends without modification to future, more complex clock-tree topologies (mesh-based or hybrid clock distribution) as they enter the benchmark corpus.

### 2.13 Auditable Timing Exception Handling
**Definition:** Every SDC-declared timing exception (false path, multicycle path, min/max delay override) must be resolved to a concrete effect on the timing graph and explicitly logged.
**Engineering Rationale:** Silent or ambiguous exception handling is among the most common sources of sign-off timing errors in industrial practice; this objective ensures every exception's effect is traceable rather than opaque.
**Validation:** A completeness check cross-referencing every SDC exception against a corresponding logged resolution record.
**Industrial Notes:** Directly mirrors the sign-off requirement for an auditable "exceptions applied" report accompanying any timing sign-off package.
**Future Scalability:** Extends to future exception types without restructuring the underlying resolution-logging mechanism.

### 2.14 Artifact Evaluation Readiness
**Definition:** Every deliverable in Part 15 must satisfy the reproducibility, availability, and functional criteria required for IEEE AE badges.
**Engineering Rationale:** Consistent with the AE-readiness objective stated as a governing goal across every predecessor 14.x document.
**Validation:** The complete Part 16 publication-readiness discussion.
**Industrial Notes:** N/A beyond what is already stated in Part 16.
**Future Scalability:** Extends automatically as future AE criteria evolve, provided this document's underlying determinism and manifest discipline are maintained.

### 2.15 Non-Overlap with Adjacent Phases
**Definition:** This document's scope must neither reproduce Phase 14.10's parasitic-extraction responsibilities nor anticipate Phase 14.12's power-integrity responsibilities.
**Engineering Rationale:** Phase-boundary discipline, maintained consistently across every 14.x document to date, is what allows each phase to be independently versioned, independently validated, and independently re-run without cascading unrelated re-computation.
**Validation:** A manual and automated (keyword/scope-linting) review confirming no IR-drop, electromigration, ECO, or physical-modification content appears anywhere in this document's stages.
**Industrial Notes:** Mirrors the standard practice of maintaining strictly scoped sign-off deliverables (a timing sign-off package is never conflated with a power sign-off package in production practice).
**Future Scalability:** N/A by design — this objective exists specifically to prevent scope creep, not to be extended.

---

## PART 3 — Inputs

| Input | Origin | Purpose in This Phase | Engineering Rationale | Validation | Failure Conditions |
|---|---|---|---|---|---|
| **Validated Routed DEF** | Phase 14.10 (originally Phase 14.1 routing stage) | Provides the physical placement/routing geometry from which the timing graph's spatial and connectivity structure is confirmed consistent with the netlist | The DEF is the authoritative record of what was actually routed; STA must analyze the design as physically implemented, not as originally synthesized, consistent with this phase's explicitly post-route scope | Cross-check DEF pin/net counts against the timing-graph construction result (Part 5, Stage B) | Missing DEF, DEF/netlist mismatch, unresolved routing (open nets) |
| **Validated Routed OpenDB** | Phase 14.10 | Provides the OpenROAD-native physical database enabling direct OpenSTA/OpenROAD interoperability without a lossy DEF re-parse | OpenDB is the binary source-of-truth format OpenROAD/OpenSTA natively share, reducing translation-layer risk relative to DEF-only interchange | OpenDB internal consistency check (a standard OpenROAD database integrity verification) | Corrupted or version-incompatible OpenDB file |
| **Validated SPEF** | Phase 14.10 | Provides the extracted parasitic (RC) data populating every net arc in the timing graph | Net-arc delay cannot be characterized without extracted parasitics; this is the single most consequential Phase 14.10 deliverable for this phase's correctness | Phase 14.10's own SPEF validation status (consumed, not re-derived, here), plus a cross-check that every net in the routed DEF has a corresponding SPEF entry | Missing SPEF, incomplete net coverage, malformed SPEF syntax |
| **Liberty Timing Libraries** | Phase 14.2 (PDK acquisition) | Provides every cell arc's delay, transition, and constraint (setup/hold) characterization | Cell arcs cannot be characterized without Liberty models; multi-corner analysis (Objective 2.11) requires one Liberty file set per declared corner | Liberty file parseability check, cell-model completeness check against every standard cell instantiated in the standardized RTL (Phase 14.4) | Missing cell model, corner/Liberty-file mismatch, malformed Liberty syntax |
| **SDC Constraints** | Phase 14.2 Part 8 / Phase 14.4 Part 8–9 (clock/reset metadata), refined per-benchmark | Declares clock definitions, generated clocks, timing exceptions, and I/O timing constraints governing the entire analysis | SDC is the sole mechanism by which design intent (as opposed to structural netlist content) enters the timing graph; without it, no required-arrival-time computation is possible | SDC syntax validation, cross-check against Phase 14.4's clock/reset metadata (`clocks.yaml`, `resets.yaml`) for consistency | Missing/incomplete SDC, clock-definition mismatch against Phase 14.4 metadata |
| **Clock Definitions** | SDC (see above) | Declares every primary clock's period, waveform, and source | Directly required by Part 5 Stage C (clock propagation) | Cross-check against Phase 14.4 Part 8's `clocks.yaml` clock-domain count | Undeclared clock domain reachable in the design |
| **Generated Clocks** | SDC | Declares derived-clock relationships (dividers, gating) relative to a primary clock | Required for correct multi-domain propagation, extending Phase 14.4 Part 8's generated-clock identification into a concrete SDC-level declaration | Cross-check against Phase 14.4's generated-clock classification | Undeclared or incorrectly related generated clock |
| **Timing Exceptions (general)** | SDC | Declares any deviation from default timing-check behavior | Required to prevent both false-violation reporting (an unhandled false path reported as a real violation) and false-clean reporting (an unhandled required exception silently ignored) | Completeness check per Objective 2.13 | Exception referencing a nonexistent pin/path |
| **False Paths** | SDC | Declares paths explicitly excluded from timing analysis by design intent | Required to prevent spurious violations on paths never intended to close timing (e.g., asynchronous configuration paths) | Cross-check that every declared false path resolves to a valid graph path | Ambiguous or unresolvable false-path specification |
| **Multicycle Paths** | SDC | Declares paths permitted more than one clock cycle for propagation | Required to prevent spurious setup violations on intentionally multi-cycle-budgeted paths | Cross-check that every declared multicycle path resolves to a valid graph path and a consistent cycle count | Multicycle specification inconsistent with the design's actual clock relationship |
| **Manifest** | Phase 14.10 aggregate manifest | Provides the authoritative cross-reference for every upstream artifact this phase consumes | Consistent with the single-manifest-as-source-of-truth principle established from Phase 14.2 onward | Manifest schema validation | Manifest referencing a missing or checksum-mismatched artifact |
| **Configuration Snapshots** | Phase 14.1–14.10 aggregate | Preserves the exact tool-version and rule-configuration state under which every upstream artifact was produced | Required for full provenance-chain reconstruction, consistent with the reproducibility discipline established throughout this project | Cross-check against the recorded tool-version metadata fields | Configuration snapshot missing or internally inconsistent |
| **Technology Files (PDK)** | Phase 14.2 Part 9 | Provides the operating-condition and corner definitions underlying the Liberty/SPEF characterization | Required for correct multi-corner dispatch (Objective 2.11) | Cross-check against Phase 14.2's PDK-compatibility metadata | PDK version mismatch against the Liberty/SPEF characterization actually used upstream |
| **Benchmark Metadata** | Phase 14.2 Part 6 | Provides `benchmark_id`, `configuration_label`, and clock-frequency-target metadata | Anchors this phase's every output record to the correct benchmark identity | Cross-check against the Phase 14.2 manifest | Metadata absent or inconsistent with the resolved SDC clock period |
| **Configuration Snapshots (rule-level)** | Phase 14.4 `normalization_rule_config.yaml` | Confirms the exact RTL-normalization rule version under which the analyzed netlist was standardized | Required for full end-to-end provenance-chain reconstruction from RTL through timing report | Cross-check against Phase 14.4's `normalization_version` metadata | Rule-configuration snapshot missing |

**Engineering Rationale (overall):** Every input above is treated as strictly read-only, consistent with the minimal-modification principle established across every predecessor document; this phase never edits, re-derives, or overrides any upstream artifact, only consumes it. Where an input is found deficient (a missing Liberty cell model, an ambiguous SDC exception), the correct engineering response is to halt this phase and escalate to the relevant upstream phase for correction, never to silently patch the input within this phase's own execution.

**Validation (overall):** A pre-flight input-completeness gate runs before Part 5's Stage A begins, checking every row of the table above against the current benchmark's manifest entry; any missing or checksum-mismatched input blocks phase execution entirely, consistent with the fail-fast philosophy established in every predecessor document's failure-handling section.

**Failure Conditions (overall):** Detailed exhaustively per-input above and aggregated in Part 12's complete failure table.

---

## PART 4 — STA Environment

**Purpose:** Describe the concrete tool and data-model environment within which every subsequent Part of this document executes, mapping this specification's abstract stage vocabulary directly onto OpenSTA's and OpenROAD's actual command and data-model surface.

**Theory / Engineering Rationale:** Consistent with the tool-fidelity discipline established in Phase 14.4 Part 18 (elaboration validation performed with the exact tool version the downstream flow itself uses, not a generic reference tool), this document specifies its environment in terms of the actual OpenSTA/OpenROAD/OpenDB toolchain rather than an abstracted, tool-independent STA description — this is a deliberate choice, since an abstracted description would risk this specification failing to anticipate genuine tool-specific behavior (OpenSTA's specific corner-handling model, its specific SPEF-parsing conventions) that materially affects reproducibility.

**OpenSTA:** The primary analysis engine, invoked either standalone (reading DEF/OpenDB, SPEF, Liberty, and SDC directly) or embedded within an OpenROAD Tcl session (the mode this document specifies as primary, given its tighter interoperability with the OpenDB physical database already established as this project's canonical physical-database format from Phase 14.1 onward). OpenSTA constructs its own internal timing-graph representation directly from the supplied netlist/Liberty/SPEF/SDC inputs, which this document's Part 5 Stage B treats as the authoritative timing-graph construction event.

**OpenROAD Interaction:** Where OpenSTA is invoked within an OpenROAD session, the physical database (OpenDB) is loaded once and shared across both the physical-design context (already finalized as of Phase 14.10) and the timing-analysis context this document specifies — this shared-database approach eliminates a class of DEF-re-parsing inconsistency risk that a standalone-OpenSTA-with-DEF-import approach would otherwise introduce.

**OpenDB:** The physical database format underlying both OpenROAD and OpenSTA's shared view of the design; this document's Part 3 input table lists OpenDB as a primary input specifically because it is the lowest-risk, most direct representation of the exact post-route physical state Phase 14.10 finalized.

**SPEF:** Parsed by OpenSTA's native SPEF reader, populating net-arc parasitics directly into the timing graph; this document requires the exact SPEF corner/net-name-mapping conventions established in Phase 14.10 to be preserved without reinterpretation at this phase's SPEF-ingestion step.

**Liberty:** Parsed by OpenSTA's native Liberty reader, populating cell-arc timing and constraint data; multi-corner analysis (Objective 2.11) requires a distinct Liberty file set per declared corner, each associated with its own operating-condition definition, loaded into a corner-specific analysis context within a single OpenSTA session (OpenSTA's native multi-corner analysis capability, rather than requiring separate tool invocations per corner).

**Timing Graph:** OpenSTA's internal graph data structure, as formally introduced in Part 1; this document treats OpenSTA's own graph representation as authoritative rather than defining a parallel, independent graph representation, consistent with this Part's overall tool-fidelity principle.

**Timing Arcs:** Populated directly from Liberty (cell arcs) and SPEF (net arcs) as described above; OpenSTA's own arc-delay-calculation methodology (its integrated delay-calculator, using the loaded Liberty timing models and SPEF-derived RC networks) is adopted as this document's authoritative delay-calculation mechanism.

**Clock Trees:** Represented within OpenSTA's timing graph as the specific subset of arcs and pins reachable from each declared clock source, propagated per Part 8's methodology; no separate clock-tree data structure beyond OpenSTA's own graph representation is introduced by this document.

**Clock Domains:** Correspond directly to OpenSTA's native clock-object model, populated from the Part 3 SDC clock declarations and cross-validated against Phase 14.4 Part 8's `clocks.yaml` domain count (Objective 2.4/2.12).

**Timing Exceptions:** Applied via OpenSTA's native SDC-exception-handling mechanism (`set_false_path`, `set_multicycle_path`, `set_max_delay`/`set_min_delay`), with this document's Part 3 input validation confirming every declared exception resolves without ambiguity before Part 5's analysis stages proceed.

**Coordinate System:** Where this phase's outputs reference physical location (e.g., a critical path's driver/sink instance coordinates, included in the critical-path corpus for downstream ML feature-extraction relevance per Phase 14.1 Part 5.1's node-feature coordinate convention), the same die-relative Cartesian coordinate system established in Phase 14.1/14.3 is used unmodified, ensuring this phase's spatially-referenced outputs remain directly joinable with Phase 14.3's spatial raster labels.

**Units:** Time quantities are reported in nanoseconds (consistent with Phase 14.3 Part 2.4/2.11–2.13's established timing-unit convention); capacitance and resistance quantities (where reported as part of a critical path's itemized delay breakdown) follow the SPEF file's own declared units, recorded explicitly per benchmark rather than assumed uniform across the corpus, since SPEF unit declarations can legitimately vary by extraction-tool configuration.

**Inputs:** The Part 3 input set.
**Outputs:** A confirmed, loaded OpenSTA analysis session per benchmark/corner/mode combination, ready for Part 5's stage pipeline.
**Dependencies:** OpenSTA, OpenROAD, OpenDB, at pinned versions recorded in this phase's configuration snapshot (Part 3).
**Runtime Expectations:** Session initialization (database load, Liberty/SPEF/SDC parsing) is the dominant cost of this Part, ranging from seconds (ISCAS/ITC-99-class) to a few minutes (CVA6/OpenTitan-class, multi-corner) — detailed further as Part 5 Stage A.
**Memory Expectations:** Dominated by the loaded OpenDB and parsed Liberty/SPEF data, consistent with Part 5 Stage A's figures.
**Failure Conditions:** Tool-version mismatch against the pinned configuration snapshot, OpenDB load failure, Liberty/SPEF/SDC parse failure — all detailed in Part 12.
**Validation:** A session-readiness check confirming the loaded design's top-module identity, clock count, and net count match the Phase 14.2/14.4/14.10 metadata expectations before Part 5 proceeds.
**Industrial Notes:** Adopting OpenSTA's native data model as authoritative, rather than introducing a parallel abstraction layer, mirrors standard industrial practice of specifying a sign-off flow in terms of the actual sign-off tool's data model, since sign-off decisions are ultimately tool-specific regardless of how technology-independent the underlying theory is.
**Reviewer Expectations:** Reviewers with OpenROAD/OpenSTA experience will specifically check whether this document's stage vocabulary maps cleanly onto real OpenSTA commands and data structures (rather than describing an idealized STA process divorced from the actual tool) — this Part is written specifically to satisfy that expectation.
**Future Extensibility:** A future additional STA engine (e.g., a commercial sign-off tool used for golden-reference cross-validation, foreshadowed in Phase 14.3 Part 8's golden-reference-comparison mechanism, now applicable at the timing layer specifically) would be integrated by adding a parallel environment-description subsection analogous to this one, without restructuring this document's stage pipeline.

---

## PART 5 — STA Architecture

**Purpose:** Define the deterministic, ten-stage (A–J) pipeline by which a loaded OpenSTA session (Part 4) is transformed into the complete Part 11 output set.

### Stage A — Initialization

**Purpose:** Load and cross-validate every Part 3 input into a ready OpenSTA analysis session.
**Theory:** Session initialization is the point at which every upstream artifact's provenance chain (Phase 14.2 through Phase 14.10) converges into a single in-memory analysis context; any inconsistency in that provenance chain is most cheaply detected here, before any analytical computation is performed.
**Engineering Rationale:** Consistent with this document's fail-fast philosophy (Part 3), initialization performs the complete pre-flight validation gate rather than deferring input-consistency checking to later stages where a failure would waste substantially more computation.
**Inputs:** The full Part 3 input set.
**Outputs:** A validated, loaded OpenSTA session, plus an initialization log recording every input's checksum and version confirmation.
**Dependencies:** OpenSTA, OpenDB, the pinned Liberty/SPEF/SDC assets.
**Runtime:** Seconds (ISCAS/ITC-99-class) to low minutes (CVA6/OpenTitan-class, multi-corner Liberty/SPEF loading).
**Memory:** 1–4 GB for the smallest benchmarks; 8–20 GB for the largest multi-corner sessions, dominated by Liberty/SPEF in-memory representation.
**Failure Conditions:** Any Part 3 input validation failure; detailed in Part 12.
**Validation:** The complete pre-flight input-completeness gate described in Part 3.
**Industrial Notes:** Mirrors the standard sign-off-flow practice of a dedicated, logged "environment setup" step preceding any actual timing computation, specifically so that environment-level failures are never conflated with genuine timing-analysis findings.
**Reviewer Expectations:** A clean separation between initialization failures and analysis-stage findings is expected by reviewers assessing whether reported timing violations are genuine design characteristics rather than artifacts of a misconfigured analysis environment.
**Future Scalability:** Extends to additional future corners/modes by parameterizing this same initialization procedure per corner/mode combination without structural change.

### Stage B — Timing Graph Construction

**Purpose:** Construct the complete timing graph (Part 1's formal definition) from the initialized session's loaded netlist, Liberty, and SPEF data.
**Theory:** Graph construction directly implements the vertex/edge formulation of Part 1 — every pin becomes a vertex, every cell arc and net arc becomes an edge, with edge delay characterization deferred to Stages D/E's actual propagation (construction itself populates structure and static arc characterization, not yet propagated arrival times).
**Engineering Rationale:** Separating graph construction from arrival-time propagation (Stage D) as a distinct pipeline stage allows Objective 2.4's completeness check to be performed immediately after construction, before any propagation computation is invested in a potentially incomplete graph.
**Inputs:** The Stage A session.
**Outputs:** The complete, constructed timing graph, plus a graph-completeness report (pin count, arc count, cross-validated against Phase 14.4's structural netlist metadata).
**Dependencies:** OpenSTA's native graph-construction mechanism.
**Runtime:** Proportional to netlist pin count; seconds for the smallest benchmarks, several minutes for the largest (CVA6/OpenTitan-class).
**Memory:** Dominant graph-storage cost of the overall analysis session; scales with pin/arc count, consistent with Part 1's stated multi-GB range for the largest benchmarks.
**Failure Conditions:** Graph incompleteness (a structural pin unreachable in the constructed graph, indicating a netlist-parsing or Liberty-characterization gap), graph cycle detection (a genuine combinational loop, which should already have been excluded at Phase 14.4 Part 6's hierarchy-standardization stage but is re-checked here defensively).
**Validation:** Objective 2.4's completeness check, plus acyclicity re-verification consistent with Phase 14.4 Part 18's defensive-redundancy principle (re-checking a property already validated upstream, since a timing-graph-level check operates at a stricter level of completeness than an RTL-hierarchy-level check).
**Industrial Notes:** This staged separation of construction from propagation mirrors how production STA tools themselves internally separate graph-build time from analysis time in their own reported runtime breakdowns, a separation this document adopts for its own stage-level reporting granularity.
**Reviewer Expectations:** A separately-reported graph-construction completeness metric (distinct from any downstream slack result) is a specific, checkable artifact substantiating Objective 2.4's claim.
**Future Scalability:** Extends without modification to future, larger benchmark additions, bounded only by memory availability.

### Stage C — Clock Propagation

**Purpose:** Propagate every declared clock (primary and generated) through the constructed timing graph, establishing each clock-tree pin's clock arrival time (clock latency) and, by comparison across register pairs, clock skew.
**Theory:** Clock propagation is formally identical to the general arrival-time propagation defined in Part 1, specialized to clock-network arcs specifically and performed prior to (and as a direct input to) Stage D's data-path arrival-time propagation, since every data-path arrival time is ultimately referenced relative to its associated clock's propagated arrival time.
**Engineering Rationale:** Performing clock propagation as an explicit, separately-validated stage (rather than folding it into general arrival-time propagation) directly operationalizes Objective 2.12's clock-network-fidelity requirement, making it possible to validate propagated (non-ideal) clock latency independently of, and prior to, the full data-path analysis.
**Inputs:** The Stage B timing graph, the Part 3 SDC clock declarations.
**Outputs:** Per-register clock arrival time, clock latency, and (via cross-register comparison) clock skew, feeding Part 8's complete clock-timing analysis.
**Dependencies:** OpenSTA's native clock-propagation mechanism (`set_propagated_clock`), applied consistent with this phase's post-route, non-ideal-clock analysis requirement.
**Runtime:** Seconds for single-clock-domain benchmarks; up to a minute for the multi-domain subset (Phase 14.4 Part 8's multi-clock-domain benchmarks).
**Memory:** Modest incremental cost over Stage B's graph-storage footprint.
**Failure Conditions:** An SDC-declared clock unreachable in the constructed graph, a generated-clock relationship unresolvable against its declared master clock; detailed in Part 12.
**Validation:** Objective 2.12's propagated-clock-latency check (confirming nonzero, SPEF-derived clock latency for every register), plus a cross-check against Phase 14.4 Part 8's clock-domain count and per-domain sequential-element association.
**Industrial Notes:** Non-ideal, fully propagated clock analysis at this stage is what distinguishes genuine post-route sign-off STA from a pre-CTS estimate, directly consistent with this phase's explicitly post-route scope and its position immediately following Phase 14.10's post-route parasitic extraction.
**Reviewer Expectations:** Reviewers will specifically check that clock latency values are nonzero and design-specific (not a suspiciously uniform default value across all registers), which would indicate an ideal-clock analysis error.
**Future Scalability:** Extends without modification to future, more complex clock-tree topologies (mesh-based or hybrid distribution networks) as noted in Objective 2.12.

### Stage D — Arrival Time Analysis

**Purpose:** Propagate data-path arrival times forward through the timing graph from every primary input and register clock/data output, using Stage C's clock-propagation results as the reference timing base.
**Theory:** Directly implements Part 1's forward recursive arrival-time formulation, $AT(v) = \max_{u \to v} (AT(u) + \delta(u,v))$ for maximum (setup-relevant) analysis and the analogous minimum-operator formulation for minimum (hold-relevant) analysis, computed simultaneously within a single graph traversal per OpenSTA's standard analysis methodology.
**Engineering Rationale:** Both maximum and minimum arrival times are computed in this single stage (rather than deferred entirely to the separate Setup/Hold analysis stages, F/G) because both quantities depend on the identical underlying graph traversal and clock-reference data — separating them here would duplicate the traversal cost without engineering benefit; Stages F/G instead perform the required-arrival-time comparison and slack computation specific to each check type, consuming this stage's shared arrival-time results.
**Inputs:** The Stage C clock-propagated graph.
**Outputs:** Per-pin maximum and minimum arrival times across the complete timing graph.
**Dependencies:** OpenSTA's native arrival-time propagation mechanism.
**Runtime:** Proportional to graph edge count; seconds to several minutes depending on benchmark scale, consistent with Stage B's figures.
**Memory:** Modest incremental cost over Stage B/C's cumulative footprint (per-pin arrival-time storage).
**Failure Conditions:** Arrival-time propagation failure at any unreachable or malformed graph region (should already be excluded by Stage B's completeness validation, but re-checked defensively); detailed in Part 12.
**Validation:** A propagation-completeness check confirming every graph vertex received both a maximum and minimum arrival-time value (excluding vertices explicitly and legitimately unreachable, e.g., an unused black-boxed stub interface per Phase 14.4 Part 14, cross-referenced and excluded consistently).
**Industrial Notes:** This single-pass, dual-bound (max/min) propagation approach mirrors standard production STA-engine internal architecture, adopted here directly rather than reimplemented independently.
**Reviewer Expectations:** N/A beyond the general completeness expectation already stated for Stage B.
**Future Scalability:** Extends without modification to future incremental-STA use (Part 1's noted future-compatible-but-unused capability), since incremental re-propagation operates on the identical underlying arrival-time data structure this stage establishes.

### Stage E — Required Arrival Time Analysis

**Purpose:** Propagate required arrival times backward through the timing graph from every primary output and register data input, using the design's SDC-declared constraints as the boundary condition.
**Theory:** Directly implements Part 1's backward recursive required-arrival-time formulation, the dual of Stage D's forward propagation.
**Engineering Rationale:** Required-arrival-time propagation is separated from arrival-time propagation as a distinct stage because it depends on a structurally distinct traversal direction (backward from outputs/register-inputs versus forward from inputs/register-outputs) and a distinct input (SDC constraints, versus Stage D's clock/input-waveform basis) — conflating the two into a single stage would obscure this document's stage-by-stage validation granularity.
**Inputs:** The Stage D arrival-time results, the Part 3 SDC constraints and declared timing exceptions.
**Outputs:** Per-pin maximum and minimum required arrival times.
**Dependencies:** OpenSTA's native required-time propagation mechanism, incorporating SDC exception resolution (Objective 2.13).
**Runtime/Memory:** Consistent with Stage D's figures, given the structurally symmetric traversal.
**Failure Conditions:** An unresolvable SDC exception (Part 3's failure condition, re-surfacing here as the point of actual application rather than merely declaration-level validation), a required-time propagation gap at any endpoint.
**Validation:** Objective 2.13's exception-application completeness check, plus a propagation-completeness check analogous to Stage D's.
**Industrial Notes:** This backward-propagation stage is where every SDC timing exception (false path, multicycle path, min/max delay override) takes concrete effect on the analysis; its correctness is foundational to every subsequent stage's validity.
**Reviewer Expectations:** Reviewers will expect this stage's exception-application log (feeding Objective 2.13) to be available as a distinct, auditable artifact, not merely inferred from the final slack results.
**Future Scalability:** Extends without modification to future additional exception types (Objective 2.13's stated future extensibility).

### Stage F — Setup Analysis

**Purpose:** Compute setup slack at every valid endpoint by comparing Stage D's maximum arrival time against Stage E's maximum required arrival time.
**Theory/Engineering Rationale/Industrial Notes:** Detailed fully in Part 6, which this stage directly operationalizes.
**Inputs:** Stage D/E maximum-analysis results.
**Outputs:** Per-endpoint setup slack, aggregated into WNS/TNS (Part 10).
**Dependencies:** OpenSTA's native setup-check mechanism.
**Runtime/Memory:** Modest incremental cost over Stage D/E (a comparison operation, not a new propagation).
**Failure Conditions:** An endpoint lacking either a Stage D arrival time or a Stage E required time (a propagation-completeness failure surfacing here); detailed in Part 12.
**Validation:** Objective 2.6's setup-verification-completeness check.
**Reviewer Expectations:** Detailed in Part 6.
**Future Scalability:** Detailed in Part 6.

### Stage G — Hold Analysis

**Purpose:** Compute hold slack at every valid endpoint by comparing Stage D's minimum arrival time against Stage E's minimum required arrival time.
**Theory/Engineering Rationale/Industrial Notes:** Detailed fully in Part 7.
**Inputs:** Stage D/E minimum-analysis results.
**Outputs:** Per-endpoint hold slack, aggregated into hold-specific WNS/TNS (Part 10).
**Dependencies:** OpenSTA's native hold-check mechanism.
**Runtime/Memory:** Consistent with Stage F.
**Failure Conditions:** Analogous to Stage F, specialized to minimum-analysis propagation completeness.
**Validation:** Objective 2.7's hold-verification-completeness check.
**Reviewer Expectations:** Detailed in Part 7.
**Future Scalability:** Detailed in Part 7.

### Stage H — Critical Path Extraction

**Purpose:** For the worst-slack endpoints identified by Stages F and G, extract and store the complete itemized timing path (every arc traversed, its individual delay contribution, and cumulative arrival time at each point along the path).
**Theory:** Critical-path extraction is a path-enumeration operation distinct from Stage D/E's arc-local propagation — reconstructing a specific path requires tracing back through the graph from a given endpoint via the specific predecessor arc that produced its recorded arrival time at each vertex, a operation OpenSTA performs on demand for a specified endpoint rather than for the graph as a whole (consistent with Part 1's stated GBA-primary/PBA-bounded-refinement methodology).
**Engineering Rationale:** This stage directly operationalizes Objective 2.8; the itemized path breakdown it produces is what transforms this phase's output from a bare scalar-slack dataset into a genuinely diagnostic and ML-feature-rich timing corpus, consistent with this project's stated ML-dataset-generation purpose (Part 1).
**Inputs:** The Stage F/G slack results, ranked to identify the extraction-eligible endpoint set (Part 9's configurable top-N depth).
**Outputs:** The complete critical-path corpus (Part 11), one itemized record per extracted path.
**Dependencies:** OpenSTA's native path-reporting mechanism (`report_checks`/path-tracing API).
**Runtime:** Proportional to the number of paths extracted (configurable depth) and each path's logic depth; seconds to low minutes even for the largest benchmarks, since extraction is applied only to the bounded worst-endpoint subset, not the full graph.
**Memory:** Modest, proportional to the extracted-path corpus size.
**Failure Conditions:** A ranked endpoint whose path cannot be reconstructed (indicating a Stage D/E internal inconsistency, escalated as a Stage D/E-attributable defect per Phase 14.4 Part 18's precedent for attributing a downstream-discovered failure to its true upstream-stage origin).
**Validation:** Objective 2.8's completeness check (every WNS/TNS-contributing endpoint has a corresponding extracted path record).
**Industrial Notes:** Mirrors the standard sign-off deliverable of a detailed critical-path timing report, typically the single most scrutinized artifact in any production timing sign-off review.
**Reviewer Expectations:** The itemized, arc-by-arc delay breakdown (rather than a bare path-delay scalar) is a specific, checkable artifact substantiating this document's stated diagnostic and ML-feature value.
**Future Scalability:** The configurable extraction depth (Part 9) allows future expansion to a broader worst-path corpus without restructuring the extraction mechanism itself.

### Stage I — QoR Extraction

**Purpose:** Compute the complete Part 10 metric set from the Stage F/G/H results.
**Theory/Engineering Rationale:** QoR extraction is a pure aggregation/summarization operation over already-computed analysis results, deliberately separated as its own stage so that a future change to QoR-metric definitions (Part 10) requires only re-running this stage against already-computed Stage F/G/H results, not a full re-analysis.
**Inputs:** The complete Stage F/G/H result set.
**Outputs:** The complete Part 10 QoR metric set, populated into the schema-validated QoR dataset (Part 11).
**Dependencies:** A metric-computation utility operating over OpenSTA's reported result set (`extract_qor.py`, Part 13).
**Runtime/Memory:** Negligible relative to Stages A–H, a summarization operation over already-computed data.
**Failure Conditions:** A QoR-schema completeness failure (Objective 2.9); detailed in Part 12.
**Validation:** Objective 2.9's QoR-completeness check.
**Industrial Notes:** Mirrors the standard practice of a dedicated QoR-reporting step distinct from the underlying analysis engine's raw output, allowing QoR-reporting-format evolution independent of the analysis engine itself.
**Reviewer Expectations:** A separately-versioned QoR-extraction stage (Part 16's schema-versioning discussion) is what allows this document's QoR schema to evolve without requiring re-analysis of already-validated benchmarks.
**Future Scalability:** New QoR metrics are added to this stage's computation logic via the schema-versioning mechanism (Part 10/16) without altering Stages A–H.

### Stage J — Validation

**Purpose:** Perform the complete, final validation pass confirming this phase's entire output set satisfies every objective in Part 2 before being marked complete and handed to Phase 14.12.
**Theory/Engineering Rationale:** Consistent with the terminal-validation-stage pattern established in Phase 14.4 Part 18 (elaboration validation as the final RTL-standardization gate) and Phase 14.3 Part 7/8 (QA and validation as the final annotation gate), this stage aggregates every Part 2 objective's individual validation mechanism into a single, comprehensive pass/fail determination for the benchmark/corner/mode combination under analysis.
**Inputs:** The complete Stage A–I output set.
**Outputs:** The Part 11 validation report.
**Dependencies:** `validate_sta.py` (Part 13).
**Runtime/Memory:** Seconds, an aggregation of already-computed per-stage validation results.
**Failure Conditions:** Any constituent objective's validation failing; detailed in Part 12.
**Validation:** This stage is itself the validation stage; its own correctness is established via the same periodic injection-testing philosophy established in Phase 14.3 Part 7 (deliberately corrupted synthetic STA results run through this stage to confirm each check fires as intended).
**Industrial Notes:** A single terminal validation gate, rather than scattered per-stage acceptance criteria alone, is what allows this phase's manifest (Part 14) to make a single, unambiguous completeness claim per benchmark.
**Reviewer Expectations:** A single, comprehensive validation report per benchmark is the specific artifact AE reviewers will consult to confirm this phase's overall completeness claim without needing to independently cross-reference every constituent stage's individual output.
**Future Scalability:** New validation checks (corresponding to future objectives) are added to this stage without restructuring Stages A–I.

---

## PART 6 — Setup Analysis

**Purpose:** Provide the complete engineering detail of setup timing analysis, extending Stage F's pipeline-level treatment with the full equation set and industrial context.

**Timing Equations:** For a launch register clocked at time $T_{launch}$ and a capture register clocked at time $T_{capture} = T_{launch} + T_{period}$ (for a same-clock-edge, single-cycle path; generalized for multicycle paths per the Part 3/Stage E exception-resolution mechanism), the setup requirement is: $AT_{data}(capture\_pin) \leq AT_{clock}(capture\_pin) + T_{period} - t_{setup} - t_{uncertainty}$, where $AT_{data}$ is the Stage D-computed maximum data arrival time, $AT_{clock}$ is the Stage C-computed clock arrival time at the capturing register, $t_{setup}$ is the capturing register's Liberty-characterized setup-time requirement, and $t_{uncertainty}$ is the Part 8-discussed configured clock-uncertainty margin. Setup slack is the signed difference between the right-hand and left-hand sides of this inequality.

**Propagation Delay:** The cumulative sum of every cell-arc and net-arc delay along the data path from launch register (or primary input) to capture register (or primary output), as computed by Stage D's forward arrival-time propagation — this is the $AT_{data}$ term above, and its itemized breakdown is precisely what Stage H's critical-path extraction makes explicit and auditable.

**Clock Latency:** The $AT_{clock}$ term above, established by Stage C's clock-propagation analysis; setup slack is directly sensitive to the *difference* between launch-clock latency and capture-clock latency (clock skew, Part 8), not merely capture-clock latency in isolation, a subtlety this document makes explicit here because it is a common source of misinterpretation when setup slack is discussed without reference to the underlying clock-latency terms.

**Data Arrival:** Synonymous with $AT_{data}$ above; the term "data arrival" is used in industrial STA reporting specifically to distinguish it from clock arrival, and this document adopts that same terminological distinction throughout.

**Required Arrival:** The right-hand side of the inequality above, computed by Stage E's backward propagation; this is the quantity against which data arrival is compared to produce the reported setup slack.

**Worst Setup Paths:** The subset of endpoints exhibiting the most negative (or least positive) setup slack, identified by ranking Stage F's complete per-endpoint result set — this ranked subset is precisely the extraction-eligible set Stage H consumes.

**Maximum Delay Analysis:** Setup analysis is, by construction, a maximum-delay analysis (Part 1's longest-path formulation) — every propagation and comparison operation described above uses the maximum-operator convention, in direct contrast to Part 7's hold analysis, which uses the minimum-operator convention throughout.

**Engineering Rationale:** Setup analysis is presented with this level of explicit equational detail (rather than merely referencing Stage F's pipeline-level description) because setup slack is this project's single most consequential timing label — it directly determines a design's achievable operating frequency (Phase 14.3 Part 2.13's critical path delay, and Part 2.14/2.15's WNS/TNS labels, all derive directly from this equation) — and any ambiguity in its precise definition would propagate as ambiguity into every downstream ML-training claim built upon it.

**Industrial Notes:** This equation set is stated in exactly the form used in standard production sign-off STA methodology and standard STA textbook treatments alike, deliberately avoiding any project-specific reformulation, consistent with this document's stated goal (Part 1) that its theoretical vocabulary should require no translation for a reader with production STA background.

**Inputs:** Stage D/E maximum-analysis results, Liberty-characterized setup-time requirements, the Part 8 clock-uncertainty configuration.
**Outputs:** Per-endpoint setup slack, feeding Part 10's WNS/TNS metrics and Stage H's critical-path extraction.
**Dependencies:** OpenSTA's native setup-check computation.
**Runtime/Memory:** Consistent with Stage F's figures.
**Failure Conditions:** Detailed in Part 12.
**Validation:** Objective 2.6.
**Reviewer Expectations:** Reviewers will specifically verify this equation set's consistency with standard STA formulation, and any deviation (a nonstandard sign convention, an omitted uncertainty term) would be flagged as a correctness concern rather than a stylistic choice.
**Future Scalability:** Extends to future recovery/removal-check requirements (an asynchronous-reset-timing check structurally analogous to setup/hold but applied to reset-release timing) via the same equation-formulation approach, should a future benchmark subset require it.

---

## PART 7 — Hold Analysis

**Purpose:** Provide the complete engineering detail of hold timing analysis, extending Stage G's pipeline-level treatment.

**Minimum Delay:** The hold requirement bounds the *minimum* propagation delay a data path must exhibit: $AT_{data}(capture\_pin) \geq AT_{clock}(capture\_pin) + t_{hold} + t_{uncertainty}$, where $AT_{data}$ here is Stage D's *minimum* arrival time (the earliest a signal could possibly arrive, accounting for the fastest-case delay through every arc along the path, in direct contrast to setup's *maximum*, or slowest-case, arrival time), $t_{hold}$ is the capturing register's Liberty-characterized hold-time requirement, and $t_{uncertainty}$ is again the Part 8 clock-uncertainty margin, now added (rather than subtracted, per Part 6) to conservatively tighten the hold requirement.

**Hold Checks:** Performed at the same launch/capture register pairs as setup analysis, but evaluated against the *same* clock edge (rather than the *subsequent* clock edge, per the setup relationship) — this is the structural essence of the setup/hold distinction: setup bounds delay against next-edge capture, hold bounds delay against same-edge capture, and both share the identical underlying timing graph and clock-propagation data (Stage C) despite governing fundamentally different physical failure modes.

**Clock Skew:** Hold slack is acutely sensitive to clock skew between launch and capture registers — a positive skew (capture clock arriving later than launch clock) directly tightens the hold margin, since it effectively extends the same-edge capture window during which prematurely arriving data could be erroneously captured; this sensitivity is why hold violations are frequently concentrated in specific clock-tree regions with high local skew (Phase 14.3 Part 2.11's clock-skew label), and why Stage C's accurate, propagated (non-ideal) clock analysis is especially consequential for hold-analysis correctness specifically.

**Launch/Capture Relationships:** Formally established per clock-domain pair in Stage E's required-arrival-time propagation, using the SDC-declared clock relationships (Part 3) to determine which specific edge pairs constitute a valid same-edge (hold-relevant) versus next-edge (setup-relevant) relationship — this determination is nontrivial for multi-clock-domain designs (Phase 14.4 Part 8's multi-clock-domain benchmark subset) where clock-domain-crossing paths require explicit SDC-declared relationship information (or, absent such information, a conservative default assumption) rather than a same-domain single-clock assumption.

**Early Timing:** A general industrial-STA term for the minimum-delay analysis regime hold checking belongs to, contrasted with "late timing" (setup's maximum-delay regime) — this document adopts this terminology consistently to align with standard STA vocabulary.

**Minimum Path Analysis:** Synonymous with the minimum-operator arrival-time propagation described in Stage D, specialized here to its hold-analysis application.

**Engineering Rationale:** Hold analysis, despite sharing its underlying timing-graph infrastructure with setup analysis, is presented as an entirely separate Part (rather than a brief addendum to Part 6) because its physical failure implication (a functional, frequency-independent defect) and its dominant sensitivity (clock skew rather than absolute propagation delay) are qualitatively distinct engineering concerns that this project's downstream ML-labeling scheme (Phase 14.3 Part 2.4 already treats timing broadly, but this document's hold-specific WNS/TNS variants, Part 10, require this distinct treatment to be meaningful as separate ML-training signals) depends on being kept analytically distinct.

**Industrial Notes:** The observation that hold violations are functional failures independent of operating frequency — and therefore can never be "fixed" merely by relaxing a design's target clock frequency, unlike setup violations — is one of the most consequential practical distinctions in production timing closure, and is restated explicitly here (having first appeared in Part 1) because it directly justifies Objective 2.7's insistence that hold verification completeness is never optional or frequency-conditional.

**Inputs:** Stage D/E minimum-analysis results, Liberty-characterized hold-time requirements, Part 8's clock-skew data.
**Outputs:** Per-endpoint hold slack, feeding Part 10's hold-specific WNS/TNS metrics and Stage H's critical-path extraction.
**Dependencies:** OpenSTA's native hold-check computation.
**Runtime/Memory:** Consistent with Stage G's figures.
**Failure Conditions:** Detailed in Part 12.
**Validation:** Objective 2.7.
**Reviewer Expectations:** Reviewers will specifically check that hold and setup results are reported as clearly distinct metric families (never conflated into a single "timing slack" figure without setup/hold disambiguation), consistent with standard sign-off reporting convention.
**Future Scalability:** Extends to future clock-domain-crossing-aware hold-checking refinement (Objective 2.7's stated future direction) as multi-domain benchmark complexity grows in future corpus expansions.

---

## PART 8 — Clock Timing Analysis

**Purpose:** Provide the complete engineering detail underlying Stage C's clock-propagation pipeline stage and its consequences for both setup (Part 6) and hold (Part 7) analysis.

**Clock Propagation:** As established in Stage C, every declared clock is propagated through its actual, post-route, SPEF-characterized clock network, producing a non-ideal, physically representative per-register clock arrival time — this is the single mechanism underlying every clock-timing quantity discussed in this Part.

**Clock Latency:** The absolute propagated delay from a clock's declared source to a given register's clock pin; reported both as an aggregate per-clock-domain statistic (mean, maximum) and per-register in the detailed clock report (Part 11), directly extending Phase 14.3 Part 2.12's clock-latency label from that document's dataset-generation-pipeline-level treatment into this phase's full post-route analysis fidelity.

**Clock Uncertainty:** The configured margin (Part 1, Part 6, Part 7) bounding unmodeled clock-network variation; this document specifies that clock uncertainty must be declared explicitly per clock domain in the Part 3 SDC (via `set_clock_uncertainty`), never left at an implicit tool default, since an implicit default would constitute exactly the kind of unstated technology/methodology assumption this document's technology-independence objective (2.2) is designed to prevent.

**Clock Skew:** The difference in propagated clock latency between any two registers within the same clock domain (or, for a clock-domain-crossing path, between registers in related domains per an SDC-declared relationship); directly extending Phase 14.3 Part 2.11's clock-skew label into this phase's full post-route computation, and directly consequential to hold-analysis margin as established in Part 7.

**Clock Domains:** Correspond to OpenSTA's native clock-object model (Part 4), cross-validated against Phase 14.4 Part 8's `clocks.yaml` domain count; this document's Part 10 QoR metrics report clock-domain count as a corpus-comparable scalar per benchmark.

**Generated Clocks:** Propagated per their declared master-clock relationship (Part 3), with generated-clock latency and skew reported as a distinct sub-category within the clock report (Part 11), consistent with Phase 14.4 Part 8's structural distinction between primary and generated clocks.

**Clock Groups:** Where multiple clock domains are declared as logically unrelated (asynchronous) via SDC (`set_clock_groups -asynchronous`), this document requires the resulting cross-domain path exclusion to be explicitly logged as a specific category of resolved timing exception (Objective 2.13), distinct from a general false-path declaration, since clock-group-based exclusion carries a distinct semantic meaning (fundamental clock-relationship independence, not merely a specific path being functionally irrelevant) that downstream ML feature extraction may wish to distinguish.

**Clock Constraints:** The complete set of SDC-declared clock-period, waveform, uncertainty, and group declarations governing this Part's analysis, cross-validated at Stage A initialization against Phase 14.2's `clock_frequency_target_mhz` metadata field for consistency.

**Engineering Rationale:** Clock timing analysis is given its own dedicated Part (rather than being folded entirely into Parts 6/7's setup/hold treatment) because clock-network behavior is the common causal factor underlying both setup and hold margin simultaneously, and because clock-network quality (latency, skew) is itself a directly meaningful, independently reportable design-quality metric (Phase 14.3 Parts 2.11/2.12) distinct from any single setup or hold slack value.

**Industrial Notes:** Explicit, non-ideal clock-network analysis at post-route stage, as specified throughout this Part, is universally required in production sign-off methodology and is never substituted with an ideal-clock assumption at this stage of a real design flow — this document's insistence on the same standard (Objective 2.12) is not a novel requirement but a direct, necessary adoption of established industrial practice.

**Inputs:** Stage C's clock-propagation results.
**Outputs:** The complete clock report (Part 11), plus the clock-latency/skew data consumed by Parts 6/7's setup/hold computations.
**Dependencies:** OpenSTA's native clock-analysis reporting mechanism.
**Runtime/Memory:** Consistent with Stage C's figures.
**Failure Conditions:** Detailed in Part 12.
**Validation:** Objective 2.12.
**Reviewer Expectations:** Reviewers will check that reported clock latency/skew values are design- and benchmark-specific (varying sensibly with clock-tree depth and design scale) rather than suspiciously uniform, as already noted in Stage C.
**Future Scalability:** Extends without modification to future clock-mesh or hybrid-distribution clock-network topologies, and to a future explicit clock-domain-crossing structural analysis phase, as noted in Phase 14.4 Part 8's own stated future-extensibility direction.

---

## PART 9 — Timing QoR (Analysis-Only)

**Purpose:** Define the analysis-only reporting methodology by which this phase's complete slack distribution is summarized, ranked, and characterized — explicitly excluding any optimization, ECO, or physical-modification activity, consistent with this document's strict phase-boundary scope.

**Critical Path Identification:** The mechanism by which Stage H's extraction-eligible endpoint set is determined — this document specifies a configurable top-N-per-category ranking (default: the worst N endpoints per setup/hold/corner/mode combination, with N itself a versioned configuration parameter, Part 13) rather than a fixed single-worst-path report, since a broader ranked corpus (rather than a single data point) is what gives this phase's output genuine ML-training value as a labeled dataset rather than a single pass/fail signal.

**Worst Negative Slack (WNS):** The minimum (most negative, or least positive if timing is fully met) slack value across the complete per-endpoint slack distribution for a given check type (setup or hold), corner, and mode — computed as a pure aggregation over Stage F/G results, with its aggregation formula (strict minimum) treated as a versioned, explicitly-stated derivation rule consistent with the derived-metric-versioning principle Phase 14.3 Part 2.14 established for the identical metric at that document's dataset-generation-pipeline level, now given its full post-route-analysis-specific computation here.

**Total Negative Slack (TNS):** The sum of every negative-slack endpoint's slack value across the complete distribution for a given check type/corner/mode — computed analogously to Phase 14.3 Part 2.15's definition, again now with full post-route fidelity.

**Timing Histograms:** A binned distribution of the complete per-endpoint slack values, computed separately per check type/corner/mode, supporting corpus-wide statistical characterization (extending Phase 14.3 Part 9's dataset-statistics methodology to this phase's specific timing-QoR layer) without requiring downstream consumers to reconstruct the distribution from the raw per-endpoint corpus themselves.

**Endpoint Classification:** Every analyzed endpoint is classified into one of several categories (register-to-register, input-to-register, register-to-output, input-to-output) reflecting its structural position in the timing graph — this classification supports downstream ML feature extraction's ability to distinguish, e.g., I/O-timing-dominated slack behavior from purely internal register-to-register slack behavior, a distinction with direct physical-design-methodology significance.

**Slack Distribution:** The complete, unaggregated per-endpoint slack corpus, retained in full (not merely as summary statistics) as the primary ML-labeling artifact this phase produces, consistent with Part 1's stated ML-dataset-generation purpose.

**Engineering Rationale:** This Part is titled and scoped explicitly as "analysis only" to make unambiguous, for both automated scope-linting (Objective 2.15) and human review, that nothing in this Part's reporting methodology constitutes or implies any optimization recommendation, ECO suggestion, or physical-design-modification action — every quantity defined here is a description of the design's current, as-routed timing behavior, never a prescription for changing it.

**Industrial Reporting Philosophy:** This Part's reporting structure (ranked critical paths, WNS/TNS summary, full distributional data, structural endpoint classification) mirrors the standard content of a production timing sign-off report package, deliberately, since this document's overarching goal (Part 1) is for its outputs to be recognizable and directly usable by a reader with production sign-off reporting experience.

**Inputs:** The complete Stage F/G/H result set.
**Outputs:** The QoR summary components of Part 11's output set (feeding directly into Part 10's formal metric definitions and Stage I's QoR extraction).
**Dependencies:** `extract_qor.py` (Part 13).
**Runtime/Memory:** Consistent with Stage I's figures.
**Failure Conditions:** Detailed in Part 12.
**Validation:** Objective 2.9.
**Reviewer Expectations:** Reviewers will specifically confirm that no optimization-adjacent content (buffer-insertion suggestions, resizing recommendations) appears anywhere in this Part's output, consistent with the explicit analysis-only scope stated in the governing task brief for this document.
**Future Scalability:** This Part's ranking/classification/distributional methodology extends without modification to a future timing-closure/ECO phase's need for a "before" baseline dataset, without this document itself ever producing "after" or corrective content.

---

## PART 10 — STA Quality Metrics

Each metric below includes its definition, importance, engineering rationale, measurement methodology, and ML relevance.

1. **Timing Endpoints (count):** Total number of valid setup/hold check endpoints in the design. *Importance:* the denominator against which coverage completeness (Objective 2.5) is measured. *Measurement:* direct count from Stage E's required-arrival-time propagation targets. *ML Relevance:* a global-feature scalar (Phase 14.1 Part 5.4-style) characterizing design scale.

2. **Timing Paths (count):** Total number of distinct timing paths reachable in the graph (a combinatorially larger quantity than endpoint count, given multiple paths may terminate at one endpoint). *Importance:* characterizes structural timing complexity beyond simple endpoint count. *Measurement:* derived from Stage B's graph structure via path-counting (bounded/approximated for very large designs to avoid combinatorial blowup, with the approximation methodology explicitly logged). *ML Relevance:* a structural-complexity feature correlated with, but distinct from, logic depth (Phase 14.3 Part 2.18).

3. **Critical Paths (count):** Number of paths actually extracted per Stage H's configurable top-N methodology. *Importance:* defines the extracted-corpus size. *Measurement:* direct count from Stage H output. *ML Relevance:* determines the granularity of the itemized-path training corpus available downstream.

4. **WNS — Setup:** Defined in Part 9. *Importance:* the single most commonly reported timing-closure headline metric. *Measurement:* Stage F aggregation. *ML Relevance:* a primary scalar prediction target, directly extending Phase 14.3 Part 2.14.

5. **WNS — Hold:** Analogous to (4), specialized to hold analysis. *Importance:* the equivalent headline metric for functional-correctness risk. *Measurement:* Stage G aggregation. *ML Relevance:* a primary scalar prediction target distinct from setup WNS, given the qualitatively different failure mode each represents (Part 7).

6. **TNS — Setup:** Defined in Part 9. *Importance:* captures violation breadth, complementing WNS's depth-only view. *Measurement:* Stage F aggregation. *ML Relevance:* directly extends Phase 14.3 Part 2.15.

7. **TNS — Hold:** Analogous to (6), specialized to hold analysis. *Importance/Measurement/ML Relevance:* analogous to (5)'s relationship to (4).

8. **Setup Violation Count:** Number of endpoints with negative setup slack. *Importance:* a direct, interpretable violation-breadth indicator complementary to TNS's magnitude-weighted view. *Measurement:* direct count from Stage F results. *ML Relevance:* supports a binarized/thresholded violation-classification training target, with class-imbalance statistics (Phase 14.3 Part 9's class-imbalance methodology) reported alongside.

9. **Hold Violation Count:** Analogous to (8), specialized to hold analysis.

10. **Arrival Time Distribution:** The full corpus of per-endpoint maximum arrival times. *Importance:* supports distributional (not merely worst-case) timing characterization. *Measurement:* Stage D output, retained in full. *ML Relevance:* a rich, per-endpoint feature set directly usable as a regression target distribution.

11. **Required Arrival Time Distribution:** Analogous to (10), from Stage E output.

12. **Slack Distribution (Setup and Hold, separately):** The complete per-endpoint slack corpus, as established in Part 9. *ML Relevance:* the primary fine-grained labeling artifact this entire phase exists to produce.

13. **Clock Latency (per-domain and per-register):** Defined in Part 8. *Importance:* characterizes clock-network quality independent of any specific data-path slack value. *Measurement:* Stage C output. *ML Relevance:* directly extends Phase 14.3 Part 2.12.

14. **Clock Uncertainty (per-domain, as configured):** Defined in Part 1/8. *Importance:* documents the conservatism margin applied, essential context for correctly interpreting any reported slack value. *Measurement:* direct read from the Part 3 SDC configuration. *ML Relevance:* a configuration-context feature required to correctly normalize slack values for cross-benchmark comparison.

15. **Clock Skew (per-domain pair, worst and average):** Defined in Part 8. *Importance:* the dominant hold-margin sensitivity factor (Part 7). *Measurement:* derived from Stage C's per-register clock-latency results. *ML Relevance:* directly extends Phase 14.3 Part 2.11.

16. **Path Depth (logic-arc count per critical path):** Number of arcs traversed along an extracted critical path. *Importance:* a structural complexity indicator of the specific critical path, distinct from corpus-wide logic depth (metric 17). *Measurement:* direct count from Stage H's extracted path record. *ML Relevance:* a per-path structural feature directly usable alongside the itemized delay breakdown.

17. **Logic Levels (design-wide maximum, cross-referenced to Phase 14.3 Part 2.18):** The maximum combinational logic-stage count across the design, as already defined structurally in Phase 14.3; this document's contribution is confirming this structural quantity's consistency against the timing graph's own longest-path structure, providing a cross-validation check between the structural (pre-timing) and timing-graph-based (this phase's) views of design depth. *ML Relevance:* supports the technology-independent-versus-technology-dependent depth-comparison analysis Phase 14.3 Part 2.18 already anticipated.

18. **Runtime (per stage, aggregate):** Wall-clock duration of each Stage A–J, and the aggregate phase runtime. *Importance:* supports performance-regression monitoring and realistic methodology-section reporting, consistent with the runtime-recording rationale established in Phase 14.3 Part 5. *Measurement:* direct timing instrumentation within `sta.py` (Part 13). *ML Relevance:* not itself a prediction target, but essential metadata for interpreting dataset-generation cost in any methodology discussion.

19. **Memory (peak, per stage and aggregate):** Analogous to (18), for peak memory consumption. *Measurement:* direct instrumentation. *ML Relevance:* analogous to (18).

20. **Analysis Iterations (corner/mode count actually completed):** The count of distinct corner/mode combinations successfully analyzed for a given benchmark, cross-validated against Objective 2.11's multi-corner completeness requirement. *Importance:* a direct completeness indicator at the multi-corner level. *Measurement:* direct count from the Stage A–J execution log. *ML Relevance:* supports corpus-wide coverage-matrix reporting (Phase 14.3 Part 9-style) at the corner/mode granularity.

21. **Validation Status (per benchmark/corner/mode):** The Stage J pass/fail determination. *Importance:* the single field gating a benchmark's inclusion in the finalized manifest (Part 14). *Measurement:* direct output of Stage J. *ML Relevance:* the primary quality-filter field any downstream training-data-selection process must consult first.

22. **Timing Exception Application Count:** The number of SDC-declared exceptions (false path, multicycle path, min/max delay override, clock groups) successfully resolved and applied, cross-validated against the Part 3 SDC-declared exception count. *Importance:* directly substantiates Objective 2.13. *Measurement:* Stage E's exception-application log. *ML Relevance:* a configuration-context feature relevant to correctly interpreting which paths were intentionally excluded from standard analysis.

23. **Endpoint Classification Distribution:** The count of endpoints per structural category (Part 9's register-to-register/input-to-register/register-to-output/input-to-output classification). *Importance:* supports stratified statistical reporting (Phase 14.3 Part 9-style) distinguishing I/O-dominated from internal timing behavior. *Measurement:* Stage F/G classification tagging. *ML Relevance:* a stratification key for any downstream training/evaluation split analysis.

**Engineering Rationale (overall):** Twenty-three metrics (exceeding the requested minimum of twenty) are specified rather than a smaller "headline-only" set (WNS/TNS alone) because this project's stated purpose (Part 1) is ML-dataset generation, which benefits substantially more from a rich, multi-granularity metric set than from a small summary sufficient only for a human sign-off review — the same reasoning Phase 14.3 Part 2's twenty-category label taxonomy already established at the dataset-generation-pipeline level, now specialized fully to the timing domain at this phase's post-route fidelity.

**Industrial Notes (overall):** Every metric above is either a standard, directly recognizable production sign-off quantity (WNS, TNS, violation counts, clock latency/skew) or a direct, well-justified extension of one (path depth, endpoint classification, exception-application count) — this document deliberately avoids introducing metrics with no clear grounding in established industrial timing-reporting practice.

**Reviewer Expectations (overall):** Reviewers will check that this metric set is genuinely computed (not merely enumerated as a wishlist) for every benchmark in the finalized corpus, a claim substantiated by Objective 2.9's QoR-completeness validation and the corpus-wide coverage-matrix reporting these metrics collectively support.

**Future Scalability (overall):** Additional metrics are added via the same schema-versioning mechanism established in Part 16, without restructuring the twenty-three metrics already defined here.

---

## PART 11 — Outputs

- **STA Reports:** Per-benchmark, per-corner, per-mode complete analysis reports summarizing Stage A–J execution and results.
- **Timing Reports:** The complete per-endpoint arrival-time, required-arrival-time, and slack corpus (setup and hold, separately), in schema-validated tabular form (consistent with the CSV-for-tabular-labels convention established in Phase 14.3 Part 6).
- **Critical Path Reports:** The Stage H itemized-path corpus, one record per extracted path, including every traversed arc's individual delay contribution.
- **Setup Reports:** The complete Part 6/Stage F setup-analysis result set, including per-endpoint slack, WNS/TNS, and violation classification.
- **Hold Reports:** The complete Part 7/Stage G hold-analysis result set, structured analogously to the setup reports.
- **QoR JSON:** The complete Part 10 metric set, schema-validated and structured per benchmark/corner/mode, consistent with the JSON QoR format already used in Phase 14.1's storage design.
- **Visualization — Slack Histograms:** Rendered per Part 9's timing-histogram methodology, as a convenience/QA layer (never a source of truth, consistent with the PNG-heatmap-as-convenience-only principle established in Phase 14.3 Part 6).
- **Visualization — Timing Graphs:** Rendered structural visualizations of the Stage B timing graph (or a representative subgraph, for the largest benchmarks where full-graph rendering is impractical), supporting human QA review.
- **Visualization — Critical Path Heatmaps:** A spatial rendering (using the coordinate system established in Part 4) of critical-path driver/sink instance locations overlaid on the design's floorplan, directly extending Phase 14.3's spatial-raster-label rendering approach to this phase's timing-path data specifically.
- **Logs:** Complete per-stage execution logs (Part 5, Stage A–J), consistent with the logging discipline established across every predecessor 14.x document.
- **Manifest:** The updated, schema-validated `sta_manifest.yaml` (Part 14), referencing every artifact this phase produces.
- **Configuration Snapshots:** The complete pinned tool-version and rule-configuration record under which this phase's analysis was performed, consistent with the configuration-snapshot discipline established from Phase 14.1 onward.

**Engineering Rationale:** This output set is structured to serve two simultaneous audiences without compromise to either: a human reviewer (via the report and visualization artifacts) and a downstream ML training pipeline (via the schema-validated tabular/JSON artifacts) — consistent with the dual-audience design principle already established in Phase 14.3 Part 6's storage-format rationale.
**Validation:** Every output artifact's presence and schema conformance is checked as part of Stage J's terminal validation pass (Part 5) before the manifest (Part 14) marks the benchmark's STA analysis complete.

---

## PART 12 — Failure Handling

| Failure Condition | Stage/Part of Origin | Detection Mechanism | Recovery Strategy | Engineering Rationale |
|---|---|---|---|---|
| **Missing SPEF** | Part 3 (input validation) | Pre-flight manifest cross-check | Halt phase execution for the affected benchmark; escalate to Phase 14.10 for re-delivery | A missing SPEF makes every net-arc delay uncharacterizable; no partial analysis is meaningful |
| **Missing Liberty** | Part 3 | Pre-flight manifest cross-check, Stage A cell-model completeness check | Halt phase execution; escalate to Phase 14.2 (PDK acquisition) for the missing cell model | Analogous to missing SPEF, specialized to cell-arc characterization |
| **Missing Clocks** | Part 3 / Stage A / Stage C | SDC cross-validation against Phase 14.4 `clocks.yaml` | Halt phase execution; escalate to the benchmark's SDC-authoring process for correction | An unanalyzed clock domain silently produces an incomplete timing graph, violating Objective 2.4/2.5 |
| **Broken Timing Graph** | Stage B | Graph-completeness and acyclicity check | Halt phase execution; escalate to Phase 14.4 (RTL standardization) if attributable to an upstream hierarchy defect, or to Stage B's own construction logic if not | Distinguishing the true root cause (upstream RTL defect versus this phase's own construction bug) is essential for correct escalation, consistent with the attribution discipline established in Phase 14.4 Part 18 |
| **Constraint Mismatch** | Part 3 / Stage A | SDC-versus-Phase-14.2/14.4-metadata cross-validation | Halt phase execution; escalate to whichever upstream metadata source (Phase 14.2 `clock_frequency_target_mhz` or Phase 14.4 `clocks.yaml`) is inconsistent with the SDC | Prevents a silent analysis-intent mismatch between this phase and its upstream provenance chain |
| **Timing Graph Corruption** | Stage B–E | Internal consistency re-verification at each stage boundary | Halt phase execution; treat as a Stage-B-attributable defect requiring investigation | Corruption discovered downstream of construction is still root-caused to construction, consistent with root-cause-not-symptom-location attribution |
| **Clock Propagation Failure** | Stage C | Propagation-completeness check | Halt phase execution; escalate per the specific unresolved clock/generated-clock relationship identified | An incomplete clock-propagation pass invalidates every downstream setup/hold result depending on it |
| **Analysis Failure (general Stage D–G)** | Stage D–G | Propagation-completeness checks per stage | Halt phase execution; attribute to the specific stage and specific unreachable graph region identified | Consistent with the per-stage validation granularity established in Part 5 |
| **Schema Failure** | Stage I / Part 11 | QoR/report schema validation | Halt phase execution for the affected artifact; do not mark the benchmark complete | Consistent with the schema-validation-as-CI-gate discipline established across every predecessor 14.x document |
| **Manifest Failure** | Part 14 | Manifest schema validation, cross-reference completeness check | Halt phase execution; do not update the aggregate manifest with an incomplete or inconsistent entry | Consistent with the manifest-completeness discipline established in Objective 2.10 |
| **Deterministic-Rerun Mismatch** | Stage J | Byte-for-byte comparison against a prior identical-input run | Escalate as a tool-version-drift or nondeterminism investigation, consistent with Objective 2.1's stated expectation of exact reproducibility | A mismatch here directly threatens this phase's central reproducibility claim and is never treated as acceptable noise |
| **Cross-Machine Validation Mismatch** | Part 2.3 / Stage J | Cross-machine rerun comparison | Escalate as an environment-dependent nondeterminism investigation | Consistent with Objective 2.3 |

**Logging (overall):** Every failure above is logged with a structured error record (benchmark identity, stage/Part of origin, specific detection-check that fired, and any available diagnostic detail) into the `failure_ledger/` directory (Part 14), preserving a complete, auditable history of every standardization attempt (successful or not) for the benchmark, consistent with the structured-error-record discipline established across every predecessor 14.x document's automation specification.

**Engineering Rationale (overall):** Every recovery strategy above escalates to the correct upstream or internal responsible stage rather than attempting an in-phase workaround, consistent with this document's minimal-modification and correct-attribution principles established throughout; this phase never silently patches around a detected defect, since doing so would undermine the very reproducibility and completeness guarantees this document exists to provide.

---

## PART 13 — Automation

| Script | Responsibility |
|---|---|
| `sta.py` | Top-level orchestrator executing the complete Stage A–J pipeline per benchmark/corner/mode combination; supports resume via per-stage checkpoint hashing (consistent with the resume philosophy established from Phase 14.1 onward), `--cluster slurm`/`--cluster k8s` execution, and a `--dry-run` mode that performs Stage A's input-validation gate only, without invoking any downstream analysis, useful for rapid pre-flight checking across a large benchmark batch before committing compute resources to full analysis. |
| `build_timing_graph.py` | Standalone utility implementing Stage B's graph-construction logic; callable independently of a full `sta.py` run for targeted graph-debugging purposes during manual review of a flagged benchmark. |
| `setup_analysis.py` | Executes Stage F's setup-analysis computation and Part 6's associated equation evaluation; produces the setup report component of Part 11. |
| `hold_analysis.py` | Executes Stage G's hold-analysis computation and Part 7's associated equation evaluation; produces the hold report component of Part 11. |
| `clock_analysis.py` | Executes Stage C's clock-propagation computation and Part 8's associated clock-latency/skew/uncertainty reporting; produces the clock report component of Part 11. |
| `extract_qor.py` | Executes Stage I's QoR-metric computation (Part 10's complete twenty-three-metric set) from already-computed Stage F/G/H results. |
| `validate_sta.py` | Executes Stage J's terminal validation pass, aggregating every Part 2 objective's constituent validation mechanism into the final pass/fail determination and producing the Part 11 validation report; exits non-zero on any hard-failure condition so it can serve as a CI gate, consistent with the CI-gate philosophy established across every predecessor 14.x document's automation specification. |

**Inputs (all scripts):** The Phase 14.10 manifest and validated artifact tree, the Part 3 Liberty/SDC/technology-file assets, and this phase's own configuration snapshots.
**Outputs (all scripts):** The complete Part 11 output set and the aggregate `sta_manifest.yaml` (Part 14).
**Dependencies:** OpenSTA, OpenROAD, OpenDB, a schema validator, a plotting library (for the Part 11 visualization outputs), standard checksum utilities.
**Failure Modes:** Each script's failures are isolated per-benchmark/corner/mode combination, consistent with the per-benchmark isolation principle established in Phase 14.2 Part 3/11 and carried through every subsequent 14.x document, and logged with structured error records per Part 12's failure ledger, never halting the full corpus batch on a single benchmark's failure.
**Support for Resume, Checkpointing, Parallel Execution, Cluster Execution, Manifest-Driven Execution, Dry-Run Mode:** All explicitly provided by `sta.py`'s top-level orchestration as described above, following the identical per-benchmark, manifest-driven, Slurm-array/Kubernetes-indexed-job parallelization pattern established consistently from Phase 14.1 Part 9 through Phase 14.4 Part 21, maintaining a single, consistent cluster-execution model across every document produced for this project to date.

**Engineering Rationale:** Seven narrowly-scoped, independently-testable scripts, mirroring the automation-decomposition philosophy applied consistently across every predecessor 14.x document, allow a targeted fix (e.g., a correction to Part 8's clock-uncertainty handling) to require re-running only `clock_analysis.py` and `validate_sta.py`, not the full `sta.py` pipeline — a direct, practical consequence of this document's Stage A–J separation (Part 5) being reflected faithfully in its automation architecture rather than collapsed into a single monolithic tool.

---

## PART 14 — Repository Structure

```
phase14_11_post_route_sta/
├── configs/
│   └── <benchmark_id>/<version_tag>/sta_config.yaml       (corner/mode declarations, clock-uncertainty settings, Stage-H extraction-depth N)
├── scripts/
│   ├── sta.py
│   ├── build_timing_graph.py
│   ├── setup_analysis.py
│   ├── hold_analysis.py
│   ├── clock_analysis.py
│   ├── extract_qor.py
│   └── validate_sta.py
├── stages/
│   └── <benchmark_id>/<version_tag>/<corner>/<mode>/
│       ├── stage_a_initialization/
│       ├── stage_b_graph/
│       ├── stage_c_clock_propagation/
│       ├── stage_d_arrival_time/
│       ├── stage_e_required_time/
│       ├── stage_f_setup/
│       ├── stage_g_hold/
│       ├── stage_h_critical_paths/
│       ├── stage_i_qor/
│       └── stage_j_validation/
├── schema/
│   ├── timing_report_schema.yaml
│   ├── qor_schema.yaml
│   └── critical_path_schema.yaml
├── runs/
│   └── <benchmark_id>/<version_tag>/<corner>/<mode>/<run_timestamp>/
├── logs/
│   └── <benchmark_id>/<version_tag>/<corner>/<mode>/<stage>.log
├── reports/
│   ├── setup/<benchmark_id>/<version_tag>/setup_report.csv
│   ├── hold/<benchmark_id>/<version_tag>/hold_report.csv
│   ├── clock/<benchmark_id>/<version_tag>/clock_report.yaml
│   ├── critical_path/<benchmark_id>/<version_tag>/critical_path_report.csv
│   └── qor/<benchmark_id>/<version_tag>/qor.json
├── visualization/
│   ├── slack_histograms/<benchmark_id>/<version_tag>/*.png
│   ├── timing_graphs/<benchmark_id>/<version_tag>/*.svg
│   └── critical_path_heatmaps/<benchmark_id>/<version_tag>/*.png
├── failure_ledger/
│   └── <benchmark_id>/<version_tag>/failure_records.yaml
├── manifests/
│   └── sta_manifest.yaml
└── docs/
    ├── sta_philosophy.md              (Part 1, human-readable rendering)
    ├── setup_hold_equations.md        (Parts 6/7, human-readable rendering)
    ├── clock_timing_methodology.md    (Part 8, human-readable rendering)
    └── qor_metric_reference.md        (Part 10, human-readable rendering)
```

**Engineering Rationale:** This structure integrates alongside, rather than nested within, the Phase 14.1–14.10 repository trees, preserving each phase's independent addressability, consistent with the repository-integration philosophy established in Phase 14.4 Part 22. The `stages/` subdirectory's explicit per-Stage-A-through-J organization directly mirrors Part 5's ten-stage pipeline structure, allowing any single stage's intermediate output to be located immediately from the pipeline diagram alone.

---

## PART 15 — Deliverables

- `reports/setup/**/setup_report.csv`, `reports/hold/**/hold_report.csv` — the complete per-endpoint setup and hold timing corpus
- `reports/critical_path/**/critical_path_report.csv` — the itemized critical-path corpus
- `reports/clock/**/clock_report.yaml` — the complete clock-latency/skew/uncertainty record
- `reports/qor/**/qor.json` — the complete twenty-three-metric QoR dataset (Part 10)
- `failure_ledger/**/failure_records.yaml` — the complete, auditable failure history per benchmark
- `visualization/**/*` — slack histograms, timing-graph renderings, and critical-path heatmaps
- `logs/**/*.log` — complete per-stage execution logs
- `manifests/sta_manifest.yaml` — the aggregate, schema-validated manifest handed to Phase 14.12
- `configs/**/sta_config.yaml` — the versioned corner/mode/extraction-depth configuration set
- `schema/*.yaml` — the schema definitions governing every tabular/JSON output
- `scripts/*.py` — the seven automation scripts (Part 13), provided as artifact-bundle components
- `docs/*.md` — publication-ready documentation

**Engineering Rationale:** This deliverable set is structured identically in spirit (though specialized in content) to the deliverable sets established in Phase 14.2 Part 13, Phase 14.3 Part 13, and Phase 14.4 Part 23, maintaining a consistent artifact-bundle shape across every phase in this project to date.

---

## PART 16 — Publication Readiness

**IEEE Reproducibility:** This document's deterministic-rerun objective (2.1), cross-machine validation objective (2.3), and terminal Stage J validation gate together constitute the specific, checkable reproducibility claim this phase makes — consistent with the reproducibility-claim structure established in Phase 14.3 Part 14 and Phase 14.4 Part 24, now specialized to the highest-stakes single label category (timing) in the entire project.

**Artifact Evaluation:** The combination of pinned OpenSTA/OpenROAD tool versions, the seven automation scripts (Part 13), and the complete failure-ledger and validation-report artifacts satisfies AE's "Functional" and "Reproducible" criteria at the post-route-STA layer, extending the identical guarantee chain established by Phase 14.2 at the acquisition layer, Phase 14.3 at the annotation layer, and Phase 14.4 at the RTL-standardization layer.

**Zenodo Compatibility:** The finalized `phase14_11_post_route_sta/` tree, alongside `sta_manifest.yaml`, is a natural fourth companion Zenodo deposit alongside the benchmark-corpus (14.2), label-corpus (14.3), and standardized-RTL (14.4) deposits, cross-referenced by DOI in all directions consistent with the provenance-chain-as-a-single-citable-unit principle established in Phase 14.3 Part 14 and reaffirmed in Phase 14.4 Part 24.

**Industrial Deployment:** This document's Stage A–J pipeline structure, its multi-corner analysis support (Objective 2.11), and its strict analysis-only scope (Part 9) are directly transferable to a production post-route sign-off timing-verification flow, not merely an academic-reproducibility convenience — extending the same dual academic/industrial applicability argument made in Phase 14.3 Part 14 and Phase 14.4 Part 24 to this phase's specific domain.

**Reviewer Expectations:** Taken together with Phase 14.2, 14.3, and 14.4, this document closes the fourth in what is now a four-part sequence of standard ML-for-EDA / AI-DTCO dataset-paper objections — "is your source RTL properly licensed and versioned" (14.2), "is your ground truth properly defined and reproducible" (14.3), "is the RTL your ground truth was computed from itself deterministic and tool-ready" (14.4), and now "is your timing analysis itself sign-off-grade, deterministic, and complete, or could an incomplete or ideal-clock-assuming STA run be silently inflating your model's apparent predictive accuracy" (this document) — leaving Phase 14.12's power-integrity analysis to address the next, distinct objection class around IR-drop and electromigration methodology, without any overlap into this document's timing-specific scope.

**Future Scalability:** Nothing in this specification is tied to the current benchmark corpus's specific scale or clock-topology complexity — the Stage A–J pipeline structure, the setup/hold equation formulations (Parts 6/7), the clock-timing methodology (Part 8), the twenty-three-metric QoR schema (Part 10), the failure-handling table (Part 12), and the automation interface (Part 13) all generalize directly to future benchmark-corpus expansion, future additional PVT corners, and future more complex clock-network topologies, without structural revision to this document — consistent with the future-extensibility commitments made at the close of every Part above, and with the identical closing commitment made in every predecessor 14.x document to date.
