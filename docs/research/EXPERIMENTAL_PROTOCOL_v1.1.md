# REA Experimental Protocol — v1.1 | DRAFT FOR FREEZE

**Date:** 2026-11-11. **Manuscript:** M1 v0.3, working version. **Status:** design specified; not preregistered/frozen; no comparative treatment results. Full editable protocol is delivered separately as DOCX; this Markdown states the governing requirements for implementation.

## 1. Factorial study and estimands

| Treatment | W (workflow structure) | I (REA/MCP instrumentation) | Operational agent |
|---|---|---|---|
| T0 | 0 | 0 | Conventional LLM agent with authorized browser |
| T1 | 1 | 0 | W with rules, skills, TDD, gates (A) |
| T2 | 0 | 1 | Conventional agent + real REA/MCP observations |
| T3 | 1 | 1 | W + I integrated (C) |

Primary: `Δmain = E[Y|T3] - E[Y|T1]`, where Y is **run-level** proportion of predeclared independent hidden behavioral tests passed. Secondary: `E[Y|T2]-E[Y|T0]`. Complementary: W, I and W×I effects with prespecified scale and uncertainty. **No hypothesized direction treated as an observed result.** RQ5 (provenance and unsupported completion claims) is descriptive/associational, because provenance is not separately randomized.

## 2. Ground-truth contract (evaluator-only content)

Each requirement has immutable `application_id, requirement_id, source_statement, precondition, action_sequence, expected_behavior, category, criticality, observability, oracle_id`. Category includes UI, state, persistence, transaction, integration, security. Observability: DIRECT, INDIRECT, INSTRUMENT_ASSISTED, UNAVAILABLE. Freeze requirements and external oracles **before** agents run; protect them in a separate restricted location. Record each agent's requirement-discovery output **before** implementation starts.

## 3. Instrumentation and information equivalence

Freeze the exact reference application, commits, LLM, tools, `rea-agents` release, MCP server digest, tool schemas, CDP/browser, permissions, budgets, prompts/Skills, stop rule and expected logging. Distinguish installed, configured, visible, executed and useful tools. Only real tool invocations with arguments/results/target/time/hash constitute REA evidence.

The authorized target/behavioral surface is shared across conditions. Representations may differ; record all instrument-exclusive observability or privileged access instead of declaring the information identical. Uncontrolled privileged access may invalidate causal attribution to I.

## 4. Oracle quality and run outcome

Oracle suite must pass against reference and fail on verified behavior-changing, compiled and executed injected defects. Detect false rejection using genuinely correct alternative implementations; add metamorphic relations for state/persistence/transaction. Predeclare mutation denominator, coverage and double-annotated sample. Validate adjudication before treatment reveal.

Run is the experimental unit. Tests are nested within workflows, runs, application and model. Report hidden test proportion, end-to-end workflow correctness, discovery P/R/F1, false inferred requirements, trace completeness, false completion/falsely rejected correct implementations, time, tokens, tool calls, cost, violations, all failures and timeouts. Code discovery, specification, implementation, verification, governance and environment failures separately.

## 5. Pilot and statistics

Pilot planning: one Rota 2 variant × four treatments × five independent runs = **20**; order randomized/counterbalanced, fresh workspace/session, no shared state. Pilot is for feasibility, variance, oracle diagnostics and study-design revision, not for confirmatory effect claims.

Candidate main study: four applications × four treatments × five runs × two LLM families = **160** (NOT a power justification). Define powered/precision sample after pilot; methods may use hierarchical models or clustered bootstraps. Freeze estimands, analysis scale, multiplicity, zero-test convention, exclusions, missing/timeouts, ethics and logs before confirmatory data collection.

## 6. Freeze gates and no-go

- **P1:** RQs, treatment definitions, causal scope, outcomes, approvals.
- **P2:** working real REA/MCP tool calls + verified environment/limits.
- **P3:** source-hidden enforced isolation, authorization-equivalence map.
- **P4:** independently validated oracles, mutation sensitivity, false rejection, adjudication.
- **P5:** 20 pilot runs retained, cost and variance observed.
- **P6:** final subjects, sample size, stop/missing rules, statistical script frozen before main study.
- **P7:** redacted logs, hashes, manifest, data dictionary, release/DOI and human approvals.

Before P5 starts, define **measurable and preapproved no-go thresholds** for P2/P3/P4, error/missing rates, time, tokens and cost; do not infer from outcomes. On failure → HOLD/REVISE; no silent deletion or post hoc gate tweaking.

**Status 2026-11-11:** P1 DRAFT; P2/P3 NOT VERIFIED; P4 NOT IMPLEMENTED; P5 NOT EXECUTED; P6 NOT FROZEN; P7 NOT ARCHIVED.
