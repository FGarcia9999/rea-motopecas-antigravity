# REA WP1–WP3: executable contracts — initial research implementation

**Date:** 2026-11-16. **Status:** IMPLEMENTATION SCAFFOLD / NOT SCIENTIFIC FREEZE. This directory does not include any actual hidden oracle, proprietary reference code, ground truth, experimental runs, REA tool-call log or human-approved threshold.

## Why this exists

The scientific study compares **T0** conventional agent, **T1** structured workflow without REA/MCP, **T2** conventional agent with REA/MCP, and **T3** structured workflow with REA/MCP. W and I are orthogonal factors. The planned confirmatory comparison is **T3−T1** on the run-level external hidden-test pass proportion. This estimates a *bundled instrumented-observation treatment*, not an isolated effect of the MCP wire protocol. Provenance (RQ5) is descriptive/associational unless separately randomized.

**REA/MCP operational definition** (coauthor-requested wording): a version-frozen, authorized observation capability that exposes selected browser interactions and runtime artifacts through command-line or Model Context Protocol tools. The treatment requires a recorded tool catalog, permissions, CDP/browser configuration and **real invocation logs containing tool name/version, arguments/result hashes, target, time, failures, and provenance**. Setup/doctor/tool visibility are not proof of execution.

## Files and responsibilities

| Area | Public implementation | Not implemented / not published |
|---|---|---|
| WP1 | Six JSON Schemas, validator, negative tests, policy template | Evaluator-authored reference requirements, signed gate thresholds |
| WP2 | Four treatment-package drafts, per-run manifest schema, live-call evidence schema | Real REA/MCP installation, tool invocations and measured environment |
| WP3 | Oracle-quality meta-report schema and denominator-safe diagnostic function | Real independent hidden tests, valid executed mutants, correct alternative implementations and adjudication |

Do not put **reference source, hidden tests, secret ground truth, live credentials, unredacted HAR, private run traces** in this public repository or any implementing-agent workspace. Public toy cases in unit tests are **synthetic schema fixtures only**, never experiments.

## Verification (Windows PowerShell or Linux)

~~~
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_research_contracts.py
python -m research.contracts validate treatment research/treatments/T0.json
python -m research.contracts validate treatment research/treatments/T1.json
python -m research.contracts validate treatment research/treatments/T2.json
python -m research.contracts validate treatment research/treatments/T3.json
python -m research.contracts validate go_no_go research/templates/go_no_go.DRAFT.json
~~~

The CLI output **schema_valid=true** means fields and consistency checks passed only; it explicitly prints **data_attested=false** and **scientific_freeze_approved=false**. Never interpret validation as successful experiment, MCP call or sign-off.

### WP2: what remains necessary before any pilot

1. Select and record exact REA release, MCP server startup configuration, tool schema hash, browser/CDP, sandbox, model family, prompt/Skills digests, permissions and budgets for each treatment.
2. Under explicit authorization, conduct **one real tool invocation** with an own/local application and retain the call/result, version, latency, timestamp, target, permitted scope, digests and limitations. Until performed, WP2 = NOT VERIFIED.
3. Prove source-hidden isolation from the *actual agent identity/container*, not merely through path naming. \`python -m research.isolation_probe --protected-file /absolute/protected/file\` reports a single read result; ACCESSIBLE is a failed check and NOT_FOUND is not proof. A DENIED outcome attests **only this pathname**, not network, credentials or other tool access.
4. Validate isolation independently for filesystem, networks, linked tools and credentials; archive blinded evidence privately.

### WP3: oracle quality without inflated metrics

The public utility \`summarize_oracle_quality()\` uses **only compiling, executed, behavior-changing mutants** as its detection denominator. Correct alternative implementations count toward false rejection only after independent correctness adjudication. A zero denominator produces \`null\`, never an automatic PASS. No metric establishes oracle validity without evaluator review and predeclared acceptance thresholds.

### No-go before the pilot

\`research/templates/go_no_go.DRAFT.json\` enumerates nine metrics. Every numerical threshold and its owner is **null** until group review. The validator refuses to mark this as APPROVED without named approvals and non-null thresholds. Do not infer thresholds after viewing pilot observations.

**Next physical milestones:** evaluator-side ground truth private store, complete authorization-equivalence map, experimental run isolation harness, independent external oracle suite, validated live REA/MCP calls, then team approval and 20-run exploratory pilot. No T0–T3 runs were performed here.

See [Experimental Protocol v1.2](../docs/research/EXPERIMENTAL_PROTOCOL_v1.2.md), [Directive v1.1](../docs/research/RESEARCH_DIRECTIVE_v1.1.md), [Roadmap v2.2](../docs/research/ROADMAP_v2.2.md).


### WP2 local CLI smoke checkpoint (16/11/2026)

A GitHub-hosted disposable Ubuntu runner successfully executed official `rea-agents@6.9.0` CLI target discovery and passive inspection of the local Rota 2 app. A separate controlled CDP driver clicked `Freios` during a 10-second REA capture, observing two HTTP 200 product requests (one category-filtered) and 2 UI products. See [auditable evidence report](WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md) and [GitHub run](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43932452118). **Do not classify this as a Windows/Antigravity MCP session, independent oracle evaluation, source-hidden comparison or P2 research-team freeze.** The running version 6.9.0 rejects the development-only `--approved` flag; explicit loopback-origin environment controls were used instead.


### P3 — Synthetic container isolation evidence (2026-11-16)

A separately restricted agent process could access only the synthetic Rota 2 API while probes for the evaluator, protected canary and source paths were blocked. This is a **scripted environment test**, not an approved real-agent P3 gate or hidden benchmark. See [engineering evidence](../docs/research/P3_ISOLATION_CHECKPOINT_2026-11-16.md) and [implementation](isolation/README.md).


### WP3/P4 — Candidate handoff and alternative correctness control (2026-11-16)

[Content-addressed transfer](handoff/README.md) allows an agent output artifact to be checked and imported into an evaluator-controlled inbox **without running code**. A public smoke uses Rota 2, a deliberately faulty category mutant and an alternative API that satisfies the same four public cases. This is **not** genuine hidden-oracle validation or scientific gate approval. [Evidence and limitations](../docs/research/P4_EVALUATOR_CHECKPOINT_2026-11-16.md).
