# WP2 — Real REA/MCP observation runbook (NOT YET EXECUTED)

**Research protocol:** v1.2. **Date:** 2026-11-16. **Status:** P2 NOT VERIFIED, no authentic REA/MCP invocation trace. These are instructions for an authorized Windows PowerShell lab.

**Official sources checked:** https://rea.tools/get-started/ ; https://rea.tools/guides/browser/ ; https://github.com/morluto/rea/blob/main/docs/getting-started/installation.md

## Authorization, client, and release freeze

A named operator must approve the selected local target, the exact REA package release, browser debugging profile, any client settings modifications, permission policy and evidence storage. Never capture unauthorized third-party apps, accounts, personal browsing, customer data or secrets. Do not use @latest in frozen runs. Fix the exact verified rea-agents package version first.

~~~powershell
node --version
npm --version
$REA_VERSION = "PREENCHER_VERSAO_HOMOLOGADA"
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

**Result of this development milestone:** RUNBOOK ONLY. Real REA/MCP tool execution, isolation and experiment remain NOT VERIFIED.
