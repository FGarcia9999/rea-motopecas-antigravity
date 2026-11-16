# WP2 — Real REA/MCP observation runbook (CLI Linux smoke completed; Windows/Antigravity pending)

**Research protocol:** v1.2. **Date:** 2026-11-16. **Status:** a real CLI-only Linux smoke was run on 2026-11-16, with browser-target discovery and filter capture (see [evidence report](WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md)). **Scientific gate P2 is NOT FROZEN**; there is no Antigravity/MCP client invocation on Windows or independent reviewer attestation. The following commands are for a separate authorized Windows PowerShell lab.

**Official sources checked:** https://rea.tools/get-started/ ; https://rea.tools/guides/browser/ ; https://github.com/morluto/rea/blob/main/docs/getting-started/installation.md

## Authorization, client, and release freeze

A named operator must approve the selected local target, the exact REA package release, browser debugging profile, any client settings modifications, permission policy and evidence storage. Never capture unauthorized third-party apps, accounts, personal browsing, customer data or secrets. Do not use @latest in frozen runs. Fix the exact verified rea-agents package version first.

~~~powershell
node --version
npm --version
# Supported Node.js: 22.23.4+, 24.22.1+, or 26.12.1+. Reject older 22.x / 24.x.
$REA_VERSION = "6.9.0" # candidate verified in isolated GitHub Actions; approve before installing locally
# After operator approval for the exact package:
npx.cmd -y "rea-agents@$REA_VERSION" --version
# Read-only setup plan:
npx.cmd -y "rea-agents@$REA_VERSION" setup --client antigravity --dry-run
# Following commands require explicit approval of planned settings changes:
# npx.cmd -y "rea-agents@$REA_VERSION" setup --client antigravity
# Restart Antigravity and verify its real visible tool list.
# npx.cmd -y "rea-agents@$REA_VERSION" doctor --client antigravity --json
~~~

Setup and doctor do NOT establish a real tool call; separate the 5 levels: installed, configured, visible, executed, decision-useful. Official rea-agents is independent of the project-local rea-instrument and rea-integrate skills.

## REA release compatibility and authorization

On 2026-11-16 the published `rea-agents@6.9.0` CLI returned **Unknown flag: --approved** when invoked with a development-branch flag. It worked without that flag, using an explicitly approved local CLI action and a fail-closed environment policy. **Never silently relax permissions:** the operator must explicitly authorize the invocation and set these process-local restrictions before starting REA:

~~~powershell
$env:REA_BROWSER_OBSERVE_ENABLED = 'true'
$env:REA_BROWSER_CDP_ENDPOINTS_JSON = '["http://127.0.0.1:9222"]'
$env:REA_BROWSER_ALLOWED_ORIGINS_JSON = '["http://127.0.0.1:8000"]'
~~~

The `--approved` flag is **not used for release 6.9.0**. Consult `--help` and the exact release's permission model before changing versions. `doctor` and `setup` are not observation proofs.

## Inspect only a local, disposable training application

Run in isolated terminals after cloning your approved laboratory repository and installing dependencies. Rota 2 can debug instrumentation, but cannot be a source-hidden confirmatory target because its source is public.

~~~powershell
# Terminal A: start demonstrator
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal B: a separate, disposable browser profile
$edge = Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path $edge)) { $edge = Join-Path ([Environment]::GetFolderPath("ProgramFilesX86")) 'Microsoft\Edge\Application\msedge.exe' }
& $edge --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir="$env:TEMP\rea_research_disposable" http://127.0.0.1:8000

# Terminal C: list real targets
npx.cmd -y "rea-agents@$REA_VERSION" list-browser-targets http://127.0.0.1:9222 --json
~~~

Use the target ID returned by the tool, not an invented value. Start recording BEFORE clicking the filter Freios. Do not use 'capacetes' as if it were a valid Rota 2 category.

~~~powershell
npx.cmd -y "rea-agents@$REA_VERSION" inspect-web-page http://127.0.0.1:9222 TARGET_ID_REAL --observation-ms 10000 --include-accessibility-text --include-json-body-shapes --json
~~~

Check the pinned release's --help before executing; command syntax changes across releases. If tool/version mismatch occurs, log it and halt; do not substitute normal browser output as REA evidence. Close disposable browser after observation.

## Evidence retention and integrity

Store raw command outputs in a PRIVATE location outside the public repository and implementing-agent workspace. Redact cookies, secrets, headers, PII and HAR. Only release approved redacted excerpts and integrity hashes.

~~~powershell
Get-FileHash -Algorithm SHA256 -Path "C:\PRIVATE_LOCAL\Evidence.json"
python -m research.hash_artifact "C:\PRIVATE_LOCAL\Evidence.json"
~~~

Hashing proves only byte integrity. A documented, witnessed call needs exact REA version, tool catalog, argument/result digests, target, timestamp, duration, success/failure, limitations and independent corroboration. JSON Schema cannot authenticate a fabricated trace.

## Full no-go before any pilot

1. Common target and authorization surface across T0–T3; classify any instrument-exclusive privileges.
2. Confirm filesystem isolation from real agent identity with a protected evaluator-only sentinel. The optional limited probe: python -m research.isolation_probe --protected-file C:\EVALUATOR_ONLY\sentinel.bin. Result DENIED covers this path only; NOT_FOUND is NOT PROOF. Also audit network, linked tools and credentials independently.
3. Freeze model ID, prompts, skills, tool catalog, package, host, resource budgets and stopping criteria for all four arms.
4. Require independent hidden oracle suites external to implementing agents; validate reference PASS, valid executed mutants, correct alternative implementations, metamorphic and double adjudication.
5. Approve numeric no-go thresholds and named owners before collecting any pilot outcomes.

**Evidence now available:** actual **REA CLI** `list-browser-targets` and `inspect-web-page` calls were successfully executed in an isolated Ubuntu GitHub Actions runner, with a controlled filter click on the Rota 2 local target and externally verifiable logs/manifest. See [WP2 evidence report](WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md). **Still NOT VERIFIED:** the Windows/Antigravity MCP client registration, independent review, a source-hidden reconstruction trial, the protocol's P2 research-team freeze, and all comparative T0–T3 results.


## Atualização 16/11/2026 — tool calls MCP verdadeiramente executados no Linux

O [novo checkpoint M02](../docs/research/M02_REAL_MCP_STDIO_CHECKPOINT_2026-11-16.md) comprova, em [CI run 43968147964](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43968147964), uma sessão **real** do servidor oficial rea-agents@6.9.0 via JSON-RPC stdio com initialize, tools/list e tools/call de list_browser_targets e inspect_web_page no alvo local autorizado. Não é mais correto descrever a pesquisa como possuidora somente de prova de CLI. O passo de **homologação específica do cliente Antigravity/Windows** continua pendente. Leia o [runbook específico](M02_ANTIGRAVITY_HOMOLOGATION_RUNBOOK.md); manter os estados INSTALL/CONFIGURE/VISIBLE/EXECUTED/DECISION_USEFUL distintos, sem substituir um pela evidência do outro.
