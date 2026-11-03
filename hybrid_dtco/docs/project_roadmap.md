# Project vision, evidence review, and roadmap

Prepared 3 November 2026; updated with the user’s six-month delivery decision. Delivery window: **3 November 2026–3 May 2027** (Asia/Kolkata). Final product: a usable AI-assisted EDA software service. TRL 8 is the qualification target for this bounded software system, subject to an agreed assessment rubric and demonstrated evidence; it is not a current status or guaranteed outcome.

## 1. Actual goal and vision

Long-term vision: build a reproducible AI-assisted semiconductor design decision system that identifies implementation, manufacturing, test, and package-related risks early enough to guide better design decisions, with every recommendation traceable to engineering evidence.

Master's product core: develop and evaluate a hybrid CNN–GNN predictor that combines netlist connectivity with spatial features available immediately after global placement to predict later routing congestion and timing risk. Use its predictions to rank permitted implementation choices, then rerun the reference EDA flow to determine whether those choices improve measured quality or reduce exploration cost.

Proposed working title: **Hybrid CNN–GNN for Early Congestion and Timing-Risk Prediction and EDA-Validated Design Optimization**.

The wider RTL-to-packaging-with-DFT program remains the long-term vision. For the six-month software release, DFT, physical packaging, fabrication and additional reliability predictors are expansion workstreams, outside the mandatory release unless a supervisor requirement establishes otherwise. They are not claimed as completed. Do not expand the release into these workstreams at the cost of the qualified core product.

With one fixed PDK/library, experiments primarily demonstrate design/implementation optimization. A full design–technology co-optimization claim additionally requires documented technology/library choices and validated tradeoffs; varying floorplan utilization alone is insufficient evidence of technology co-optimization.

## 2. What the final demonstrator should do

1. Accept licensed RTL, top-module/build information, timing constraints, and one supported PDK/library configuration.
2. Reproduce synthesis, floorplanning, and global placement, recording tool versions, seeds, constraints, and artifact hashes.
3. Extract the netlist graph and spatial maps from that exact early checkpoint.
4. Predict downstream congestion and timing outcomes, with confidence/uncertainty information and declared limits of applicability.
5. Rank a bounded set of design choices, such as utilization, aspect ratio, or supported placement settings, using only information available at the prediction checkpoint.
6. Validate selected choices through the downstream reference flow. Report actual outcomes, including failures, rather than treating model scores as achieved improvements.
7. Produce a reproducible report with baseline comparisons, design-family-held-out results, accuracy, runtime, resource use, and traceable artifacts.
8. For qualification, support an independent evaluator running the documented workflow within the declared operating envelope.

The primary user is an RTL/physical-design engineer or researcher making early implementation decisions. The research question is whether joint structural and spatial modeling adds useful predictive and decision-making value over simpler models at the same information boundary and compute budget. Architecture alone does not establish novelty; a literature review must establish the contribution.

## 3. Evidence review: present state

The Hybrid-CNN-GNN-ShiftLeft-DTCO repository contains detailed Phase 14.x specifications, a Python package skeleton, and a small amount of class/interface code. The other repository contains only a README.

| Area | Evidence observed | Meaning |
|---|---|---|
| Development environment | Previous onboarding verified CPU GraphSAGE forward/backward, LMDB read/write, dependency compatibility and imports | Dependency readiness; not project-model validation |
| Dataset implementation | `dataset.py` returns length zero; `get()` raises `NotImplementedError` | No functioning project dataset loader |
| Hybrid model | `hybrid_core.py` has uninstantiated branches and an unimplemented forward pass | No trainable project model demonstrated |
| Fusion | `scatter_fusion.py` forward is unimplemented | Claimed joint representation is not implemented |
| Training/API/configuration/tests | Empty files | No training run, API demo, or meaningful repository test suite |
| EDA integration | Loading/placement methods unimplemented; native parser implementation empty | No executable project RTL-to-layout pipeline demonstrated |
| Routing and extraction specification | Phase 14.9 is effectively empty; Phase 14.10 absent | Missing dependencies before downstream STA/sign-off claims |
| Results and release evidence | No model weights, benchmark results, or physical-design evidence identified in selected checkouts | No basis for a current TRL 8 claim |
| DFT and physical packaging | No implemented workflows identified | Scope, tools and qualification evidence still required |

These observations support describing the checked-in project as a concept/specification with scaffolded code. A formal numeric TRL assessment requires the institution's rubric and evidence for the defined system. Unshared work may change this assessment.

## 4. Corrections needed before implementation

- Establish one canonical phase/dependency map. Phase 14.3 refers to 14.4 as feature extraction and 14.5 as graph construction, but the actual 14.4/14.5 documents specify RTL normalization and synthesis. Add explicit feature/graph construction work rather than following those conflicting references.
- Complete routing and parasitic-extraction contracts before claiming post-route labels, STA, or final sign-off.
- Fix the prediction boundary. Existing documentation uses placement coordinates and RUDY; these support post-global-placement prediction. A pre-placement claim would require a separate representation and experiment without real placement coordinates.
- Generate labels after their producing EDA stages, then assemble the ML dataset. Document chapter numbering is not an executable pipeline order.
- Exclude downstream information from features. Final SPEF capacitance, final critical-path flags, final congestion and post-route power cannot be used as early features. Early estimates are allowed only with their origin recorded.
- Keep all variants, seeds and derivatives of a design/source family together across dataset splits. Fit all normalization and feature transforms using training data only; do not normalize a target using its own unknown test-design extrema.
- Phase 14.11 specifies analysis only, while 14.12 assumes a timing-closed input. Define a separate bounded remediation loop and checkpoint invalidation policy, or explicitly retain failing designs as analysis samples. Running STA does not establish closure.
- Treat expected accuracy and runtime numbers in specifications as hypotheses until measured. Do not present speculative percentage correlations or thermal accuracy as results.
- Audit tool capabilities before assigning labels. Static PDN analysis does not by itself supply a validated thermal solver, dynamic IR solver, or foundry-qualified electromigration analysis.
- Correct benchmark metadata: CVA6/Ariane is an in-order core; the out-of-order description in Phase 14.1 is inaccurate. Confirm configuration-specific properties before dataset labeling.
- Distinguish an archive of tapeout files from semiconductor packaging. GDSII generation does not demonstrate package design, fabrication, assembly, test, or foundry acceptance. Foundry checklists and rule-deck coverage govern manufacturing claims.

## 5. Step-by-step roadmap and acceptance gates

Complete each gate with evidence before expanding scope. Run documentation and thesis writing alongside the engineering work. The six-month calendar below bounds the mandatory software product; optional workstreams must not delay closure.

| Step | Work | Evidence required to advance |
|---|---|---|
| 0. Freeze the research charter | Confirm thesis question, system boundary, prediction checkpoint, two initial targets, TRL rubric, mandatory DFT/package scope, resources and deadline; review relevant literature | Supervisor-aligned scope and claim-to-evidence matrix; recorded success criteria |
| 1. Build one reference EDA path | Select one supported open PDK and pinned tool flow. Take one small licensed design through synthesis → floorplan → placement → CTS → routing → extraction → STA. Add physical verification for layout claims | Repeatable tool runs, logs and real artifacts; documented supported capabilities and failure handling |
| 2. Define the data contract | Implement graph/spatial extraction, units, coordinate mapping, net representation, feature availability, labels and provenance from saved checkpoints | One real sample passes schema, alignment, identity and leakage checks; independently inspect tool reports against extracted labels |
| 3. Prove a small complete experiment | Implement dataset loader and a minimal train/evaluate path on a few real designs; use a simple baseline first | Real EDA sample → features → baseline → held-out prediction → scored report runs end-to-end; failure cases visible |
| 4. Build the benchmark corpus | Acquire licensed independent designs; sweep limited legal configurations; quarantine failures; group by source/design family | Dataset manifest, design and sample counts, distributions, fixed grouped train/validation/test assignments and resource-cost report |
| 5. Establish credible baselines | Compare global-feature/simple regression, spatial heuristic, CNN-only and GNN-only models as applicable; select tuning using validation data | Reproducible baseline results on identical target definitions, information boundaries and splits |
| 6. Implement hybrid CNN–GNN | Build graph encoder, spatial encoder/decoder, scatter/gather alignment, target heads, losses, masks and trainer; test meaningful gradients and variable-size batching | Working forward/backward passes and training; fusion ablations; reproducible checkpoints and metrics |
| 7. Evaluate generalization and uncertainty | Lock test set; evaluate unseen design families, errors by scale/target, seed variation, confidence intervals, uncertainty and OOD behavior | Untouched-test report, ablations, failed-case analysis, measured accuracy/runtime tradeoffs; no unsupported cross-PDK claim |
| 8. Validate optimization value | Define allowed actions and constraints. Compare model-guided search against unguided/random and simple-heuristic search using equal total compute budgets | EDA-measured timing/congestion/area outcomes, feasibility and total search cost including preprocessing/inference; paired comparisons across designs/seeds |
| 9. Integrate DFT if required | Choose supported scan/test tools and a small block; add scan insertion, scan simulation and fault/ATPG analysis where available; propagate the scan netlist through physical design | Scan correctness, tool-defined fault coverage and untestable-fault accounting, area/timing/power overhead, updated physical results; no fabricated-silicon test claim |
| 10. Integrate package/reliability scope | Select one concrete package question and obtain geometry/material/electrical/thermal data plus a suitable reference solver. Couple die power/interface assumptions to package models | Validated solver reference cases, boundary-condition/mesh checks where relevant, sensitivity study and measured error; explicit modeling limits |
| 11. Qualify the defined system toward TRL 8 | Freeze supported inputs, operating envelope and requirements; run integrated acceptance tests, independent reproduction, failure/recovery cases, resource/performance tests; resolve critical defects | Qualification dossier with requirements-to-test traceability, independent evaluation, versioned release, limitations and supervisor/assessor review |
| 12. Submit the thesis and evidence | Consolidate methods, literature, dataset/model versions, statistical results, negative results, demo and reproducibility instructions | Defensible thesis, live reproducible demo, complete results package and accurately bounded claims |

Steps 9 and 10 become mandatory gates before Step 11 when the qualified system includes DFT or packaging. Otherwise they remain explicit extensions of the broader program. Do not qualify a narrower predictor and describe the entire RTL-to-packaged-device vision as TRL 8.

## 6. TRL 8: define what must be qualified

The usual TRL 8 interpretation is an actual system completed and qualified through test and demonstration. Use the university or sponsor's exact definition for the formal assessment.

| Intended system | What can support qualification | What is insufficient |
|---|---|---|
| Software decision-support system | Completed integrated workflow, frozen operating envelope, agreed acceptance tests, representative real designs, independently reproduced results, reliability/failure handling and versioned release | Dependency installation, specifications, synthetic-only examples, a high accuracy number, an API or screenshots alone |
| RTL-to-layout research flow | Executed and checked artifacts under a specified tool/PDK/rule-deck scope, validation coverage and independently reproduced results | GDSII existence alone or a blanket assertion of industrial sign-off |
| Fabricated and packaged semiconductor system | Fabrication and assembly access, actual devices, DFT/test evidence, package validation and applicable hardware qualification evidence | Simulated RTL, package CAD, an archive called a tapeout package or software qualification alone |

An industry/foundry partner may be needed for access and hardware evidence, but formal acceptance must follow the actual institutional rubric. No TRL is earned simply by completing a numbered documentation phase.

## 7. Measurement plan

Freeze exact thresholds after pilot feasibility and supervisor review, before inspecting the final test set. The following are proposed metrics, not achieved results or universal qualification thresholds.

| Claim | Measure and comparison |
|---|---|
| Better congestion prediction | MAE/RMSE of the chosen demand/overflow definition; hotspot precision-recall AUC and recall at a fixed false-positive budget; compare spatial heuristics and learned baselines |
| Better timing prediction | WNS/TNS prediction error in declared units and relative to clock period; timing-violation classification metrics; carefully distinguish endpoint and design-level targets |
| Useful joint modeling | Hybrid versus CNN-only, GNN-only and fusion-disabled variants with comparable tuning budgets |
| Faster decisions | Inference plus all required upstream processing versus computing the reference target from the same starting point; include hardware and batching details |
| Useful optimization | Actual EDA-validated quality/feasibility and wall-clock/core-hour cost under equal exploration budgets; report area/power/timing regressions as well as gains |
| Generalization | Grouped held-out design-family evaluation, seed variation and confidence intervals computed with design-level dependence respected |
| Reproducibility | Independent execution from pinned inputs and configuration; numerical tolerances appropriate to each tool/metric |

No promise of a fixed accuracy percentage, tapeout, publication acceptance or TRL outcome is made before supporting evidence exists. If the hybrid model fails to beat a simpler model, report that outcome and investigate its causes rather than changing the test set or hiding the baseline.

## 8. Resources and immediate next actions

Current verified capability from onboarding is CPU Python development. GPU allocation, EDA tool/PDK installation, dataset generation throughput, commercial licenses, foundry access, ATPG support and package-solver access have not been established.

Next implementation milestone: one small licensed design in one pinned open flow, with saved global-placement inputs and real downstream congestion/timing labels, followed by one complete baseline experiment. This tests the main feasibility risks before large training or solver investments.

Pilot resource planning: measure elapsed time, peak memory and artifact size for one design/configuration; estimate total cost as independent designs × variants × seeds × measured flow cost, accounting for failures and retries. Extra variants do not replace independent designs for generalization evidence.

Decided by the user: six months to finish and close the project; TRL 8 refers to a final usable product or service. Selected delivery form: the software predictor plus EDA-validated decision loop. Remaining planning inputs: institutional qualification rubric, supervisor-specific scope requirements, GPU/EDA compute budget and access. Proceed with one open toolchain/PDK and CPU development while measuring training and EDA compute needs; do not assume access to licensed or hardware facilities.

## 9. Source locations reviewed

- `Hybrid-CNN-GNN-ShiftLeft-DTCO/hybrid_dtco/docs/Phase14.1 Dataset Engineering Specification.md`: dataset, features, splits and label assumptions.
- `Hybrid-CNN-GNN-ShiftLeft-DTCO/hybrid_dtco/docs/Phase14.3 annotation label generation specification.md`: provenance and conflicting phase references.
- Actual Phase 14.4/14.5 documents: RTL normalization and synthesis.
- Phase 14.9 inventory and absent Phase 14.10: routing/extraction gap.
- Phase 14.11/14.12: analysis-versus-closure and power-integrity assumptions.
- Phase 14.13/14.14: physical verification and final tapeout-file specification; these are requirements, not execution evidence.
- `Hybrid-CNN-GNN-ShiftLeft-DTCO/hybrid_dtco/src/hybrid_dtco/`: dataset, model, fusion, EDA and training/API implementation status.
- `Research-on-ADV.-ATMP---RTL-TO-PACKAGING---WITH-DFT/README.md`: broader theme only.

No application source or published environment configuration was changed for this review.


## 10. Six-month delivery calendar and scope lock

**Final product:** an AI-assisted EDA analysis and design-exploration service for a documented subset of synthesizable RTL and one supported open PDK/library/toolchain. Provide a reliable batch/CLI workflow, a small API wrapper for job submission/status/results, versioned models, run manifests and an engineer-readable report. A dashboard is optional. User-supplied RTL is treated as untrusted input: isolate tool execution, limit resources, validate paths and protect job artifacts. Authentication and deployment controls must match the chosen pilot setting; do not expose an unfinished service publicly.

**Primary outputs:** global-route congestion prediction and downstream timing-risk prediction from global-placement inputs. Prediction targets must state their exact reference stages. **Decision function:** rank a bounded set of supported implementation configurations; rerun the EDA flow to validate selected choices. The service may cache completed early-stage artifacts, but must report cold-run and cached-run costs separately.

| Period | Main delivery | Exit gate |
|---|---|---|
| Month 1: 3 Nov–2 Dec 2026 | Scope/rubric/literature review; one pinned EDA flow; complete one real design; implement extraction and a simple end-to-end baseline | Real RTL-to-label-to-prediction demonstration, checked provenance, measured resource needs and frozen feature/target definitions |
| Month 2: 3 Dec 2026–2 Jan 2027 | Acquire diverse independent designs, generate controlled variants, implement robust storage/validation and grouped splits | Versioned corpus, leakage report, useful target variation, documented counts/failures and frozen evaluation protocol |
| Month 3: 3 Jan–2 Feb 2027 | Baselines, CNN/GNN branches, fusion, training, ablations and uncertainty evaluation | Reproducible validation results with model-selection decisions recorded; investigate any hybrid-model failure to add value |
| Month 4: 3 Feb–2 Mar 2027 | Model-guided configuration ranking; real EDA reruns; batch/CLI and API product integration | Working product candidate with measured optimization quality/cost and meaningful integration/failure tests |
| Month 5: 3 Mar–2 Apr 2027 | Evaluate frozen models on untouched design families; independent pilot by a supervisor/engineer/evaluator; performance and reliability improvements | Pilot findings, final scientific results, limitations and closed critical product issues; no test-set-driven model tuning |
| Month 6: 3 Apr–3 May 2027 | Qualification against agreed requirements, clean-environment reproduction, release freeze, thesis/demo/manuals and archive | Versioned final release and qualification dossier; explicit assessed TRL and unresolved limits; project closure on 3 May |

### Resource and failure contingencies

- By the end of Month 1, calculate the corpus/training budget from actual pilot runs. Prefer fewer supported features and one technology over unverifiable breadth; document statistical limits if independent design diversity is insufficient.
- If suitable GPU access is unavailable, use smaller graphs, sampling and bounded models; measure feasibility before committing to corpus-scale training. CPU dependency checks do not establish a training budget.
- An empty or almost always zero target does not validate a predictor. Revisit legal operating points or target scope during pilot work so congestion/timing risks are meaningfully represented.
- If the hybrid model does not improve over baselines, preserve the negative result and deploy the best validated model where useful. Do not claim the hybrid research hypothesis succeeded. Review whether the resulting contribution still meets thesis requirements.
- If optimization does not improve outcomes, distinguish a predictive analysis product from a validated optimizer; qualify only demonstrated functions.
- Final qualification cases must remain separate from model training/tuning. Record failures and their disposition; do not silently remove failed jobs or narrow acceptance rules after observing results.
- Freeze nonessential feature additions at the end of Month 4. Months 5–6 prioritize independent evidence, defect repair, release and thesis completion.
- TRL 8 remains conditional on the acceptance evidence. If evidence supports a lower level on 3 May, close with that honest assessment and a precise gap list rather than relabeling an incomplete product.

### Final acceptance dossier

1. Supported inputs, PDK/library/toolchain, operating limits and requirements-to-test matrix.
2. Dataset provenance, licensing, design-family splits and feature/label leakage audit.
3. Versioned checkpoints, training configuration, baseline/ablation/generalization results and uncertainty analysis.
4. EDA-validated decision results and complete runtime/resource comparisons, including all upstream work.
5. Functional, integration, invalid-input, job isolation, timeout/recovery and deployment-appropriate access-control evidence.
6. Independent user/evaluator execution records, clean-environment reproduction and resolved critical defects.
7. Release package, installation/run guide, API/CLI documentation, limitations, thesis and demonstration.
8. Supervisor/assessor review against the selected TRL rubric, with the assessed system and evidence stated explicitly.


## 11. Execution checkpoint — 3 November 2026

The first physical-design/data-path checkpoint is complete. A new original 16-bit GCD design ran through pinned OpenROAD-flow-scripts with Sky130HD, including synthesis, floorplan, placement, CTS, global/detailed routing, parasitic extraction and GDSII generation. Seven concrete bounded SAT transactions and four repository artifact tests passed. A fresh corrected run exported the global-placement graph (646 instances, 552 signal nets) and validated downstream scalar labels. Worst setup slack was +16.2104 ns at a 20 ns clock; WNS/TNS and reported global-route congestion were zero. Evidence: `/workspace/experiments/sky130-gcd/run-002/manifest.json` and `summary.json`. Source/run instructions: `Hybrid-CNN-GNN-ShiftLeft-DTCO/hybrid_dtco/docs/reference_flow.md`.

This completes the initial EDA/data-path smoke test, not all Month 1 deliverables: spatial labeling/rasterization, independent-design corpus, baseline prediction, formal requirements and literature assessment remain. The next engineering gate is spatial label/feature alignment and a versioned multi-design dataset. No model training, foundry sign-off or TRL qualification is claimed. The final deadline remains **3 May 2027**.


## 12. Integrated laboratory predictor — 3 November 2026

The core CNN–GNN laboratory prototype is implemented and validated on 18 actual Sky130HD EDA runs from six original RTL families. Family-held-out splitting produced 9 training, 3 validation and 6 test samples. GraphSAGE, differentiable scatter fusion, spatial encoder/decoder, post-route timing prediction, checkpoint reload, CLI and local HTTP inference were exercised. All 16 tests and the separate trained-service HTTP/CLI checks passed. All 2,199 raw EDA artifact hashes were verified.

Held-out effective timing-delay MAE: hybrid 0.3822 ns, training mean 0.9235 ns, ridge 0.3127 ns. Held-out aggregate routing-utilization MAE: hybrid 0.07038, training mean 0.08700, ridge 0.09078. Ridge is still better on timing. These are preliminary results from two small held-out families, not a generalization or sign-off claim.

The frozen laboratory gates passed; the restricted predictor now has a TRL 4 candidate evidence package for independent/institutional assessment. No blanket TRL upgrade is claimed for the wider optimization, DFT, physical packaging or production-service vision. Evidence: `/workspace/experiments/trl4-lab-20261103/READINESS.md`; implementation/run guide: `Hybrid-CNN-GNN-ShiftLeft-DTCO/hybrid_dtco/docs/lab_validation.md`.

Next gates: independent reproduction/review, expanded benchmark diversity, stronger timing baselines and calibrated uncertainty, followed by actual EDA-validated optimization. Keep the untouched-test protocol for future iterations. The final product deadline remains **3 May 2027**.
