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


### WP3 — Avaliador: entrada de benchmark privado (16/11/2026)

O novo [contrato de custódia e intake](benchmark/README.md) verifica a estrutura e os hashes de fonte e oráculos externos ao repositório e gera apenas metadados públicos minimizados. O [checkpoint](../docs/research/WP3_BENCHMARK_INTAKE_CHECKPOINT_2026-11-16.md) descreve o que não foi comprovado: nenhum benchmark privado independente, isolamento sob LLM real, aprovação de P1–P4 ou piloto T0–T3.


### Proteção de publicação e bloqueio científico do piloto (16/11/2026)

Antes de qualquer push ao repositório público, executar `python scripts/check_research_public_boundary.py`. A verificação no CI examina arquivos rastreados, mas **não substitui** revisão humana de segredos nem saneia histórico já publicado. O estado atual de P1–P4 pode ser lido em `python -m research.gates.readiness`, que **não autoriza** o piloto. Consulte [registro de prontidão](../docs/research/PILOT_P1_P4_READINESS_2026-11-16.md) e [orientação do gate](gates/README.md).


### Pre-pilot planning v0.1 (2026-11-16)

The [execution plan](../docs/research/PRE_PILOT_EXECUTION_PLAN_v0.1_2026-11-16.md), [custody SOP](../docs/research/EVALUATOR_CUSTODY_SOP_v0.1_2026-11-16.md), [pre-registration decisions](../docs/research/PREREGISTRATION_DECISIONS_v0.1_2026-11-16.md), and [machine-readable milestones](planning/README.md) establish dependencies and acceptance evidence for the **unstarted** WP4. They add no private oracle or reference sources, do not approve the nine no-go gates, and do not supersede Protocol v1.2 or Manuscript M1 v0.4.


### M00 — Custody and explicit-denial preflight (2026-11-16)

A [public DRAFT role matrix and single-canary access probe](custody/README.md) are implemented with a synthetic, scoped Linux container smoke: accessible authorized runtime and protected canary `DENIED`. See [M00 engineering checkpoint](../docs/research/M00_CUSTODY_ACCESS_CHECKPOINT_2026-11-16.md). This does **not** constitute a real Antigravity/MCP agent identity or an approval of P1–P4. Actual private assets, actors, and account permissions remain to be arranged by independent custodians.


### M02 — execução MCP stdio real, cliente Antigravity pendente (16/11/2026)

O [checkpoint de execução MCP](../docs/research/M02_REAL_MCP_STDIO_CHECKPOINT_2026-11-16.md) e a implementação testada em [research/mcp_stdio_smoke.py](mcp_stdio_smoke.py) documentam **dois tools/call reais** do REA oficial no ambiente descartável. O [procedimento Antigravity](M02_ANTIGRAVITY_HOMOLOGATION_RUNBOOK.md) permanece a ser executado no cliente Windows, com prova independente. P2 científico permanece HOLD, T0–T3 não iniciados.


### M02 — Operator evidence kit for actual Antigravity Windows (16 November 2026)

The [Antigravity evidence kit](antigravity/README.md) and [technical checkpoint](../docs/research/M02_ANTIGRAVITY_EVIDENCE_KIT_CHECKPOINT_2026-11-16.md) provide Windows PowerShell setup for a private records folder, checksums and negative verification controls. Unlike the real independent stdio MCP smoke, this kit **does not run the Antigravity agent** and cannot self-authenticate its records. P2 scientific HOLD; no T0–T3 trial.
