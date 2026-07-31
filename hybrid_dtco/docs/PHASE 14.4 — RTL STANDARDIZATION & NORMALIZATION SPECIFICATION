# PHASE 14.4
## RTL Standardization & Normalization Specification (RSNS)

**Document Classification:** Industrial RTL Standardization & Normalization Specification
**Project:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target Conference:** IEEE International Conference on Microelectronics (ICM 2026)
**Long-Term Target Journals/Venues:** IEEE TCAD · IEEE TVLSI · DAC · ICCAD · DATE — Artifact Evaluation Ready
**Predecessor Documents:** Phase 14.1 (Industrial Dataset Engineering Specification) · Phase 14.2 (Benchmark Acquisition Specification) · Phase 14.3 (Dataset Annotation & Label Generation Specification)
**Successor Document:** Phase 14.5 (Logic Synthesis & Technology Mapping Specification)

**Boundary Statement:** This document governs the interval **after** Phase 14.2 delivers QA-complete, license-cleared, checksummed RTL and **before** Phase 14.5 performs synthesis. Its sole output is a deterministic, standardized, tool-ready RTL representation, together with the complete metadata describing every normalization decision applied. This document does not perform synthesis, technology mapping, logic optimization, timing analysis, placement, or routing. Any reader looking for those topics should proceed to Phase 14.5 and beyond; this document ends precisely where elaboration-for-synthesis begins, not one step further.

---

## PART 1 — RTL Standardization Philosophy

**Purpose:** Establish why RTL standardization is treated as an independently engineered, auditable subsystem rather than an implicit, informal cleanup step folded silently into the synthesis stage.

**Theory / Engineering Rationale:** Phase 14.2 established that benchmark acquisition must be immutable, checksummed, and license-cleared, and Phase 14.2 Part 8 already recognized that acquired RTL frequently requires preprocessing before it is tool-compatible — but deliberately scoped that preprocessing narrowly, as a lightweight dry-run-elaboration feasibility check rather than a full normalization subsystem. Phase 14.4 is that full subsystem, promoted to first-class status because the heterogeneity of the benchmark corpus (Verilog, SystemVerilog, VHDL, Chisel-generated Verilog, OpenTitan `reggen`/`topgen`-generated RTL, and gate-level netlist sources per Phase 14.2 Part 2) makes ad hoc, per-benchmark cleanup both scientifically indefensible and operationally unscalable. A model trained on physical-design outcomes derived from inconsistently normalized RTL inherits an unquantifiable confound: any observed prediction error could originate from genuine design variation or from an undocumented normalization artifact, and the two are indistinguishable after the fact unless normalization itself is deterministic, versioned, and independently auditable.

**Ground-Truth-Adjacent Philosophy:** Although this document produces no ground-truth labels (that is Phase 14.3's completed responsibility, upstream in the pipeline ordering but downstream in document sequence — see the note on pipeline-vs-document ordering below), it inherits the same immutability and determinism principles Phase 14.3 Part 1 established for labels: a standardized RTL artifact, once finalized under a given `normalization_version`, is never edited in place. A correction or methodology change produces a new `normalization_version`, and prior versions remain queryable.

**Note on Pipeline-vs-Document Ordering:** It is important to state explicitly, since this is a common point of confusion when phases are read out of sequence: Phase 14.4 (this document) executes **before** Phase 14.1's physical-design pipeline and before Phase 14.3's annotation pipeline in actual execution order — standardized RTL is the true entry point to synthesis (Phase 14.1 Stage A / Phase 14.3 Part 3's Synthesis stage). Phases 14.1–14.3 were documented first because they establish the pipeline's overall shape, the labeling taxonomy, and the acquisition discipline that this document's normalization rules must remain consistent with; Phase 14.4 now retroactively formalizes the step that was previously only informally assumed (as "RTL sources" entering Phase 14.1 Stage A). This document's outputs are what Phase 14.1 Stage A and Phase 14.3 Part 3's Synthesis stage actually consume, and both predecessor documents should be understood as implicitly depending on this document's discipline even though it is being formalized after them.

**Deterministic Standardization:** Every normalization transformation defined in this document (Parts 5–16) is implemented as a pure, deterministic function of the acquired RTL plus a pinned rule-configuration version — re-running standardization against identical inputs and an identical `normalization_version` is expected to produce byte-identical standardized RTL output, with any divergence treated as a validation failure (Part 18/20), not an accepted source of noise.

**Relationship with Phase 14.2:** This document consumes Phase 14.2's `benchmarks/manifest.yaml` and the QA-complete, license-cleared RTL tree it references as its sole entry point; no normalization stage overrides or re-derives benchmark-level identity (license, source URL, RTL version) — those fields remain read-only, exactly as Phase 14.3 established for its own relationship with Phase 14.2.

**Relationship with Phase 14.5:** This document's output — the standardized RTL tree plus its accompanying metadata (Part 19) — is the sole, exclusive input contract handed to Phase 14.5. Phase 14.5 is expected to treat every file in the standardized RTL tree as read-only and complete; any RTL-level gap discovered during Phase 14.5's synthesis attempts is resolved by revising this document's normalization rules and regenerating a new `normalization_version`, never by Phase 14.5 performing ad hoc RTL patching of its own. This mirrors the same non-negotiable boundary Phase 14.3 Part 1 established for its relationship with Phase 14.4 at the time it was written (then referring to feature extraction; the same discipline now applies one document earlier in the numbering but one step earlier in execution).

**Industrial Annotation-Adjacent Workflow:** This mirrors how a production RTL sign-off or IP-qualification team operates when accepting third-party or cross-team RTL into a shared design flow — a formal linting, normalization, and hierarchy-validation gate exists precisely so that downstream synthesis and physical-design teams never have to individually rediscover a source RTL's quirks.

**Artifact Evaluation Expectations:** AE reviewers attempting to reproduce any Phase 14.5-onward result will first need to reproduce the standardized RTL exactly; this document's determinism and versioning discipline is what makes that reproduction possible without requiring the reviewer to independently reverse-engineer normalization decisions from the standardized output alone.

**Future Extensibility:** New RTL source types (a future benchmark family using a different generator ecosystem, for example) are admitted by extending Part 2's supported-language taxonomy and adding corresponding intake/normalization rules in Parts 6–16, without altering this document's governing philosophy.

---

## PART 2 — Supported RTL Languages

**Purpose:** Enumerate every RTL source representation this specification must normalize, and define the language-specific handling boundary for each.

**Theory / Engineering Rationale:** The benchmark corpus assembled under Phase 14.2 is deliberately heterogeneous (Part 2.10 of that document) to support generalization claims across design style and language; this heterogeneity, however, is precisely what makes a single, uniform intake path impossible without an explicit per-language normalization strategy. Treating "RTL" as one undifferentiated category would silently bias the corpus toward whichever language happens to parse most easily under a single default tool configuration.

**Verilog (IEEE 1364):** The baseline, most broadly tool-compatible representation; used directly by PicoRV32 and several OpenCores projects (Phase 14.2 Parts 2.4, 2.5). Verilog sources are normalized primarily for naming/interface consistency (Parts 10–11) rather than language-construct translation, since Verilog is natively Yosys-compatible.

**SystemVerilog (IEEE 1800):** Used by Ibex, CVA6, and OpenTitan (Phase 14.2 Parts 2.6, 2.8, 2.9). SystemVerilog requires the most extensive construct-compatibility screening (Part 16) of any supported language, since modern SystemVerilog files frequently contain verification-oriented constructs (interfaces, assertions, some class-based elements in adjacent files) that are not synthesizable and must be identified and separated from the design-intent RTL before standardization proceeds.

**VHDL (IEEE 1076):** Present in a subset of ITC-99 and OpenCores sources (Phase 14.2 Parts 2.2, 2.4). VHDL normalization follows an analogous rule set to Verilog/SystemVerilog but requires a distinct parser front-end; this document defines VHDL-specific handling wherever a rule diverges from the Verilog/SystemVerilog path (notably in Part 9's reset-normalization and Part 11's naming-convention sections, where VHDL's entity/architecture separation changes what "module name" and "port name" mean structurally).

**Generated Verilog (Chisel/FIRRTL, RocketChip/TinyRocket):** Per Phase 14.2 Part 2.7, this source category is emitted from Chisel via the FIRRTL compiler and requires acquisition-time recording of both the Chisel source commit and the generated-Verilog snapshot. This document's Part 13 governs the additional normalization concerns specific to generator-emitted RTL, distinct from hand-written RTL, particularly around generator-introduced naming patterns and generate-block artifacts that a hand-written-RTL normalization pass would not anticipate.

**Generated RTL (OpenTitan `reggen`/`topgen`):** Per Phase 14.2 Part 2.9, OpenTitan's register-interface and top-level integration RTL is produced by the project's own configuration-driven code generation tooling rather than hand-written. Part 13 defines how this document treats `reggen`/`topgen` output as a distinct generated-RTL sub-category with its own reproducibility requirements (the generation step itself must be re-run deterministically as part of standardization, not merely copied from a prior acquisition).

**Gate-Level Netlist Sources (EPFL Suite):** Per Phase 14.2 Part 2.3, the EPFL combinational benchmark suite is distributed as gate-level Verilog/BLIF rather than behavioral RTL. This document treats gate-level sources as a structurally distinct intake category throughout (flagged explicitly wherever a Part's rules assume behavioral RTL, e.g., Part 5's top-module detection and Part 7's parameter resolution are substantially simplified or not applicable for pre-mapped gate-level sources), consistent with the distinct-acquisition-subcategory treatment Phase 14.2 Part 2.3 already established.

**Inputs:** The Phase 14.2 benchmark manifest's `rtl_language` metadata field (Phase 14.2 Part 6), which this document uses as the dispatch key selecting which language-specific normalization path (Parts 5–16) a given benchmark follows.

**Outputs:** A per-benchmark language classification confirmed (or corrected, with justification logged) at intake time, feeding every subsequent Part of this document.

**Dependencies:** Front-end parsers capable of each listed language: a Verilog/SystemVerilog parser (this document assumes a Yosys-compatible front-end, optionally supplemented by a dedicated SystemVerilog frontend such as `slang` for stricter IEEE 1800 conformance checking ahead of Yosys ingestion), a VHDL front-end (e.g., GHDL as an analysis/elaboration front-end), and the Chisel/FIRRTL/`sbt` toolchain for regenerating Chisel-sourced Verilog deterministically.

**Runtime Expectations:** Language classification itself is near-instantaneous (a manifest lookup); the cost lies downstream in Parts 3 and 6–16, scaled per language as detailed there.

**Memory Expectations:** Negligible at this stage.

**Failure Conditions:** A benchmark whose `rtl_language` metadata field does not match any of the six categories above is treated as an intake-blocking condition requiring this document to be extended (Part 2's stated future-extensibility path) before that benchmark can proceed.

**Validation:** A cross-check against Phase 14.2's recorded `rtl_language` field, plus a lightweight structural sniff-test (file extension distribution, presence of `entity`/`architecture` keywords for VHDL versus `module`/`endmodule` for Verilog/SystemVerilog) confirming the acquisition-time classification remains accurate at standardization time.

**Industrial Notes:** Maintaining six distinct, explicitly-scoped language-handling paths rather than one generalized "RTL ingestion" routine mirrors how production RTL sign-off flows maintain distinct linting/elaboration configurations per source language rather than forcing a lowest-common-denominator single path.

**Reviewer Expectations:** A reviewer auditing cross-language generalization claims will expect this document to demonstrate that language-specific handling did not introduce a systematic normalization bias favoring one language's design style over another; Parts 10–11's naming/interface standardization is designed specifically to remove language-surface differences while preserving structural/semantic content.

**Future Extensibility:** A future seventh language category (e.g., a Chisel-adjacent HDL such as SpinalHDL, or a direct FIRRTL-native intake path bypassing Verilog emission) is added as a new row in this taxonomy with a corresponding new normalization path, without disturbing the existing six.

---

## PART 3 — RTL Intake Workflow

**Purpose:** Define the ordered sequence of operations by which a QA-complete Phase 14.2 benchmark is transformed into a standardization-ready working representation, prior to any content-level normalization being applied.

**Theory / Engineering Rationale:** Intake must be separated from normalization proper (Parts 5–16) because intake failures (a missing dependency file, an unresolvable include path) are categorically different from normalization decisions (how a reset signal is renamed) — conflating the two makes failure triage substantially harder, since a normalization-rule bug and a missing-file error would otherwise surface through the same failure path.

**Repository Discovery:** The intake process begins by resolving, from the Phase 14.2 manifest, the complete file set constituting a given benchmark's RTL — this is non-trivial for monorepo-structured sources (OpenTitan) where only a specific IP subdirectory is in scope, and for Chisel-based sources where the "RTL" is itself a build product rather than a static file set. Repository discovery produces an explicit, enumerated file manifest (distinct from and more granular than Phase 14.2's benchmark-level manifest entry) listing every source file that will participate in standardization.

**Hierarchy Extraction:** A preliminary module/entity hierarchy is extracted via a lightweight structural parse (not full elaboration) identifying every module/entity declaration and every instantiation reference across the discovered file set — this preliminary hierarchy is later validated and finalized in Part 6, but is first produced here as an intake-stage artifact to detect gross file-set incompleteness (an instantiated module with no corresponding declaration anywhere in the discovered file set) before investing further effort in normalization.

**Dependency Graph Generation:** From the preliminary hierarchy, a directed dependency graph is constructed (module A depends on module B if A instantiates B, or if A's file `includes` a header B resides in) — this graph is the structural backbone consumed by Part 6 (hierarchy standardization), Part 12 (macro/include resolution), and Part 18 (elaboration validation), and its generation at the intake stage (rather than being re-derived independently in each downstream Part) ensures all downstream Parts operate on a single, consistent dependency view.

**RTL Parsing:** A full syntactic parse (not yet elaboration) of every discovered file is performed using the language-appropriate front-end (Part 2), producing an abstract syntax representation retained for the remainder of the standardization process — this is the point at which gross syntax errors (as opposed to semantic/elaboration issues, handled in Part 18) are first detected.

**Validation (Intake-Stage):** A structural completeness check confirms every dependency-graph edge resolves to a discovered file, every parsed file produced a syntactically valid parse tree, and no file was silently skipped due to an unrecognized extension or encoding issue.

**Inputs:** The Phase 14.2 QA-complete RTL tree for a given `(benchmark_id, version_tag)`, plus that benchmark's `rtl_language` classification (Part 2).
**Outputs:** An enumerated file manifest, a preliminary hierarchy/dependency graph, and a validated syntax-tree representation per file, all retained as intake-stage artifacts (Part 4's directory organization defines where these are stored).
**Dependencies:** The language-appropriate parser front-ends (Part 2), plus a graph-construction utility for the dependency graph.
**Runtime Expectations:** Seconds for small benchmarks (ISCAS, PicoRV32) to a few minutes for the largest monorepo-derived sources (OpenTitan block extraction, full CVA6), dominated by file discovery and full parsing rather than the lightweight preliminary-hierarchy step.
**Memory Expectations:** 1–4 GB for the majority of benchmarks; up to 8 GB for OpenTitan's larger subdirectory extractions given the monorepo's total file count even when only a subset is in scope.
**Failure Conditions:** Unresolvable include path, instantiation of a module absent from the discovered file set, syntax error in any file, or an encoding issue (non-UTF-8 source, historically occasional in older academic benchmarks) — every intake failure halts standardization for that specific benchmark only, consistent with Phase 14.2's per-benchmark isolation principle, and is logged with a structured error record rather than silently working around the gap.
**Validation:** As stated above; additionally, the intake-stage file manifest's file count and aggregate line count are cross-checked against Phase 14.2's `rtl_loc` metadata field (Phase 14.2 Part 6) as a sanity bound, flagging large discrepancies for investigation.
**Industrial Notes:** This staged intake discipline (discovery → hierarchy → dependency graph → parse → validate, each with its own checkpoint) mirrors how a production RTL compiler's front-end pipeline is itself staged, and is what allows Part 21's automation to resume from the correct checkpoint after an interrupted run rather than restarting intake from scratch.
**Reviewer Expectations:** Reviewers assessing reproducibility will expect the intake process to be fully mechanical and free of manual, undocumented file-selection judgment calls — the explicit file manifest produced here is the artifact that demonstrates this.
**Future Extensibility:** New source-discovery strategies (e.g., a future package-manager-based dependency resolution for a benchmark family that adopts one) plug into this same discovery → hierarchy → dependency-graph → parse → validate sequence without restructuring it.

---

## PART 4 — Directory Organization

**Purpose:** Define the filesystem layout in which every intake- and normalization-stage artifact is stored, preserving strict separation between the untouched Phase 14.2 source and every derived, standardized representation.

**Theory / Engineering Rationale:** Phase 14.2 Part 4 established that acquired RTL (`benchmarks/rtl/`) is strictly read-only and verbatim; this document's directory design extends that same discipline one layer downstream — standardized RTL is always a *derived*, separately stored artifact, never an in-place modification of the Phase 14.2 tree, so that the acquisition layer's audit integrity (Phase 14.2 Part 4's stated rationale) remains intact indefinitely regardless of how many normalization passes are later applied.

```
rtl_standardization/
├── original/
│   └── <benchmark_id>/<version_tag>/
│       └── (read-only symlink or reference into benchmarks/rtl/, never copied/duplicated)
├── standardized/
│   └── <benchmark_id>/<version_tag>/<normalization_version>/
│       ├── rtl/                       (fully standardized, tool-ready source)
│       ├── top_module.yaml            (Part 5 output)
│       ├── hierarchy.yaml             (Part 6 output)
│       ├── parameters.yaml            (Part 7 output)
│       ├── clocks.yaml                (Part 8 output)
│       ├── resets.yaml                (Part 9 output)
│       ├── interface_map.yaml         (Part 10 output)
│       ├── naming_map.yaml            (Part 11 output)
│       ├── macro_resolution.yaml      (Part 12 output)
│       ├── blackbox_stubs/            (Part 14 output)
│       └── generated_artifacts/       (Part 13 output, generator-sourced RTL only)
├── logs/
│   └── <benchmark_id>/<version_tag>/<normalization_version>/<stage>.log
├── reports/
│   ├── lint/<benchmark_id>/<version_tag>/lint_report.yaml
│   ├── elaboration/<benchmark_id>/<version_tag>/elaboration_report.yaml
│   └── qa/<benchmark_id>/<version_tag>/qa_report.yaml
├── metadata/
│   └── <benchmark_id>/<version_tag>/<normalization_version>/standardization_metadata.yaml
└── configs/
    └── <benchmark_id>/normalization_rule_config.yaml
```

**Inputs:** The intake-stage artifacts from Part 3.
**Outputs:** The directory tree above, fully populated for every standardized benchmark.
**Dependencies:** None beyond the filesystem and the automation scripts (Part 21).
**Runtime/Memory Expectations:** Negligible beyond the standardization work itself; directory materialization is an organizational operation.
**Failure Conditions:** A `normalization_version` directory partially populated due to an interrupted run is detected via Part 20's completeness check and never mistaken for a finalized standardized artifact.
**Validation:** A structural completeness check verifies every expected subdirectory/file is populated for a given `(benchmark_id, version_tag, normalization_version)` triple before that version is marked standardization-complete in the manifest (Part 19/22).
**Industrial Notes:** The explicit `original/` versus `standardized/` separation, with the former containing only references rather than duplicated files, keeps disk footprint bounded even as many `normalization_version`s accumulate over the project's lifetime, while preserving Phase 14.2's single-source-of-truth principle for the acquired RTL itself.
**Reviewer Expectations:** This layout directly demonstrates, structurally rather than merely by written assertion, that standardization never mutates acquired source — a common and easily-verified AE reproducibility check.
**Future Extensibility:** Additional per-benchmark artifact categories (e.g., a future `formal_equivalence/` directory holding formal-equivalence-checking results between original and standardized RTL, foreshadowed in Part 18) slot in as new top-level categories under `standardized/<benchmark_id>/<version_tag>/<normalization_version>/` without disturbing the existing structure.

---

## PART 5 — Top Module Detection

**Purpose:** Deterministically identify the top-level module/entity for every benchmark, since every downstream Part of this document and every stage of Phase 14.5 onward requires an unambiguous top-level reference point.

**Theory / Engineering Rationale:** Top-module identity is not always self-evident from RTL structure alone. A module instantiated by no other module in the discovered file set is a *necessary* but not *sufficient* condition for being the intended top — a benchmark's file set may include multiple uninstantiated modules (e.g., alternate configurations, deprecated variants, or files belonging to a testbench mistakenly swept into the RTL file set during Part 3 discovery) that satisfy the same structural criterion without being the design's actual entry point.

**Automatic Detection:** The primary detection strategy identifies every module/entity with zero incoming instantiation edges in the Part 3 dependency graph as a top-module *candidate*, then applies a disambiguation ranking: candidates whose name matches the benchmark's `configuration_label` (Phase 14.2 Part 6) or whose file path matches a conventional top-level naming pattern (e.g., a file named identically to the benchmark's declared top in project documentation) are ranked above structurally-uninstantiated candidates lacking such a match.

**Manual Override:** Where automatic detection yields either zero candidates (a cyclic or fully-mutually-instantiated file set, rare but possible in malformed or partial acquisitions) or multiple equally-ranked candidates, a manual override is required — recorded explicitly in `top_module.yaml` with a `detection_method: manual_override` field and a justification string, never silently defaulting to an arbitrary candidate. This manual decision, once made, becomes part of the deterministic record for that `(benchmark_id, version_tag)` and is reused automatically on every subsequent re-standardization unless the underlying RTL changes.

**Hierarchical Projects:** For monorepo-derived sources (OpenTitan) and generator-emitted sources (RocketChip family), the "top module" is scoped to the specific IP block or core configuration selected at acquisition time (Phase 14.2's `configuration_label` field), not the monorepo's overall top-level integration unless that integration-level top is itself the benchmark unit in question — this scoping decision is recorded explicitly rather than left to be inferred from the dependency graph alone, since a monorepo's true top-level module is frequently *not* the intended benchmark-level top.

**Multiple Candidates:** Where legitimate ambiguity remains after ranking (e.g., a benchmark family shipping several genuinely independent top-level variants, as with several ITC-99 benchmarks), each variant is treated as a **separate `benchmark_id`** per Phase 14.2 Part 5's naming convention (`<suite>_<core_or_circuit_name>_<config_label>`) rather than this document attempting to select one arbitrarily — top-module ambiguity at the RTL-structure level is resolved at the benchmark-identity level established one document earlier, not invented anew here.

**Validation Strategy:** Every detected or manually-overridden top module is validated by confirming full hierarchical reachability — every other module/entity in the discovered file set must be reachable from the declared top via the dependency graph, with any unreachable module flagged (feeding Part 6's unused-module detection) rather than silently retained as dead weight in the standardized output.

**Inputs:** The Part 3 dependency graph, Phase 14.2's `configuration_label` and `benchmark_id` metadata.
**Outputs:** `top_module.yaml`, recording the declared top module/entity name, detection method (`automatic` or `manual_override`), and (where applicable) the justification for a manual override.
**Dependencies:** The dependency-graph construction utility from Part 3.
**Runtime Expectations:** Near-instantaneous for the automatic path (a graph traversal); manual-override cases are bounded by human review turnaround, tracked as a pending-status flag consistent with Phase 14.2 Part 7's handling of ambiguous license cases.
**Memory Expectations:** Negligible, bounded by the dependency graph's size, consistent with Part 3.
**Failure Conditions:** Zero candidates with no successful manual override, or a declared top module failing the full-reachability validation check, both block standardization for that benchmark.
**Validation:** As described above (full hierarchical reachability).
**Industrial Notes:** This mirrors the top-level-identification step every RTL sign-off flow requires before synthesis can even be scoped, typically handled informally via project convention in a single-team context but requiring explicit, auditable resolution in a heterogeneous multi-source corpus such as this one.
**Reviewer Expectations:** Explicit, logged justification for every manual-override decision preempts a class of reviewer skepticism around whether benchmark selection/scoping was performed consistently across the corpus.
**Future Extensibility:** The ranking heuristics used in automatic detection are themselves versioned as part of `normalization_rule_config.yaml` (Part 4), so a future improvement to the disambiguation ranking is a new, auditable rule-configuration version rather than a silent behavioral change.

---

## PART 6 — Hierarchy Standardization

**Purpose:** Finalize and normalize the module/entity instantiation hierarchy established preliminarily in Part 3 and anchored at the top module identified in Part 5.

**Theory / Engineering Rationale:** A preliminary hierarchy (Part 3) is sufficient for gross completeness checking but insufficient as a standardization artifact in its own right, since it may still contain unreachable modules, ambiguous instantiation naming, or ordering that varies arbitrarily depending on file-discovery order rather than logical dependency order — all of which introduce non-determinism risk into downstream tooling that is sensitive to file/module ordering (certain Yosys read-order-sensitive behaviors, for instance).

**Module Graph:** The finalized module graph is a directed acyclic graph (verified acyclic explicitly, since a genuine instantiation cycle indicates either a parsing error at Part 3 or a genuinely malformed source requiring intake-blocking treatment) rooted at the Part 5 top module, with every node annotated by its source file, its parameter set (cross-referenced to Part 7), and its instance count within the design (a module instantiated many times, e.g., a bit-slice in a datapath, is recorded once as a graph node with an instance-count annotation, not duplicated per instance).

**Dependency Ordering:** From the module graph, a deterministic topological ordering (leaf modules first, top module last) is computed and recorded — this ordering governs the file concatenation/read order used when standardized RTL is later consumed by Phase 14.5's synthesis front-end, removing a subtle but real source of non-determinism present in naive alphabetical or discovery-order file listing.

**Unused Module Detection:** Any module/entity present in the Part 3 discovered file set but unreachable from the Part 5 top module (per that Part's reachability validation) is explicitly classified here as unused, and is **excluded from the standardized RTL output** rather than silently carried forward — this exclusion is recorded in `hierarchy.yaml` with the excluded module's identity and file origin, preserving auditability of the exclusion decision without polluting the standardized tool-input tree with dead code that could otherwise cause spurious synthesis warnings or, worse, be inadvertently instantiated by a Phase 14.5 configuration error.

**Recursive Hierarchy Validation:** For any module graph containing recursive generate-block-driven self-instantiation patterns (rare but present in some parameterizable datapath generators), the graph construction explicitly bounds recursion depth using the resolved parameter set from Part 7, converting what would otherwise be an unbounded structural pattern into a concrete, finite, standardized hierarchy — recursion that cannot be bounded from the resolved parameter set (indicating either a missing parameter override or a genuinely malformed generate construct) is treated as a Part 18 elaboration-validation failure.

**Inputs:** Part 3's preliminary hierarchy and dependency graph, Part 5's declared top module, Part 7's resolved parameter set (a forward dependency noted here and resolved by this document's overall processing order placing parameter resolution logically prior to hierarchy finalization in implementation, even though it is presented as Part 7 for narrative continuity with the intake-to-output ordering).
**Outputs:** `hierarchy.yaml`, recording the finalized module graph, dependency ordering, and the explicit unused-module exclusion list.
**Dependencies:** Graph algorithms for acyclicity verification and topological sort, consistent with Part 3's dependency-graph utility.
**Runtime Expectations:** Seconds for the majority of the corpus; low tens of seconds for the largest hierarchies (CVA6, OpenTitan block-level extractions with deep sub-hierarchies).
**Memory Expectations:** Bounded by module count, negligible relative to the parsing-stage memory costs already incurred in Part 3.
**Failure Conditions:** A genuine instantiation cycle, an unbounded recursive generate pattern, or a top module found unreachable from itself (a defensive check against a Part 5 detection error) all block standardization for that benchmark.
**Validation:** Acyclicity verification (a formal graph property, checked exactly, not approximately) and a cross-check that every module in the finalized hierarchy has a resolvable file origin.
**Industrial Notes:** Deterministic dependency ordering of this kind is standard practice in any production RTL build system (e.g., how a Makefile-driven or `fusesoc`-style RTL build orders file compilation) and is adopted here for the identical reason — removing file-order-dependent non-determinism from downstream tool behavior.
**Reviewer Expectations:** The explicit, logged unused-module exclusion list is a specific, checkable artifact that demonstrates the standardized RTL tree is neither incomplete (missing something the top module needs) nor bloated (carrying dead code that could confound gate-count-based structural labels established in Phase 14.3 Part 2.16/2.18).
**Future Extensibility:** The bounded-recursion handling generalizes directly to any future benchmark family with more extensive generate-block usage than the current corpus exhibits, without requiring new graph-construction logic beyond parameterizing the existing bound-resolution step against Part 7's parameter set.

---

## PART 7 — Parameter Resolution

**Purpose:** Resolve every module parameter, generic, and generate-block condition to a single, concrete, recorded value set per benchmark, eliminating parameterization as a source of ambiguity in the standardized RTL.

**Theory / Engineering Rationale:** Phase 14.2 Part 2.6 and Part 2.8 already established that Ibex and CVA6 are parameterizable core families where the exact configuration (extension set, PMP region count, cache sizes) must be pinned and recorded as part of benchmark identity (`configuration_label`); this document's Part 7 is where that pinning is made concrete at the RTL level, converting the abstract `configuration_label` metadata field into an explicit, resolved parameter-value manifest applied directly to the RTL's parameter/generic declarations.

**Parameter Overrides:** Every top-level parameter (Verilog `parameter`/`localparam`, VHDL `generic`) reachable from the Part 5 top module is resolved to a concrete value, either from an explicit override supplied at acquisition/configuration time (matching the `configuration_label`) or from the RTL's own declared default where no override is specified — every resolved value is recorded regardless of whether it came from an override or a default, so that `parameters.yaml` is always a complete, self-contained record rather than a partial override list requiring cross-reference back to RTL defaults to interpret fully.

**Generate Blocks:** Every `generate`/`for-generate` construct conditioned on a now-resolved parameter is evaluated at standardization time (not deferred to synthesis-time elaboration) — the resulting concrete instance set (which generate-block iterations are active, how many instances of a given sub-module exist) is recorded in `hierarchy.yaml` (Part 6) as an annotation on the relevant module graph node, and this resolution is what allows Part 6's hierarchy finalization to treat generate-block-driven structure as a concrete, non-ambiguous part of the module graph rather than a deferred construct.

**Configuration Locking:** Once a benchmark's parameter set is resolved and recorded, it is locked for that `(benchmark_id, version_tag, normalization_version)` triple — a different configuration of the same underlying core (e.g., Ibex with a different PMP region count) is, consistent with Phase 14.2 Part 2.6's stated concern about configuration-driven identity, always treated as a distinct `benchmark_id`/`configuration_label` pair, never as a runtime-selectable option within a single standardized RTL artifact.

**Parameterized RISC-V Cores:** For Ibex, CVA6, and RocketChip-family benchmarks specifically, parameter resolution additionally cross-validates the resolved value set against the Phase 14.2-recorded `configuration_label` string, flagging any mismatch (e.g., a `configuration_label` claiming `RV32IMC` while the resolved parameter set indicates the compressed-instruction extension is disabled) as a standardization-blocking inconsistency requiring resolution before the benchmark can proceed — this cross-check is the primary mechanism preventing configuration-identity drift between the acquisition-layer metadata and the RTL-layer reality.

**Inputs:** Phase 14.2's `configuration_label` metadata, the Part 3 parsed syntax trees, Part 5's declared top module.
**Outputs:** `parameters.yaml`, recording every resolved parameter/generic value and every generate-block resolution decision.
**Dependencies:** A parameter-evaluation engine capable of resolving Verilog/SystemVerilog parameter expressions and VHDL generic expressions, including arithmetic and conditional expressions commonly used in parameter defaults.
**Runtime Expectations:** Seconds for the majority of the corpus; up to a minute for the most heavily parameterized generate-block-driven sources (RocketChip-family, OpenTitan `topgen`-generated integration RTL).
**Memory Expectations:** Modest, bounded by the number of distinct parameter/generate-block evaluation contexts, well under 1 GB for all corpus members.
**Failure Conditions:** An unresolvable parameter expression (referencing an undefined external constant, for instance), a `configuration_label` cross-validation mismatch, or an unbounded generate-block recursion (feeding back into Part 6's failure condition) all block standardization for that benchmark.
**Validation:** The `configuration_label` cross-check described above, plus a completeness check confirming every parameter/generic reachable from the top module received an explicit resolved-value record.
**Industrial Notes:** Locking configuration at standardization time, rather than leaving it synthesis-tool-resolvable, mirrors how a production IP-integration flow typically pins a configurable IP's parameter set at RTL-freeze time rather than leaving it open through to synthesis, precisely to avoid configuration drift between design intent and implementation.
**Reviewer Expectations:** The explicit cross-validation against acquisition-time `configuration_label` metadata is a specific, checkable mechanism directly answering a reviewer's likely question about whether "the RISC-V core configuration used" is trustworthy given the corpus's use of highly configurable core families.
**Future Extensibility:** A future benchmark family with a more complex, multi-stage parameter-resolution process (e.g., a design using both compile-time and elaboration-time configurable parameters) extends this Part's evaluation engine without changing its recorded-output contract (`parameters.yaml`'s schema, formalized in Part 19).

---

## PART 8 — Clock Normalization

**Purpose:** Identify every clock signal within a benchmark's hierarchy and normalize its representation into a single, consistent, tool-independent clock-metadata record.

**Theory / Engineering Rationale:** Phase 14.2 Part 8 previously noted, in general terms, that a synthesis-oriented clock constraint must be authored where none is provided upstream; this document's Part 8 is the formalized, general clock-handling subsystem that produces the concrete clock identification feeding that constraint authoring, extended to handle the full range of clocking complexity present across the corpus rather than the single-clock case implicitly assumed by Phase 14.2's original brief description.

**Clock Identification:** Primary clock identification proceeds from the Part 5 top module's port list, using a combination of structural heuristics (a single-bit input port driving the clock input of the majority of sequential elements reachable in the hierarchy) and, where available, the Phase 14.2-recorded naming-convention metadata (Phase 14.2 Part 8's per-benchmark clock-port-name mapping table) as a higher-confidence signal than structural inference alone.

**Multiple Clocks:** Where a benchmark's hierarchy contains genuinely distinct clock domains (present in a subset of OpenCores peripheral IP with independent bus/core clocks, and in some OpenTitan blocks), every distinct clock source is identified and recorded as a separate entry in `clocks.yaml`, each independently associated with the specific sequential-element subset it drives — this per-domain association is what allows Phase 14.5 onward to apply domain-appropriate constraints rather than a single global clock assumption that would misrepresent a genuinely multi-clock design.

**Generated Clocks:** Internally generated clocks (clock-gating-cell outputs, clock-dividers) are distinguished explicitly from primary (port-level) clocks in `clocks.yaml`, tagged with their generating logic's location in the hierarchy — this distinction matters because a generated clock's frequency is a function of its primary clock and its generating logic, not an independent constraint input, and conflating the two would produce an incorrect or redundant constraint at the Phase 14.5 boundary.

**Clock Metadata:** Every identified clock (primary or generated) is recorded with: its port or internal signal name, its associated Phase 14.2 `clock_frequency_target_mhz` value (for primary clocks directly, or a derived expected frequency relationship for generated clocks), its driven sequential-element count, and its domain membership.

**Clock Consistency:** A consistency check cross-validates that every sequential element reachable from the top module is associated with exactly one identified clock domain (primary or generated) — a sequential element reachable by no identified clock indicates either a clock-identification gap requiring investigation, or a genuinely asynchronous/latch-based element requiring explicit classification rather than silent omission.

**Inputs:** Part 5's top module, Part 6's finalized hierarchy, Phase 14.2's `clock_frequency_target_mhz` and naming-convention metadata.
**Outputs:** `clocks.yaml`, the complete per-benchmark clock-domain record.
**Dependencies:** The Part 3 syntax-tree representation, used to identify sequential-element clock-port connections structurally.
**Runtime Expectations:** Seconds for single-clock benchmarks (the majority of the corpus); up to a minute for the multi-clock-domain subset requiring per-domain sequential-element association.
**Memory Expectations:** Modest, comparable to Part 6's hierarchy-processing footprint.
**Failure Conditions:** A sequential element with no resolvable clock association (per the consistency check above) that cannot be classified as an intentional asynchronous/latch element blocks standardization pending manual classification.
**Validation:** The clock-consistency check described above, applied exhaustively across every sequential element in the finalized hierarchy.
**Industrial Notes:** Explicit multi-clock-domain identification at this stage is what allows Phase 14.5's constraint authoring to be correct-by-construction for multi-clock designs rather than requiring per-benchmark manual constraint correction discovered only after a synthesis run produces implausible timing results.
**Reviewer Expectations:** Reviewers with production STA/constraint-authoring experience will specifically check whether multi-clock designs in the corpus (a nontrivial subset, given OpenTitan and some OpenCores peripherals) are handled correctly rather than being force-fit into a single-clock assumption — this Part's explicit domain-association mechanism is the direct answer to that expectation.
**Future Extensibility:** Clock-domain-crossing (CDC) structural analysis, not required for this document's scope but a natural adjacent concern, can be layered onto the domain-association data already captured here in a future phase without requiring new clock-identification infrastructure.

---

## PART 9 — Reset Normalization

**Purpose:** Identify every reset signal, determine its polarity and synchronicity, and normalize this information into a single consistent metadata record, extending the informal reset-handling description in Phase 14.2 Part 8 into a complete, general subsystem.

**Theory / Engineering Rationale:** Reset polarity (active-high/active-low) and synchronicity (synchronous/asynchronous) genuinely vary across this corpus's constituent benchmarks by design convention, not by error — normalizing this variation into a consistent metadata representation (rather than attempting to rewrite every benchmark's RTL to a single reset convention, which would risk introducing functional bugs into acquired, previously-verified third-party RTL) is the approach consistent with this document's minimal-RTL-modification principle (Part 1, and consistent with Phase 14.2 Part 8's original "normalization is metadata, not RTL modification, wherever possible" stance).

**Reset Polarity:** Every identified reset signal is classified as active-high or active-low via structural inspection of its usage pattern in sequential-element reset conditions (e.g., `if (!rst_n)` versus `if (rst)`), with the classification recorded per reset signal rather than assumed uniform across a benchmark, since some designs (particularly generator-emitted RTL) mix conventions across sub-hierarchies.

**Reset Synchronization:** Every identified reset signal is additionally classified as synchronous or asynchronous based on whether it appears in a sequential element's sensitivity list (asynchronous) or only within the synchronous clocked block's conditional logic (synchronous) — this classification is recorded per reset signal per clock domain (Part 8), since a design may legitimately use synchronous reset in one domain and asynchronous reset in another.

**Metadata Generation:** The complete reset classification (polarity, synchronicity, associated clock domain, driven sequential-element count) is recorded in `resets.yaml`, structured analogously to Part 8's `clocks.yaml` for consistency.

**Reset Mapping:** Where multiple reset signals exist within a single clock domain (e.g., a global reset and a domain-specific soft reset), the mapping between each reset signal and the specific sequential-element subset it drives is recorded explicitly, mirroring Part 8's per-domain clock-to-sequential-element association — this mapping is what allows Phase 14.5's reset-strategy configuration to be generated correctly rather than assuming a single global reset applies uniformly.

**Inputs:** Part 6's finalized hierarchy, Part 8's clock-domain associations, the Part 3 syntax-tree representation.
**Outputs:** `resets.yaml`, the complete per-benchmark reset-signal record.
**Dependencies:** The same structural-inspection utilities used in Part 8, extended to reset-specific usage-pattern recognition.
**Runtime Expectations:** Consistent with Part 8's runtime figures, given the structurally similar analysis approach.
**Memory Expectations:** Consistent with Part 8.
**Failure Conditions:** A sequential element with no resolvable reset association that cannot be classified as an intentional no-reset element (rare but occasionally legitimate, e.g., certain pipeline-stage registers in performance-optimized designs) blocks standardization pending manual classification, mirroring Part 8's clock-consistency failure handling.
**Validation:** An exhaustive per-sequential-element reset-association check, analogous to Part 8's clock-consistency validation.
**Industrial Notes:** Recording rather than rewriting reset convention is the same discipline a production multi-IP integration flow applies when integrating third-party IP blocks with differing reset conventions at their boundaries — convention differences are documented and bridged at the integration boundary rather than forcibly unified within each IP's own RTL.
**Reviewer Expectations:** Explicit per-signal polarity/synchronicity classification, rather than a single corpus-wide assumption, is the specific evidence a reviewer would look for to confirm the standardization process did not silently misinterpret a benchmark's actual reset behavior — a class of error that could otherwise produce subtly incorrect downstream timing/functional results without any obvious failure signal.
**Future Extensibility:** Reset-domain-crossing analysis, analogous to the future CDC extension noted in Part 8, can be layered onto this Part's per-domain reset-association data in a future phase without new infrastructure.

---

## PART 10 — Interface Standardization

**Purpose:** Normalize the external port interface of every benchmark's top module into a consistent, predictable representation without altering the underlying design's functional port set.

**Theory / Engineering Rationale:** Downstream automation (Phase 14.1 Stage A and beyond) benefits substantially from a uniform interface description convention; without it, every downstream tool invocation must special-case each benchmark's idiosyncratic port-naming and bus-representation choices, which is precisely the per-benchmark special-casing this document's Part 8 (of Phase 14.2) already identified as undesirable and which this Part now resolves generally rather than piecemeal.

**Port Naming:** Every top-module port is recorded in `interface_map.yaml` with both its original (as-acquired) name and, where applicable, its mapped standardized alias — the underlying RTL port name is never altered (consistent with this document's minimal-RTL-modification principle), and standardization instead occurs at the metadata-mapping layer, exactly as Phase 14.2 Part 8 established for clock/reset port naming specifically, now generalized to the full port set.

**Bus Normalization:** Multi-bit buses following common structural conventions (byte-enable vectors, valid/ready handshake pairs, address/data bus pairs) are identified and annotated with a recognized bus-role tag (e.g., `role: valid_ready_handshake`) where a confident structural match exists, supporting downstream tooling that benefits from bus-role awareness (e.g., Phase 14.1's feature-extraction pin-classification logic) without requiring that tooling to independently re-derive bus semantics from raw port names.

**Signal Width Consistency:** Every port's declared bit-width is recorded and cross-validated against its usage at every instantiation site reachable in the hierarchy (relevant primarily for hierarchical sub-block interfaces, less so for the top-level interface itself, but recorded uniformly for consistency) — a width mismatch discovered here is treated as an elaboration-validation failure (Part 18), surfaced early rather than allowed to propagate into a confusing downstream synthesis error.

**Direction Checking:** Every port's declared direction (input/output/inout) is validated against its actual usage pattern within the module (a port declared as output but never driven, for instance, is flagged) — this check operates at the structural level available at standardization time and is a lighter-weight precursor to the fuller elaboration-stage checking performed in Part 18, not a replacement for it.

**Inputs:** Part 5's top module, Part 3's syntax-tree representation, Phase 14.2 Part 8's existing clock/reset naming-convention metadata (extended, not duplicated, by this Part's broader port coverage).
**Outputs:** `interface_map.yaml`, the complete port-naming, bus-role, width, and direction record.
**Dependencies:** The Part 3 syntax-tree representation.
**Runtime Expectations:** Seconds to low tens of seconds, scaling with top-module port count, which is bounded even for the largest corpus members (CVA6, OpenTitan blocks) relative to their internal gate/module count.
**Memory Expectations:** Negligible.
**Failure Conditions:** A width mismatch or an undriven-output/unused-input direction anomaly not attributable to an intentionally unused interface (e.g., a debug port genuinely left unconnected in this benchmark's configuration) blocks standardization pending classification.
**Validation:** The width-consistency and direction-checking mechanisms described above.
**Industrial Notes:** Bus-role tagging of this kind mirrors interface-metadata conventions used in production IP-XACT-style IP packaging, adopted here in a lighter-weight, project-specific form appropriate to this corpus's scale rather than adopting the full IP-XACT standard.
**Reviewer Expectations:** A reviewer assessing whether downstream feature extraction (Phase 14.1) can meaningfully distinguish, e.g., a handshake-control signal from a general data-path signal will look for exactly this kind of structural interface annotation as evidence the distinction is principled rather than incidental.
**Future Extensibility:** Additional recognized bus-role patterns (e.g., a future AXI-role tagging scheme, directly relevant given the project's stated broader interest in AMBA-protocol RTL) extend the bus-normalization rule set without altering the underlying port-naming/width/direction mechanisms.

---

## PART 11 — Naming Convention Normalization

**Purpose:** Establish a single, consistent naming convention applied at the metadata-mapping layer across module names, file names, and signal names corpus-wide, resolving the naming heterogeneity inherent to a multi-source benchmark corpus.

**Theory / Engineering Rationale:** Module naming, file naming, and signal naming vary across this corpus's constituent suites by historical convention (academic benchmarks, OpenCores projects, and modern RISC-V-ecosystem projects each follow distinct, internally-consistent but mutually-divergent conventions) — without a normalization-mapping layer, any downstream automation attempting corpus-wide pattern matching (e.g., a feature-extraction routine identifying all "control/status register" modules) would need to independently learn each suite's convention, which does not scale and is not principled.

**Module Naming:** A standardized module-name alias is generated per module (distinct from the underlying RTL declaration, which remains unaltered, consistent with this document's stated minimal-modification principle throughout) following a single project-wide convention (`<benchmark_id>__<original_module_name>`), recorded in `naming_map.yaml`, disambiguating module names that would otherwise collide across benchmarks sharing a common generic name (e.g., multiple benchmarks independently declaring a module literally named `fifo` or `mux`).

**File Naming:** A parallel standardized file-naming alias is generated for every source file, following the same disambiguation logic, supporting consistent file organization within the `standardized/rtl/` tree (Part 4) without requiring the original file names (which are preserved as the authoritative reference in the `naming_map.yaml` mapping) to be altered in a way that would break traceability back to the Phase 14.2 acquisition record.

**Signal Naming:** Top-level and cross-hierarchy-boundary signal names (clock, reset, and the Part 10 interface-mapped ports specifically) receive standardized aliases as already established in Parts 8–10; this Part's signal-naming coverage extends that same aliasing convention to any additional cross-benchmark signal-naming pattern not already covered by the clock/reset/interface-specific handling (for instance, a common but non-standardized "interrupt" or "debug" signal naming pattern appearing informally across several OpenCores projects with inconsistent spelling/capitalization).

**Reserved Keywords:** A specific validation pass checks every original signal, module, and file name against the reserved-keyword lists of every downstream tool this corpus is intended to support (Yosys, OpenROAD, OpenSTA, and the target PDK's cell-naming conventions) — any collision (an RTL signal happening to share a name with a tool-reserved keyword, an occasional but real occurrence particularly with older academic benchmarks predating some tools' reserved-keyword lists) is resolved via the same aliasing mechanism used elsewhere in this Part, with the collision and its resolution explicitly logged.

**Inputs:** Part 6's finalized hierarchy, Part 10's interface map, the Part 3 file manifest.
**Outputs:** `naming_map.yaml`, the complete module/file/signal naming-alias record, including all reserved-keyword collision resolutions.
**Dependencies:** A maintained reserved-keyword list per downstream tool, kept in sync with the specific tool versions pinned in Phase 14.2/14.3's metadata.
**Runtime Expectations:** Seconds to low tens of seconds, scaling with module and file count.
**Memory Expectations:** Negligible.
**Failure Conditions:** An unresolvable naming collision (extremely rare given the disambiguation strategy's benchmark-ID-prefixing approach, but retained as a defensive check) blocks standardization pending rule-set extension.
**Validation:** A completeness check confirming every module, file, and cross-hierarchy-boundary signal received an alias record, plus the reserved-keyword collision check described above.
**Industrial Notes:** Prefixing every standardized alias with `benchmark_id` rather than attempting a more elaborate globally-unique-name-generation scheme is a deliberately simple, low-risk convention choice, consistent with this document's general preference (echoed from Phase 14.2's benchmark-ID design) for simple, deterministic, easily-audited naming schemes over cleverness.
**Reviewer Expectations:** The explicit original-name-to-alias mapping, rather than an irreversible renaming, is what allows a reviewer (or downstream researcher) to always trace a standardized-tree signal back to its exact original RTL declaration — a specific, checkable reproducibility guarantee.
**Future Extensibility:** Additional downstream tool reserved-keyword lists (for a future tool added to the flow) are incorporated by extending the maintained keyword-list set referenced above, without altering the aliasing mechanism itself.

---

## PART 12 — Macro and Include Resolution

**Purpose:** Fully resolve every preprocessor-level construct (`` `include``, `` `define``/macro usage, and conditional-compilation directives) into a single, concrete, standardized RTL representation free of unresolved preprocessor dependencies.

**Theory / Engineering Rationale:** Preprocessor directives introduce a class of non-determinism and tool-portability risk distinct from the language-level constructs handled elsewhere in this document — the same source file can elaborate to functionally different RTL depending on which header search path or macro-definition set is active at compile time, which is fundamentally incompatible with this document's determinism principle (Part 1) unless fully resolved and fixed at standardization time.

**`` `include`` Resolution:** Every `` `include`` directive is resolved to a specific, concrete file (using the Part 3 dependency graph's already-established include-edge tracking), and the *effect* of that inclusion — the included content, verbatim — is what participates in downstream parsing and normalization, rather than the standardized RTL tree retaining unresolved include directives that would require the exact original header search path to be reconstructed at every future re-elaboration.

**Header Files:** Every header file (`.vh`, `.svh`, and VHDL package-equivalent files) participating in a resolved `` `include`` chain is itself tracked as a first-class file in the Part 3 file manifest and Part 4 directory structure, ensuring header-file provenance is preserved with the same rigor as primary RTL source files, not treated as an incidental, untracked dependency.

**Macro Expansion:** Every `` `define``-based macro reachable from the Part 5 top module's hierarchy is expanded to its concrete value at standardization time, with the expansion recorded in a macro-resolution log (`macro_resolution.yaml`) mapping every macro invocation site to its resolved value — this is distinct from, and complementary to, Part 7's parameter resolution, since macros and parameters are handled by genuinely different language mechanisms (textual preprocessing versus elaboration-time constant resolution) even though both ultimately serve a configuration role.

**Conditional Compilation:** `` `ifdef``/`` `ifndef``/`` `else``/`` `endif`` blocks are resolved deterministically based on the benchmark's locked configuration (Part 7), with only the active branch's content retained in the standardized RTL output and the inactive branch's content explicitly logged (not silently discarded without record) in `macro_resolution.yaml`, preserving the ability to audit what alternative configuration paths existed in the original source even though they are not part of this specific standardized artifact.

**Dependency Tracking:** The complete macro/include resolution process updates the Part 3 dependency graph to its final, fully-resolved form — this final dependency graph, not the Part 3 preliminary version, is what is recorded as authoritative in `hierarchy.yaml` (Part 6) and consumed by Part 18's elaboration validation.

**Inputs:** Part 3's preliminary dependency graph and file manifest, Part 7's locked parameter/configuration set.
**Outputs:** `macro_resolution.yaml`, the fully-resolved standardized RTL tree (with all `` `include``/macro/conditional-compilation directives resolved to concrete content), and an updated authoritative dependency graph feeding Part 6.
**Dependencies:** A preprocessor-resolution engine compatible with the Verilog/SystemVerilog preprocessor specification and, for VHDL sources, the equivalent package/context-resolution mechanism.
**Runtime Expectations:** Seconds for the majority of the corpus; up to a few minutes for the most macro-heavy generated sources (OpenTitan `reggen`-generated register-interface RTL is a notable heavy user of parameterized macro patterns).
**Memory Expectations:** Modest, bounded by the total resolved-content size, which for this corpus remains well under 1 GB even for the largest benchmarks.
**Failure Conditions:** An unresolvable `` `include`` path (a header file absent from the discovered file set), an undefined macro reference, or a conditional-compilation branch whose condition cannot be resolved from the locked configuration set all block standardization pending investigation.
**Validation:** A completeness check confirming zero unresolved preprocessor directives remain in the standardized RTL output — this is a hard, mechanically-checkable acceptance criterion (a simple scan for remaining `` ` `` -prefixed directives in the output tree), not a judgment call.
**Industrial Notes:** Fully resolving preprocessor dependencies at standardization time, rather than deferring resolution to each downstream tool invocation, mirrors the "flattened," fully-resolved RTL delivery convention frequently used in production IP handoff specifically to eliminate build-environment-dependent elaboration differences between the IP provider's and IP consumer's toolchains.
**Reviewer Expectations:** The explicit, auditable macro-resolution log (including the logged-but-inactive conditional-compilation branches) is the specific artifact that demonstrates configuration decisions were deliberate and traceable rather than accidental byproducts of whatever preprocessor environment happened to be active during a given standardization run.
**Future Extensibility:** A future benchmark family relying more heavily on VHDL generic-package-based configuration (a mechanism structurally analogous to, but syntactically distinct from, Verilog macro/conditional-compilation) extends this Part's resolution engine with a VHDL-specific resolution path without altering the recorded-output contract.

---

## PART 13 — Generated RTL Handling

**Purpose:** Define the additional, generator-specific normalization requirements for RTL sources that are themselves the output of an upstream code-generation toolchain (RocketChip/TinyRocket's Chisel/FIRRTL pipeline, OpenTitan's `reggen`/`topgen` tooling), extending Part 2's taxonomy-level distinction into concrete standardization procedure.

**Theory / Engineering Rationale:** Generator-emitted RTL introduces a reproducibility concern absent from hand-written RTL: the acquired Verilog snapshot (Phase 14.2 Part 2.7) is only one deterministic output of a generator-toolchain-plus-configuration pair, and full reproducibility requires the generator toolchain's exact version to be pinned and, ideally, the generation step to be independently re-runnable and verified to reproduce the identical acquired snapshot — otherwise, an unstated generator-version drift between acquisition time and any future re-standardization attempt could silently produce different RTL than what was actually used for a published result.

**RocketChip / TinyRocket (Chisel/FIRRTL):** Per Phase 14.2 Part 2.7, the Chisel source commit and generated-Verilog snapshot are both recorded at acquisition time. This document's Part 13 additionally requires, at standardization time, a **regeneration verification step**: the pinned Chisel toolchain (specific Scala/`sbt`/FIRRTL-compiler versions) is invoked against the pinned Chisel source commit, and the freshly regenerated Verilog is diffed against the Phase 14.2-acquired Verilog snapshot — an exact match confirms full generator-level reproducibility; any diff is treated as a standardization-blocking discrepancy requiring investigation (most commonly attributable to an unpinned or drifted toolchain component, occasionally to a genuine acquisition-time recording error), never silently accepted or silently resolved by preferring one snapshot over the other without explicit justification recorded in the standardization metadata.

**Chisel / FIRRTL (general handling, beyond RocketChip specifically):** Any future benchmark sourced from the broader Chisel ecosystem follows the identical regeneration-verification procedure defined above for RocketChip/TinyRocket, since the reproducibility concern is a property of the Chisel/FIRRTL generation mechanism generally, not specific to any one project built on it.

**OpenTitan `reggen`:** OpenTitan's register-interface RTL is generated from per-IP-block register configuration files (Hjson format) via the project's `reggen` tool. Standardization requires the pinned `reggen` tool version (tracked as part of OpenTitan's overall pinned commit hash, per Phase 14.2 Part 2.9) to be re-invoked against the pinned Hjson configuration during standardization, with the same regeneration-verification diff-check applied as described above for Chisel-sourced RTL.

**OpenTitan `topgen`:** For any benchmark scope including OpenTitan's top-level integration RTL (as opposed to an individually-extracted peripheral block), the analogous `topgen`-driven regeneration-verification step is required, operating on the project's top-level system configuration (also Hjson-based) rather than per-block register configuration.

**Generated Artifacts:** All intermediate generator-toolchain artifacts (FIRRTL intermediate representations, `reggen`/`topgen` intermediate configuration-processing outputs) produced during the regeneration-verification step are retained in the `standardized/<benchmark_id>/<version_tag>/<normalization_version>/generated_artifacts/` directory (Part 4), preserving the complete generation provenance chain rather than discarding intermediate representations once the final Verilog match is confirmed.

**Version Locking:** The exact generator-toolchain version set (Scala version, `sbt` version, FIRRTL compiler version for Chisel-sourced RTL; `reggen`/`topgen` tool version and their Python-ecosystem dependency versions for OpenTitan-sourced RTL) is recorded in `standardization_metadata.yaml` (Part 19) as a distinct field set from the RTL-source-level tool versions (Yosys/OpenROAD, tracked from Phase 14.1/14.3 onward) — generator-toolchain versioning and physical-design-toolchain versioning are governed by independent version axes, consistent with this document's general preference (echoed throughout the 14.x series) for precisely-scoped, non-conflated versioning dimensions.

**Inputs:** Phase 14.2's pinned generator-source commit hashes (Chisel source, Hjson configuration files) and generator-toolchain version metadata.
**Outputs:** A regeneration-verification report (pass/fail plus diff detail on failure) per generator-sourced benchmark, the retained intermediate generated artifacts, and the generator-toolchain version record within `standardization_metadata.yaml`.
**Dependencies:** The pinned Chisel/`sbt`/FIRRTL toolchain, or the pinned `reggen`/`topgen` toolchain and its Python dependencies, as applicable per benchmark.
**Runtime Expectations:** Several minutes for Chisel-based regeneration (dominated by Scala/`sbt` compilation overhead, consistent with general Chisel-ecosystem build-time characteristics) to under a minute for `reggen`/`topgen`-based regeneration (a comparatively lightweight Python-based generation process).
**Memory Expectations:** 4–8 GB for Chisel/`sbt`-based regeneration (JVM-based toolchain overhead); under 2 GB for `reggen`/`topgen`-based regeneration.
**Failure Conditions:** A regeneration-verification diff failure, an unresolvable generator-toolchain dependency (e.g., an `sbt`-managed dependency no longer resolvable from its originally-pinned package repository, a real long-term-archival risk this Part explicitly anticipates and flags for the long-term-archival discussion in Part 24), or a Hjson configuration parse failure all block standardization for the affected benchmark.
**Validation:** The exact-match regeneration-verification diff described above is itself the primary validation mechanism for this entire Part.
**Industrial Notes:** Requiring regeneration verification, rather than trusting a single acquired snapshot indefinitely, mirrors the discipline a production IP-generator-consuming team applies when a generated-IP deliverable is version-locked at integration time specifically to catch silent generator-version drift before it propagates into a downstream design.
**Reviewer Expectations:** This is one of the more operationally demanding checks in this document, and reviewers with specific Chisel/RocketChip or OpenTitan experience will recognize and specifically credit its presence, since generator-reproducibility gaps are a known, real failure mode in academic RISC-V-core-based research that is frequently left unaddressed in comparable prior work.
**Future Extensibility:** Any future generator-toolchain-based benchmark family (a hypothetical future benchmark using a different HCL such as SpinalHDL or Amaranth, foreshadowed in Part 2's future-extensibility note) follows this identical regeneration-verification pattern, generalized as "any RTL source whose acquisition-time snapshot is itself a build product of a versioned toolchain requires regeneration verification," a principle rather than a RocketChip/OpenTitan-specific procedure.

---

## PART 14 — Black-Box Management

**Purpose:** Identify and formally manage any module reference within a benchmark's hierarchy that cannot be resolved to synthesizable RTL content within the acquired source itself, converting an otherwise-fatal elaboration gap into an explicitly declared, standardization-time decision.

**Theory / Engineering Rationale:** Phase 14.2 Part 8 anticipated this concern in general terms ("hard-macro or vendor-IP references... rare in this benchmark set, but a real concern for any future benchmark"); this document's Part 14 formalizes the concrete handling procedure now that the full standardization pipeline (Parts 3–13) provides the necessary hierarchy and dependency-graph infrastructure to detect such references systematically rather than relying on ad hoc discovery during a downstream synthesis failure.

**Memory Macros:** SRAM/register-file macro instantiations lacking synthesizable RTL implementation within the acquired source (present in a small subset of the corpus, most notably certain OpenTitan memory instances and any RocketChip-family configuration using a memory-compiler-generated cache array) are identified via the Part 6 hierarchy's unresolved-instantiation detection (an instantiated module with no corresponding declaration anywhere in the fully-resolved, Part 12-macro-expanded file set) and classified explicitly as memory-macro black-boxes.

**Vendor Primitives:** Any instantiation referencing a vendor-specific or technology-specific primitive cell (rare in this open-source-focused corpus by deliberate acquisition-time selection per Phase 14.2 Part 2, but retained as a general-purpose detection category for future corpus expansion) is classified analogously.

**Behavioral Replacements:** Where a black-box reference has a documented, functionally-equivalent open behavioral model available (for instance, a simple behavioral SRAM model suitable for functional simulation/elaboration purposes, distinct from a physical-implementation-ready memory-compiler output), that behavioral replacement is substituted into the standardized RTL tree, with the substitution explicitly logged (original reference, replacement source, and justification) in a dedicated black-box resolution record — this substitution is treated as a normalization decision requiring the same auditability as every other decision in this document, never as an invisible convenience patch.

**Stub Generation:** Where no suitable behavioral replacement exists, a minimal, explicitly-non-functional interface stub (matching the black-boxed module's port list and width, per Part 10's interface-standardization data, but containing no functional implementation) is generated and placed in `standardized/<benchmark_id>/<version_tag>/<normalization_version>/blackbox_stubs/`, allowing elaboration-level structural validation (Part 18) to proceed while making unambiguously explicit — both in the stub's own generated content via a header comment and in the standardization metadata — that this module cannot be treated as synthesis-ready in its current form and requires resolution (via a future memory-compiler integration, most commonly) before Phase 14.5 can produce a physically meaningful result for the affected hierarchy region.

**Inputs:** Part 6's finalized hierarchy and its unresolved-instantiation detection, Part 10's interface data for any black-boxed module requiring stub generation.
**Outputs:** A black-box resolution record (per black-boxed module: classification, resolution method — behavioral replacement or stub — and justification), plus any generated stub files.
**Dependencies:** A maintained library of available open behavioral replacement models, where applicable, consistent with the open-source-focused acquisition philosophy established in Phase 14.2.
**Runtime Expectations:** Seconds per black-boxed module; the corpus as currently scoped (Phase 14.2 Parts 2.1–2.9) contains few such cases, keeping aggregate runtime for this Part negligible relative to Parts 3–13.
**Memory Expectations:** Negligible.
**Failure Conditions:** An unresolved-instantiation reference that cannot be classified as either a legitimate black-box case (memory macro, vendor primitive) or a genuine file-set-completeness gap (an intake-stage error properly belonging to Part 3, not this Part) is escalated for manual investigation rather than defaulted to either classification.
**Validation:** A completeness check confirming every unresolved instantiation identified by Part 6 has a corresponding black-box resolution record — no unresolved instantiation may pass through to the finalized standardized RTL tree without an explicit disposition.
**Industrial Notes:** This mirrors the standard handling of hard-macro black-boxing in any production RTL-to-GDSII flow, where a memory compiler's or foundry's macro model is explicitly black-boxed during RTL-level work and only resolved to a physical implementation at a later, dedicated integration stage — this document adopts the identical discipline, appropriately scoped to this project's open-PDK, largely macro-light benchmark corpus.
**Reviewer Expectations:** Explicit black-box disposition records are what allow a reviewer to distinguish "this design genuinely contains no unresolved dependencies" from "this design's apparent completeness is an artifact of silently-stubbed content" — a distinction directly relevant to trusting any downstream gate-count or macro-density label (Phase 14.3 Parts 2.19) computed from the standardized RTL.
**Future Extensibility:** A future corpus expansion including more macro-heavy commercial-adjacent designs would substantially increase this Part's operational load; the behavioral-replacement-library mechanism is deliberately structured as an extensible, maintained asset (rather than a one-off per-benchmark decision) specifically to scale to that future scenario.

---

## PART 15 — Vendor Primitive Handling

**Purpose:** Define PDK-specific compatibility handling for any RTL construct whose synthesizability or interpretation depends on the target technology, extending Part 14's general black-box mechanism with PDK-specific detail.

**Theory / Engineering Rationale:** Although this corpus is deliberately open-PDK-focused (Phase 14.2 Part 9 established Sky130, GF180, and ASAP7 as the supported targets, with no vendor-proprietary PDK in scope), certain RTL patterns can still exhibit PDK-sensitive interpretation even without an explicit vendor-primitive instantiation — most notably, technology-specific memory-macro sizing assumptions embedded in generate-block parameter defaults, and any RTL-level clock-gating-cell inference pattern that a given synthesis tool maps differently depending on the target PDK's available gate library.

**Sky130 Compatibility:** As the corpus's primary target (Phase 14.2 Part 9), every benchmark's standardized RTL is validated for Sky130-path compatibility as the default, required compatibility check — any construct identified during Parts 3–14 as PDK-sensitive is specifically checked against Sky130 cell-library availability, since a Sky130 compatibility failure blocks the primary intended use of the standardized artifact.

**GF180 Compatibility:** A secondary, non-blocking compatibility check is performed against GF180 for the same PDK-sensitive constructs, with any identified incompatibility recorded (not blocking standardization) as a caveat in `standardization_metadata.yaml`, consistent with Phase 14.2 Part 9's "compatible-with-caveat" status category.

**ASAP7 Compatibility:** An analogous secondary, non-blocking, caveated compatibility check is performed against ASAP7, consistent with Phase 14.2 Part 9's treatment of ASAP7 as a predictive/illustrative rather than fabricable target requiring explicit caveating wherever it is used.

**Replacement Policies:** Where a PDK-sensitive construct is identified, this Part applies the same behavioral-replacement-or-stub disposition mechanism established in Part 14, extended with a PDK-scope qualifier — a replacement judged compatible with Sky130 but flagged incompatible with GF180 is recorded as such explicitly, rather than the replacement decision being treated as a single, PDK-independent choice.

**Inputs:** Part 14's black-box resolution record, Phase 14.2 Part 9's PDK-compatibility-matrix philosophy (extended here to the RTL-construct level rather than the whole-benchmark level Phase 14.2 operated at).
**Outputs:** A per-benchmark, per-PDK compatibility annotation extending the black-box resolution record, recorded in `standardization_metadata.yaml`.
**Dependencies:** Access to each target PDK's cell-library availability information, sufficient to check construct-level compatibility without requiring a full synthesis run (which remains out of scope per this document's boundary statement).
**Runtime Expectations:** Seconds per benchmark, given the narrow scope of PDK-sensitive constructs actually present in this open-source-focused corpus.
**Memory Expectations:** Negligible.
**Failure Conditions:** A Sky130-path incompatibility (the primary, blocking target) halts standardization for the affected benchmark pending resolution; GF180/ASAP7 incompatibilities are recorded as non-blocking caveats consistent with Phase 14.2 Part 9's established policy.
**Validation:** The compatibility checks described above, cross-validated against the PDK cell-library reference data.
**Industrial Notes:** Treating Sky130 compatibility as blocking while GF180/ASAP7 compatibility is caveated-but-non-blocking directly operationalizes, at the RTL-construct level, the same primary/secondary/tertiary PDK-priority structure Phase 14.2 Part 9 established at the whole-benchmark level.
**Reviewer Expectations:** This fine-grained, construct-level PDK compatibility annotation is what allows the eventual cross-PDK generalization claims (Phase 14.1 Part 3's cross-PDK split) to be defended with RTL-level evidence rather than only physical-design-stage evidence discovered incidentally during a Phase 14.1 run.
**Future Extensibility:** A future open FinFET-class PDK (foreshadowed in Phase 14.2 Part 9) is added as a new compatibility-check column, following the same primary/secondary-target extensibility pattern already established.

---

## PART 16 — Unsupported Construct Detection

**Purpose:** Systematically identify every RTL-file construct that is non-synthesizable, verification-only, or otherwise unsupported by the downstream Phase 14.5 synthesis toolchain, and explicitly separate such constructs from the standardized, synthesis-ready RTL output.

**Theory / Engineering Rationale:** Phase 14.2 Part 8 identified this concern narrowly, as a dry-run-elaboration-triggered discovery process; this document's Part 16 replaces that reactive discovery approach with a systematic, proactive scan applied uniformly across the corpus, since reactive discovery (waiting for an elaboration failure to reveal an unsupported construct) does not scale reliably across a corpus this heterogeneous and risks inconsistent handling depending on which specific construct happens to trigger a visible failure first.

**Unsupported SystemVerilog:** Modern SystemVerilog interface constructs, certain parameterized virtual-interface patterns, and select IEEE 1800 constructs with incomplete open-toolchain support (varying by the specific Yosys version pinned per Phase 14.2/14.3 metadata) are scanned for explicitly across every SystemVerilog-classified benchmark (Part 2), with each detected instance logged, regardless of whether it would actually trigger an elaboration failure in the currently pinned tool version — this proactive, complete-inventory approach (rather than only logging constructs that happen to currently fail) is deliberate, since a future tool-version upgrade could silently change which constructs fail, and a complete inventory taken now remains a stable reference point independent of that future drift.

**Assertions:** SystemVerilog Assertion (SVA) constructs (`assert property`, `assume property`, `cover property`) are identified and separated from the synthesizable RTL content entirely — assertions are verification-intent constructs by definition and are never part of the standardized synthesis-ready output, though they are retained as a distinct, separately-tracked artifact category (not discarded) since they carry documentation value about designer-intended invariants that could inform future verification-adjacent phases beyond this document's current scope.

**Simulation-Only Code:** Constructs meaningful only in a simulation context (`$display`, `$monitor`, `$fwrite`, timing-control delay statements such as `#` delays used for testbench pacing rather than synthesizable timing) are identified and excluded from the standardized output, following the same separate-tracking-not-discarding principle as assertions.

**Tasks and Functions:** Verilog/SystemVerilog `task` and `function` constructs are evaluated individually — synthesizable functions (used within combinational/sequential logic in a manner supported by the downstream toolchain) are retained in the standardized output; non-synthesizable tasks (typically verification-only, containing simulation-only constructs internally) are excluded following the same principle applied to other verification-only content.

**Interfaces:** SystemVerilog `interface` constructs, where used purely as a verification-convenience bundling mechanism around ports that are otherwise individually synthesizable, are resolved (their constituent signals expanded back into individually-declared ports at the standardization layer) rather than excluded outright, since the underlying signals remain functionally necessary even though the `interface` wrapper construct itself may not be — this resolution is recorded explicitly in `interface_map.yaml` (Part 10) as an interface-expansion entry.

**UVM Remnants:** Any Universal Verification Methodology (UVM) class-based content occasionally present in files adjacent to (but not part of) a benchmark's actual design-intent RTL (most commonly in verification-infrastructure directories swept in during Part 3's repository discovery from projects that co-locate design and verification code, notably CVA6's `core-v-verif` submodule dependency noted in Phase 14.2 Part 2.8) is explicitly excluded from the discovered design-RTL file set at this stage, with the exclusion decision cross-referenced back to Part 3's file-manifest scope to ensure it reflects a deliberate, documented scoping decision rather than an accidental inclusion subsequently patched over.

**Inputs:** Part 3's parsed syntax-tree representation, Part 12's fully macro/include-resolved file content.
**Outputs:** A construct-classification report per benchmark (synthesizable-retained versus excluded-and-why, per construct instance), and the separately-tracked non-synthesizable content archive (assertions, simulation-only code, excluded tasks) retained for documentation value per the principle stated above.
**Dependencies:** A construct-level static analysis capability sufficient to classify each language construct against the synthesizability criteria defined above — implemented as a rule-based scan over the parsed syntax tree rather than requiring a full elaboration pass (which would conflate this Part's proactive detection goal with Part 18's later, elaboration-specific validation goal).
**Runtime Expectations:** Seconds for the majority of the corpus; up to a minute for the SystemVerilog-heaviest, verification-adjacent-content-heaviest sources (CVA6, OpenTitan), given the larger file count requiring per-construct classification.
**Memory Expectations:** Modest, bounded by syntax-tree size already established in Part 3.
**Failure Conditions:** A construct that cannot be confidently classified as either synthesizable-retained or verification-only-excluded by the rule-based scan is escalated for manual classification rather than defaulted to either disposition, consistent with this document's general escalate-rather-than-guess principle.
**Validation:** A completeness check confirming every construct in every parsed file received an explicit classification, and a cross-check that the resulting standardized RTL output contains zero constructs from the explicitly-unsupported category list.
**Industrial Notes:** Proactive, complete-inventory construct scanning rather than reactive failure-driven discovery mirrors how a production RTL linting policy (Part 17) is itself typically structured — comprehensive rule coverage checked uniformly, not merely reactive bug-fixing triggered by whichever issue happens to surface first in a given tool run.
**Reviewer Expectations:** The separate, non-discarded archival of excluded verification-intent content (assertions particularly) is a specific, thoughtful detail reviewers with RTL verification backgrounds are likely to notice and credit, since naively discarding assertions would lose genuinely valuable design-intent documentation with no compensating benefit.
**Future Extensibility:** A future verification-oriented phase (explicitly out of scope for the current 14.x series but a natural extension point) could consume the archived assertion content as a structured source of design-intent invariants, without requiring this Part's exclusion logic to be revisited.

---

## PART 17 — Static RTL Linting

**Purpose:** Apply a comprehensive, corpus-wide static lint pass to every standardized RTL output, catching latent structural risks not necessarily surfaced by the construct-level classification of Part 16 or the intake-stage syntax validation of Part 3.

**Theory / Engineering Rationale:** Static linting operates at a different level of analysis than either syntax parsing (Part 3, catching malformed code) or construct-classification (Part 16, catching non-synthesizable constructs) — linting catches semantically-valid, synthesizable code that nonetheless exhibits patterns strongly associated with functional bugs or synthesis-result ambiguity (unintended latch inference, incomplete case-statement coverage, multiply-driven nets), and is a standard, expected quality gate in any production RTL flow that this document adopts at the standardization stage specifically so that lint findings are available before, not after, the more expensive Phase 14.5 synthesis investment is made.

**Lint Policy:** The lint rule set applied is drawn from established open lint tooling (Verilator's `--lint-only` mode as the primary reference tool, given its widespread adoption and compatibility with the Verilog/SystemVerilog subset this corpus already targets for Yosys compatibility) supplemented by any VHDL-specific lint checks available through the pinned VHDL front-end (Part 2) for the VHDL-classified subset of the corpus.

**Warning Classification:** Every lint finding is classified into one of three severity tiers: **informational** (style-only, e.g., signal-width-implicit-truncation warnings that do not indicate a functional risk given the surrounding context), **advisory** (a genuine but non-blocking structural concern, e.g., an unusually large case statement lacking a default branch where the design's own logic otherwise ensures exhaustive coverage), and **blocking** (a finding strongly correlated with functional incorrectness, e.g., a signal driven from multiple always-blocks with conflicting conditions, or unintended latch inference in a block clearly intended to be purely combinational).

**Error Classification:** True lint errors (as opposed to warnings) — findings indicating the lint tool itself could not complete its analysis of a given construct — are treated identically to a Part 3 intake-stage syntax failure, blocking standardization for the affected benchmark, since an incomplete lint analysis provides no reliable severity information for any subsequent finding in the same file.

**Acceptance Criteria:** A benchmark's standardized RTL passes the Part 17 lint gate when it contains zero blocking-severity findings; informational and advisory findings are recorded in `lint_report.yaml` (Part 4) without blocking standardization, consistent with Phase 14.2 Part 10's precedent of distinguishing lint-warning-tolerant acceptance from lint-error-blocking rejection at the benchmark-acquisition layer, now applied identically at the RTL-standardization layer.

**Inputs:** The finalized standardized RTL output from Parts 3–16.
**Outputs:** `lint_report.yaml` per benchmark, recording every finding, its severity classification, and its resolution status (accepted-as-advisory, or resolved via a documented RTL-preserving metadata adjustment where applicable — never via silent RTL rewriting, consistent with this document's minimal-modification principle).
**Dependencies:** Verilator (`--lint-only` mode) as the primary lint engine, the pinned VHDL front-end's lint capability for VHDL sources.
**Runtime Expectations:** Seconds for the majority of the corpus; up to a few minutes for the largest, most construct-dense sources (CVA6, OpenTitan blocks at full scope).
**Memory Expectations:** Comparable to or slightly below Part 3's parsing-stage memory footprint for the same benchmark.
**Failure Conditions:** Any blocking-severity finding, or a true lint-tool error as distinguished above, halts standardization for the affected benchmark pending resolution.
**Validation:** The lint report's completeness (every file in the standardized RTL tree received lint coverage) and the acceptance-criteria check described above.
**Industrial Notes:** This three-tier severity classification, rather than a binary pass/fail lint gate, mirrors how production RTL sign-off lint policies are typically structured — a binary gate would either be too permissive (accepting genuine risk-indicating patterns) or too strict (blocking on stylistic non-issues present throughout large swaths of legitimately-functioning third-party IP), neither of which serves this corpus's heterogeneous-source reality well.
**Reviewer Expectations:** A complete, severity-classified lint report per benchmark, included as supplementary artifact-bundle material, is precisely the evidence a reviewer would expect to substantiate a claim that the corpus's standardized RTL is of consistent, audited quality rather than merely "whatever happened to elaborate without error."
**Future Extensibility:** Additional lint tools (e.g., a future formal-linting tool with deeper semantic-equivalence-checking capability than Verilator's structural lint) can be incorporated as additional severity-classified finding sources within the same `lint_report.yaml` schema, without restructuring the three-tier classification scheme itself.

---

## PART 18 — RTL Elaboration Validation

**Purpose:** Perform a final, comprehensive elaboration-level validation of the fully standardized RTL tree, confirming it is genuinely complete and tool-ready before being handed to Phase 14.5, distinct from and more comprehensive than any single upstream Part's more narrowly-scoped structural checks.

**Theory / Engineering Rationale:** Every prior Part in this document (5 through 17) performs a structural or lightweight-parse-level check specific to its own concern (hierarchy completeness, parameter resolution, naming, macro resolution, construct classification, lint); none of them individually performs a full elaboration — the process by which a synthesis-capable tool actually resolves every hierarchical reference, parameter binding, and generate-block instantiation into a single, concrete, flattened-reference design representation. Part 18 closes this gap by performing exactly that full elaboration, using the same front-end (Yosys, for Verilog/SystemVerilog-classified benchmarks; GHDL analysis/elaboration, for VHDL-classified benchmarks) that Phase 14.5 will itself use, but explicitly stopping at elaboration completion — no technology mapping, no optimization pass, no timing analysis is performed here, preserving this document's stated boundary with Phase 14.5.

**Hierarchy Validation:** Full elaboration independently re-confirms every hierarchy-completeness property already checked structurally in Part 6 (acyclicity, full reachability from the declared top module, zero unresolved instantiations outside the explicitly-dispositioned Part 14/15 black-box set) — this re-confirmation at the elaboration level, rather than trusting Part 6's structural-level check alone, is deliberate redundancy, since elaboration-level tools apply a stricter, more complete notion of hierarchy validity than a structural parse alone can guarantee.

**Dependency Validation:** Full elaboration confirms every macro/include resolution performed in Part 12 was genuinely complete — an elaboration-time failure attributable to an unresolved preprocessor dependency at this stage indicates a gap in Part 12's resolution logic that the earlier, lighter-weight completeness scan failed to catch, and is treated as a Part 12-attributable defect requiring that Part's resolution logic to be revisited, not merely a Part 18-local failure to be patched around.

**Module Resolution:** Every module/entity reference in the fully elaborated design is confirmed to resolve to exactly one concrete implementation (either standardized RTL content or an explicitly-dispositioned Part 14/15 black-box stub) — an elaboration-time module-resolution ambiguity (multiple candidate implementations for a single reference, which can arise from subtle naming-collision edge cases not fully caught by Part 11's naming normalization) is treated analogously to the dependency-validation case above.

**Tool Compatibility:** Elaboration is performed using the exact pinned tool version recorded in the relevant benchmark's eventual Phase 14.1/14.3 tool-version metadata (cross-referenced forward, since this document's own `standardization_metadata.yaml`, Part 19, separately pins the elaboration-validation tool version used here) — confirming, as a final compatibility gate, that the standardized RTL is genuinely compatible with the exact tool version the corpus's downstream physical-design pipeline actually uses, not merely with a generic or differently-versioned reference tool.

**Acceptance Criteria:** A benchmark's standardized RTL passes Part 18's elaboration validation when full elaboration completes with zero errors and zero unresolved references of any kind (module, parameter, macro) — this is the final, most comprehensive gate a benchmark's standardized RTL must clear before this document marks it complete and hands it to Phase 14.5, and it is treated as a strictly binary, non-caveated acceptance criterion (unlike Part 17's tiered lint severity), since an elaboration failure at this stage indicates the standardized RTL is not, in fact, tool-ready — the entire deliverable this document exists to produce.

**Inputs:** The fully standardized RTL tree (Parts 3–17's complete output) for a given benchmark.
**Outputs:** `elaboration_report.yaml`, recording the elaboration result (pass/fail), the exact tool version used, and full diagnostic detail on any failure.
**Dependencies:** Yosys (Verilog/SystemVerilog) or GHDL (VHDL), at the exact pinned version matching the downstream Phase 14.1/14.3 toolchain.
**Runtime Expectations:** Consistent with Phase 14.1 Stage A's already-established elaboration-adjacent runtime figures for the same benchmark (seconds for ISCAS/ITC-99-class designs, up to several minutes for CVA6/OpenTitan-class designs), since this Part performs materially the same elaboration work Phase 14.1 Stage A will itself perform, deliberately duplicated here as an explicit standardization-stage gate rather than deferred entirely to Phase 14.1's own execution.
**Memory Expectations:** Consistent with the corresponding Phase 14.1 Stage A figures for the same benchmark.
**Failure Conditions:** Any elaboration error or unresolved reference, as detailed above, blocks this benchmark's standardization from being marked complete.
**Validation:** The elaboration result itself is the validation outcome for this Part; no further meta-validation layer is applied beyond the Part 20 QA aggregation and the Part 8 (of Phase 14.3, this document's sibling annotation specification)-consistent deterministic-rerun philosophy applied generally across this document's own Part 20.
**Industrial Notes:** Performing a full, tool-matched elaboration pass as an explicit standardization-stage gate — rather than allowing Phase 14.1 to be the first point at which elaboration is actually attempted — mirrors the standard RTL-freeze discipline in production ASIC flows, where a design is not considered "frozen" and handed to the physical-design team until it has independently cleared a full elaboration checkpoint, precisely so that any elaboration-level defect is caught and attributed to the RTL-preparation team rather than surfacing confusingly deep within the physical-design team's own tool run.
**Reviewer Expectations:** A dedicated, tool-matched elaboration-validation gate performed prior to and independent of the actual downstream synthesis run is a specific, meaningful signal of engineering rigor that directly distinguishes this project's RTL-preparation discipline from a more informal "we ran synthesis and fixed whatever broke" approach common in less rigorously documented ML-for-EDA dataset efforts.
**Future Extensibility:** Should Phase 14.5 introduce support for an additional synthesis front-end beyond Yosys, this Part's elaboration-validation gate extends to include a matched elaboration pass under that additional front-end as well, without altering its acceptance-criteria logic.

---

## PART 19 — Metadata Schema

**Purpose:** Define the complete, schema-validated metadata record accompanying every standardized RTL artifact, aggregating and formalizing the individual metadata outputs produced by Parts 5 through 18 into a single authoritative schema.

**Theory / Engineering Rationale:** Parts 5 through 18 each produce their own focused metadata output (`top_module.yaml`, `hierarchy.yaml`, `parameters.yaml`, `clocks.yaml`, `resets.yaml`, `interface_map.yaml`, `naming_map.yaml`, `macro_resolution.yaml`, plus the Part 17/18 reports) — this Part defines the aggregate `standardization_metadata.yaml` record that references and summarizes all of them, providing the single entry-point metadata file Phase 14.5 (and any AE reviewer) is expected to consult first, consistent with the single-manifest-as-source-of-truth philosophy established in Phase 14.2 Part 6 and Phase 14.3 Part 5.

**Standardized RTL Metadata (top-level fields):** `benchmark_id`, `version_tag` (both inherited read-only from Phase 14.2), `normalization_version` (this document's own independently-scoped version, per Part 24's versioning discussion), `top_module_reference` (pointer to `top_module.yaml`), `standardization_timestamp`, `standardization_status` (`complete`/`blocked`/`in_progress`), `standardized_rtl_checksum` (SHA-256 over the finalized `standardized/.../rtl/` tree, consistent with the checksum discipline established throughout the 14.x series).

**Hierarchy Metadata:** A summary cross-reference to `hierarchy.yaml`, additionally including corpus-comparable scalar summaries (module count, maximum hierarchy depth, unused-module exclusion count) computed once here so that corpus-wide statistics (a natural Part 20/23 concern) do not each need to independently re-parse the full `hierarchy.yaml` structure.

**Clock Metadata:** A summary cross-reference to `clocks.yaml`, including a scalar clock-domain count and a flag indicating whether the benchmark is single-clock or multi-clock, supporting fast corpus-wide filtering for downstream split-strategy purposes (a Phase 14.1 concern this metadata directly supports).

**Reset Metadata:** A summary cross-reference to `resets.yaml`, structured analogously to the clock-metadata summary.

**Dependency Metadata:** A summary cross-reference to the Part 12-finalized dependency graph, including the file count and total resolved-source line count (comparable to, and cross-validated against, Phase 14.2's `rtl_loc` field per Part 3's validation step).

**Configuration Metadata:** A summary cross-reference to `parameters.yaml`, directly restating the resolved `configuration_label` cross-validation result from Part 7 for immediate visibility without requiring a separate file lookup.

**Additional Required Fields:** `generator_toolchain_version` (populated only for Part 13-applicable generator-sourced benchmarks; explicitly `null` otherwise, not omitted, so its absence is always a positive statement rather than an ambiguous gap), `blackbox_disposition_summary` (count and classification breakdown from Part 14/15), `lint_summary` (finding counts per severity tier from Part 17), `elaboration_validation_status` (pass/fail from Part 18, the single most safety-critical field in this entire schema given Part 18's role as the final acceptance gate).

**Inputs:** Every Part 5–18 output artifact for a given benchmark.
**Outputs:** `standardization_metadata.yaml`, the complete aggregate record.
**Dependencies:** A schema validator, consistent with the JSON-Schema/YAML-schema validation approach established in Phase 14.2 Part 6 and Phase 14.3 Part 5.
**Runtime/Memory Expectations:** Negligible — this Part is a bookkeeping aggregation step, not a computational one, consistent with the equivalent metadata-aggregation Parts in the predecessor documents.
**Failure Conditions:** A missing required field, or an internal inconsistency between this aggregate record and any of its constituent Part-level source files (e.g., `elaboration_validation_status: pass` while the underlying `elaboration_report.yaml` records a failure), blocks the benchmark from being marked `standardization_status: complete`.
**Validation:** Full-schema validation as a CI gate, plus the internal cross-consistency check described above.
**Industrial Notes:** A single aggregate metadata record referencing, rather than duplicating, the detailed per-Part outputs mirrors the same top-level-manifest-plus-detailed-sub-records pattern already established by Phase 14.2's `manifest.yaml` and Phase 14.3's `annotation_metadata.yaml`, maintaining structural consistency across all three predecessor documents and this one.
**Reviewer Expectations:** A single, complete, schema-validated entry-point metadata file is what allows an AE reviewer to assess a given benchmark's standardization completeness and quality without needing to manually cross-reference eight or more separate files — a meaningful usability consideration for the actual reviewing process, not merely a structural nicety.
**Future Extensibility:** New fields are added with a `schema version` bump (Part 24), following the identical backward-compatible-optional-field policy established in Phase 14.2 Part 6 and Phase 14.3 Part 10.

---

## PART 20 — Quality Assurance

**Purpose:** Define the corpus-wide QA aggregation layer confirming every standardized benchmark meets this document's complete acceptance criteria before being included in the finalized manifest handed to Phase 14.5.

**Structural QA:** Aggregates the Part 3 (intake completeness), Part 6 (hierarchy acyclicity/reachability), and Part 18 (elaboration validation) results into a single structural-soundness verdict per benchmark — a benchmark fails structural QA if any of these three constituent checks failed, regardless of how minor any individual failure might otherwise appear in isolation.

**RTL QA:** Aggregates Part 16 (unsupported-construct classification completeness) and Part 17 (lint acceptance criteria) into a single content-quality verdict, distinguishing benchmarks with zero blocking findings (pass) from those with any blocking finding (fail), consistent with Part 17's own stated acceptance criteria.

**Normalization QA:** Aggregates Parts 7–11 (parameter resolution, clock/reset normalization, interface standardization, naming normalization) into a single normalization-completeness verdict, confirming every required metadata field across these Parts was populated (per each Part's own stated validation criteria) with no unresolved escalation pending.

**Regression QA:** For benchmarks undergoing re-standardization following a `normalization_version` bump (Part 24), a regression check compares the newly-produced `standardized_rtl_checksum` (Part 19) against the immediately preceding `normalization_version`'s checksum for the same benchmark — an unexpected checksum change (one not attributable to an intentional, logged methodology change accompanying the version bump) is flagged for investigation, mirroring the deterministic-rerun validation philosophy Phase 14.3 Part 8 established for annotation labels, now applied to standardized RTL.

**Inputs:** Every constituent Part's output for a given benchmark, plus (for regression QA specifically) the prior `normalization_version`'s recorded checksum.
**Outputs:** `qa_report.yaml` (Part 4 location: `reports/qa/<benchmark_id>/<version_tag>/qa_report.yaml`), recording the four-category verdict (structural/RTL/normalization/regression) and an overall pass/fail summary.
**Dependencies:** `validate_normalization.py` equivalent functionality within Part 21's automation (specified there).
**Runtime Expectations:** Seconds per benchmark, since this Part aggregates already-computed upstream results rather than performing new analysis, with the exception of the regression-QA checksum comparison, itself negligible in cost.
**Memory Expectations:** Negligible.
**Failure Conditions:** Any of the four category verdicts failing blocks the benchmark's inclusion in the finalized `standardization_manifest.yaml` (Part 22).
**Validation:** The QA gate itself is periodically validated via the same injection-testing philosophy Phase 14.3 Part 7 established (deliberately corrupted synthetic standardized-RTL samples run through the QA pipeline to confirm each check fires as intended).
**Industrial Notes:** A four-category QA aggregation, mirroring the multi-category QA structure already established in Phase 14.2 Part 10 (structural/compile/simulation/lint) and Phase 14.3 Part 7 (missing/NaN/coordinate/cross-tool/statistical), maintains this document's consistency with the predecessor documents' QA philosophy while being scoped to this document's own specific concerns (structural soundness, RTL content quality, normalization completeness, and version-to-version regression stability).
**Reviewer Expectations:** A corpus-wide QA pass-rate summary, aggregable from these per-benchmark reports, is the kind of evidence an AE reviewer expects to see substantiating a "the standardized RTL corpus is clean and complete" claim, consistent with the same expectation already established for the acquisition and annotation layers.
**Future Extensibility:** A future fifth QA category (e.g., a dedicated cross-benchmark consistency check, verifying that naming/interface conventions per Parts 10–11 are applied uniformly across the entire corpus rather than merely correctly within each individual benchmark) can be added without restructuring the existing four-category framework.

---

## PART 21 — Automation

**Purpose:** Specify the tooling operationalizing Parts 3–20, at the level of responsibility and interface, consistent with the automation-specification approach established in Phase 14.2 Part 11 and Phase 14.3 Part 11.

| Script | Responsibility |
|---|---|
| `standardize_rtl.py` | Executes the full Parts 3–16 intake-through-normalization pipeline per benchmark: repository discovery, hierarchy/dependency-graph construction, top-module detection, parameter resolution, clock/reset normalization, interface/naming standardization, macro/include resolution, generated-RTL regeneration verification (Part 13, where applicable), and black-box/vendor-primitive disposition (Parts 14–15). Supports resume via per-stage checkpoint hashing, consistent with the resume philosophy established in Phase 14.1 and carried through Phase 14.2/14.3, and supports `--cluster slurm`/`--cluster k8s` execution. |
| `dependency_analyzer.py` | Standalone utility implementing Part 3's dependency-graph construction and Part 6's hierarchy-finalization logic; callable independently of a full `standardize_rtl.py` run for targeted hierarchy-debugging purposes during manual review of a flagged benchmark. |
| `rtl_linter.py` | Executes Part 17's lint pass and produces `lint_report.yaml`; wraps the underlying Verilator/GHDL-lint invocation with this document's three-tier severity classification logic. |
| `elaboration_check.py` | Executes Part 18's full elaboration-validation pass using the pinned, downstream-matched tool version, and produces `elaboration_report.yaml`; exits non-zero on any elaboration failure so it can serve as a CI gate. |
| `metadata_generator.py` | Aggregates every Part 5–18 output into the Part 19 `standardization_metadata.yaml` schema instance, applying full schema validation and refusing to mark a benchmark `standardization_status: complete` if any required field is missing or internally inconsistent. |

**Inputs (all scripts):** The Phase 14.2 benchmark manifest and QA-complete RTL tree, this document's directory conventions (Part 4), and the per-benchmark `normalization_rule_config.yaml` (Part 4) governing versioned rule-set behavior.
**Outputs (all scripts):** The populated `rtl_standardization/` tree (Part 4) plus the aggregate `standardization_manifest.yaml` (Part 22).
**Dependencies:** Yosys, GHDL, Verilator, the pinned Chisel/`sbt`/FIRRTL toolchain and OpenTitan `reggen`/`topgen` toolchain (both only invoked where Part 13 applies), a JSON-Schema/YAML-schema validator, standard checksum utilities.
**Failure Modes:** `standardize_rtl.py` failures are isolated per-benchmark, consistent with the per-benchmark isolation principle established in Phase 14.2 Part 3/11, and logged with structured error records; `rtl_linter.py` and `elaboration_check.py` failures block only the affected benchmark's progression through their respective gates; `metadata_generator.py` refuses incomplete records rather than silently populating partial metadata.
**Runtime/Memory Expectations:** Consistent with the per-stage figures already established across Parts 3–18 of this document, since these five scripts are the direct operational implementation of those specifications.
**Cluster Execution:** All scripts follow the identical per-benchmark, manifest-driven, Slurm-array/Kubernetes-indexed-job parallelization pattern established in Phase 14.1 Part 9, Phase 14.2 Part 11, and Phase 14.3 Part 11, maintaining a single consistent cluster-execution model across all four documents produced to date.

**Industrial Notes:** Five narrowly-scoped, independently-testable scripts (rather than one monolithic standardization script) continues the same CI/CD decomposition philosophy applied consistently across the 14.x series — e.g., a fix to Part 17's lint-severity classification logic requires re-running only `rtl_linter.py` and `metadata_generator.py`, not the full `standardize_rtl.py` pipeline.
**Reviewer Expectations:** Providing these five scripts as artifact-bundle components, precisely scoped as specified here, earns the AE "Functional" and "Reproducible" badges at the RTL-standardization layer, exactly as the predecessor documents' automation scripts did at the acquisition and annotation layers.
**Future Extensibility:** A future dedicated `regeneration_verify.py` script, formalizing Part 13's currently `standardize_rtl.py`-embedded regeneration-verification logic as a standalone, independently-invokable tool, would slot into this same five-script (becoming six) pattern without disrupting the existing scripts' responsibilities.

---

## PART 22 — Repository Layout

**Purpose:** Present the complete repository tree resulting from this document's execution, integrated with the repository structures already established by Phase 14.1–14.3.

```
project_root/
├── benchmarks/                              (Phase 14.2, unaffected)
├── pipeline/                                (Phase 14.1, unaffected)
├── labels/                                  (Phase 14.3, unaffected)
├── rtl_standardization/
│   ├── original/
│   │   └── <benchmark_id>/<version_tag>/    (references only, never copies)
│   ├── standardized/
│   │   └── <benchmark_id>/<version_tag>/<normalization_version>/
│   │       ├── rtl/
│   │       ├── top_module.yaml
│   │       ├── hierarchy.yaml
│   │       ├── parameters.yaml
│   │       ├── clocks.yaml
│   │       ├── resets.yaml
│   │       ├── interface_map.yaml
│   │       ├── naming_map.yaml
│   │       ├── macro_resolution.yaml
│   │       ├── blackbox_stubs/
│   │       └── generated_artifacts/
│   ├── logs/
│   │   └── <benchmark_id>/<version_tag>/<normalization_version>/<stage>.log
│   ├── reports/
│   │   ├── lint/<benchmark_id>/<version_tag>/lint_report.yaml
│   │   ├── elaboration/<benchmark_id>/<version_tag>/elaboration_report.yaml
│   │   └── qa/<benchmark_id>/<version_tag>/qa_report.yaml
│   ├── metadata/
│   │   └── <benchmark_id>/<version_tag>/<normalization_version>/standardization_metadata.yaml
│   └── configs/
│       └── <benchmark_id>/normalization_rule_config.yaml
├── manifests/
│   └── standardization_manifest.yaml        (aggregate, schema-validated)
├── standardization_scripts/
│   ├── standardize_rtl.py
│   ├── dependency_analyzer.py
│   ├── rtl_linter.py
│   ├── elaboration_check.py
│   └── metadata_generator.py
├── cluster/                                 (shared Slurm/k8s configs, extended not duplicated from prior phases)
└── docs/
    ├── rtl_standardization_philosophy.md    (Part 1, human-readable rendering)
    ├── supported_rtl_languages.md           (Part 2, human-readable rendering)
    ├── generated_rtl_reproducibility.md     (Part 13, human-readable rendering)
    └── standardization_reproducibility.md   (Parts 18, 20, 24 synthesized)
```

**Inputs:** The complete Part 3–21 outputs.
**Outputs:** The tree above.
**Dependencies:** None beyond what is already established per-script in Part 21.
**Runtime/Memory Expectations:** Negligible for the layout-materialization step itself.
**Failure Conditions:** Consistent with Part 4's directory-organization failure conditions, extended to the full tree.
**Validation:** A structural completeness check across the full tree, consistent with Part 4.
**Industrial Notes:** Integrating this document's repository contribution alongside, rather than nested within, the Phase 14.1–14.3 trees preserves each phase's independent addressability while making the overall project structure navigable as a single coherent repository.
**Reviewer Expectations:** A reviewer navigating the full project repository should be able to locate any given phase's contribution immediately from the top-level directory structure alone, without needing this document's text to explain where things are — the tree above is designed to satisfy that expectation directly.
**Future Extensibility:** Phase 14.5's own repository contribution (a `synthesis/` top-level directory, by natural extension of this pattern) will sit alongside this one without requiring any restructuring of the tree established here.

---

## PART 23 — Deliverables

- `rtl_standardization/standardized/**/rtl/` — the finalized, standardized, tool-ready RTL tree per benchmark
- `rtl_standardization/standardized/**/top_module.yaml`, `hierarchy.yaml`, `parameters.yaml`, `clocks.yaml`, `resets.yaml`, `interface_map.yaml`, `naming_map.yaml`, `macro_resolution.yaml` — the complete per-Part metadata record set (Parts 5–12)
- `rtl_standardization/standardized/**/blackbox_stubs/`, `generated_artifacts/` — black-box disposition artifacts (Parts 14–15) and generator-regeneration provenance artifacts (Part 13)
- `rtl_standardization/reports/lint/**/lint_report.yaml` — Part 17 lint results
- `rtl_standardization/reports/elaboration/**/elaboration_report.yaml` — Part 18 elaboration-validation results
- `rtl_standardization/reports/qa/**/qa_report.yaml` — Part 20 aggregate QA verdicts
- `rtl_standardization/metadata/**/standardization_metadata.yaml` — Part 19 aggregate metadata records
- `rtl_standardization/configs/**/normalization_rule_config.yaml` — the versioned rule-configuration set governing every deterministic normalization decision
- `manifests/standardization_manifest.yaml` — the aggregate, schema-validated manifest handed to Phase 14.5
- `standardization_scripts/*.py` — the five automation scripts (Part 21), provided as artifact-bundle components
- Checksum ledger, consistent with the checksum discipline established across Phase 14.2/14.3 and this document
- `docs/rtl_standardization_philosophy.md`, `docs/supported_rtl_languages.md`, `docs/generated_rtl_reproducibility.md`, `docs/standardization_reproducibility.md` — publication-ready documentation

---

## PART 24 — Publication Readiness

**IEEE ICM 2026 / TCAD / TVLSI / DAC / ICCAD / DATE Fit:** This document's per-benchmark, per-Part audit trail (top-module detection through elaboration validation) directly substantiates the specific, checkable claim that every physical-design-stage result reported in downstream phases traces back to a deterministic, fully-documented RTL preparation process — a claim reviewers at these venues increasingly expect to see substantiated rather than merely asserted, particularly given this project's stated long-term ambition of quantitative manufacturing/packaging/reliability prediction claims that depend entirely on the integrity of the RTL those predictions are ultimately computed from.

**Artifact Evaluation:** The combination of the five automation scripts (Part 21), the deterministic regeneration-verification mechanism for generator-sourced RTL (Part 13), and the tool-matched elaboration-validation gate (Part 18) together satisfy AE's "Functional" and "Reproducible" criteria at the RTL-standardization layer, extending the same guarantee chain established by Phase 14.2 at the acquisition layer and Phase 14.3 at the annotation layer one further step.

**Industrial Reproducibility:** This document's `normalization_version` axis (Part 19/20), independent of Phase 14.2's `version_tag` and Phase 14.3's `annotation_version`, completes a now five-axis versioning scheme across the project as a whole (benchmark version, normalization version, dataset version, annotation version, schema/manifest versions per document), a level of versioning granularity that mirrors, and is directly defensible by analogy to, production RTL configuration-management discipline in industrial ASIC design flows.

**Version Control:** Every normalization decision (top-module selection where manual override was required, black-box disposition, PDK-compatibility caveat) is individually versioned and justified per Parts 5, 14, and 15's explicit-justification requirements, rather than this document's reproducibility claim resting on RTL-file-checksum stability alone — the checksum confirms *what* was produced, while these per-decision justification records confirm *why*, and both are required for a complete reproducibility argument.

**Long-Term Archival:** Consistent with the archival reasoning established in Phase 14.2 Part 14 and Phase 14.3 Part 14, this document explicitly anticipates (Part 13) that generator-toolchain dependencies (Chisel/`sbt`/FIRRTL package-repository-resolved dependencies specifically) are a distinct, real long-term-archival risk beyond the RTL-source-availability risk already addressed at the acquisition layer — the retained intermediate `generated_artifacts/` (Part 4/23) exist specifically to preserve regeneration provenance even in a future scenario where the exact generator-toolchain dependency set becomes unresolvable from its original package sources, a risk not otherwise mitigated by RTL-checksum preservation alone.

**Zenodo / DOI:** The finalized `rtl_standardization/` tree, alongside `standardization_manifest.yaml`, is a natural third companion Zenodo deposit alongside the Phase 14.2 benchmark-corpus deposit and the Phase 14.3 label-corpus deposit, cross-referenced by DOI in all directions consistent with the provenance-chain-as-a-single-citable-unit principle established in Phase 14.3 Part 14.

**Industrial Deployment:** This document's minimal-RTL-modification, metadata-mapping-layer-first normalization philosophy (established in Part 1 and applied consistently through Parts 8–12) is directly transferable to a production multi-source IP-integration RTL-preparation flow, not merely an academic-reproducibility convenience, extending the same dual academic/industrial applicability argument Phase 14.3 Part 14 made for its own annotation subsystem.

**Reviewer Expectations:** Taken together with Phase 14.2 and Phase 14.3, this document is intended to close the third of what is now a three-part sequence of standard ML-for-EDA dataset-paper objections — "is your source RTL properly licensed and versioned" (Phase 14.2), "is your ground truth properly defined and reproducible" (Phase 14.3), and now "is the RTL your ground truth was actually computed from itself deterministic, complete, and tool-ready, or could unstated preprocessing be silently confounding your results" (this document) — leaving Phase 14.5's synthesis and technology-mapping specification to address the next, distinct objection class around synthesis methodology and technology-mapping fidelity.

**Future Scalability:** Nothing in this specification is tied to the current six-language, benchmark-count-bounded corpus scope — the standardization philosophy, intake workflow, per-construct normalization rule structure (Parts 5–18), metadata schema, QA gate, versioning scheme, and automation interface all generalize directly to future benchmark-corpus expansion (additional RISC-V cores, additional HCL-generated sources, a future non-open-PDK-targeting benchmark subset) without structural revision to this document, consistent with the future-extensibility commitments made at the close of every Part above.
