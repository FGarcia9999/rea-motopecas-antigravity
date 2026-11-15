# REA Experimental Protocol v1.2 — draft for scientific freeze

**Date:** 2026-11-15. **Status:** NOT PREREGISTERED; no controlled experimental results. Full edited DOCX retained privately. This repository file summarizes enforceable design constraints, not hidden oracle contents.

## 2×2 factorial design

W (structured workflow) and I (authorized REA CLI/MCP instrumented observation) are independently toggled. T0=(0,0); T1=(1,0); T2=(0,1); T3=(1,1). Primary estimand: E[Y(T3)]−E[Y(T1)] where Y is the run-level proportion of fixed hidden behavioral tests passed. Planned secondary: T2−T0; supplementary: W, I, W×I. Effects require randomization/balance, uniform authorization and frozen measurement scale. **T3−T1 estimates the effect of the entire instrumentation bundle**, not isolated causal attribution to the MCP protocol. Provenance utilization is post-treatment and cannot be treated as a randomized mediator.

## Reference source and observable behavior

The authorized surface and application initial state must be common. Information *representations* differ across treatments and are to be measured. Categorize DIRECT/INDIRECT/INSTRUMENT_ASSISTED/UNAVAILABLE; instrument-exclusive privilege beyond common authorization may invalidate attribution. Hide reference code, test suite and evaluator-owned requirement contract behind actual container/filesystem/network/credential isolation. The publicly available Rota 2 prototype is for development and pilot only.

## Freeze and metrics

| Construct | Proposed scoring | Caveat |
|---|---|---|
| Discovery precision/recall/F1 | Match pre-coding snapshot to evaluator ground truth | Missing predictions, UNKNOWN and inaccessible requirements need frozen convention |
| Observational coverage | Valid observed behaviors / eligible behaviors on common authorized surface | Separate observability classes; deduplicate traces |
| Evidence utilization | Valid items with verified decision links / valid unique collected items | Post-treatment descriptive diagnostic, not causal mediation |
| Fidelity | Passed independent hidden tests / fixed applicable hidden tests per run | Run is primary experimental unit; failed/timeout handling frozen |
| False completion | Failed critical external validation among runs self-declared complete | Separately measure false rejection |
| Efficiency | Total run cost, time, human intervention and cost/externally correct behavior | Zero-correct denominator reported separately |
| Security | Unauthorized requests, policy blocks and MCP trust-boundary incidents | Only controlled authorized tests, redacted logs |

The complete run, not each nested test, is the primary independent unit. Candidate analysis: hierarchical binomial models or clustered bootstraps selected after pilot diagnostics; final model, denominators, missingness, timeouts, multiplicity and exact confirmatory contrasts frozen before main study.

## Oracle meta-evaluation

Validate independent oracle contracts on reference; only compiled/valid/executed mutants are counted as detectably faulty; test alternative correct implementations to estimate false rejection; include metamorphic invariants and predeclared double annotation/adjudication. Missing controls prohibit confirmatory trials.

## Pilot and no-go

Pilot planning: 5 repetitions per treatment = 20 independent runs, with fresh session/workspace and randomized/counterbalanced order; pilot is exploratory. A possible main study of 4 apps × 4 treatments × 5 reps × 2 model families = 160 runs must be revised for precision/power after pilot.

Before first pilot: freeze measurable thresholds and owners for real REA/MCP tool-call success/trace coverage, zero reference-source leakage, acceptable oracle mutation detection/false rejection, intervention limits, cost/timeout and attrition. Failed gate => documented HOLD/REVISE; thresholds cannot be silently reset after observing results.

## Current status

P1 draft; P2 real tool-call validation pending; P3 isolation pending; P4 independent oracles not implemented; P5 pilot not executed; P6 confirmatory model not frozen; P7 reproduction not archived. Setup/doctor/CI do not count as actual instrument use.

## Literature

Kim et al. (2026), ProgramDistill, arXiv:2609.18805 **preprint**; Chen et al. (2026), IWR-Bench, ICLR 2026; Song et al. (2026), DOI:10.1109/TSE.2026.3694876; Hou et al. (2026), DOI:10.1145/3796519; Baltes et al. (2027/online 2026), DOI:10.1007/s10664-026-10922-3. No WebProgramBench citation until primary verification.
