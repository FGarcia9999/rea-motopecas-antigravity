# REA WP3/P4 — Evaluator handoff and oracle-quality controls (16 November 2026)

**Classification:** ENGINEERING FEASIBILITY / PUBLIC SYNTHETIC CONTROLS ONLY. This document records **no completed T0–T3 treatment runs, hidden benchmark, genuine independent evaluator approval, or empirical efficacy measurement**.

## Motivation and link to manuscript M1 v0.4

The manuscript proposes source-hidden, independently verified functional reconstruction and a planned primary T3−T1 fidelity contrast. Its validity depends on at least two independent controls: (1) no implementing agent can read reference code or hidden oracles and (2) oracles must discriminate faulty implementations without rejecting behaviorally correct alternatives. The WP3 oracle engine previously demonstrated one deliberately faulty category filter. This checkpoint adds **content-hashed submission handoff** and one **alternative behaviorally correct with respect to the four publicly defined demo cases**.

## Public technical implementation

- `research/handoff/bundle.py`: per-file SHA-256 transfer manifest, deterministic ZIP, restricted source paths/types, byte caps, symlink/traversal/duplicate detection, and separate evaluator-side integrity verification. **No code execution by the transfer verifier**.
- `research/oracles/toy_correct_alternative.py`: independent, simplified alternative API with the behavior needed to satisfy the **four published sample cases**. It does **not** reproduce the entire Rota 2 app, and is not a verified correct alternative for any real hidden benchmark.
- `research/oracles/toy_meta_quality.py`: cross-checks that three reports have the same suite digest and reference+alternative PASS while the known mutant FAILS in the injected category behavior. Outputs a **DRAFT** oracle-quality record with the status `PUBLIC_TOY_CONTROLS_ONLY_NON_GENERALIZABLE`.
- `tests/test_research_handoff.py`, `tests/test_research_oracle_meta.py`: positive/negative tests covering forged archives, ZIP nonregular members, unsafe paths, wrong controls, altered suite digests and failures.
- `.github/workflows/p4-public-evaluator-smoke.yml`: controlled ephemeral runner (own local API targets only). No private oracles, credential material or user data are accessed or published.

## Executed engineering smoke

[Public P4 handoff and oracle control smoke](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43949121130) passed:

| Control | Outcome in synthetic demonstration | Valid interpretation |
|---|---|---|
| Agent candidate ZIP transfer | SHA-256 exported/verified, 2 toy files, no code executed | Transport integrity check |
| Public Rota 2 reference | Four published test cases pass | Positive evaluator control |
| Public deliberately faulty category implementation | Evaluation fails on category behavior | Negative evaluator control |
| Public alternative API | Same four published cases pass | No rejection of **this one** toy alternative |
| Hidden behavior tests, real reference secrecy and independent review | **Not present** | No scientific oracle quality claim |

The values `mutation_detection_rate = 1.0` and `false_rejection_rate = 0.0` refer to **one known toy mutant and one known toy alternative** only. They are not generalizable estimators, must not be used to accept no-go thresholds, and **must not enter the manuscript's confirmatory Results tables**.

## Outstanding research gates

| Gate | Current classification | Required next work |
|---|---|---|
| P1 | DRAFT | Scientific team approves exact contracts and quantitative no-go thresholds/owners |
| P2 | CLI captured; real Antigravity/MCP not verified | Freeze tool catalog, permissions and real MCP invocation |
| P3 | Limited synthetic Docker smoke passed | Demonstrate real agent identity and true source-hidden reference isolation |
| P4 | Public oracle demonstrator passed | Private evaluator-authored tests, multiple valid mutants/alternatives, blinded adjudication |
| WP4 | NOT EXECUTED | Exploratory 20-run pilot only after P1–P4 approvals |
| M1 v0.4 | Working manuscript | Results empty pending verified experiments |

**Decision:** retain draft status and do not merge or claim scientific readiness. The handoff/output metadata can later appear in the reproducibility supplement, clearly differentiated from measured treatment results.

Related: [P3 checkpoint](P3_ISOLATION_CHECKPOINT_2026-11-16.md), [protocol v1.2](EXPERIMENTAL_PROTOCOL_v1.2.md), [directive v1.1](RESEARCH_DIRECTIVE_v1.1.md).
