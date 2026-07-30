# PHASE 14.2
## Official Benchmark & Dataset Acquisition Specification (BDAS)

**Document Classification:** Industrial Benchmark Acquisition Specification
**Target Venues:** IEEE TCAD · IEEE TVLSI · DAC · ICCAD · DATE — Artifact Evaluation Ready
**Predecessor Document:** Phase 14.1 — Dataset Generation Pipeline (dataset generation is out of scope here; this document governs *acquisition of source RTL benchmarks only*, prior to any generation step)

---

## PART 1 — Benchmark Philosophy

**Purpose:** Establish the governing principles by which any RTL benchmark is admitted into the project, independent of what will later be done with it.

**Theory / Engineering Rationale:** A benchmark acquisition layer must be treated as a **first-class, independently versioned subsystem**, decoupled from the downstream dataset-generation pipeline (Phase 14.1). This separation exists for three reasons: (1) benchmark sources change independently of the generation pipeline's release cadence — RTL repositories receive upstream commits on their own schedule; (2) licensing obligations attach to the *source RTL itself*, not to derived artifacts, and must be tracked at the acquisition boundary; (3) reproducibility claims for IEEE/DAC/ICCAD Artifact Evaluation require that the *exact RTL snapshot* used in any experiment be independently verifiable, which is only possible if acquisition is a pinned, checksummed, auditable event distinct from generation.

**Governing Principles:**
1. **Provenance-first** — no RTL enters the repository without a recorded origin (URL, commit hash, tag, or DOI).
2. **Immutability post-acquisition** — once a benchmark version is pinned, its RTL is treated as read-only; upstream updates require a new, separately versioned acquisition, never an in-place overwrite.
3. **License-gated admission** — a benchmark is not acquired until its license has been classified and cleared (Part 7).
4. **Diversity-by-design** — benchmark selection spans structural scale (gate count from hundreds to hundreds of thousands), RTL language (Verilog, SystemVerilog, VHDL, Chisel-generated Verilog), and domain (combinational ISCAS-class circuits through full application-class RISC-V cores), to support the split strategy defined in Phase 14.1 Part 2/3 without redefining it here.
5. **Acquisition ≠ Curation** — this document governs *getting the RTL in, verified and licensed*; it does not decide train/val/zero-shot/OOD assignment (that is a Phase 14.1 decision consuming this document's manifest as input).

**Industrial Notes:** This mirrors how commercial EDA/IP organizations manage third-party IP intake — a formal IP-receiving desk with license review, checksum registration, and version locking, separate from the engineering teams that later consume the IP.

**Reviewer Expectations:** AE reviewers at DAC/ICCAD/DATE increasingly check whether a "benchmark suite" claim is backed by pinned commit hashes rather than a loose "we used OpenCores" statement. This document's structure directly answers that expectation.

**Future Scalability:** New benchmark families (future FinFET-era open cores, additional RISC-V implementations, chiplet-interconnect IP) are admitted by appending new entries to the acquisition manifest schema (Part 6) without altering the philosophy or the automation scripts (Part 11).

---

## PART 2 — Academic Benchmark Selection

For each benchmark: why selected, expected complexity, cell/gate count, RTL language, expected synthesis/placement runtime, memory requirement, license, maintainer, official repository, industrial relevance, limitations. Counts/runtimes below are **order-of-magnitude engineering estimates** for planning purposes (typical open-PDK, standard-effort synthesis) — exact figures depend on the target library, clock constraint, and synthesis effort and must be re-measured and recorded per acquisition (Part 6 metadata schema captures the measured values, not these estimates).

### 2.1 ISCAS-85 / ISCAS-89

- **Why selected:** Canonical, decades-long reference point in EDA/ML literature; mandatory for baseline comparability against prior congestion/timing/power ML-for-EDA work.
- **Expected complexity:** Trivial to small; purely combinational (ISCAS-85) or small sequential (ISCAS-89).
- **Cell/gate count:** ~10 to ~3,500 gates.
- **RTL language:** Originally gate-level netlist/bench format; Verilog wrappers widely available via community mirrors.
- **Expected synthesis runtime:** Seconds.
- **Expected placement runtime:** Seconds to low tens of seconds.
- **Memory requirement:** <1 GB.
- **License:** Public-domain / unrestricted academic benchmark (no formal OSI license; treated as "freely redistributable for research" per long-standing community norm — must still be explicitly recorded per source mirror, since mirror-added wrapper code may carry its own license).
- **Maintainer:** No single active maintainer; distributed via multiple long-standing academic mirrors (e.g., university EDA course repositories).
- **Official repository:** No single canonical GitHub source; acquisition must select and pin a specific, well-documented mirror and record it explicitly (Part 3).
- **Industrial relevance:** Low on its own (obsolete as real IP) but high as a controlled, low-noise regression sanity-check tier for the pipeline itself.
- **Limitations:** Not representative of modern design styles; must never be the sole evidence of generalization in a paper.

### 2.2 ITC-99

- **Why selected:** Extends ISCAS with larger, more structurally diverse sequential benchmarks; standard scalability tier between ISCAS and modern IP.
- **Expected complexity:** Small-to-medium.
- **Cell/gate count:** ~100 to ~30,000 gates depending on benchmark (b01–b22 family).
- **RTL language:** VHDL and Verilog variants both circulate; version must be pinned explicitly.
- **Expected synthesis runtime:** Seconds to ~1 minute.
- **Expected placement runtime:** Tens of seconds to a few minutes.
- **Memory requirement:** <2 GB.
- **License:** Public academic benchmark, unrestricted research use per originating consortium norms; source-specific redistribution terms must be checked per mirror.
- **Maintainer:** No active maintainer; academic legacy benchmark.
- **Official repository:** No canonical GitHub; typically obtained via university/EDA-course mirrors — pin exact mirror and file hash.
- **Industrial relevance:** Moderate — useful mid-scale regression tier; limited direct industrial analog.
- **Limitations:** Same generation-era limitations as ISCAS; sparse macro/hierarchy content.

### 2.3 EPFL Combinational Benchmark Suite

- **Why selected:** Modern (2015-era), arithmetic/datapath-heavy benchmarks (adders, multipliers, ALUs, control logic) that stress feature extractors on high-fanout and regular-structure netlists largely absent from ISCAS/ITC-99.
- **Expected complexity:** Small to large (explicitly split by the suite's authors into "arithmetic" and "random/control" categories).
- **Cell/gate count:** From a few hundred gates up to ~500,000+ for the largest arithmetic benchmarks (e.g., large multipliers).
- **RTL language:** Distributed as gate-level Verilog/BLIF (AIG-derived); not hand-written behavioral RTL.
- **Expected synthesis runtime:** Seconds for small circuits; minutes for the largest multipliers due to `abc` mapping cost on very wide arithmetic structures.
- **Expected placement runtime:** Minutes for large arithmetic circuits due to high local connectivity density.
- **Memory requirement:** 1–8 GB depending on benchmark.
- **License:** Released for open academic use by the EPFL Integrated Systems Laboratory; must confirm current license file at acquisition time (historically permissive, no formal SPDX tag on original release — record explicitly).
- **Maintainer:** EPFL Integrated Systems Laboratory (original authors); community-maintained mirrors exist on GitHub.
- **Official repository:** GitHub organization `lsils` (Logic Synthesis and Verification Group, EPFL) hosts the EPFL benchmark suite and related logic-synthesis tooling — pin exact commit.
- **Industrial relevance:** High for datapath/arithmetic-unit stress-testing of congestion and thermal predictors, since real designs' hot regions are frequently arithmetic-dense.
- **Limitations:** No behavioral RTL (gate-level only) means Stage A synthesis (Phase 14.1) is effectively a technology-mapping pass rather than full elaboration+synthesis — must be documented as a distinct acquisition sub-category, not conflated with RTL-sourced benchmarks.

### 2.4 OpenCores (selected IP cores)

- **Why selected:** Real-world IP heterogeneity (UARTs, SPI/I2C controllers, DSP blocks, small SoC peripherals) not present in academic-only suites; improves generalization to realistic peripheral logic.
- **Expected complexity:** Highly variable, small-to-medium per core.
- **Cell/gate count:** Roughly hundreds to tens of thousands of gates per core, project-dependent.
- **RTL language:** Predominantly Verilog; some VHDL cores.
- **Expected synthesis runtime:** Seconds to a few minutes per core.
- **Expected placement runtime:** Tens of seconds to minutes.
- **Memory requirement:** 1–4 GB.
- **License:** **Per-project, not suite-wide** — individual OpenCores/FreeCores projects carry independently declared licenses (commonly LGPL, GPL, or a permissive project-specific license); the acquisition process must record and clear the license of **each individual core**, not assume a blanket license for the OpenCores platform.
- **Maintainer:** No single maintainer; the OpenCores project itself is community-run with per-project maintainers of widely varying activity level (many projects are dormant).
- **Official repository:** Historically hosted on opencores.org (project-hosting portal, not a single git host); many active cores have since migrated to individual GitHub repositories — acquisition must record the specific host actually used per core.
- **Industrial relevance:** High — directly analogous to real peripheral/glue-logic IP found in production SoCs.
- **Limitations:** Inconsistent code quality and documentation across projects; some projects are unmaintained/abandoned, increasing preprocessing burden (Part 8); license heterogeneity is the single largest compliance risk in the entire benchmark set and requires per-core sign-off.

### 2.5 PicoRV32

- **Why selected:** Minimal RV32I(+M/C) core; ideal low-complexity anchor for pipeline sanity-checking and as an easy tier in the train split.
- **Expected complexity:** Small.
- **Cell/gate count:** Roughly 3,000–7,000 gates depending on configuration (multiplier/compressed-ISA options).
- **RTL language:** Verilog.
- **Expected synthesis runtime:** Well under 1 minute.
- **Expected placement runtime:** Under 1 minute.
- **Memory requirement:** <2 GB.
- **License:** ISC License (permissive) — confirmed at the project's `LICENSE` file.
- **Maintainer:** Clifford Wolf (original author); repository remains widely used/forked though update cadence has slowed.
- **Official repository:** GitHub, `cliffordwolf/picorv32`.
- **Industrial relevance:** Moderate — genuinely used in real embedded/FPGA products historically; good "simple real core" anchor.
- **Limitations:** Single-cycle-ish minimal microarchitecture is not representative of pipelined/superscalar design classes used for larger-scale OOD evaluation.

### 2.6 Ibex

- **Why selected:** Small-to-medium 2-stage in-order RISC-V core from lowRISC, used as the **zero-shot** benchmark (Phase 14.1 Part 2.2) — architecturally related to the training-split RISC-V cores but held out entirely from training.
- **Expected complexity:** Medium.
- **Cell/gate count:** Roughly 15,000–40,000 gates depending on configuration (RV32IMC, PMP, etc.).
- **RTL language:** SystemVerilog.
- **Expected synthesis runtime:** 1–5 minutes.
- **Expected placement runtime:** A few minutes.
- **Memory requirement:** 2–6 GB.
- **License:** Apache License 2.0.
- **Maintainer:** lowRISC (also used as the CPU core inside OpenTitan).
- **Official repository:** GitHub, `lowRISC/ibex`.
- **Industrial relevance:** High — used in real silicon (OpenTitan root-of-trust chips), actively maintained.
- **Limitations:** Configurability means "Ibex" is really a family of netlists; the acquisition manifest must record the exact configuration (extension set, PMP region count) used, since two Ibex configurations can differ enough in gate count to matter for split-integrity auditing.

### 2.7 RocketChip / TinyRocket

- **Why selected:** Parameterizable Chisel-generated core family; used carefully (per Phase 14.1 Part 3 leakage rules) since multiple generated configurations can share structural sub-blocks.
- **Expected complexity:** Medium to large depending on configuration; TinyRocket is a deliberately minimized configuration for fast-iteration testing.
- **Cell/gate count:** TinyRocket roughly 20,000–50,000 gates; full RocketChip configurations can exceed 100,000+ gates depending on cache sizes and extensions.
- **RTL language:** Generated Verilog, emitted from Chisel (Scala-based hardware construction language) — acquisition must record both the Chisel source commit **and** the generated Verilog snapshot, since regenerating from a different Chisel/FIRRTL toolchain version can change netlist structure.
- **Expected synthesis runtime:** 2–15 minutes depending on configuration.
- **Expected placement runtime:** Several minutes.
- **Memory requirement:** 4–12 GB.
- **License:** BSD 3-Clause (Rocket Chip Generator, UC Berkeley Architecture Research).
- **Maintainer:** UC Berkeley / RISC-V ecosystem community (chipyard/rocket-chip organizations); active but with periodic maintenance gaps.
- **Official repository:** GitHub, `chipyard/rocket-chip` (current canonical location; historically `freechipsproject/rocket-chip` — acquisition record must note the redirect/migration explicitly).
- **Industrial relevance:** High — RocketChip-derived cores have shipped in real silicon (e.g., early SiFive products); TinyRocket specifically valuable as a fast CI-friendly regression tier.
- **Limitations:** Chisel-generated Verilog requires the Chisel/FIRRTL toolchain as a **pre-acquisition dependency**, not just an RTL file — this must be captured as a build-tool version pin, not merely a source-file checksum (see Part 5).

### 2.8 CVA6 (Ariane)

- **Why selected:** Large, application-class, 6-stage, single-issue RISC-V core capable of booting Linux; provides the **OOD** upper-complexity tier (Phase 14.1 Part 2.2) — structurally distinct from the smaller embedded cores.
- **Expected complexity:** Large.
- **Cell/gate count:** Roughly 80,000–200,000+ gates depending on configuration (FPU, MMU, cache sizes, hypervisor extension).
- **RTL language:** SystemVerilog.
- **Expected synthesis runtime:** 10–20+ minutes.
- **Expected placement runtime:** 10–30+ minutes.
- **Memory requirement:** 8–24 GB.
- **License:** Permissive Apache/Solderpad license, which eases industrial adoption.
- **Maintainer:** OpenHW Foundation (formerly OpenHW Group), a not-for-profit, global, member- and contributor-driven organization; the core was originally developed as "Ariane" by ETH Zürich / University of Bologna before being contributed to OpenHW Group.
- **Official repository:** GitHub, `openhwgroup/cva6`; the project also depends on the separate `core-v-verif` submodule for verification infrastructure, which acquisition must track alongside the core RTL if any verification-derived metadata is needed.
- **Industrial relevance:** High — actively developed with industrial (e.g., Thales-affiliated) contributors and used in real research/industrial SoC integrations.
- **Limitations:** Large configuration space (CV32A6 vs. CV64A6, optional F/D/hypervisor extensions) means, as with Ibex, the exact configuration must be pinned and recorded; submodule dependencies (toolchains, `core-v-verif`) increase acquisition complexity relative to single-repository cores.

### 2.9 OpenTitan

- **Why selected:** Full silicon-root-of-trust SoC monorepo (Ibex core plus a large set of peripheral IP blocks) — valuable both as an additional large-scale OOD candidate and as a second, independent source of realistic peripheral IP (complementing OpenCores) with much higher code-quality and maintenance standards.
- **Expected complexity:** Large at full-chip (Earlgrey) scope; individual peripheral IP blocks within it are small-to-medium and can be acquired independently.
- **Cell/gate count:** Full Earlgrey top-level in the hundreds of thousands of gates; individual peripheral blocks (UART, SPI host, AES, HMAC, etc.) range from a few thousand to tens of thousands of gates each.
- **RTL language:** SystemVerilog, with significant auto-generated register-interface RTL (produced by the project's own `reggen`/`topgen` tooling from configuration files).
- **Expected synthesis runtime:** Seconds-to-minutes per individual peripheral block; tens of minutes for full top-level synthesis.
- **Expected placement runtime:** Minutes per block; potentially an hour-plus at full top-level scope.
- **Memory requirement:** 2–6 GB per block; 16–32 GB at full top-level scope.
- **License:** Unless otherwise noted, everything in the repository is covered by the Apache License, Version 2.0.
- **Maintainer:** Administered by lowRISC CIC as a collaborative project.
- **Official repository:** GitHub, `lowRISC/opentitan` (structured as a single monorepo containing hardware, software, and tooling).
- **Industrial relevance:** Very high — a genuine production-track silicon program with multiple industry partners; represents realistic full-SoC integration complexity.
- **Limitations:** Monorepo structure means acquisition must extract specific IP subdirectories rather than treating the whole repository as one benchmark unit; heavy reliance on project-specific code-generation tooling (`reggen`, `topgen`) means "RTL acquisition" for OpenTitan blocks is not a pure file-copy but requires running the project's own generation step as a documented pre-synthesis dependency — this must be flagged distinctly from hand-written-RTL acquisitions in the manifest (Part 6).

### 2.10 Summary Table

| Benchmark | Scale Tier | RTL Language | License | Split Role (per Phase 14.1) |
|---|---|---|---|---|
| ISCAS-85/89 | Trivial | Verilog/bench | Public/unrestricted (per-mirror) | Train (sanity tier) |
| ITC-99 | Small–Medium | VHDL/Verilog | Public academic | Train |
| EPFL | Small–Large | Gate-level Verilog/BLIF | Open academic (EPFL) | Train |
| OpenCores | Small–Medium | Verilog/VHDL | Per-project (mixed) | Train |
| PicoRV32 | Small | Verilog | ISC | Train |
| Ibex | Medium | SystemVerilog | Apache-2.0 | **Zero-shot** |
| RocketChip/TinyRocket | Medium–Large | Generated Verilog (Chisel) | BSD-3-Clause | Train / **OOD** (full configs) |
| CVA6 (Ariane) | Large | SystemVerilog | Apache/Solderpad | **OOD** |
| OpenTitan | Medium (blocks) – Large (top) | SystemVerilog | Apache-2.0 | Train (blocks) / **OOD** (top-level) |

---

## PART 3 — Official Download Sources

**Purpose:** Guarantee that every RTL file entering the repository is traceable to an authoritative origin with a cryptographically verifiable, version-pinned snapshot.

**Inputs:** Benchmark selection list (Part 2), organizational GitHub URLs, any DOI-bearing archival record.

**Outputs:** Per-benchmark acquisition record containing: source URL, mirror type (primary GitHub / official mirror / archival DOI), pinned commit hash or release tag, SHA-256 checksum of the acquired archive, acquisition timestamp.

**Dependencies:** Network access to GitHub (and, for Chisel-based benchmarks, to the Scala/sbt package ecosystem required to regenerate Verilog if the acquisition policy requires source-level rather than generated-Verilog acquisition).

**Runtime Expectations:** Seconds to low minutes per repository clone, dominated by repository size (OpenTitan's monorepo is the largest, potentially several minutes on a constrained link).

**Memory Expectations:** Negligible (I/O-bound, not compute-bound); disk footprint is the binding constraint (OpenTitan monorepo alone can be multiple GB with history).

**Failure Conditions:** Upstream repository moved/renamed without redirect (must be treated as a **manifest-blocking event** requiring manual re-verification, not a silent URL substitution); tag/commit no longer resolvable (force-push or history rewrite upstream); checksum mismatch between acquisition-time download and previously recorded checksum for an already-pinned version (indicates either corruption or an integrity concern requiring investigation before use).

**Validation:** Post-download SHA-256 verification against the recorded checksum; for git-based sources, verification that the resolved commit hash matches exactly the one recorded in the acquisition manifest (not just "latest of a branch").

**Source Policy by Type:**
- **GitHub (primary):** the default and preferred source for all actively maintained benchmarks (Ibex, RocketChip, CVA6, OpenTitan, PicoRV32, EPFL suite mirrors).
- **Official mirrors:** used only where no single canonical GitHub source exists (ISCAS, ITC-99) — the specific mirror chosen must be documented with justification (e.g., "hosted by [university] EDA course, cross-checked against two independent mirrors for file-count and hash consistency").
- **DOI-bearing archival sources:** used where available (e.g., a Zenodo-archived snapshot of a benchmark release) as the preferred long-term-stable reference; DOI recorded alongside the live GitHub URL so that if the live repository disappears, the archival record remains resolvable.

**Version Pinning Policy:** Every acquisition pins to an explicit **commit hash**, never a mutable branch reference (`main`/`master` alone is insufficient); where a project publishes tagged releases, the release tag is recorded in addition to the underlying commit hash for human readability.

**Industrial Notes:** This mirrors standard third-party-IP intake practice — legal/compliance teams at semiconductor companies never accept "we pulled it from the internet," they require a pinned, checksummed receipt.

**Reviewer Expectations:** AE reviewers will attempt to re-download the exact benchmark versions from the recorded URLs/hashes; any mismatch is an automatic AE failure, so this part of the specification is treated as load-bearing for the badge, not administrative overhead.

**Future Extensibility:** New benchmarks are added by appending a new acquisition record following the same schema; no structural change to the acquisition process is needed as the benchmark set grows.

---

## PART 4 — Directory Organization

**Purpose:** Provide a single, predictable filesystem layout so that acquisition, license audit, and downstream generation (Phase 14.1) can locate any benchmark's RTL, constraints, configuration, metadata, and license text deterministically.

```
benchmarks/
├── rtl/
│   └── <benchmark_id>/<version_tag>/
│       └── (verbatim upstream RTL tree, unmodified)
├── constraints/
│   └── <benchmark_id>/<version_tag>/
│       ├── clock.sdc
│       └── reset_config.yaml
├── configs/
│   └── <benchmark_id>/<version_tag>/
│       └── acquisition_config.yaml   (build/generation dependencies, e.g. Chisel toolchain version, reggen invocation)
├── metadata/
│   └── <benchmark_id>/<version_tag>/
│       └── metadata.yaml             (Part 6 schema instance)
└── licenses/
    └── <benchmark_id>/<version_tag>/
        ├── LICENSE                   (verbatim upstream license text)
        └── license_audit.yaml        (Part 7 classification record)
```

**Inputs:** Raw acquisition output per Part 3.
**Outputs:** The structured tree above, ready for consumption by Phase 14.1 Stage A.
**Dependencies:** None beyond filesystem and the acquisition scripts (Part 11).
**Runtime/Memory Expectations:** Negligible beyond the acquisition step itself; directory materialization is a copy/organize operation.
**Failure Conditions:** Namespace collision (two benchmarks mapped to the same `benchmark_id`), missing required subdirectory for a given benchmark (e.g., a benchmark acquired without a recorded license file blocks promotion out of a staging area).
**Validation:** A structural completeness check (Part 10) verifies all five subdirectories are populated for every `benchmark_id`/`version_tag` pair before that version is marked "acquisition-complete" in the manifest.

**Industrial Notes:** `rtl/` is treated as strictly read-only/verbatim — any RTL cleanup required for tool compatibility (Part 8) is applied in a *separate, derived* location outside this tree, never by mutating the acquired source in place, preserving the acquisition's audit integrity.

**Reviewer Expectations:** A clean separation between "what we downloaded" (`rtl/`) and "what we had to fix to synthesize it" (a separate preprocessing output) is exactly the kind of provenance discipline AE reviewers look for when assessing whether reported results are traceable to unmodified third-party IP versus project-modified IP.

**Future Extensibility:** Additional per-benchmark artifact types (e.g., a future `simulation_models/` category for co-simulation testbenches) can be added as new top-level categories without disturbing existing ones, since the `<benchmark_id>/<version_tag>` addressing scheme is category-agnostic.

---

## PART 5 — Version Control

**Purpose:** Guarantee that any dataset sample or paper result can be traced back to an exact, immutable benchmark version, and that benchmark updates over time are handled as additive history rather than destructive overwrites.

**Semantic Versioning Applied to Benchmark Acquisition:**
- **MAJOR** — a new upstream release with structurally significant RTL changes (e.g., a new CVA6 major version with a different pipeline stage count), or a change in which *configuration* of a parameterizable core (Ibex, RocketChip, CVA6, OpenTitan blocks) is used.
- **MINOR** — upstream bug-fix/feature commits pulled into a refreshed acquisition of the same configuration.
- **PATCH** — acquisition-process-only changes (e.g., corrected metadata, re-verified checksum after a transient download issue) with zero change to the underlying RTL content.

**Benchmark IDs:** `<suite>_<core_or_circuit_name>_<config_label>` (e.g., `riscv_ibex_rv32imc_pmp4`, `iscas85_c1908`, `opencores_uart16550`) — globally unique within the manifest, referenced by every downstream Phase 14.1 dataset sample.

**Dataset IDs:** Distinct from benchmark IDs — a dataset ID (assigned in Phase 14.1) always references exactly one `(benchmark_id, version_tag)` pair, but one benchmark version may be referenced by many dataset IDs (e.g., multiple floorplan-variant samples). This document is the authority for `benchmark_id`; Phase 14.1 is the authority for `dataset_id`.

**Manifest:** A single top-level `benchmarks/manifest.yaml` aggregates every `(benchmark_id, version_tag)` acquisition record — this is the acquisition-layer counterpart to the Phase 14.1 dataset manifest, and the two are cross-linked by `benchmark_id`.

**Hashing:** Two independent hash layers are maintained per acquired benchmark: (1) a **file-level SHA-256** over the archived RTL tree, for integrity verification; (2) a **structural WL graph hash** (consistent with Phase 14.1 Part 3.2's leakage-screening methodology) computed once the benchmark reaches gate-level form downstream — recorded here as a forward reference so that acquisition-time and generation-time hashing use the same canonical hashing procedure and cannot drift out of sync.

**Failure Conditions:** Two different upstream commits mistakenly assigned the same `version_tag`; a `version_tag` reused after the underlying RTL has changed (strictly forbidden — any RTL change requires a new tag, even for a MINOR bump).

**Validation:** A manifest-consistency check confirms every `version_tag` maps to exactly one immutable checksum for the lifetime of the project.

**Industrial Notes:** This is the same discipline used for third-party IP version locking in production tapeouts — an IP version, once used in a signed-off design, is never silently updated underneath the design team.

**Reviewer Expectations:** Explicit versioning answers the standard AE question, "if I re-run this in six months after the upstream repository has moved on, will I get the same benchmark?" — the answer here is yes, by construction.

**Future Extensibility:** The versioning scheme accommodates future benchmark families (e.g., a hypothetical future open FinFET-targeted RISC-V core) without modification, since it is defined generically over `(benchmark_id, version_tag)`.

---

## PART 6 — Benchmark Metadata Schema

**Purpose:** Define a single canonical, machine-validated schema (expressed equivalently in JSON Schema and YAML) capturing every property needed by both license audit (Part 7) and downstream dataset generation (Phase 14.1), so no benchmark property is ever tribal knowledge.

**Required Fields (schema definition, structure only, no example instance data):**

| Field | Type | Description |
|---|---|---|
| `benchmark_id` | string | Globally unique identifier (Part 5 naming convention) |
| `version_tag` | string | Semantic version per Part 5 |
| `source_url` | string (URI) | Canonical acquisition URL (Part 3) |
| `commit_hash` | string | Pinned git commit hash, or `null` for non-git sources with a DOI instead |
| `doi` | string, nullable | Archival DOI if available |
| `checksum_sha256` | string | Integrity checksum of the acquired archive |
| `rtl_language` | enum | One of: `verilog`, `systemverilog`, `vhdl`, `generated_verilog_chisel`, `gate_level_netlist` |
| `rtl_loc` | integer | Lines-of-code count of the acquired RTL tree, excluding auto-generated boilerplate where separable |
| `clock_frequency_target_mhz` | float | Nominal target frequency used for the associated constraint file |
| `target_utilization_pct` | float, nullable | Only populated once a floorplan variant is defined in Phase 14.1; `null` at pure-acquisition stage |
| `macro_count_expected` | integer | Expected count of hard macros/memory instances (0 for pure-logic benchmarks) |
| `configuration_label` | string | Human-readable configuration descriptor (e.g., `RV64GC_hyp`) for parameterizable cores |
| `license_spdx_id` | string | SPDX identifier where one exists (e.g., `Apache-2.0`, `BSD-3-Clause`, `ISC`); `NOASSERTION` where none exists |
| `maintainer_org` | string | Organization or individual maintainer of record |
| `acquisition_timestamp` | ISO-8601 datetime | When the acquisition event occurred |
| `build_dependency_notes` | string, nullable | Free-text note on any required pre-synthesis generation step (Chisel/FIRRTL build, OpenTitan `reggen`/`topgen`, etc.) |
| `split_role_hint` | enum, nullable | One of `train`, `zero_shot`, `ood`, `unassigned` — a *hint* only; authoritative assignment remains a Phase 14.1 decision |

**Inputs:** Raw acquisition record (Part 3) plus manual/automated inspection of the acquired RTL (Part 8/10 outputs feed several fields, notably `rtl_loc` and `build_dependency_notes`).

**Outputs:** One validated `metadata.yaml` per `(benchmark_id, version_tag)`, plus the aggregate `benchmarks/manifest.yaml`.

**Dependencies:** A JSON Schema validator run as part of `generate_manifest.py` (Part 11).

**Runtime/Memory Expectations:** Negligible — schema validation is near-instantaneous per record.

**Failure Conditions:** Missing required field, `license_spdx_id` of `NOASSERTION` without an accompanying manual legal-review note in `license_audit.yaml` (Part 7) — this specific combination is treated as a hard block, not a warning.

**Validation:** Full-manifest schema validation as a CI gate; any malformed or incomplete record blocks the acquisition from being marked complete.

**Industrial Notes:** This schema is deliberately the acquisition-layer analog of a component datasheet in a hardware BOM — every downstream consumer (license audit, dataset generation, paper writing) reads from this single structured source rather than re-deriving facts about each benchmark ad hoc.

**Reviewer Expectations:** A populated, schema-valid metadata table is exactly the kind of appendix material AE reviewers expect to see accompanying a benchmark-suite claim in a submission.

**Future Extensibility:** New fields can be added to the schema with a MINOR schema-version bump (the schema itself is versioned, independent of individual benchmark `version_tag`s), with backward compatibility maintained by treating new fields as optional until a full re-acquisition pass populates them.

---

## PART 7 — License Compliance

**Purpose:** Ensure every acquired benchmark's use, redistribution, and citation in publications complies with its upstream license, and that the overall project's benchmark corpus carries no incompatible-license contamination.

**License Classes Present in the Selected Set:**

| License | Present In | Key Obligation |
|---|---|---|
| **Apache License 2.0** | Ibex, CVA6 (Apache/Solderpad), OpenTitan | Preserve copyright/license notices; state changes if modified; patent grant included — generally the most industrial-use-friendly class in this set |
| **BSD 3-Clause** | RocketChip/TinyRocket | Preserve copyright notice and disclaimer; no endorsement-implying use of contributor names |
| **ISC License** | PicoRV32 | Functionally similar to MIT/BSD-2-Clause; minimal obligation (preserve notice) |
| **GPL / LGPL (project-dependent)** | Some OpenCores projects | **Copyleft** — any derivative/modified RTL redistributed must itself be GPL/LGPL-compatible; this is the highest-risk license class in the corpus and requires per-project sign-off before any preprocessing (Part 8) is applied |
| **Public-domain / unrestricted academic use** | ISCAS-85/89, ITC-99, EPFL suite | No formal SPDX obligation but citation is an academic-norm expectation, not a legal one — tracked separately from formal license obligations |
| **Commercial/proprietary (none currently selected)** | N/A | No PDK-bundled or commercially licensed RTL is included in this benchmark set; any future addition of such material requires a distinct, separately gated compliance process not covered by this document |

**Redistribution Policy:** Verbatim upstream RTL (`benchmarks/rtl/`) is redistributed under its original license, unmodified, with the original `LICENSE` file always co-located (Part 4). Any *derived* artifact (preprocessed RTL, extracted metadata, generated netlists from Phase 14.1) inherits the same license obligations as the source it was derived from, tracked per-file in `license_audit.yaml`.

**Citation Requirements:** Independent of formal license terms, the project maintains a `CITATIONS.bib`-style record per benchmark (paper citation where the benchmark suite originates from a publication, e.g., the EPFL suite's originating paper, RocketChip's originating technical report) — required for good academic practice and frequently an explicit AE checklist item.

**Commercial Restrictions:** None of the selected benchmarks carry field-of-use or commercial-use restrictions beyond standard copyleft obligations (i.e., no benchmark in this set is "non-commercial research only"); this must be re-verified per acquisition since license terms can change on new upstream releases.

**Purpose (subsection) — GPL/LGPL Handling Specifically:** Because copyleft terms are the corpus's primary compliance risk, any OpenCores project under GPL/LGPL is flagged in `license_audit.yaml` with an explicit reviewer sign-off field before it is promoted from staging to the active `benchmarks/` tree; unresolved flags block that specific benchmark's use, without blocking the rest of the corpus.

**Inputs:** Upstream `LICENSE`/`COPYING` files as acquired.
**Outputs:** Per-benchmark `license_audit.yaml` (SPDX classification, obligation summary, redistribution clearance status, citation record).
**Dependencies:** `license_audit.py` (Part 11); for ambiguous cases, manual legal/compliance review outside the automated pipeline.
**Runtime Expectations:** Automated SPDX-pattern matching runs in seconds per benchmark; manual review (GPL/LGPL/ambiguous cases) is a human-timescale process tracked as a pending-status flag, not something the pipeline blocks on indefinitely.
**Failure Conditions:** No LICENSE file present upstream (triggers mandatory manual classification, default status "unresolved — do not redistribute" until cleared); conflicting license statements between repository root and subdirectory (common in monorepos like OpenTitan) — resolved by recording the *most restrictive applicable* license for the specific subdirectory acquired.
**Validation:** Every benchmark in the active tree must have a non-"unresolved" `license_audit.yaml` status; this is a hard CI gate.
**Industrial Notes:** This mirrors exactly how a semiconductor company's legal/IP team gates third-party RTL intake before design teams are permitted to touch it.
**Reviewer Expectations:** A clean, per-benchmark license table (as summarized above) heads off the single most common AE-track objection to benchmark-suite papers: unclear redistribution rights for the artifact bundle.
**Future Extensibility:** The classification process is license-class-agnostic and extends to any future license type (e.g., CERN-OHL for future open-hardware benchmarks) by adding a new row to the obligation table without process changes.

---

## PART 8 — Preprocessing Requirements

**Purpose:** Define what minimal, strictly-necessary transformations are applied to acquired RTL to make it tool-compatible for the Phase 14.1 synthesis stage, while preserving acquisition integrity (Part 4's "verbatim `rtl/`" principle).

**RTL Cleanup:** Removal or stubbing of simulation-only constructs incompatible with Yosys synthesis (e.g., certain SystemVerilog assertions, `$display`/`$fwrite` calls inside otherwise-synthesizable modules, testbench-only files mistakenly included in a benchmark's RTL manifest scope) — performed only in the derived preprocessing output, never on the acquired source.

**Unsupported Constructs:** Modern SystemVerilog interfaces, some parameterized generate-block patterns, and certain UVM-adjacent constructs occasionally appear even in nominally-synthesizable files (particularly in CVA6 and OpenTitan, given their SystemVerilog verification-adjacent tooling) and must be identified per-benchmark during a dry-run Yosys elaboration pass; unsupported constructs are documented per-benchmark in `build_dependency_notes` (Part 6) rather than silently patched.

**Clock Constraints:** Each benchmark requires an explicit `.sdc`-equivalent clock definition; where the upstream project provides no synthesis-oriented constraint file (common for academic benchmarks), a constraint is authored based on the project's documented target frequency (where stated) or a conservative default derived from comparable benchmarks in the same complexity tier — always recorded, never left implicit.

**Reset Strategy Normalization:** Benchmarks vary in reset polarity (active-high/active-low) and synchronicity (synchronous/asynchronous); acquisition preprocessing normalizes a per-benchmark reset descriptor into `reset_config.yaml` (Part 4) without altering the RTL itself — the normalization is metadata, not RTL modification, wherever possible.

**Naming Normalization:** Top-module names, clock/reset port names, and file-naming conventions vary significantly across suites; a per-benchmark mapping table (top module name, clock port name, reset port name) is recorded in `configs/<benchmark_id>/<version_tag>/acquisition_config.yaml` so downstream automation (Phase 14.1 Stage A) can consume any benchmark through one uniform interface without per-benchmark special-casing in the generation code itself.

**Black-Box Modules:** Hard-macro or vendor-IP references that cannot be synthesized from open-source cell libraries (rare in this benchmark set, but a real concern for any future benchmark referencing vendor-specific memory compilers) are explicitly declared as black-box stubs in the acquisition config, with the stub's interface (not implementation) recorded — this is decided at acquisition time so Phase 14.1 does not have to rediscover it during synthesis failures.

**Inputs:** Verbatim acquired RTL (`rtl/`), dry-run elaboration logs.
**Outputs:** A derived, tool-compatible RTL variant stored outside the acquisition tree, plus the normalization/config metadata described above.
**Dependencies:** Yosys (for dry-run elaboration feasibility checks only, at acquisition-verification time — not full synthesis, which remains a Phase 14.1 responsibility).
**Runtime Expectations:** Seconds (small benchmarks) to a few minutes (CVA6/OpenTitan) per dry-run elaboration check.
**Memory Expectations:** Consistent with Phase 14.1 Stage A estimates for the same benchmark, since this is effectively a lightweight subset of that stage.
**Failure Conditions:** Elaboration failure persisting after documented cleanup (escalated as an "acquisition-blocked" status for that benchmark, not silently worked around); reset/clock ambiguity that cannot be resolved from upstream documentation (escalated for manual resolution).
**Validation:** A successful dry-run Yosys elaboration (parse + hierarchy check, not full mapping) is the acceptance criterion for "preprocessing-complete" status.
**Industrial Notes:** Keeping cleanup strictly separate from the acquired source is what allows the project to truthfully claim "unmodified third-party IP" in any publication while still being pipeline-compatible.
**Reviewer Expectations:** Reviewers checking reproducibility will look specifically for whether "preprocessing" secretly means "we rewrote significant RTL" — this section's discipline (metadata-first, minimal-touch) is the intended answer to that concern.
**Future Extensibility:** The per-benchmark config/normalization-table approach scales to arbitrarily many future benchmarks without growing pipeline-side special-case code.

---

## PART 9 — PDK Compatibility

**Purpose:** Record, per benchmark, which open PDKs it is known/expected to be compatible with at the acquisition stage, so that Phase 14.1's cross-PDK split (Phase 14.1 Part 3.1) has a validated starting point rather than discovering incompatibilities mid-generation.

**Sky130 (SkyWater 130nm, open PDK):** Primary/default target for this benchmark corpus given its maturity within the open-source EDA ecosystem (OpenLane/OpenROAD reference flow); all benchmarks in Part 2 are expected compatible at this node given their moderate cell/macro complexity, with the caveat that OpenTitan's larger memory instances may require Sky130-compatible open memory-compiler output rather than a vendor SRAM macro.

**GF180 (GlobalFoundries 180nm, open PDK):** Secondary target for the cross-node split; compatible with the full benchmark set in principle, though larger cores (CVA6, full OpenTitan top-level) will show substantially larger die area at this older node and correspondingly longer placement runtimes — flagged in the acquisition metadata as a "large-at-GF180" caveat rather than an incompatibility.

**ASAP7 (predictive 7nm academic PDK):** Tertiary target, primarily for cross-node extrapolation studies; because ASAP7 is a predictive/academic PDK rather than a fabricable open PDK, its use must be explicitly caveated in any publication (results are illustrative of scaling trends, not signoff-representative at this node) — this caveat is recorded once at the PDK level, not repeated per benchmark.

**Future FinFET Support:** No fully open FinFET-class fabricable PDK exists at the time of this specification; the acquisition schema's `configuration_label` and PDK-compatibility fields are deliberately left extensible (an enum-style field, not a hardcoded pair) so that a future open FinFET PDK can be added as a new compatibility target without restructuring the benchmark metadata.

**Inputs:** Benchmark RTL/metadata (Parts 2/6), target PDK `.lib`/`.lef` availability.
**Outputs:** A per-benchmark PDK-compatibility matrix entry (compatible / compatible-with-caveat / untested) recorded in `metadata.yaml`.
**Dependencies:** Access to the relevant open PDK cell libraries (a Phase 14.1 dependency, referenced here only for compatibility *recording*, not consumption).
**Runtime/Memory Expectations:** N/A at the acquisition stage — actual synthesis/placement runtime under each PDK is measured and recorded in Phase 14.1, not here.
**Failure Conditions:** A benchmark whose macro requirements cannot be satisfied by any available open PDK's memory-compiler output (flagged "PDK-incompatible" rather than force-generated with a mismatched stand-in).
**Validation:** Compatibility matrix completeness check — every benchmark must have an explicit status (not a blank field) for each of the three PDKs listed.
**Industrial Notes:** Recording compatibility explicitly, including "compatible with caveat," is what allows the cross-PDK/cross-node claims in Phase 14.1's split strategy to be defended as intentional rather than incidental.
**Reviewer Expectations:** A PDK-compatibility matrix is exactly the kind of table ICCAD/DATE reviewers expect when a paper claims "cross-technology generalization."
**Future Extensibility:** New PDKs (including a future open FinFET node) are added as new matrix columns without touching existing benchmark records.

---

## PART 10 — Quality Assurance

**Purpose:** Independently verify that every acquired benchmark is complete, uncorrupted, and minimally functional before it is promoted into the active `benchmarks/` tree.

**Benchmark Validation (structural):** File-count and directory-structure check against the expected upstream layout; verifies no partial/truncated download.

**Compile Verification:** The Part 8 dry-run Yosys elaboration serves double duty as both preprocessing validation and QA compile-verification — a benchmark that does not elaborate cleanly (after documented, minimal cleanup) does not pass QA.

**Simulation Verification:** Where the upstream project ships its own basic self-check testbench (true for PicoRV32, Ibex, CVA6, OpenTitan, RocketChip — less commonly for ISCAS/ITC-99/EPFL, which are typically distributed without testbenches), a lightweight functional smoke-test (e.g., the project's own "hello world"/basic instruction-execution regression) is run using an open simulator (Verilator or Icarus Verilog) as acquisition-time evidence that the RTL is functionally sound, not just syntactically elaborable. This is **not** full verification — it is a smoke test bounding acquisition-time risk before expensive downstream generation work is spent on broken RTL.

**Linting:** Static linting (e.g., Verilator `--lint-only` or an equivalent open linter) run per benchmark to catch latent width mismatches, unused-signal warnings, and combinational-loop risks before they surface as confusing failures deep in Phase 14.1 Stage A.

**Inputs:** Preprocessed RTL from Part 8, upstream testbenches where available.
**Outputs:** A per-benchmark `qa_report.yaml` (structural check: pass/fail; elaboration: pass/fail; smoke simulation: pass/fail/not-applicable; lint: warning count and severity summary).
**Dependencies:** Yosys, Verilator or Icarus Verilog, the linter tool.
**Runtime Expectations:** Seconds (small benchmarks) to several minutes (CVA6/OpenTitan smoke simulation, which may involve a short boot/instruction sequence).
**Memory Expectations:** Comparable to or slightly below the corresponding Phase 14.1 Stage A estimate for the same benchmark.
**Failure Conditions:** Any QA category returning fail blocks promotion from staging to the active tree; lint warnings alone (as opposed to lint errors) do not block promotion but are recorded for downstream awareness.
**Validation:** A benchmark is "QA-complete" only when structural, elaboration, and (where applicable) smoke-simulation checks all pass; this status is a required field before `generate_manifest.py` will include the benchmark in the finalized manifest.
**Industrial Notes:** This QA gate is the acquisition-layer equivalent of an incoming-inspection step in a hardware supply chain — catching a broken benchmark here is orders of magnitude cheaper than discovering it after hours of downstream Phase 14.1 generation work.
**Reviewer Expectations:** A QA pass/fail table per benchmark, included as supplementary material, preempts reviewer questions about whether reported "failures" in the downstream pipeline were pipeline bugs or bad source data.
**Future Extensibility:** The QA check set is designed to be extended (e.g., a future formal-equivalence check between acquired RTL and a regenerated version, for Chisel-sourced benchmarks) by adding new fields to `qa_report.yaml` without restructuring the QA process.

---

## PART 11 — Automation

**Purpose:** Provide the tooling that operationalizes Parts 3–10 as a repeatable, resumable, auditable process, described here at the level of responsibility and interface — not implementation.

| Script | Responsibility |
|---|---|
| `download_benchmarks.py` | Executes Part 3's acquisition process per benchmark: clones/downloads from the recorded source, pins the commit/tag, computes the SHA-256 checksum, and populates the initial `metadata.yaml` fields available at download time. Supports resume (skips already-checksummed, already-pinned benchmarks) and a `--benchmark-id` filter for targeted re-acquisition. |
| `verify_benchmarks.py` | Runs Part 10's QA gate (structural check, dry-run elaboration, smoke simulation where available, lint) and emits `qa_report.yaml` per benchmark; exits non-zero on any hard failure so it can act as a CI gate. |
| `generate_manifest.py` | Aggregates every benchmark's `metadata.yaml` and `qa_report.yaml` into the top-level `benchmarks/manifest.yaml`, applying the Part 6 schema validation; refuses to include any benchmark lacking QA-complete or license-cleared status. |
| `license_audit.py` | Runs Part 7's SPDX-pattern classification against upstream `LICENSE`/`COPYING` files, flags GPL/LGPL and no-license cases for mandatory manual review, and emits `license_audit.yaml`. |

**Inputs (all scripts):** The benchmark selection list (Part 2) and the directory conventions (Part 4).
**Outputs (all scripts):** Populated `benchmarks/` tree plus the aggregate manifest, all machine-validated.
**Dependencies:** Git, Yosys, an open RTL simulator, an open linter, a JSON Schema validator, standard checksum utilities.
**Runtime Expectations:** Dominated by `download_benchmarks.py` for large repositories (OpenTitan) and by `verify_benchmarks.py`'s smoke-simulation step for large cores (CVA6); overall corpus acquisition is expected to complete well within a working day on a standard workstation, and far faster on a cluster.
**Memory Expectations:** Bounded by the largest individual benchmark's QA step (CVA6/OpenTitan elaboration/simulation), consistent with figures in Part 2.
**Failure Conditions:** Any script failure halts progression for the affected benchmark only (per-benchmark isolation, not a whole-corpus abort) and is logged with a structured error record for later triage.
**Validation:** `generate_manifest.py`'s refusal to include incomplete/unlicensed/unverified benchmarks is itself the primary automated validation gate for the entire acquisition subsystem.
**Cluster Execution:** All four scripts are designed to be invoked per-benchmark, enabling Slurm array-job or Kubernetes indexed-job parallelization identical in structure to Phase 14.1 Part 9's cluster execution strategy, sharing the same manifest-driven resume semantics.

**Industrial Notes:** Four narrowly scoped, independently testable scripts (rather than one monolithic acquisition script) mirrors standard industrial CI/CD pipeline decomposition and makes it straightforward to re-run only the affected stage when, e.g., only a license re-audit is needed after a policy change.

**Reviewer Expectations:** Providing these four scripts as part of the artifact bundle (not just describing them) is what actually earns the AE "Functional" and "Reproducible" badges — this document specifies their responsibilities precisely so implementation can proceed without further design ambiguity.

**Future Extensibility:** New scripts (e.g., a future `pdk_compatibility_probe.py` operationalizing Part 9's matrix) slot into the same per-benchmark, manifest-driven pattern without disrupting the existing four.

---

## PART 12 — Expected Repository Structure (Post Phase 14.2)

```
project_root/
├── benchmarks/
│   ├── rtl/
│   ├── constraints/
│   ├── configs/
│   ├── metadata/
│   ├── licenses/
│   └── manifest.yaml
├── acquisition/
│   ├── download_benchmarks.py
│   ├── verify_benchmarks.py
│   ├── generate_manifest.py
│   └── license_audit.py
├── qa_reports/
│   └── <benchmark_id>/<version_tag>/qa_report.yaml
├── docs/
│   ├── benchmark_card.md            (human-readable summary of Part 2's table)
│   ├── license_compliance_report.md (aggregate of Part 7)
│   └── pdk_compatibility_matrix.md  (Part 9's matrix)
├── cluster/
│   ├── slurm/
│   └── k8s/
└── (pipeline/, scripts/, dataset_root/, etc. — as established in Phase 14.1, unaffected by this document)
```

---

## PART 13 — Deliverables

- `benchmarks/rtl/**` — verbatim, checksummed RTL for every acquired benchmark
- `benchmarks/constraints/**`, `benchmarks/configs/**` — per-benchmark clock/reset/normalization configuration
- `benchmarks/metadata/**/metadata.yaml` — Part 6 schema instances, one per `(benchmark_id, version_tag)`
- `benchmarks/licenses/**` — verbatim upstream license text plus `license_audit.yaml` per benchmark
- `benchmarks/manifest.yaml` — aggregate, schema-validated acquisition manifest
- `qa_reports/**/qa_report.yaml` — structural/elaboration/simulation/lint QA results per benchmark
- `docs/benchmark_card.md`, `docs/license_compliance_report.md`, `docs/pdk_compatibility_matrix.md` — publication-ready summary documentation
- `acquisition/*.py` — the four automation scripts (Part 11), provided as artifact-bundle components
- Checksum ledger (`benchmarks/checksums.sha256` or equivalent, aggregated across all benchmarks)

---

## PART 14 — Publication Readiness

**IEEE TCAD / TVLSI / DAC / ICCAD / DATE Fit:** This document, together with its deliverables, directly answers the standard benchmark-provenance questions reviewers raise: *which exact RTL version was used, under what license, verified how, compatible with which PDKs.*

**Artifact Evaluation:** The combination of pinned commit hashes, SHA-256 checksums, and the four automation scripts satisfies the "Available" and "Functional" AE criteria at the acquisition layer; the QA reports and manifest completeness checks satisfy "Reproducible."

**IEEE Reproducibility:** Every benchmark's `metadata.yaml` provides the full provenance chain (source URL, commit hash, checksum, license, configuration) required for an independent party to reacquire the identical benchmark corpus without ambiguity.

**Long-Term Archival:** Because upstream GitHub repositories are not guaranteed to persist indefinitely (organizational moves, repository deletion, force-pushes), the acquisition process's DOI-preference policy (Part 3) and the recommendation to mirror the finalized `benchmarks/` tree itself into a long-term archival repository (e.g., Zenodo) closes this risk.

**Zenodo / DOI Generation:** The finalized, QA-complete `benchmarks/` tree (Part 12 structure) is the natural unit to archive as a single Zenodo deposit, generating a project-level DOI that can be cited independently of any individual upstream benchmark's DOI — this DOI becomes the canonical citation target in the eventual paper's artifact-availability statement, and is recorded back into `benchmarks/manifest.yaml` once minted, closing the provenance loop.

**Industrial Note:** Long-term archival discipline of this kind is standard practice for any organization that must defend design decisions years after tapeout — the same rigor applies directly to defensible research claims.

**Reviewer Expectations:** A benchmark-acquisition specification this explicit is above the norm for most ML-for-EDA submissions (which frequently just name-drop "ISCAS and some RISC-V cores") and is intended to preempt, rather than merely survive, AE scrutiny.

**Future Scalability:** Nothing in this specification is tied to the specific twelve benchmarks enumerated in Part 2 — the acquisition philosophy, directory structure, versioning scheme, metadata schema, license process, PDK-compatibility matrix, QA gate, and automation interface all generalize directly to any future benchmark corpus expansion.
