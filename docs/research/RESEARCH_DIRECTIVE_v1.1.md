# REA Scientific Development Directive v1.1 — 2026-11-15

**Status: research-team review draft.** Supersedes v1.0 for new planning; v1.0 is retained as an audit record. This document authorizes no external target inspection, raw-data publication, merge, release or empirical efficacy claim.

## Scientific aim

Estimate the incremental benefit, limits and full operating cost of authorized `rea-agents` CLI/MCP observation during source-hidden reconstruction of web applications. The causal question concerns the **defined bundled observation intervention**, not the MCP wire protocol in isolation. The REA educational methodology and the external rea-agents software must always be distinguished.

| Treatment | Workflow W | Instrumentation I | Meaning |
|---|---|---|---|
| T0 | no | no | Conventional coding agent + authorized browser |
| T1 | yes | no | Skills/TDD/gates without rea-agents |
| T2 | no | yes | Conventional coding agent + real instrumented observation |
| T3 | yes | yes | Workflow + real instrumented observation |

Primary prospective effect: run-level fidelity contrast T3−T1; secondary: T2−T0; W, I, W×I and other behavior strata are supplementary analyses. The design does **not** identify a causal effect of provenance or independent review without additional randomization. RQ5 remains descriptive/associational.

## New verified literature and novelty boundaries

- **Kim et al. (2026), ProgramDistill**, arXiv:2609.18805, is a *preprint* about reference-guided web tasks: 26 apps and 4,063 tasks. In its failure analysis **59.2% of 977 failed atomic behaviors** (not all tasks) had not been observed. This motivates separating discovery from implementation, not a claim that the present project has demonstrated superior coverage.
- **Chen et al. (2026), IWR-Bench**, ICLR 2026: interaction-video reconstruction benchmark, underscoring the weakness of screenshot-only fidelity.
- **Song et al. (2026)**, IEEE TSE, DOI 10.1109/TSE.2026.3694876: malicious MCP server/tool attacks.
- **Hou et al. (2026)**, ACM TOSEM, DOI 10.1145/3796519: MCP ecosystem and 16 threat scenarios.
- **Baltes et al. (2027; online Nov 2026)**, Empirical Software Engineering, DOI 10.1007/s10664-026-10922-3: guidelines for reproducible SE studies involving LLMs.

No unidentified **WebProgramBench** citation may be added without a verifiable bibliographic primary source. Claims to be the first reference-guided reconstruction method are ruled out by existing literature. Potential novelty lies in *randomized treatment contrasts* and interpretable evidence/cost mechanisms.

## Data contracts and outcomes

- **Ground truth** (evaluator-only): immutable application_id, requirement_id, source_statement, precondition, action_sequence, expected_behavior, category, criticality, observability and oracle_id; completed before any reconstruction.
- **Discovery snapshot**: timestamp and hash **before implementation**, plus mapped requirement IDs, epistemic status and adjudication rules.
- **Evidence record**: evidence_id, version, tool/arguments/result digest, time, target, behavior link, validity, downstream decision ID and independent check. A configured REA server is not a live tool call.
- **Coverage of observation**: eligible reference behaviors actually observed / **common evaluator-defined authorized reference behavior set**, stratified by DIRECT/INDIRECT/INSTRUMENT_ASSISTED/UNAVAILABLE. Do not change denominators by treatment without disclosure.
- **Evidence utilization**: valid unique evidence linked to a checkable change of requirement/test/implementation / all unique valid evidence collected; descriptive post-treatment indicator, not a validated causal mediator.
- **Behavioral fidelity**: independent prespecified hidden-oracle test pass proportion per **complete run**. Tests are nested, not independent experimental units. Retain failed/timeout/budget-exhausted executions under frozen rules.
- **Economic analysis**: tokens, charges, setup time, wall-clock, tool calls, retries, human labor, failures and cost per externally correct behavior; zero-correct cases not discarded.
- **MCP safety**: tool catalog digests, least privilege, local disposable CDP profiles, network allowlist, refused calls, attempted unauthorized egress, prompt injection/tool-poisoning symptoms; publish only approved redacted evidence.

## Execution prohibitions and controls

1. Keep reference source, ground truth and hidden external oracles outside all agent workspaces with **filesystem, network and credential** isolation; public Rota 2 is **pilot-only**.
2. Freeze model IDs, sampling settings, software release digests, host, browser, tool schemas, prompt/Skills, budgets, permissions and stopping rules; use independent workspaces and balanced/randomized assignment.
3. Author independent oracles and meta-evaluate against reference, valid executed injected faults and behaviorally correct alternate implementations; double-review a stratified sample.
4. Obtain **measurable, preapproved no-go thresholds and named owners before pilot** for real MCP calls/trace completeness, isolation, authorization, oracle fault detection/false rejection, cost, attrition and intervention.
5. The pilot target (20 runs) and possible main-study plan (160) are preliminary, **not** a powered sample, and **not executed**. No results may be synthesized.
6. CI green is a test result for configured checks, never proof of reference equivalence, T0–T3 execution, a separate independent reviewer, or human G7 approval.
7. Keep research results separate from ASF; disclose reused concepts/harnesses, never double count the same result.

**Working manuscript:** M1 v0.4. **Experimental Protocol:** v1.2. **Roadmap:** v2.2. DOCX originals are available privately to the research team and are not public repository artifacts.
