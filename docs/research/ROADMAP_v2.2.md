# REA Research Roadmap v2.2 — 2026-11-15

**Status:** planning/draft; no T0–T3 controlled runs and no study efficacy results. Preserve ASF and REA as scientifically distinct studies; explicitly declare reused conceptual infrastructure.

| Phase | Work product | Exit criterion | Status |
|---|---|---|---|
| WP1 | Protocol v1.2, requirement-ground-truth schema, observability and baseline contracts | Approved hypotheses, estimands, attribution limits, no-go owners/thresholds | DRAFT |
| WP2 | Versioned T0–T3 prompts/Skills/tool catalog with **live** REA/MCP trace | Target permissions, digests, tool call parameters/results/hashes and limits verified | NOT VERIFIED |
| WP3 | Evaluator-side hidden tests and ground truth, independent oracles | Reference PASS, valid mutation sensitivity, correct-alternative no false rejection, review | NOT IMPLEMENTED |
| WP4 | Pilot: 20 planned isolated runs | All fail/pass/timeout/blocked runs retained with resources and quality assessments | NOT EXECUTED |
| WP5 | Confirmatory: multiple applications/models and frozen statistics | Study size justified after pilot; independent test analysis and uncertainty | NOT STARTED |
| WP6 | Manuscript M1 and replication release | Verified results, hashes/DOI, source limitations, declarations and human approval | NOT READY |

**Interdependencies:** P1–P4 must pass before WP4; WP5 begins only after a pilot review and immutable protocol/analysis freeze. Inadequate MCP reliability, privileged tool differences, source leakage, inadequate oracle sensitivity/false rejections or unsustainable cost trigger preapproved HOLD/REVISE.

**Manuscript convergence:** M1 v0.4 updates related work with ProgramDistill (preprint), IWR-Bench and 2026 MCP security studies, operationalizes observational coverage, verified use of evidence and result fidelity separately, and clarifies T3−T1 as a bundled treatment effect. RQ5 remains associative. Only real controlled results can replace the reserved Results/Discussion placeholders.

**Publication rules:** Do not publish hidden oracle suites, reference code or private logs in this public repository before the study's agreed release stage. Use redacted, hash-tracked archive assets. Maintain existing draft PRs for engineering and scientific documents and avoid merging without approval.
