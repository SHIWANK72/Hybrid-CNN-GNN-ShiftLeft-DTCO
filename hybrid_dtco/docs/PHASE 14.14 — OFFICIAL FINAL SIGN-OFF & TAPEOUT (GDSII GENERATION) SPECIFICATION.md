# PHASE 14.14 — OFFICIAL FINAL SIGN-OFF & TAPEOUT (GDSII GENERATION) SPECIFICATION

**Paper:** AI-Driven Design Technology Co-Optimization for Early Prediction and Mitigation of Manufacturing, Packaging, and Reliability Challenges in Semiconductor Systems
**Target Venue:** IEEE International Conference on Microelectronics (ICM 2026)
**Scope Boundary:** This phase begins at the collected, individually validated sign-off evidence produced by Phases 14.10–14.13 (parasitic extraction, static timing analysis sign-off, IR-drop/electromigration reliability analysis, and physical verification/DRC/LVS/antenna sign-off) together with the fully routed design database carried through the entire Phase 14 methodology, and terminates at a FINAL, VALIDATED, MANUFACTURING-READY TAPEOUT PACKAGE containing signed-off GDSII, its complete supporting artifact set, and full reproducibility metadata. This is the terminal phase of the Phase 14 physical-implementation methodology; no phase follows it. No design optimization, no re-placement, no re-routing, no re-synthesis, and no timing/power/physical-verification remediation occurs within this phase — this phase performs review, aggregation, conversion, packaging, and validation only, as elaborated in Part 9.

---

## PART 1 — FINAL SIGN-OFF PHILOSOPHY

**Purpose.** Final Sign-off exists to perform the single, non-negotiable function that every preceding phase of this methodology has been building toward: confirming, with full traceability back to Phase 14.1, that the design under consideration is fit for fabrication, and then converting that design into the industry-standard GDSII stream format that a foundry consumes as its literal manufacturing instruction set. This phase is simultaneously the narrowest in creative latitude (nothing may be changed) and the broadest in required evidence review (every prior phase's sign-off artifact must be re-examined) of any phase in the methodology.

**Theory.** Final Sign-off is formulated not as an optimization problem — there is no objective function to minimize or maximize here — but as a *verification aggregation and transformation* problem: given a finite, enumerable set of previously produced sign-off artifacts (timing reports from Phase 14.11, power/reliability reports from Phase 14.12, physical verification reports from Phase 14.13, and the routed database from Phase 14.9 as extracted in Phase 14.10), this phase must (a) verify that each artifact independently reports a PASS verdict under its own phase's validation gate, (b) verify that the artifacts are mutually consistent (i.e., they all describe the *same* design revision, not accidentally mismatched snapshots from different runs), (c) convert the final verified physical database into GDSII, and (d) verify that the GDSII conversion itself introduced no discrepancy relative to the DEF/ODB database it was derived from. This is a closed, decidable verification problem, not an open-ended search problem, which is precisely why no optimization step belongs here.

**Engineering rationale.** Concentrating final cross-phase consistency checking into a single terminal phase — rather than trusting each individual phase's own internal PASS verdict as sufficient in isolation — exists because inter-phase consistency failures (a stale artifact from an abandoned earlier run being accidentally carried forward, a hash mismatch indicating a database was edited outside the tracked pipeline, a manifest pointing to the wrong SPEF corner) are a categorically different failure mode than any single phase's own internal quality failure, and are only detectable by an aggregation step that has visibility into every phase's artifact set simultaneously. No single upstream phase (14.10 through 14.13) has the visibility to detect that *another* phase's artifact is stale or mismatched; only a final, dedicated aggregation phase does.

**Manufacturing philosophy.** This phase treats the foundry's GDSII ingestion process as the ultimate, unforgiving consumer of this project's entire output: a foundry mask shop does not re-run STA, does not re-check power integrity, and does not re-verify DRC/LVS on its own initiative before committing photomasks — it trusts the GDSII stream and the sign-off documentation package accompanying it. This phase's manufacturing philosophy is therefore that *the tapeout package itself must be the complete, self-sufficient proof of manufacturing readiness*, since no downstream human or process will re-derive that proof.

**Tapeout philosophy.** "Tapeout" is treated in this specification as an information-completeness event, not merely a file-format conversion event: a design is not "taped out" merely because a GDSII file exists, but only when that GDSII file is accompanied by a complete, hash-verified, cross-referenced evidence package proving every sign-off gate from Phase 14.10 onward was satisfied by the exact design revision the GDSII represents. This distinction is the organizing principle behind this phase's sixteen-part structure: GDSII generation (Part 6) is only one of ten pipeline stages (Part 5), deliberately positioned after timing, power, and physical-verification review (Stages C, D, E) rather than before them, so that GDSII is never generated from a design that has not already cleared every review gate.

**Inputs.** Verified routed DEF and ODB (carried forward from Phase 14.9, as re-extracted in Phase 14.10), verified SPEF (Phase 14.10 output), STA sign-off reports (Phase 14.11 output), IR-drop and electromigration reliability reports (Phase 14.12 output), physical verification reports — DRC, LVS, antenna — (Phase 14.13 output), the complete Liberty/LEF/TechLEF/technology file set, the gate-level Verilog netlist, the project manifest accumulated across all prior phases, and the final sign-off configuration manifest for this phase.

**Outputs.** Final signed-off GDSII, the complete tapeout package (Part 8), final QoR/sign-off JSON and CSV summaries, final documentation, and the final project manifest recording the phase's own PASS/FAIL verdict.

**Dependencies.** Requires that Phases 14.10, 14.11, 14.12, and 14.13 each independently produced a Stage-J-equivalent PASS verdict; any phase in that set reporting FAIL, or any phase whose artifact cannot be located or hash-verified, causes this phase to halt at Stage B before any review or conversion activity is attempted.

**Runtime expectations.** For benchmark designs in the 10K–500K instance range, this phase — being aggregation-, conversion-, and packaging-dominated rather than search- or optimization-dominated — is expected to complete in 2–20 minutes on a 16-thread commodity workstation, with GDSII generation (Stage F) and final consistency checking (Stage G) together typically accounting for the majority of that time.

**Memory expectations.** Peak RSS is dominated by the GDSII-generation stage's in-memory hierarchical database representation and is expected to fall in the 500 MB–6 GB range for the benchmark corpus sizes targeted in this project, scaling primarily with total instance count and hierarchy depth rather than with any search-space size (since no search occurs in this phase).

**Failure conditions.** Any upstream phase artifact reporting FAIL or being unlocatable/unhashable; any inter-artifact consistency mismatch (differing design-revision hashes across phases); any GDSII-generation error (unmapped layer, malformed hierarchy reference, precision-loss detection); any final consistency check discovering a discrepancy between the GDSII and its DEF/ODB source; and any packaging-integrity failure (incomplete file set, checksum mismatch) are all treated as hard failures routed to the failure ledger (Part 12), with no automatic remediation attempted for any of them, consistent with the no-optimization-after-sign-off philosophy of Part 9.

**Validation philosophy.** This phase's validation philosophy differs fundamentally from every optimization-bearing phase (14.6 through 14.9) and even from the review-bearing sign-off phases (14.10–14.13) in one respect: where those phases validate *whether the design meets a quality bar*, this phase validates *whether the accumulated evidence that the design meets every quality bar is itself complete, consistent, and correctly reflected in the final manufacturing artifact*. It is, in a precise sense, a validation of validations — a meta-verification phase — and its Stage J gate is accordingly the most consequential PASS/FAIL decision in the entire Phase 14 methodology, since it is the last opportunity to catch any error before the design is irreversibly committed to physical fabrication.

**Industrial notes.** This phase's structure mirrors the industrial "tapeout review" or "release-to-fab" process used across the semiconductor industry, in which a dedicated sign-off/release engineering function performs exactly this kind of cross-team evidence aggregation and GDSII streaming, distinct from and downstream of the individual timing, power, and physical-verification sign-off teams whose work this phase reviews rather than repeats.

**Reviewer expectations.** Reviewers evaluating this phase under IEEE ICM Artifact Evaluation criteria will expect the tapeout package itself to be presentable as direct evidence of the paper's DTCO methodology claims — that is, a reviewer should be able to inspect the released package and independently confirm, without re-running any EDA tool, that every sign-off gate in Phases 14.10–14.13 was satisfied for the exact design whose GDSII is included.

**Future extensibility.** While this phase is the terminal phase of the Phase 14 physical-implementation methodology, its manifest-driven, artifact-indexed architecture is deliberately designed to support a future Phase 15 (post-silicon correlation / silicon-to-model feedback) without modification, by ensuring every artifact in the tapeout package carries the full provenance chain (design revision hash, per-phase manifest linkage) that such a future phase would need to correlate measured silicon behavior back to the exact pre-fabrication model state recorded here.

**Why Final Sign-off is the ultimate quality gate before fabrication.** Every phase from 14.1 (logic synthesis) through 14.13 (physical verification) has produced a PASS verdict *local to its own scope* — Phase 14.7 verified placement legality, Phase 14.8 verified clock-tree correctness, Phase 14.9 verified routing completeness and legality, Phase 14.10 verified extraction fidelity, Phase 14.11 verified timing closure, Phase 14.12 verified power/reliability margins, and Phase 14.13 verified physical/electrical correctness against foundry rules. None of these phases, individually, verified that *all of these things are simultaneously true of the same design revision* — that is a distinct, higher-order claim that only a final aggregation phase can make, and it is precisely the claim a foundry (and an IEEE Artifact Evaluation reviewer) needs asserted before treating the design as fabrication-ready. This is why Final Sign-off, not any single upstream phase, is positioned as the ultimate gate: it is the only phase whose PASS verdict is a conjunction over every other phase's PASS verdict plus a fresh consistency check that those verdicts all describe one coherent design state.

**How every previous phase contributes to manufacturing readiness.** Logic synthesis (14.3) establishes a technology-mapped, DRC-clean-at-cell-level netlist; floorplanning (14.4) and the power distribution network (14.5) establish the physical and electrical foundation every subsequent phase builds on; placement preparation and placement (14.6–14.7) establish a legal, timing/congestion-aware spatial arrangement; clock tree synthesis (14.8) establishes a skew/latency/slew-bounded clock distribution network; routing (14.9) establishes complete, DRC-legal interconnect; parasitic extraction (14.10) establishes an accurate electrical model of that interconnect; STA sign-off (14.11) establishes that the extracted design meets its timing budget under all required corners; power/reliability sign-off (14.12) establishes that the design will not fail from IR drop or electromigration under expected operating conditions; and physical verification (14.13) establishes that the design's geometry is manufacturable (DRC-clean) and topologically faithful to its schematic intent (LVS-clean). Final Sign-off's contribution is the capstone: it does not add new engineering content to the design, but it is the phase that certifies, in one auditable artifact, that all of the above is simultaneously and consistently true.

**Why no optimization occurs after sign-off.** Once every upstream phase has certified its own PASS verdict and this phase has cross-verified consistency, any further change to the design — however small, however well-intentioned — invalidates every one of those upstream certifications, because each was computed against a specific, fixed design state. A "quick fix" applied after sign-off (e.g., a manual ECO edit to close a last-minute timing corner) would require re-running extraction, STA, power/reliability, and physical verification to remain valid, which is to say it would require re-entering the methodology at Phase 14.10 or earlier, not proceeding within this phase. This phase is therefore architecturally incapable of optimization by design: its ten stages (Part 5) contain no placement, no routing, no buffer insertion, and no netlist modification of any kind — only review, conversion, and packaging steps, elaborated fully in Part 9.

---

## PART 2 — OBJECTIVES

1. **Deterministic tapeout.** Identical inputs (all upstream phase artifacts, configuration, seed) must produce a bit-identical final GDSII and tapeout package across runs and machines. *Definition:* run-to-run byte-identical GDSII stream output. *Rationale:* determinism is the final-phase culmination of the determinism guarantee established in every prior phase (14.6 through 14.13); a non-deterministic tapeout phase would undermine the reproducibility of the entire preceding methodology at its last step. *Validation:* checksum comparison of final GDSII across ≥3 independent re-runs. *Industrial notes:* GDSII streaming tools (Magic, KLayout) are configured in deterministic-output mode, with cell-ordering and record-ordering fixed by the source database's canonical instance/net ordering rather than by any non-deterministic traversal.
2. **Technology independence.** The sign-off review logic, GDSII layer-mapping mechanism, and final QoR schema must be expressible without hard-coding a specific PDK's layer map or manufacturing grid. *Definition:* the phase's stage implementations reference layer identities exclusively through the technology file set's layer-mapping table, never through a hard-coded layer name/number. *Rationale:* enables this methodology to be applied across multiple technology nodes without flow rewrites, consistent with every prior phase's technology-independence objective. *Validation:* successful execution of the identical pipeline against ≥2 distinct open PDKs with distinct GDSII layer maps. *Industrial notes:* mirrors the technology-independence objective established in Phase 14.7 Part 2 through Phase 14.9 Part 2.
3. **Reproducibility.** Every run must emit a self-contained configuration snapshot, referencing every upstream phase's own configuration snapshot by hash, sufficient to reconstruct the entire multi-phase provenance chain from this single terminal artifact. *Definition:* a manifest tree rooted at this phase's manifest, with verifiable hash links to every ancestor phase's manifest. *Rationale:* required for Zenodo/Artifact Evaluation packaging of the *entire* Phase 14 methodology, not merely this phase in isolation. *Validation:* fresh-environment replay of the full provenance chain from this phase's manifest alone. *Industrial notes:* this objective is unique to the terminal phase; no earlier phase is required to reference the *entire* upstream chain, only its immediate predecessor.
4. **Manufacturing readiness.** The final GDSII, together with its accompanying documentation, must constitute a complete, self-sufficient package that a foundry could, in principle, accept for fabrication without requesting additional artifacts. *Definition:* the tapeout package (Part 8) contains every artifact category a standard foundry tapeout checklist requires. *Rationale:* this is the phase's core manufacturing philosophy claim (Part 1) made measurable. *Validation:* checklist-based completeness audit against a configured foundry-tapeout-requirements template (Part 7). *Industrial notes:* the specific checklist template is technology/foundry-specific and supplied as a configuration input (Part 3), not hard-coded, preserving Objective 2.
5. **Complete sign-off.** Every one of the four upstream sign-off phases (14.10 STA-supporting extraction, 14.11 timing, 14.12 power/reliability, 14.13 physical verification) must report an unambiguous PASS verdict for the exact design revision under review in this phase. *Definition:* a boolean AND over four independently-sourced PASS verdicts. *Rationale:* this is the most fundamental gating objective of the entire phase — the single fact this phase exists to certify. *Validation:* direct verdict-field extraction and logical conjunction from each upstream phase's Stage-J-equivalent output. *Industrial notes:* corresponds directly to the industrial "all sign-offs green" tapeout release criterion.
6. **Zero critical violations.** No upstream artifact may report any violation classified as CRITICAL under its own phase's severity taxonomy (timing violations beyond configured slack tolerance, IR-drop/EM violations beyond configured margin, any DRC violation, any LVS mismatch, any unresolved antenna violation). *Definition:* zero-count check across each upstream phase's critical-violation-classified metric fields. *Rationale:* distinguishes an unambiguous, unqualified PASS from a conditional or WARN-qualified pass that should not proceed to tapeout without explicit human waiver (a case this phase does not itself decide, but flags, per Part 12). *Validation:* direct field extraction from each upstream phase's QoR JSON. *Industrial notes:* mirrors the industrial concept of a "showstopper" bug list that must be empty before release.
7. **Artifact reproducibility.** Every artifact referenced by this phase's manifest must be independently re-derivable from its own recorded inputs and configuration, not merely present as an opaque file. *Definition:* every upstream artifact's manifest entry includes sufficient provenance (tool version, seed, input hashes) to support independent regeneration. *Rationale:* a tapeout package that includes final files but not the means to reproduce them falls short of this project's IEEE Artifact Evaluation ambitions. *Validation:* provenance-completeness check per artifact against the manifest schema (Part 14). *Industrial notes:* distinct from Objective 3 (which concerns this phase's own reproducibility) — this objective concerns whether *every constituent artifact across the whole methodology* is reproducible, checked here because this is the only phase with visibility into the complete set.
8. **Database integrity.** The final ODB, DEF, and GDSII must all describe geometrically and electrically identical designs — no instance, net, or geometry present in one representation may be absent or altered in another. *Definition:* cross-representation geometric and connectivity equivalence check. *Rationale:* this is the specific, measurable form of the "GDSII conversion introduced no discrepancy" concern raised in Part 1's theory section. *Validation:* automated cross-format diff (Stage G) comparing instance count, net count, pin coordinates, and layer geometry across ODB, DEF, and GDSII. *Industrial notes:* directly corresponds to the industrial GDSII-vs-DEF "database compare" step routinely performed before release.
9. **Configuration integrity.** Every configuration parameter used across every phase of the entire methodology must be captured, versioned, and internally consistent (no contradictory parameter values between phases that should share a single source of truth, such as the technology node identifier or the target clock period). *Definition:* cross-phase configuration-parameter consistency check. *Rationale:* a configuration inconsistency (e.g., Phase 14.11's STA sign-off run against a different SDC than Phase 14.9's routing-stage timing-criticality weighting) would silently invalidate the meaningfulness of the sign-off chain even if every individual phase reported PASS. *Validation:* automated cross-phase configuration-field comparison against a defined set of must-match parameters (Part 5, Stage B). *Industrial notes:* this is a class of error notoriously difficult to detect manually and is precisely why this phase exists as an automated aggregation step rather than a manual checklist.
10. **Manifest integrity.** The complete manifest tree (this phase's manifest plus every ancestor phase's manifest, transitively) must be internally consistent, acyclic, and fully hash-verified. *Definition:* a graph-integrity and hash-verification check over the full manifest DAG. *Rationale:* the manifest is the backbone of every reproducibility and provenance claim made throughout this methodology; a corrupted or inconsistent manifest undermines all of them simultaneously. *Validation:* automated manifest-graph traversal and hash re-verification (Stage B). *Industrial notes:* mirrors the concept of a build-provenance/SBOM (software bill of materials) verification step, applied here to a hardware design's provenance chain.
11. **Complete documentation.** The tapeout package must include human-readable documentation summarizing every phase's key results (not merely raw JSON/CSV), sufficient for a reviewer or foundry engineer unfamiliar with the automated pipeline to understand what was done and why. *Definition:* presence and completeness of the documentation deliverable (Part 8) against a fixed table-of-contents template. *Rationale:* raw machine-readable artifacts alone do not satisfy the human-reviewability requirement of IEEE Artifact Evaluation or industrial tapeout review. *Validation:* template-completeness check (Stage H). *Industrial notes:* directly informed by the documentation expectations of IEEE ICM/TCAD/TVLSI supplementary-material requirements.
12. **Dataset completeness.** The full corpus of QoR data generated across all fourteen phases of this methodology must be present, correctly indexed, and schema-valid in this phase's final aggregated dataset output. *Definition:* presence and schema validation of the final aggregated JSON/CSV dataset (Part 10, Part 11). *Rationale:* this project's stated broader aim is ML-dataset generation for DTCO research; the terminal phase is the natural point at which the complete, cross-phase dataset is assembled and validated as a single coherent artifact. *Validation:* schema conformance and cross-phase completeness check (Stage H). *Industrial notes:* this objective is unique to this project's DTCO/ML research orientation and has no direct industrial-tapeout analogue, though it is structurally similar to a design-history/lessons-learned archive maintained by industrial release engineering teams.
13. **Industrial compatibility.** The final GDSII and its accompanying LEF/Liberty/netlist artifacts must be directly consumable by standard industrial and open-source physical-verification and layout tools (Magic, KLayout, Netgen, and commercial equivalents) without format translation. *Definition:* successful round-trip open/inspect of the final GDSII in ≥2 independent tools. *Rationale:* validates that this methodology's fully open-source-EDA-based pipeline produces output indistinguishable, at the format level, from an industrially produced tapeout package. *Validation:* automated round-trip open/geometry-count check in each target tool (Stage E, re-confirmed at Stage J). *Industrial notes:* directly supports the industrial-deployment claim elaborated in Part 16.
14. **Open-source reproducibility.** Every tool invoked throughout the phase, and transitively throughout the entire methodology, must be open-source and version-pinned, such that the complete tapeout package can be regenerated using only publicly available tooling. *Definition:* a manifest-recorded, version-pinned tool inventory with no proprietary-tool dependency. *Rationale:* this is a foundational commitment of the entire Phase 14 methodology (established beginning in Phase 14.6) and is re-verified here as a terminal-phase objective specifically because it is the last opportunity to catch an inadvertent proprietary-tool dependency before the package is archived/released. *Validation:* tool-inventory audit against an allow-list of open-source tools (Stage B). *Industrial notes:* directly supports the Zenodo/GitHub archival objectives elaborated in Part 16.
15. **Future scalability.** The final package's structure and manifest schema must support extension to future post-tapeout phases (e.g., a post-silicon correlation phase) without requiring modification to any already-archived artifact. *Definition:* additive-only schema versioning policy for the manifest and QoR schemas. *Rationale:* per Part 1's future-extensibility discussion, this phase's terminal position in the current methodology does not imply it is the terminal artifact of the broader research program. *Validation:* schema-versioning-policy compliance check (a static review of the schema definition itself, not a per-run computation). *Industrial notes:* mirrors standard API/schema-versioning discipline (additive, non-breaking extension) used in long-lived industrial design databases.

**Engineering rationale (aggregate).** These fifteen objectives are jointly necessary and, as in every prior phase's Part 2, mutually constraining: manufacturing readiness without database integrity would certify a package that looks complete but contains an undetected GDSII/DEF mismatch; complete sign-off without configuration integrity could certify four independently-PASS-ing phases that were nonetheless run against inconsistent assumptions. The objective set is evaluated as a strict conjunction; any single hard-gate objective (5, 6, 8, 9, 10, 13, 14) failing marks the run FAIL, while documentation- and dataset-completeness objectives (11, 12) are tracked as WARN-eligible if incomplete but do not by themselves block a PASS verdict unless configured as hard gates by the sign-off configuration manifest.

**Validation.** A Final Sign-off run is marked PASS only if all hard-gate objectives above independently pass their respective gates (Part 5, Stage J); any single hard-gate failure routes to Part 12 failure handling and the design is not packaged for tapeout.

**Industrial notes.** These fifteen objectives collectively correspond to the standard industrial "release-to-fabrication" checklist function, distributed here across a deterministic, automatable pipeline rather than a manual sign-off meeting, consistent with this entire methodology's automation-first philosophy.

**Future scalability.** As with every prior phase, objective *thresholds* (e.g., what constitutes a CRITICAL violation under Objective 6, which foundry checklist template governs Objective 4) are externalized to the Final Sign-off configuration manifest (Part 3), while objective *definitions* remain fixed, preserving the sweep-parameter philosophy established throughout Phases 14.6–14.13.

---

## PART 3 — INPUTS

| Input | Description | Format | Source |
|---|---|---|---|
| Verified Routed DEF | Final routed design geometry, post-Phase-14.9 | DEF 5.8 | Phase 14.9 output, re-confirmed |
| Verified ODB | Binary OpenDB database of the same final design state | `.odb` | Phase 14.9 output, re-confirmed |
| Verified GDSII (preliminary) | Any preliminary/intermediate GDSII produced during physical verification (Phase 14.13), if applicable | GDSII stream | Phase 14.13 output (if generated for DRC/LVS purposes) |
| Liberty | Full multi-corner timing/power views used across STA and power sign-off | `.lib`/`.lib.gz` | PDK |
| LEF | Cell-level geometry, pin shapes, obstruction definitions | LEF 5.8 | PDK |
| Technology LEF | Metal stack, via rules, DRC-relevant geometric rules | LEF 5.8 (tech section) | PDK |
| Verilog / Netlist | Final gate-level structural netlist corresponding to the signed-off design | Verilog (structural) | Upstream synthesis/ECO phases |
| SPEF | Extracted parasitics used by the STA sign-off phase | SPEF | Phase 14.10 output |
| STA reports | Timing sign-off summary and detailed reports across all corners | JSON + text reports | Phase 14.11 output |
| IR reports | IR-drop analysis reports (static and, if applicable, dynamic) | JSON + text reports | Phase 14.12 output |
| EM reports | Electromigration analysis reports | JSON + text reports | Phase 14.12 output |
| Physical Verification reports | DRC summary/detail reports | JSON + text reports | Phase 14.13 output |
| DRC reports | Design rule check violation reports (should be empty/zero-violation) | JSON + text reports | Phase 14.13 output |
| LVS reports | Layout-vs-schematic comparison reports | JSON + text reports | Phase 14.13 output |
| Antenna reports | Final antenna-rule compliance reports | JSON + text reports | Phase 14.9/14.13 outputs |
| Manifest | The complete, transitively-linked manifest tree spanning every prior phase | JSON (DAG) | Auto-accumulated across all phases |
| Configuration snapshots | Frozen configuration files from every prior phase, plus this phase's own | Directory snapshot | Auto-generated, cumulative |
| Metadata | Design name, benchmark ID, technology node, foundry-checklist template identifier | JSON | Project-level manifest |
| Tool versions | Full version-pinned inventory of every tool invoked across the entire methodology | JSON | Auto-accumulated across all phases |
| Hashes | Cryptographic hashes of every artifact referenced above | JSON (hash manifest) | Auto-generated at each phase, re-verified here |

**Engineering rationale.** Unlike every prior phase, whose input table draws from at most one or two immediately preceding phases, this phase's input table is deliberately the union of *every* sign-off-relevant artifact produced from Phase 14.9 onward, because this phase's Objective 5 (complete sign-off) and Objective 8 (database integrity) require simultaneous visibility into all of them; no subset would allow the cross-artifact consistency checking that is this phase's defining function.

**Validation.** Input ingestion performs: (a) presence and parseability validation for every artifact in the table above, (b) hash re-verification of every artifact against its manifest-recorded hash, (c) cross-artifact design-revision consistency check (confirming every artifact's recorded design-revision identifier matches), (d) PASS-verdict extraction and logical conjunction across the four upstream sign-off phases (Objective 5).

**Failure conditions.** Any missing, unparsable, or hash-mismatched artifact from the table above; any artifact whose recorded design-revision identifier does not match the consensus revision established by the majority of other artifacts (itself flagged as a `REVISION_MISMATCH` failure requiring investigation, not automatic resolution); any upstream phase reporting FAIL. All input-validation failures are logged as `STAGE_A_INPUT_FAILURE` or `STAGE_B_INTEGRITY_FAILURE` (Part 5) and halt before any review or conversion activity begins.

---

## PART 4 — SIGN-OFF ENVIRONMENT

**OpenROAD.** Supplies this phase's final consistency-checking utilities (cross-format geometry/connectivity comparison) and re-invokes its STA (OpenSTA) and power-analysis (`psm`/`pdn` reporting utilities, as established in Phase 14.12) engines in read-only, report-regeneration mode where this phase needs to independently re-derive a summary figure rather than trust a possibly-stale cached report.

**OpenLane2.** Supplies the orchestration layer for this phase's `Odb.SignOff`-equivalent step sequencing, consistent with the manifest-driven, resumable-step pattern established across every prior phase's environment specification.

**OpenDB.** The shared physical database serving as this phase's canonical intermediate representation for the final DEF/ODB state prior to GDSII conversion, exactly as established in Phases 14.6 through 14.9.

**Magic.** The primary open-source layout tool used in this phase for GDSII stream generation (Stage F) and for one leg of the cross-tool GDSII round-trip verification (Objective 13); Magic's DEF-to-GDSII conversion path is the reference conversion mechanism this phase relies on for layer-mapped, hierarchy-preserving stream-out.

**Netgen.** Invoked in this phase specifically to re-confirm LVS cleanliness (re-running, not merely re-reporting, the schematic-vs-extracted-layout comparison established in Phase 14.13) as part of Stage E's physical-verification review, providing an independent, fresh verification rather than relying solely on Phase 14.13's cached report.

**KLayout.** Used as the second, independent tool for the GDSII round-trip verification required by Objective 13, and for GDSII-level visual inspection/screenshot generation consumed by this phase's visualization deliverables (Part 11); using a second, independent tool for verification (rather than trusting Magic's own output uncritically) is a deliberate cross-validation choice consistent with this phase's meta-verification philosophy (Part 1).

**OpenSTA.** Re-invoked in Stage C in a report-regeneration (not full re-analysis) capacity, to confirm that the STA sign-off summary figures reported by Phase 14.11 can still be independently reproduced from the same SPEF/SDC/Liberty inputs, catching any possible artifact tampering or staleness between Phase 14.11's original run and this phase's review.

**PDK.** The complete process design kit — Liberty, LEF, TechLEF, GDSII layer-mapping table, DRC/LVS/antenna rule decks — treated in this phase as an immutable, version-pinned reference; this phase's technology-independence objective (Part 2, Objective 2) depends on every stage consuming PDK data exclusively through this uniform interface.

**Technology database.** The specific GDSII layer-number-to-name mapping table (distinct from, but derived from, the TechLEF) that Stage F's conversion mechanism consults to translate OpenDB's internal layer representation into foundry-specified GDSII layer/datatype numbers.

**Database consistency.** The overarching property, checked explicitly in Stage B and Stage G, that the ODB, DEF, SPEF, and (post-Stage-F) GDSII representations of the design are all describing the identical set of instances, nets, and geometric shapes; this is the single most safety-critical property this phase exists to verify, since a database inconsistency undetected here becomes an undetectable, silent fabrication defect.

**Layer mapping.** The explicit, version-pinned correspondence between OpenDB's internal layer identifiers and the foundry's GDSII layer/datatype numbering scheme; layer-mapping errors (e.g., a routing layer mapped to the wrong GDSII layer number) are among the most consequential possible defects this phase's Stage F/G checks are designed to catch, since such an error can produce a geometrically "valid-looking" but functionally catastrophic GDSII file.

**Coordinate systems.** Cartesian, origin at core-area lower-left corner, units in Database Units (DBU) throughout the OpenDB/DEF representation, converted at Stage F to the GDSII stream format's own user-unit/database-unit convention (typically expressed in the GDSII header as microns-per-database-unit and user-units-per-database-unit); this phase's coordinate-precision validation (Part 6) exists specifically to confirm this conversion introduces no rounding-induced geometric drift beyond the technology's manufacturing grid resolution.

**Manufacturing database.** The final GDSII file itself, once generated and validated, is treated from Stage F onward as the manufacturing database — the authoritative geometric representation for all subsequent fabrication purposes — with the DEF/ODB representations retained thereafter only as verification references, not as the primary output artifact.

**Engineering rationale.** Deploying two independent GDSII-capable tools (Magic for generation, KLayout for independent verification) rather than a single tool for both generation and verification is a direct application of this phase's meta-verification philosophy (Part 1): a single tool's self-consistency check cannot catch a systematic bug in that tool's own conversion logic, whereas an independent second tool's round-trip check can.

**Industrial notes.** This environment definition mirrors the industrial practice of employing independent physical-verification sign-off tools (often from different vendors) specifically to avoid single-tool systematic-bug blind spots at the tapeout gate, a practice this phase reproduces using two independent open-source tools (Magic, KLayout) in place of two independent commercial tools.

**Future scalability.** Because this phase's tool interactions are all mediated through the same OpenDB/GDSII-standard file-format boundaries established in every prior phase, substituting an alternative GDSII generation or verification tool in a future revision of this methodology requires no change to the Stage A–J architecture (Part 5), only a configuration-level tool-selection change.

---

## PART 5 — FINAL SIGN-OFF ARCHITECTURE

The Final Sign-off stage is a deterministic ten-stage pipeline (Stage A–J). Each stage consumes the aggregated artifact/manifest state emitted by the prior stage and emits an updated state plus a stage-local log/QoR fragment, in direct structural parallel with the Stage A–J architectures of Phases 14.6 through 14.13.

### Stage A — Database Initialization
**Purpose.** Load the final routed ODB/DEF, the complete upstream artifact set (Part 3), and the complete manifest tree into a single consistent review session.
**Theory.** Establishes the shared in-memory and on-disk representation all subsequent stages operate on, identical in role to the Stage A definitions of every prior phase.
**Engineering rationale.** A single initialization point guarantees every stage sees an identical starting artifact set, required for this phase's own determinism objective (Objective 1) and for the validity of every cross-artifact check performed in later stages.
**Inputs.** All Part 3 inputs.
**Outputs.** Initialized review session; input-presence-and-parseability validation report.
**Dependencies.** None (first stage).
**Runtime.** Seconds to tens of seconds, dominated by the sheer number of distinct artifact files being loaded and parsed.
**Memory.** Modest; dominated by manifest-tree in-memory representation, since geometric data is not yet loaded in full detail at this stage.
**Failure conditions.** Any Part 3 artifact missing or unparsable.
**Validation.** Every Part 3 artifact successfully located and parsed.
**Industrial notes.** Mirrors the initial artifact-collection step of an industrial tapeout-review kickoff meeting, automated here as a deterministic pipeline stage.
**Reviewer expectations.** Exact tool/library versions for every invoked tool (Magic, KLayout, Netgen, OpenSTA, OpenROAD) logged at this stage.
**Future scalability.** Supports incremental initialization (loading only artifacts that changed since a prior partial run) for future ECO-tapeout-review workflows without structural change.

### Stage B — Artifact Integrity Verification
**Purpose.** Verify the hash, provenance, and cross-artifact revision consistency of every input artifact, and verify the complete manifest tree's internal graph integrity.
**Theory.** Treats artifact integrity as a distinct, prior concern to content review (Stages C–E): an artifact must first be proven to be the *correct, untampered, matching-revision* artifact before its *content* (timing numbers, DRC results) is meaningfully reviewable at all.
**Engineering rationale.** Performing integrity verification as an explicit, isolated stage — rather than implicitly assuming artifact correctness while reviewing content in Stages C–E — is what directly satisfies Objectives 8, 9, and 10 (database, configuration, and manifest integrity) as first-class, independently auditable checks rather than as incidental byproducts of content review.
**Inputs.** Stage A initialized session; manifest tree; recorded hashes.
**Outputs.** Integrity verification report (per-artifact hash match/mismatch, manifest-graph validity, cross-phase configuration-consistency check).
**Dependencies.** Stage A.
**Runtime.** Seconds to tens of seconds, dominated by hash computation over potentially large artifact files (notably the routed DEF/ODB and any preliminary GDSII).
**Failure conditions.** Any hash mismatch; any manifest-graph inconsistency (cycle, dangling reference, orphaned artifact); any cross-phase configuration parameter mismatch on a must-match field (e.g., technology node identifier, target clock period, foundry process corner set).
**Validation.** 100% hash match; manifest graph acyclic and fully resolvable; zero must-match configuration-field mismatches.
**Industrial notes.** Corresponds to the industrial "release audit" step in which a release engineering function independently re-verifies checksums and configuration consistency before accepting a design package for sign-off review, rather than trusting the submitting team's own self-report.
**Reviewer expectations.** Full hash-verification table and configuration-consistency report archived.
**Future scalability.** The must-match configuration-field list is manifest-exposed and extensible, allowing future methodology revisions to add new cross-phase consistency checks without altering this stage's algorithmic structure.

### Stage C — Timing Sign-off Review
**Purpose.** Independently re-confirm the Phase 14.11 STA sign-off PASS verdict by re-deriving summary timing figures (worst negative slack, total negative slack, per-corner pass/fail) from the same SPEF/SDC/Liberty inputs, and cross-check them against Phase 14.11's originally reported figures.
**Theory.** A lightweight, report-regeneration-only re-invocation of OpenSTA (not a full re-optimization or re-analysis) against the exact same inputs Phase 14.11 used, structured as a consistency re-derivation rather than an independent from-scratch analysis, since this phase's purpose is to catch artifact staleness/tampering, not to perform new timing analysis.
**Engineering rationale.** Re-deriving rather than merely re-reading Phase 14.11's reported figures is what allows this stage to catch a class of error invisible to simple report-reading: a report file that has been accidentally regenerated from a different (e.g., accidentally reverted) SPEF or SDC than the one currently referenced by the manifest. A pure re-read cannot detect this; a re-derivation from the referenced inputs can.
**Inputs.** SPEF, SDC, Liberty (from Stage A); Phase 14.11's originally reported summary figures (for comparison).
**Outputs.** Re-derived timing summary; consistency-comparison report (re-derived vs. originally reported).
**Dependencies.** Stage B (integrity-verified inputs).
**Runtime.** Seconds to a couple of minutes, scaling with corner count and design size, but substantially cheaper than Phase 14.11's original full sign-off run since this is a summary-figure re-derivation, not an exhaustive path-by-path re-analysis.
**Failure conditions.** Re-derived figures differing from Phase 14.11's originally reported figures beyond a configured floating-point tolerance (indicating an artifact mismatch); re-derived figures themselves showing a timing failure (indicating Phase 14.11's own PASS verdict was itself incorrect or has since been invalidated by an upstream artifact change).
**Validation.** Re-derived and originally reported figures match within tolerance for every corner; all corners show PASS.
**Industrial notes.** Corresponds to the industrial practice of an independent timing-sign-off review team re-running summary STA checks before accepting another team's sign-off report at face value.
**Reviewer expectations.** Side-by-side re-derived-vs-original comparison table archived for every corner.
**Future scalability.** Corner set and tolerance are manifest-exposed, supporting future multi-corner/multi-mode sign-off review expansion without structural change.

### Stage D — Power & Reliability Review
**Purpose.** Independently re-confirm the Phase 14.12 IR-drop and electromigration sign-off PASS verdicts through the same re-derivation-and-compare methodology established in Stage C, applied to power/reliability summary figures.
**Theory.** Identical in structure to Stage C, substituting IR-drop and EM analysis re-invocation for STA re-invocation.
**Engineering rationale.** Applying the identical re-derivation-and-compare philosophy to power/reliability sign-off as to timing sign-off (Stage C) ensures this phase's meta-verification coverage is uniform across all upstream sign-off domains, rather than being deeper for timing than for power/reliability merely due to implementation convenience.
**Inputs.** Power/current data and reliability rule tables (from Stage A); Phase 14.12's originally reported IR-drop and EM summary figures.
**Outputs.** Re-derived power/reliability summary; consistency-comparison report.
**Dependencies.** Stage C (sequential ordering for reviewer-report readability; no data dependency requires this order, but a fixed order is maintained for determinism, Objective 1).
**Runtime.** Seconds to a couple of minutes.
**Failure conditions.** Re-derived figures differing from Phase 14.12's originally reported figures beyond configured tolerance; re-derived figures themselves showing an IR-drop or EM violation.
**Validation.** Re-derived and originally reported figures match within tolerance; all reliability checks show PASS.
**Industrial notes.** Corresponds to the industrial practice of independent power-integrity sign-off review preceding tapeout release.
**Reviewer expectations.** Side-by-side re-derived-vs-original comparison table archived.
**Future scalability.** Reliability-rule-table versioning is manifest-exposed, supporting future foundry-reliability-rule-revision tracking without structural change.

### Stage E — Physical Verification Review
**Purpose.** Independently re-confirm the Phase 14.13 DRC, LVS, and antenna sign-off PASS verdicts, using a fresh Netgen LVS invocation and cross-tool DRC spot-check (rather than a full DRC re-run, given its cost) against the final routed database.
**Theory.** For LVS, a full independent re-invocation is performed (Netgen re-comparing the extracted-from-layout netlist against the reference gate-level netlist) because LVS re-verification cost is modest relative to its criticality; for DRC, a targeted spot-check re-run (a configured sample of the full rule deck, focused on the highest-severity rule categories) is performed rather than a full re-run, balancing thoroughness against this phase's non-optimization, review-oriented runtime budget.
**Engineering rationale.** Treating LVS and DRC re-verification asymmetrically (full re-run for LVS, spot-check for DRC) is a deliberate, documented engineering tradeoff: LVS failures are typically global and cheap to detect via full re-comparison, whereas full DRC re-runs are often the single most expensive operation in the entire methodology (as established in Phase 14.13) and a full re-run here would substantially undermine this phase's design goal of being a fast, aggregation-dominated terminal review rather than a repeat of Phase 14.13's own expensive work.
**Inputs.** Final routed DEF/ODB, reference gate-level netlist (for LVS); DRC rule deck and Phase 14.13's originally reported DRC violation count (for spot-check comparison).
**Outputs.** Fresh LVS comparison report; DRC spot-check report; consistency-comparison against Phase 14.13's originals.
**Dependencies.** Stage D.
**Runtime.** LVS re-run: tens of seconds to a few minutes; DRC spot-check: tens of seconds to a couple of minutes, both substantially cheaper than a full Phase-14.13-equivalent run.
**Failure conditions.** Fresh LVS reporting any mismatch; DRC spot-check finding any violation in the sampled rule subset; either result diverging from Phase 14.13's originally reported zero-violation state.
**Validation.** Fresh LVS clean (zero mismatches); DRC spot-check clean (zero violations in sampled rules); both consistent with Phase 14.13's original report.
**Industrial notes.** Corresponds to the industrial practice of a final, lighter-weight physical-verification spot-check performed by release engineering immediately before GDSII generation, distinct from and downstream of the full physical-verification sign-off team's own complete run.
**Reviewer expectations.** Full LVS report and DRC spot-check rule-coverage list archived, with the spot-check's sampled-rule-subset explicitly documented so reviewers can assess its coverage.
**Future scalability.** The DRC spot-check rule-subset selection policy is manifest-exposed, allowing future methodology revisions to expand or reweight spot-check coverage without structural change.

### Stage F — GDSII Generation
**Purpose.** Convert the final, fully sign-off-reviewed OpenDB/DEF design database into the GDSII stream format via Magic's DEF-to-GDSII conversion path, applying the technology database's layer-mapping table.
**Theory.** GDSII generation is treated as a faithful, lossless serialization of the existing OpenDB geometric and hierarchical representation, not as an opportunity for any further geometric modification; the conversion process traverses OpenDB's cell/instance hierarchy, translates each layer's shapes according to the layer-mapping table (Part 4), and serializes the result according to the GDSII binary stream specification (structure references, boundary/path/text records, and the stream's own precision/units header).
**Engineering rationale.** Performing GDSII generation only after all sign-off review stages (C, D, E) — rather than generating it earlier in the phase for efficiency — is a direct architectural expression of this phase's core philosophy (Part 1): GDSII must never be generated from a design that has not already cleared every review gate, since generating it earlier would create the possibility (however remote) of a stale or subsequently-invalidated GDSII being accidentally included in the tapeout package.
**Inputs.** Stage E-approved final OpenDB/DEF; technology database layer-mapping table; GDSII generation configuration (precision, units, hierarchy-flattening policy).
**Outputs.** Final GDSII stream file.
**Dependencies.** Stage E.
**Runtime.** Tens of seconds to a few minutes, scaling with total geometry count and hierarchy depth.
**Memory.** This phase's peak memory consumer, dominated by the in-memory hierarchical geometry representation during conversion.
**Failure conditions.** Unmapped layer reference (a layer present in OpenDB with no corresponding technology-database GDSII mapping entry); hierarchy-reference corruption (a cell reference to a non-existent or circularly-defined cell); precision-loss detection (a geometric coordinate that cannot be represented exactly in the GDSII stream's configured database-unit precision).
**Validation.** Zero unmapped-layer errors; zero hierarchy-reference errors; zero precision-loss detections beyond the technology's configured manufacturing-grid tolerance.
**Industrial notes.** Directly corresponds to Magic's `gds write` streaming mechanism as invoked in OpenLane2's final GDSII-generation step.
**Reviewer expectations.** Full layer-mapping table used for this specific run archived alongside the generated GDSII, so reviewers can independently confirm layer-mapping correctness.
**Future scalability.** Hierarchy-flattening policy (fully hierarchical vs. partially flattened GDSII) is manifest-exposed, supporting future foundry-specific submission-format preferences without structural change.

### Stage G — Final Consistency Checks
**Purpose.** Perform the cross-format geometric and connectivity equivalence check between the final GDSII (Stage F output) and its DEF/ODB source, directly satisfying Objective 8 (database integrity).
**Theory.** An automated diff comparing instance count, net count, pin coordinate positions, and per-layer geometry area/perimeter between the DEF/ODB representation and the GDSII representation (the latter re-parsed independently via KLayout, per Part 4's cross-tool-verification rationale), flagging any discrepancy beyond a configured floating-point/grid tolerance.
**Engineering rationale.** Performing this check as an explicit, dedicated stage — rather than trusting Stage F's own internal "conversion succeeded" status — is what allows this phase to catch a systematic Magic-conversion bug that might produce a GDSII file with no internal error flag but with subtly incorrect geometry, since the check is performed by re-parsing the GDSII with an entirely independent tool (KLayout) rather than trusting Magic's self-report.
**Inputs.** Stage F GDSII; Stage E-approved DEF/ODB (source of truth for comparison).
**Outputs.** Cross-format consistency report.
**Dependencies.** Stage F.
**Runtime.** Tens of seconds to a couple of minutes, dominated by KLayout's independent GDSII re-parse and geometric comparison computation.
**Failure conditions.** Any instance-count, net-count, pin-position, or per-layer-geometry discrepancy beyond configured tolerance.
**Validation.** Zero discrepancies beyond tolerance across all checked categories.
**Industrial notes.** Corresponds to the industrial "GDS-vs-DEF compare" or "stream-out verification" step performed as standard practice immediately following GDSII generation at any responsible tapeout-release function.
**Reviewer expectations.** Full cross-format comparison report, including the specific tolerance values used, archived.
**Future scalability.** Comparison categories and tolerances are manifest-exposed, supporting future methodology revisions that may add new geometric-fidelity checks (e.g., fill-shape consistency, if chip-fill insertion is added in a future phase) without structural change.

### Stage H — Report & Metadata Generation
**Purpose.** Generate the complete set of human-readable documentation and machine-readable metadata summarizing every phase's key results, satisfying Objectives 11 (complete documentation) and 12 (dataset completeness).
**Theory.** Aggregates the QoR JSON output of every phase from 14.1 through 14.13, plus this phase's own Stage B–G results, into both a structured final dataset (JSON/CSV, Part 10/11) and a narrative documentation set (Part 8) following a fixed table-of-contents template.
**Engineering rationale.** Generating documentation and metadata as a distinct, dedicated stage — after all review and conversion stages, but before final packaging (Stage I) — ensures the documentation always reflects the final, fully-reviewed, post-GDSII-generation state of the design, rather than risking documentation generated from an intermediate or pre-review state.
**Inputs.** QoR JSON from every prior phase (14.1–14.13); Stage B–G results from this phase.
**Outputs.** Complete documentation set; final aggregated dataset (JSON/CSV).
**Dependencies.** Stage G.
**Runtime.** Seconds to tens of seconds.
**Failure conditions.** Any required documentation section (per the fixed table-of-contents template) unable to be populated due to a missing upstream QoR field; final aggregated dataset failing schema validation.
**Validation.** 100% table-of-contents template completion; final dataset schema-valid.
**Industrial notes.** Corresponds to the industrial practice of generating a "tapeout summary report" or "release notes" document as a standard, expected release artifact.
**Reviewer expectations.** The documentation set is the primary artifact a human reviewer (as distinct from an automated Artifact Evaluation script) will read first.
**Future scalability.** The table-of-contents template itself is a versioned configuration artifact, supporting future documentation-scope expansion without structural change to this stage's generation logic.

### Stage I — Packaging
**Purpose.** Assemble the complete tapeout package (Part 8) — final GDSII, DEF, ODB, netlist, Liberty/LEF, all reports, all metadata, all configuration snapshots, all documentation, and all checksums — into the final, archivable directory/archive structure.
**Theory.** A deterministic, manifest-driven assembly step that copies (never modifies) every constituent artifact into the final package structure (Part 14) and computes a final, top-level checksum manifest covering every packaged file.
**Engineering rationale.** Performing packaging as a distinct, final-but-one stage (before only the final validation gate, Stage J) ensures that packaging itself — a mechanical, non-analytical operation — cannot introduce or mask any analytical discrepancy, since all analytical review (Stages C–E) and consistency checking (Stage G) has already concluded before packaging begins.
**Inputs.** Every output artifact from Stages A–H; the packaging configuration (archive format, compression policy, checklist template).
**Outputs.** Assembled tapeout package (directory tree and/or compressed archive).
**Dependencies.** Stage H.
**Runtime.** Seconds to a couple of minutes, dominated by file-copy and checksum-computation I/O for potentially large GDSII/DEF/ODB files.
**Failure conditions.** Any required package component (per the Part 8 template) missing at assembly time; checksum computation failure; archive-creation failure (e.g., insufficient disk space).
**Validation.** 100% of the Part 8 package template populated; every packaged file's checksum successfully computed and recorded.
**Industrial notes.** Corresponds to the industrial "tapeout package assembly" step, typically the final mechanical action taken by a release engineering function before formal submission to a foundry or mask shop.
**Reviewer expectations.** The final checksum manifest is what a reviewer or foundry recipient will use to verify package integrity upon receipt.
**Future scalability.** Archive format and compression policy are manifest-exposed configuration parameters, supporting future foundry-specific submission-format requirements (e.g., specific archive formats mandated by a given foundry's submission portal) without structural change.

### Stage J — Final Tapeout Validation
**Purpose.** Final automated gate-check confirming the assembled tapeout package satisfies every hard-gate objective in Part 2 before the package is marked TAPEOUT-READY.
**Theory.** A deterministic checklist evaluator over every prior stage's report, in direct structural parallel with the validation stages of every prior phase in this methodology, but distinguished as the single highest-consequence PASS/FAIL decision in the entire Phase 14 methodology given its position as the terminal gate before physical fabrication.
**Engineering rationale.** Centralizing all pass/fail logic in one final stage — exactly as established in Phase 14.7 Stage J through Phase 14.13's own validation stage — gives a single, auditable PASS/FAIL record for the entire methodology's output, which is the artifact Part 16's Artifact Evaluation and industrial-deployment claims are ultimately built on.
**Inputs.** All Stage A–I reports and outputs.
**Outputs.** PASS/FAIL verdict; final tapeout validation report; if PASS, the formal TAPEOUT-READY designation applied to the packaged artifact.
**Dependencies.** Stage I.
**Runtime.** Sub-second to a few seconds.
**Failure conditions.** Any Part 2 hard-gate objective failing at any point across Stages B–I.
**Validation.** This *is* the validation stage; its own output is the validation record — the final word of the entire Phase 14 methodology.
**Industrial notes.** Equivalent to the final "release approval" signature/gate in an industrial tapeout process, automated here as a deterministic, auditable pipeline stage rather than a manual approval meeting.
**Reviewer expectations.** This is the single report a reviewer, a co-author, or a foundry recipient will consult to answer the question "is this design ready for fabrication," and it must answer that question unambiguously.
**Future scalability.** Gate thresholds remain manifest-driven exactly as in every prior phase, but this stage's *structure* (an unconditional conjunction over every hard-gate objective) is intentionally the least configurable of any stage in the entire methodology, since weakening the terminal gate's rigor would undermine the manufacturing-readiness guarantee that is this phase's entire reason for existing.

---

## PART 6 — GDSII GENERATION

**Database conversion.** The transformation of OpenDB's internal, hierarchical, technology-agnostic geometric representation into the GDSII Stream Format's binary, record-based, technology-specific representation; this phase treats the conversion as strictly information-preserving — every instance, net-derived shape, and hierarchical reference present in OpenDB must have a corresponding, faithful GDSII representation, with no simplification, no shape merging beyond what the source database itself already represents, and no geometric approximation beyond the technology's manufacturing-grid precision.

**Geometry serialization.** Each layer's polygon, path, and rectangle shapes are serialized into GDSII BOUNDARY and PATH records according to the GDSII specification's binary record format, with coordinate values expressed in the stream's declared database units; this phase's Stage F is responsible for ensuring every OpenDB shape type maps to a GDSII-legal record type without loss of shape fidelity (e.g., a rectangular OpenDB shape is serialized as a four-point BOUNDARY or, where the technology database template prefers it, as a GDSII BOX record).

**Layer mapping.** Every OpenDB layer (routing layers, via layers, cell-boundary/obstruction layers, text/label layers for pin and net-name annotation) is translated to its corresponding GDSII layer number and datatype according to the technology database's layer-mapping table (Part 4); this table is the single most safety-critical piece of configuration data in this entire phase, since an incorrect mapping produces a GDSII file that is syntactically well-formed but semantically wrong — the specific failure mode Stage G's cross-format consistency check (Part 5) is designed to catch.

**Hierarchy preservation.** OpenDB's instance hierarchy (top-level design, standard-cell/macro instances, and — where the technology database template requests it — internal macro sub-hierarchy) is preserved in the GDSII output as STRUCTURE and SREF/AREF (structure reference / array reference) records, rather than being flattened to a single flat structure; hierarchy preservation is the default policy because it produces a smaller, more efficient GDSII file and preserves the design's logical structure for any downstream tool that benefits from hierarchical navigation (e.g., KLayout's hierarchical viewer used in Stage G's verification).

**Cell references.** Every standard-cell and macro instance is emitted as an SREF (or, for identical instance arrays such as certain memory-compiler-generated structures, an AREF) record referencing a single shared STRUCTURE definition for that cell type, rather than duplicating the cell's full geometry at every instantiation site; this is both a standard GDSII space-efficiency convention and a direct mechanism by which Stage G's consistency check can efficiently verify per-cell-type geometric fidelity once, rather than needing to re-verify identical geometry at every instance location independently.

**Compression.** The GDSII stream format itself does not mandate compression, and this phase's default policy emits an uncompressed `.gds` stream as the canonical manufacturing artifact (since foundry ingestion tooling universally expects uncompressed or foundry-specified-compression GDSII); however, the tapeout package (Part 8) may additionally include a separately compressed archive copy (e.g., gzip) purely for storage/transmission efficiency in the Zenodo/GitHub archival context (Part 16), with this compressed copy explicitly never treated as the canonical manufacturing artifact.

**Integrity checking.** Beyond Stage G's cross-format consistency check, this phase performs an internal GDSII stream-integrity check (verifying the stream's own record structure is well-formed — correct record-length fields, correctly terminated structures, a valid ENDLIB record) as part of Stage F's own completion validation, distinct from and prior to Stage G's cross-format semantic check.

**Technology mapping.** Beyond simple layer-number mapping, this phase's Stage F applies any technology-specific GDSII generation conventions required by the target foundry's submission template (e.g., specific structure-naming conventions, specific required top-level structure names, specific units/precision header values), all sourced from the technology database (Part 4) rather than hard-coded, preserving this phase's technology-independence objective (Part 2, Objective 2).

**Coordinate precision.** The GDSII stream header declares both a user-unit size (typically 1 micron) and a database-unit size (typically a small fraction of a nanometer, matching or exceeding the technology's manufacturing grid resolution); this phase's Stage F configuration fixes this precision to match the TechLEF's declared manufacturing grid exactly, and Stage F's failure-condition check (Part 5) explicitly flags any source-database coordinate that cannot be represented exactly at this precision, since such a coordinate would indicate an upstream (pre-Phase-14.9) grid-alignment defect that should have been caught far earlier in the methodology.

**Engineering rationale.** Treating GDSII generation as strictly information-preserving serialization — never an opportunity for geometric simplification or approximation — is the direct consequence of this phase's no-optimization philosophy (Part 9): any geometric change introduced during "conversion" would in fact be an undocumented, unreviewed design modification occurring after every sign-off gate had already been cleared, which is precisely the failure mode this entire phase's architecture is designed to prevent.

**Industrial notes.** This GDSII generation methodology directly mirrors the industrial DEF-to-GDSII streaming step performed by commercial and open-source layout tools alike (Magic, Cadence Virtuoso/Innovus streaming, Synopsys IC Compiler streaming), differing from commercial equivalents only in tool identity, not in the underlying information-preservation principle or layer-mapping mechanism.

---

## PART 7 — FINAL SIGN-OFF CHECKLIST

**Timing sign-off.** Verified as a hard gate via Stage C's re-derivation-and-compare check against Phase 14.11's original STA sign-off; PASS requires zero corners showing negative worst-slack beyond the configured tolerance and full consistency between re-derived and originally reported figures.

**Power sign-off.** Verified as a hard gate via Stage D's re-derivation-and-compare check against Phase 14.12's original IR-drop analysis; PASS requires zero IR-drop violations beyond configured margin and full consistency between re-derived and originally reported figures.

**IR Drop sign-off.** A specific sub-component of power sign-off, separately tracked because static and (where performed) dynamic IR-drop analyses carry distinct pass/fail criteria in Phase 14.12's own methodology; this phase's checklist tracks both sub-verdicts independently even though both roll up into the single Stage D hard gate.

**Electromigration sign-off.** Verified as a hard gate via Stage D's re-derivation-and-compare check against Phase 14.12's original EM analysis; PASS requires zero EM-rule violations beyond configured current-density margin and full consistency between re-derived and originally reported figures.

**DRC sign-off.** Verified as a hard gate via Stage E's DRC spot-check re-run, cross-checked against Phase 14.13's original full-rule-deck DRC report; PASS requires zero violations in both the spot-check subset and the originally reported full-deck result.

**LVS sign-off.** Verified as a hard gate via Stage E's full Netgen LVS re-run; PASS requires zero mismatches (device count, connectivity, net-name correspondence where tracked) between the extracted-from-layout netlist and the reference gate-level netlist.

**Antenna sign-off.** Verified as a hard gate by direct re-confirmation of Phase 14.9's/14.13's antenna-checker zero-violation result (re-invoked as part of Stage E where the antenna rule deck is included in the configured DRC spot-check subset, given antenna rules' typical classification as a DRC-adjacent rule category in most foundry rule decks).

**Database consistency.** Verified as a hard gate via Stage B (cross-artifact revision consistency) and Stage G (cross-format DEF/ODB/GDSII geometric and connectivity equivalence); PASS requires zero discrepancies at either check.

**Manifest consistency.** Verified as a hard gate via Stage B's manifest-graph integrity check; PASS requires an acyclic, fully resolvable manifest DAG with zero orphaned or dangling references.

**Configuration integrity.** Verified as a hard gate via Stage B's cross-phase must-match configuration-field comparison; PASS requires zero mismatches on any field designated must-match by the sign-off configuration manifest.

**Artifact integrity.** Verified as a hard gate via Stage B's per-artifact hash re-verification; PASS requires 100% hash match across every Part 3 input artifact.

**Hash verification.** The specific cryptographic mechanism underlying artifact-integrity checking above; this phase uses a configured cryptographic hash function (project convention: SHA-256) applied to every artifact file, with hashes recorded at each artifact's originating phase and re-computed and compared at Stage B of this phase.

**Engineering rationale.** Organizing this checklist as twelve individually named, individually validated items — rather than a single opaque "sign-off complete" flag — directly supports both this phase's reviewer-transparency objective (a reviewer can see exactly which of the twelve sub-checks passed) and its failure-diagnosis objective (a failure in any one sub-check is immediately attributable to a specific engineering domain, rather than requiring investigation of an undifferentiated overall failure).

**Validation.** Final Sign-off's Stage J PASS verdict (Part 5) is, precisely, the logical conjunction of all twelve checklist items enumerated above; any single item's failure is sufficient and necessary to produce an overall FAIL verdict, with no partial-credit or majority-vote mechanism, consistent with the hard-gate treatment established for these objectives in Part 2.

---

## PART 8 — TAPEOUT PACKAGE

**Final GDSII.** The Stage F/G-validated, manufacturing-ready GDSII stream file; the single most important artifact in the entire package, and the only artifact a foundry mask shop strictly requires to begin fabrication.

**DEF.** The final routed DEF, retained in the package as a human-and-tool-readable cross-reference against the GDSII, supporting Objective 8's database-integrity verification by any downstream party who wishes to independently re-confirm Stage G's consistency check.

**ODB.** The final OpenDB binary database, retained for any downstream party wishing to re-open the design in OpenROAD-family tooling without needing to re-derive an OpenDB state from DEF alone.

**Netlist.** The final gate-level structural Verilog netlist, retained both as the LVS reference netlist and as a human-readable record of the design's logical structure.

**Liberty.** The complete multi-corner Liberty view set used throughout the methodology's timing/power analyses, retained so that any downstream re-analysis (e.g., a future post-silicon correlation phase) can be performed without needing to separately re-source PDK Liberty files.

**LEF.** The complete LEF/TechLEF set used throughout the methodology, retained for the same re-analysis-support rationale as Liberty above.

**Manifest.** The complete, transitively-linked manifest tree spanning every phase of the methodology (Phase 14.1 through this phase), the definitive machine-readable provenance record for the entire design.

**Metadata.** Design name, benchmark ID, technology node, foundry-checklist-template identifier, complete tool-version inventory, and the final Stage J PASS verdict record.

**Reports.** The complete set of human-readable reports generated across every phase (synthesis reports, placement/CTS/routing QoR reports, STA sign-off reports, power/reliability reports, physical-verification reports) plus this phase's own Stage B–G review reports.

**Configuration snapshots.** The complete, cumulative set of frozen configuration files from every phase of the methodology, plus this phase's own configuration.

**Documentation.** The Stage H-generated narrative documentation set, following the fixed table-of-contents template (Part 2, Objective 11), written for human (not machine) consumption.

**Visualization.** The complete cross-phase visualization corpus (placement density/congestion heatmaps, clock-tree topology diagrams, routing congestion/density maps, and this phase's own GDSII-level visual screenshots generated via KLayout), assembled into a single visualization deliverable for both manual review and dataset documentation.

**Checksums.** The Stage I-computed, top-level cryptographic checksum manifest covering every file in the assembled package, the mechanism by which any recipient (reviewer, foundry, future researcher) can verify the package's integrity upon receipt without needing to re-run any analysis.

**Engineering rationale.** Including the complete PDK-derived reference files (Liberty, LEF/TechLEF) in the package — rather than merely referencing them by version identifier and expecting the recipient to separately source them — is a deliberate self-sufficiency choice consistent with Part 1's manufacturing philosophy: the package must be usable by a recipient who may not have independent access to the exact PDK revision used, particularly relevant for the project's open-PDK (sky130/gf180mcu) usage, where the PDK itself is redistributable and including it materially improves the package's long-term reproducibility.

**Industrial notes.** This package composition directly mirrors a standard industrial tapeout submission package (GDSII plus supporting sign-off documentation), extended here with the additional manifest/configuration/dataset artifacts this project's ML-dataset-generation and IEEE-reproducibility objectives require beyond what a purely industrial (non-research) tapeout would need.

---

## PART 9 — FINAL OPTIMIZATION PHILOSOPHY

**Why no optimization occurs after sign-off.** As established in Part 1, every one of this phase's ten stages performs review, re-derivation-for-consistency-checking, format conversion, or packaging — never placement, never routing, never buffer insertion, never netlist modification, and never parameter re-tuning of any upstream phase's algorithm. This is not merely a stylistic choice but a structural necessity: every upstream phase's PASS verdict (Phases 14.7 through 14.13) is a claim about a *specific, fixed* design state, and any modification performed after those verdicts were established would silently invalidate every one of them simultaneously, since none of those verdicts carries any information about whether they remain true of a *subsequently modified* design.

**Only validation.** Stages B, C, D, E, and J perform validation — confirming that a claimed property (artifact integrity, timing closure, power/reliability margin, physical correctness, overall sign-off completeness) holds for the design as it currently exists, without altering that design in the process. Validation stages are, by construction, read-only with respect to the design database; only their own report/log outputs are newly generated.

**Only packaging.** Stage I performs packaging — copying, checksumming, and archiving already-finalized artifacts — an operation that is by construction incapable of altering design content, since it operates on already-generated files as opaque byte sequences rather than as design representations subject to interpretation or modification.

**Only archival.** The Part 16 archival objectives (Zenodo, GitHub) that this phase's output feeds are themselves further downstream of even this phase's own Stage J gate; archival is, definitionally, the preservation of a fixed artifact, not an operation performed on the design at all.

**Only reproducibility.** Every re-derivation performed in Stages C, D, and E (the re-invocation of OpenSTA, IR-drop/EM analysis, and Netgen LVS) exists solely to verify that a previously reported result remains reproducible from its recorded inputs — not to produce a new or different result that would then be substituted for the original. If a re-derivation in Stage C, D, or E produces a result differing from the original beyond configured tolerance, this phase's response is to FAIL (flagging a `REVISION_MISMATCH` or equivalent failure per Part 12), never to silently accept the re-derived result as an "improved" or "corrected" figure — accepting a differing re-derived figure would itself constitute an undocumented modification of the design's certified state, exactly the failure mode this entire phase exists to prevent.

**Engineering rationale.** This four-fold philosophy (validation, packaging, archival, reproducibility, and nothing else) is what makes Final Sign-off's own behavior — like every prior phase's core objective — deterministic and auditable: a reviewer inspecting this phase's stage implementations can confirm, by code inspection alone, that no stage contains a placement call, a routing call, a netlist-mutation call, or a parameter-optimization loop, and can therefore trust that this phase's PASS verdict says something meaningful about the *unmodified* design that entered the phase, not about some silently-improved variant of it.

---

## PART 10 — FINAL QUALITY METRICS

Each metric below is emitted in this phase's final QoR JSON with: definition, importance, engineering rationale, measurement, and publication relevance.

1. **Timing PASS (bool).** *Definition:* Stage C re-derivation confirms zero corners with negative worst-slack beyond tolerance. *Importance:* hard gate, checklist item 1. *Rationale:* the single most consequential functional-correctness claim in the package. *Measurement:* direct Stage C verdict. *Publication relevance:* primary claim supporting the paper's timing-closure-methodology narrative.
2. **DRC PASS (bool).** *Definition:* Stage E spot-check plus Phase 14.13 original report both zero-violation. *Importance:* hard gate. *Rationale:* manufacturability claim. *Measurement:* direct Stage E verdict. *Publication relevance:* primary manufacturability evidence.
3. **LVS PASS (bool).** *Definition:* Stage E fresh Netgen re-run zero-mismatch. *Importance:* hard gate. *Rationale:* schematic-layout correspondence claim. *Measurement:* direct Stage E verdict. *Publication relevance:* primary functional-correctness-of-layout evidence.
4. **Antenna PASS (bool).** *Definition:* zero antenna violations confirmed at Stage E. *Importance:* hard gate. *Rationale:* manufacturing-process-compatibility claim. *Measurement:* direct Stage E verdict. *Publication relevance:* supports manufacturability narrative alongside DRC PASS.
5. **IR PASS (bool).** *Definition:* Stage D re-derivation confirms zero IR-drop violations beyond margin. *Importance:* hard gate. *Rationale:* power-integrity claim. *Measurement:* direct Stage D verdict. *Publication relevance:* supports the paper's reliability-prediction/DTCO narrative.
6. **EM PASS (bool).** *Definition:* Stage D re-derivation confirms zero EM violations beyond margin. *Importance:* hard gate. *Rationale:* reliability claim. *Measurement:* direct Stage D verdict. *Publication relevance:* supports the paper's reliability-prediction/DTCO narrative.
7. **Database consistency (bool + discrepancy count).** *Definition:* Stage G cross-format check result. *Importance:* hard gate. *Rationale:* GDSII-fidelity claim. *Measurement:* direct Stage G output. *Publication relevance:* supports the open-source-EDA-fidelity claim of Part 16.
8. **Manifest integrity (bool + issue count).** *Definition:* Stage B manifest-graph validity result. *Importance:* hard gate. *Rationale:* provenance-chain claim. *Measurement:* direct Stage B output. *Publication relevance:* supports IEEE reproducibility claims.
9. **Artifact completeness (fraction).** *Definition:* fraction of Part 3 input artifacts present and parseable. *Importance:* hard gate (must equal 1.0). *Rationale:* precondition for any further review. *Measurement:* Stage A presence check. *Publication relevance:* basic package-completeness evidence.
10. **Configuration integrity (bool + mismatch count).** *Definition:* Stage B cross-phase must-match field comparison result. *Importance:* hard gate. *Rationale:* cross-phase-consistency claim. *Measurement:* direct Stage B output. *Publication relevance:* supports the paper's methodological-rigor narrative.
11. **Hierarchy integrity (bool + reference-error count).** *Definition:* Stage F hierarchy-reference validity during GDSII generation. *Importance:* hard gate. *Rationale:* GDSII structural-correctness claim. *Measurement:* direct Stage F output. *Publication relevance:* supports manufacturability narrative.
12. **Cell count.** *Definition:* total standard-cell and macro instance count in the final design. *Importance:* basic design-scale descriptor. *Rationale:* provides scale context for every other metric. *Measurement:* direct OpenDB query. *Publication relevance:* benchmark-scale reporting for the paper's experimental section.
13. **Net count.** *Definition:* total net count in the final design. *Importance:* basic design-scale descriptor. *Rationale:* provides scale context, particularly for routing/QoR-density metrics. *Measurement:* direct OpenDB query. *Publication relevance:* benchmark-scale reporting.
14. **Layer count.** *Definition:* total number of distinct routing/via layers used in the final design. *Importance:* technology-scale descriptor. *Rationale:* contextualizes routing-phase QoR against the available metal stack. *Measurement:* direct TechLEF-derived query. *Publication relevance:* technology-node reporting.
15. **Via count (final).** *Definition:* total via instance count in the final routed/signed-off design. *Importance:* reliability/yield-relevant scale descriptor, carried forward from Phase 14.9's own via-count QoR. *Rationale:* final confirmation of the routing-phase via-minimization objective's end state. *Measurement:* direct OpenDB query, cross-checked against Stage G's GDSII-derived count. *Publication relevance:* supports the paper's reliability/yield-prediction narrative.
16. **Sign-off Runtime.** *Definition:* wall-clock time per stage and total for this phase. *Importance:* engineering/scalability metric. *Rationale:* required for the runtime-expectation claims in Part 1. *Measurement:* stage-boundary timestamps. *Publication relevance:* supports the paper's automation/scalability claims.
17. **Sign-off Memory Usage.** *Definition:* peak RSS per stage and total for this phase. *Importance:* engineering/scalability metric. *Rationale:* required for the memory-expectation claims in Part 1. *Measurement:* periodic RSS sampling. *Publication relevance:* supports the paper's automation/scalability claims.
18. **Packaging size.** *Definition:* total byte size of the assembled tapeout package. *Importance:* practical archival/distribution-planning metric. *Rationale:* relevant to Zenodo/GitHub archival planning (Part 16). *Measurement:* direct Stage I file-size aggregation. *Publication relevance:* supports supplementary-material size disclosure often required by IEEE submission portals.
19. **Checksum count.** *Definition:* total number of individual file checksums recorded in the final package manifest. *Importance:* package-completeness/integrity-verification-scope descriptor. *Rationale:* documents the granularity of the package's integrity-verification mechanism. *Measurement:* direct Stage I count. *Publication relevance:* supports reproducibility-mechanism disclosure.
20. **Hash algorithm / value set.** *Definition:* the cryptographic hash algorithm used (project convention: SHA-256) and the complete set of computed hash values. *Importance:* the specific mechanism underlying Artifact integrity and Database/Manifest integrity. *Rationale:* must be explicitly disclosed for any recipient to independently re-verify package integrity. *Measurement:* direct Stage B/I output. *Publication relevance:* required disclosure for IEEE Artifact Evaluation.
21. **Verification completeness (fraction).** *Definition:* fraction of the twelve Part 7 checklist items that were successfully evaluated (as opposed to skipped due to a missing upstream artifact). *Importance:* meta-metric on this phase's own thoroughness. *Rationale:* distinguishes "all twelve checks ran and passed" from a hypothetical (and here disallowed) partial-checklist scenario. *Measurement:* direct count across Stages B–E. *Publication relevance:* supports the paper's sign-off-rigor narrative.
22. **Documentation completeness (fraction).** *Definition:* fraction of the Stage H table-of-contents template successfully populated. *Importance:* gates Objective 11. *Rationale:* ensures the package is human-reviewable, not merely machine-verifiable. *Measurement:* direct Stage H output. *Publication relevance:* supports the paper's Artifact-Evaluation-readiness narrative.
23. **Visualization completeness (fraction).** *Definition:* fraction of the expected cross-phase visualization set present in the final package. *Importance:* supports reviewer/reader comprehension of the design's physical characteristics. *Rationale:* visualizations are a key mechanism by which reviewers unfamiliar with raw QoR JSON can assess design quality. *Measurement:* direct Stage H/I aggregation check. *Publication relevance:* directly supports figures typically included in the paper's results section.
24. **Technology version.** *Definition:* the specific PDK version/revision identifier used throughout the methodology. *Importance:* provenance/reproducibility descriptor. *Rationale:* required for any future re-derivation attempt to source the identical PDK revision. *Measurement:* direct metadata field, cross-verified for consistency at Stage B. *Publication relevance:* required methodology disclosure.
25. **Tool version inventory.** *Definition:* the complete, version-pinned list of every tool invoked across the entire methodology. *Importance:* reproducibility descriptor. *Rationale:* required for Objective 14 (open-source reproducibility). *Measurement:* direct metadata aggregation, cross-verified for consistency at Stage B. *Publication relevance:* required methodology disclosure, directly supporting Artifact Evaluation reproducibility claims.
26. **Final PASS (bool).** *Definition:* the overall Stage J verdict — the logical conjunction of all Part 2 hard-gate objectives. *Importance:* the single most important metric in the entire package. *Rationale:* this is, precisely, the claim the entire phase exists to certify. *Measurement:* direct Stage J output. *Publication relevance:* the paper's central claim of successful, complete, sign-off-clean tapeout.
27. **Tapeout readiness (bool).** *Definition:* synonymous with Final PASS but explicitly framed against the Part 2 Objective 4 manufacturing-readiness checklist rather than the full hard-gate conjunction, allowing the (rare, WARN-only) case where every hard gate passes but a soft, documentation-completeness objective is incomplete to be distinguished from unconditional Final PASS. *Importance:* nuanced completeness descriptor. *Rationale:* provides a slightly finer-grained readiness signal than the binary Final PASS alone. *Measurement:* derived from Final PASS plus Objective 11/12 status. *Publication relevance:* supports precise, non-overstated claims in the paper's conclusion.
28. **Manufacturing readiness (bool + checklist-completeness fraction).** *Definition:* the Part 2 Objective 4 foundry-checklist-template completeness result. *Importance:* directly measures this phase's core manufacturing-philosophy claim. *Rationale:* per Part 1's manufacturing philosophy. *Measurement:* direct Stage I/J checklist-audit output. *Publication relevance:* central to the paper's manufacturing-readiness claim.
29. **Artifact reproducibility (fraction).** *Definition:* fraction of all artifacts across the entire methodology carrying sufficient provenance metadata (per Objective 7) to support independent regeneration. *Importance:* gates Objective 7. *Rationale:* distinguishes "artifacts present" (Objective 9's Artifact completeness) from "artifacts reproducible" (a strictly stronger claim). *Measurement:* Stage B provenance-completeness audit across every manifest entry. *Publication relevance:* central to the paper's Artifact Evaluation reproducibility claims.
30. **ML dataset completeness (fraction).** *Definition:* fraction of the full, cross-phase QoR dataset schema successfully populated in this phase's final aggregated dataset output. *Importance:* gates Objective 12. *Rationale:* directly measures this project's stated broader DTCO/ML-dataset-generation aim at the point where the complete, final dataset is assembled. *Measurement:* Stage H schema-validation output. *Publication relevance:* central to the paper's dataset-contribution claim, distinct from and complementary to the design-quality claims (metrics 1–20 above).
31. **Cross-format geometric discrepancy (count).** *Definition:* the raw discrepancy count from Stage G's GDSII-vs-DEF/ODB check (should be zero for PASS). *Importance:* hard-gate-supporting diagnostic metric. *Rationale:* provides the specific numeric evidence underlying the Database consistency boolean (metric 7). *Measurement:* direct Stage G output. *Publication relevance:* supports detailed methodology disclosure beyond the summary boolean.
32. **Re-derivation tolerance compliance (per-domain fraction).** *Definition:* for each of Stages C, D, and E, the fraction of re-derived figures matching their originally reported counterparts within configured tolerance. *Importance:* supporting diagnostic for the meta-verification philosophy (Part 1). *Rationale:* documents not merely that re-derivation passed, but by how comfortable a margin, providing a graded confidence signal beyond the binary PASS/FAIL. *Measurement:* direct Stage C/D/E comparison output. *Publication relevance:* supports a nuanced discussion of sign-off-review confidence in the paper's methodology section.

---

## PART 11 — OUTPUTS

- **Final GDSII.** The Stage F/G-validated manufacturing-ready GDSII stream file, the phase's and the entire methodology's primary deliverable.
- **Tapeout package.** The complete Part 8 package assembled at Stage I.
- **Final DEF.** Retained final routed DEF as cross-reference and reproducibility artifact.
- **Final ODB.** Retained final OpenDB binary database.
- **Reports.** The complete cross-phase and this-phase-native report set (Part 8).
- **Metadata.** Complete design/technology/tool-version metadata (Part 8).
- **Manifest.** The complete, transitively-linked manifest tree (Part 8).
- **Checksums.** The final, top-level cryptographic checksum manifest (Part 8).
- **Visualization.** The complete cross-phase visualization corpus plus this phase's GDSII-level visualizations (Part 8).
- **Final JSON.** The Stage H/Part 10-schema-validated aggregated final QoR/sign-off dataset in JSON form.
- **Final CSV.** A flattened, tabular CSV rendering of the same final dataset, provided specifically for direct ingestion by common ML/data-analysis tooling without requiring JSON parsing.
- **Documentation.** The Stage H narrative documentation set (Part 8).

**Engineering rationale.** Providing both JSON and CSV renderings of the final aggregated dataset is a deliberate accessibility choice: JSON preserves the dataset's full nested structure (useful for programmatic, schema-aware consumers), while CSV provides a flattened, immediately spreadsheet-and-dataframe-compatible rendering, directly supporting this project's ML-dataset-generation objective (Part 2, Objective 12) for consumers who prefer tabular ingestion over JSON parsing.

**Validation.** All outputs are validated against their respective schemas/formats before the phase is marked complete; a run producing a Stage J PASS verdict but failing any output schema validation is itself marked FAIL and logged to the failure ledger, identical in mechanism to every prior phase's output-validation discipline.

---

## PART 12 — FAILURE HANDLING

| Failure Mode | Detection Stage | Recovery Strategy | Logging | Retry Policy | Fatal vs. Recoverable |
|---|---|---|---|---|---|
| Database mismatch (cross-format discrepancy) | Stage G | No automated recovery; halt and flag for manual investigation of the Stage F conversion or upstream database state | Full discrepancy report logged to failure ledger | No automatic retry (a re-run with identical inputs will reproduce the identical mismatch, per Objective 1's determinism guarantee) | **Fatal** |
| Hash mismatch | Stage B | Re-fetch/re-verify the specific artifact from its recorded originating phase; if the mismatch persists, halt | Mismatch details (expected vs. computed hash) logged | One automatic re-verification attempt; else halt | **Fatal** if persistent |
| Missing report | Stage A/B | Halt; flag the specific missing upstream phase/artifact for re-run | Missing-artifact identity logged | No automatic retry (requires upstream phase re-execution, outside this phase's scope) | **Fatal** |
| Manifest corruption | Stage B | Attempt manifest-graph repair only if a redundant/backup manifest copy exists and matches expected hash; otherwise halt | Corruption details logged | One repair attempt from backup if available; else halt | **Fatal** if no valid backup |
| Configuration corruption | Stage A/B | Halt; flag the specific inconsistent configuration field(s) for manual review | Field-level mismatch details logged | No automatic retry | **Fatal** |
| Sign-off failure (timing/power/physical) | Stage C/D/E | No automated recovery; this phase does not perform remediation (Part 9); halt and route the design back to the appropriate upstream phase (14.10–14.13) for re-analysis/correction | Full re-derivation-vs-original comparison logged | No automatic retry within this phase | **Fatal** (requires upstream phase re-entry) |
| Packaging failure | Stage I | Retry packaging once (addressing transient I/O conditions such as temporary disk-space exhaustion); if the retry fails, halt | Failure cause (I/O error, missing component) logged | One automatic retry | **Recoverable** if transient; **Fatal** if persistent |
| Tool failure (crash/non-zero exit) | Any stage | Retry the specific tool invocation once with identical inputs (to rule out a transient environment issue); if the retry fails identically, halt and flag as a tool-environment defect | Tool exit code and stderr logged | One automatic retry | **Recoverable** if transient; **Fatal** if persistent |
| GDS corruption | Stage F internal integrity check / Stage G | Regenerate GDSII from Stage F once; if the regenerated file exhibits the identical corruption, halt and flag as a Magic/conversion-tooling defect | Stream-integrity check failure details logged | One automatic regeneration attempt | **Recoverable** if transient; **Fatal** if persistent |
| Incomplete artifact (partial file) | Stage A | Halt; flag the specific incomplete artifact for re-generation by its originating phase | File-size/completeness-check details logged | No automatic retry within this phase | **Fatal** |
| Revision mismatch (cross-artifact) | Stage B | Halt; flag the specific artifact(s) whose recorded design-revision identifier diverges from consensus | Full revision-identifier comparison table logged | No automatic retry | **Fatal** |
| Antenna/DRC/LVS spot-check divergence from original | Stage E | Halt; this divergence itself indicates either an upstream Phase 14.13 artifact staleness or a genuine undetected defect, either of which requires manual investigation outside this phase's remediation scope (Part 9) | Full comparison report logged | No automatic retry | **Fatal** |

**Engineering rationale.** Unlike every prior phase's failure-handling table (Phases 14.7–14.9), which included a substantial recoverable-via-bounded-retry category for genuinely tunable optimization difficulty (density overflow, skew non-convergence, routing congestion), this phase's failure table is overwhelmingly Fatal-classified, with only transient, non-analytical failures (packaging I/O errors, tool crashes, GDS-generation transients) treated as recoverable-via-single-retry. This asymmetry is the direct and correct consequence of Part 9's no-optimization philosophy: this phase has no tunable parameter whose adjustment could legitimately resolve a sign-off or consistency failure, since doing so would require modifying the design itself, an action explicitly outside this phase's scope. A sign-off failure discovered here is not a problem this phase is equipped to solve — it is a signal that the design must re-enter the methodology at the appropriate upstream phase.

**Logging.** Every failure emits a structured log entry (stage, error class, relevant comparison/discrepancy data, retry count) to both the run-local log and the project-level failure ledger, which — as in every prior phase — is treated as a first-class Part 15 deliverable; for this specific phase, the failure ledger carries particular research value as a record of *which* upstream sign-off claims failed to survive final cross-verification, directly relevant to future work on sign-off-robustness and cross-phase-consistency-prediction research.

---

## PART 13 — AUTOMATION

- **`final_signoff.py`** — top-level orchestrator invoking Stages A–J in order, reading the final sign-off configuration manifest and writing all Part 11 outputs.
- **`generate_gds.py`** — invokes Stage F (GDSII generation) as an isolable sub-pipeline against a fixed, Stage-E-approved database snapshot, supporting standalone GDSII regeneration (e.g., following a layer-mapping-table correction) without re-running the full review chain.
- **`package_tapeout.py`** — invokes Stage I (packaging) standalone against a fixed set of already-validated Stage A–H outputs, supporting re-packaging (e.g., following a documentation-template revision) without re-running any review or conversion stage.
- **`verify_artifacts.py`** — invokes Stage B (artifact integrity verification) standalone, supporting rapid, low-cost re-verification of artifact hashes and manifest integrity independent of the full pipeline, useful for periodic archival-integrity spot-checks long after initial tapeout.
- **`validate_manifest.py`** — invokes the manifest-graph-integrity sub-check of Stage B in isolation, supporting fast manifest-correctness checking during methodology development/debugging without invoking any hash computation over large artifact files.
- **`generate_checksums.py`** — invokes the checksum-computation sub-function of Stage I in isolation, supporting checksum regeneration (e.g., following a deliberate, explicitly-versioned package-content update) without re-running packaging assembly itself.
- **`archive_release.py`** — invokes the Part 16 archival-preparation logic (Zenodo/GitHub-release-format packaging) against a fixed, Stage-J-PASS-verified tapeout package, kept as a distinct script from `package_tapeout.py` because archival-format preparation (e.g., Zenodo deposit metadata generation) is a concern distinct from and downstream of tapeout-package assembly itself.

**Resume capability.** Every script checkpoints its own stage's state at completion; `final_signoff.py` can resume from any completed stage's checkpoint rather than restarting from Stage A, keyed by the manifest's stage-completion record, identical in mechanism to every prior phase.

**Checkpointing.** Given this phase's read-heavy, review-oriented nature, checkpointing here is comparatively lightweight relative to Phases 14.7–14.9 (there is no iterative optimization trace to checkpoint mid-convergence); each stage's checkpoint consists simply of its completion status and output report, sufficient for full resume capability without any partial-convergence-state complexity.

**Manifest-driven execution.** All scripts read their full parameter set from the frozen configuration snapshot, never from ad hoc CLI flags alone, exactly as established throughout this methodology.

**Parallel execution.** Independent designs (distinct tapeout candidates) are trivially parallelizable across processes/nodes; within a single design, Stages C, D, and E (timing, power/reliability, and physical-verification review) have no data dependency on one another and may be executed in parallel by the orchestrator, with Stage B's completion as their only shared prerequisite — a deliberate exception to the otherwise strictly sequential Stage A–J ordering used for reporting-order determinism in every prior phase, justified here because these three stages' *review* activities are genuinely independent even though their *reported order* in the final documentation (Stage H) remains fixed for readability.

**Dry-run mode.** All scripts support a `--dry-run` flag performing Stage A input-presence validation and configuration echoing without executing any actual review, conversion, or packaging computation, used for fast manifest-correctness checking across large sweep batches or prior to a genuinely expensive full sign-off run.

**Engineering rationale.** Exposing per-stage-group entry points in addition to the monolithic `final_signoff.py` directly supports both the ML-corpus-generation use case established throughout this methodology and this phase's specific long-term archival-maintenance use case (e.g., re-verifying artifact integrity or re-generating checksums years after initial tapeout, without needing to re-run the entire review pipeline).

---

## PART 14 — REPOSITORY STRUCTURE

```
phase14_14_final_signoff_tapeout/
├── configs/
│   ├── signoff_default.yaml
│   ├── foundry_checklist_templates/
│   │   ├── sky130_checklist.yaml
│   │   └── gf180mcu_checklist.yaml
│   ├── gds_layer_maps/
│   │   ├── sky130_layermap.json
│   │   └── gf180mcu_layermap.json
│   └── technology/
│       ├── sky130.yaml
│       └── gf180mcu.yaml
├── scripts/
│   ├── final_signoff.py
│   ├── generate_gds.py
│   ├── package_tapeout.py
│   ├── verify_artifacts.py
│   ├── validate_manifest.py
│   ├── generate_checksums.py
│   └── archive_release.py
├── stages/
│   ├── stage_a_init.py
│   ├── stage_b_integrity.py
│   ├── stage_c_timing_review.py
│   ├── stage_d_power_reliability_review.py
│   ├── stage_e_physical_verification_review.py
│   ├── stage_f_gds_generation.py
│   ├── stage_g_final_consistency.py
│   ├── stage_h_report_metadata.py
│   ├── stage_i_packaging.py
│   └── stage_j_final_validation.py
├── schema/
│   ├── final_signoff_qor.schema.json
│   ├── manifest.schema.json
│   └── tapeout_package.schema.json
├── reports/
│   └── <design>/<config_id>/<run_id>/
│       ├── timing_review.md
│       ├── power_reliability_review.md
│       ├── physical_verification_review.md
│       ├── consistency_check.md
│       └── final_checklist.md
├── runs/
│   └── <design>/<config_id>/<run_id>/
│       ├── logs/
│       └── manifest_snapshot.json
├── release/
│   └── <design>/<config_id>/<run_id>/
│       ├── zenodo_metadata.json
│       └── github_release_notes.md
├── tapeout/
│   └── <design>/<config_id>/<run_id>/
│       ├── final.gds
│       ├── final.def
│       ├── final.odb
│       ├── netlist.v
│       ├── lef/
│       ├── liberty/
│       ├── qor_final.json
│       ├── qor_final.csv
│       └── documentation/
│           └── tapeout_summary.md
├── artifacts/
│   └── <design>/<config_id>/<run_id>/
│       └── (copies/links of every upstream-phase artifact referenced by the manifest)
├── manifest/
│   └── <design>/<config_id>/<run_id>/
│       └── manifest_tree.json
├── logs/
│   └── <design>/<config_id>/<run_id>/
│       └── (full stage-by-stage execution logs)
├── failure_ledger/
│   └── <design>/<config_id>/<run_id>/failure.json
└── docs/
    └── phase14_14_specification.md
```

**Engineering rationale.** This phase's repository structure introduces three new top-level directories not present in prior phases — `release/`, `tapeout/`, and `artifacts/` — reflecting this phase's unique terminal-phase responsibilities: `tapeout/` holds the actual manufacturing-ready package contents, `release/` holds archival-platform-specific metadata (Zenodo/GitHub) prepared by `archive_release.py`, and `artifacts/` provides a single consolidated location referencing every upstream artifact the manifest depends on, rather than requiring a package consumer to navigate back through every individual phase's own `runs/` directory structure.

---

## PART 15 — FINAL DELIVERABLES

1. **Complete implementation.** The full Stage A–J pipeline implementation (scripts + stage modules) as described in Parts 5 and 13, representing the terminal automation component of the entire Phase 14 methodology.
2. **Final GDSII.** The Stage F/G-validated, manufacturing-ready GDSII stream file for every design × configuration × seed combination executed for this project.
3. **Tapeout package.** The complete, assembled Part 8 package for every executed combination.
4. **Documentation.** The complete Stage H narrative documentation set for every executed combination.
5. **Reports.** The complete cross-phase and this-phase-native report set for every executed combination.
6. **Metadata.** The complete design/technology/tool-version metadata for every executed combination.
7. **Manifest.** The complete, transitively-linked manifest tree spanning all fourteen phases, for every executed combination.
8. **Visualization.** The complete cross-phase visualization corpus, including this phase's own GDSII-level visualizations.
9. **Failure ledger.** The complete record of all failed final-sign-off runs (Part 12), retained as first-class negative-example data documenting which cross-phase consistency or re-derivation checks failed and why.
10. **Configuration snapshots.** The complete, cumulative set of frozen configuration files spanning the entire methodology, for every executed combination.

**Engineering rationale.** As in every prior phase, the failure ledger is treated as a formal deliverable rather than discarded data; for this specific terminal phase, failure-ledger entries carry unusually high research value, since a Final Sign-off failure — by construction, given this phase's no-optimization philosophy (Part 9) — always indicates either a genuine, previously-undetected upstream defect or a cross-phase consistency problem, making these entries a particularly information-dense resource for future sign-off-robustness and reproducibility-failure-prediction research.

---

## PART 16 — PUBLICATION READINESS

**IEEE reproducibility.** Every deliverable in Part 15, and by extension every deliverable produced across the entire Phase 14 methodology, is produced under the determinism guarantees established beginning in Phase 14.6 and re-certified as a terminal-phase objective in this phase's Objective 1 and Objective 3; the complete manifest tree assembled and integrity-verified in this phase's Stage B is the definitive artifact by which IEEE reviewers, and any future researcher, can confirm that every reported number throughout the entire fourteen-phase methodology is independently regenerable from its recorded inputs.

**Artifact Evaluation.** The repository structure (Part 14), the twelve-item Final Sign-off checklist (Part 7), and the dry-run mode (Part 13) are specifically designed to satisfy the most demanding tier of IEEE Artifact Evaluation expectations: a reviewer can inspect the released tapeout package's manifest tree and checksum set, independently re-verify artifact integrity via `verify_artifacts.py`, and independently re-derive the terminal Stage J PASS verdict's supporting evidence via `final_signoff.py`'s review-only stage subset, all without needing to re-run the full, multi-hour, fourteen-phase physical implementation methodology from Phase 14.1 onward.

**Industrial deployment.** Because this phase, like every phase preceding it, is built exclusively on open-source EDA tooling (OpenROAD, Magic, Netgen, KLayout, OpenSTA) and open PDKs, with no proprietary substitution anywhere in the flow, the complete methodology — culminating in this phase's manufacturing-ready GDSII output — is directly portable to industrial open-source-EDA-based tapeout workflows without translation, and the tapeout package itself is format-compatible with standard foundry submission requirements as verified by this phase's Objective 13 (industrial compatibility) cross-tool checks.

**Zenodo archival.** The `tapeout/`, `release/`, `manifest/`, and `failure_ledger/` directory hierarchies (Part 14) are structured as flat, self-describing directory trees suitable for direct Zenodo archival, with `archive_release.py` (Part 13) generating the specific Zenodo deposit metadata (title, description, version, license, and the complete checksum manifest) required for a well-formed Zenodo deposit, consistent with the Zenodo-compatibility objective established in every prior phase and elevated here to a fully realized, ready-to-submit deposit package rather than merely a compatible directory structure.

**GitHub release.** `archive_release.py` additionally generates GitHub-release-format release notes summarizing this phase's Final PASS verdict, the complete checklist result (Part 7), and links to the corresponding Zenodo deposit, supporting a coordinated dual-platform archival strategy (GitHub for code/methodology, Zenodo for versioned, citable data/artifact releases) consistent with current best practice for reproducible computational research.

**Long-term reproducibility.** The inclusion of complete PDK reference files (Liberty, LEF/TechLEF) within the tapeout package itself (Part 8), rather than by external reference alone, together with the fully version-pinned, open-source tool inventory (Objective 14, Objective 25) recorded in this phase's metadata, is specifically designed to maximize the probability that this package remains independently regenerable years after initial release, even in the event that upstream PDK or tool-distribution infrastructure changes or becomes unavailable.

**Reviewer expectations.** Reviewers should expect, and this specification provides: an unambiguous, single terminal PASS/FAIL verdict (Stage J) representing the logical conjunction of every sign-off domain examined across the entire methodology; a complete, hash-verified provenance chain from this single terminal artifact back to Phase 14.1; and a self-sufficient tapeout package requiring no external artifact lookup to independently confirm the paper's central manufacturing-readiness and reproducibility claims.

**Open-source sustainability.** By constructing the entire fourteen-phase methodology exclusively from actively maintained open-source projects (OpenROAD, OpenLane2, Magic, Netgen, KLayout, OpenSTA) and openly licensed PDKs, this project's reproducibility does not depend on any single commercial vendor's continued tool availability or licensing terms, a sustainability property this final phase's long-term-reproducibility design (above) is specifically structured to preserve.

**Future research extensions.** The manifest schema's additive-only versioning policy (Part 2, Objective 15) and the `artifacts/` directory's consolidated, provenance-complete artifact indexing (Part 14) are specifically designed to support a future Phase 15 (post-silicon correlation and silicon-to-model feedback, in which measured silicon behavior would be correlated back against the exact pre-fabrication model state recorded throughout this methodology) without requiring any modification to the artifacts and manifests this phase has already archived — a design choice that treats this phase's terminal position in the *current* Phase 14 methodology as compatible with, rather than foreclosing, future extension of the broader research program.

---

**CONCLUSION OF THE PHASE 14 METHODOLOGY.**

Phase 14 — comprising logic synthesis (14.3), floorplanning (14.4), power distribution network design (14.5), placement preparation (14.6), placement (14.7), clock tree synthesis (14.8), global and detailed routing (14.9), parasitic extraction (14.10), static timing analysis sign-off (14.11), power and reliability sign-off (14.12), physical verification (14.13), and this phase, Final Sign-off and Tapeout (14.14) — is hereby concluded. Each phase in this sequence has been specified with the same deterministic, technology-independent, reproducible, ML-dataset-oriented engineering discipline, culminating in this terminal phase's aggregation, cross-verification, and packaging of every upstream phase's evidence into a single, self-sufficient, manufacturing-ready artifact.

The tapeout package produced by this phase represents a fully validated, manufacturing-ready semiconductor design: every timing corner has been shown to close, every power and reliability margin has been shown to hold, every physical-verification rule has been shown to be satisfied, every cross-phase artifact has been shown to be mutually consistent and independently reproducible, and the resulting GDSII has been shown, via independent cross-tool verification, to be a faithful, information-preserving representation of that validated design. No further design modification occurs, or is intended to occur, downstream of this phase.

This package therefore serves a dual purpose consistent with the stated aims of this research project. First, as an industrial artifact, it constitutes a complete, standards-compliant tapeout submission suitable for physical fabrication through any foundry accepting open-source-EDA-originated GDSII and standard supporting sign-off documentation. Second, as a research artifact, it constitutes the terminal, fully-labeled data point of a complete, fourteen-phase, cross-referenced QoR and provenance dataset spanning the entirety of physical implementation — from technology-mapped netlist through manufacturing-ready GDSII — suitable for direct use in AI-driven Design Technology Co-Optimization research, including but not limited to early prediction of manufacturing yield risk, packaging-relevant reliability risk, and cross-stage quality-of-results correlation, the stated central aim of this paper's contribution to IEEE ICM 2026 and to the broader semiconductor DTCO research community.

Phase 14 is complete. The resulting artifacts constitute the complete, reproducible, end-to-end physical implementation and sign-off flow for this research project, suitable for IEEE ICM 2026 supplementary methodology disclosure, Zenodo artifact release, GitHub archival, and future AI-driven semiconductor DTCO research.

*End of Phase 14.14 — Final Sign-off & Tapeout Specification. End of the Phase 14 Physical Implementation and Sign-off Methodology.*
