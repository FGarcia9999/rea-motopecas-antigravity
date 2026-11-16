# WP2 — Real REA CLI evidence (controlled local synthetic demo)

**Date:** 2026-11-16. **Classification:** technical CLI smoke, NOT an experimental reconstruction run and NOT a completed scientific P2 gate.

**Primary audit trail:** [GitHub Actions run 43932452118](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43932452118). The workflow `.github/workflows/wp2-local-rea-smoke.yml` was executed on the code snapshot `e54701bcf5b53cd705b82b6c2a30815557021cf0`; its provenance is retained in the run logs and 14-day GitHub Actions artifact. The source itself was subsequently SHA-256-manifested on the research branch.

## Runtime and execution boundary

- GitHub-hosted Ubuntu runner; **Node 24.22.2**, npm 11.19.1, Python 3.11.18, Chrome 157 (disposable headless profile), own FastAPI application on `http://127.0.0.1:8000`.
- Official npm package **`rea-agents@6.9.0`**, registry package integrity `sha512-KqDn1UR5BMqHoQ3MGAnPuWiSKwgdFaz1L/uUNgrKt+1W8kPtgYP8AWEOXIF1lDIOBVyPuYIIst2iamo1Wf3r8g==`.
- Explicit policy: `REA_BROWSER_OBSERVE_ENABLED=true`, CDP endpoint `http://127.0.0.1:9222`, permitted origin `http://127.0.0.1:8000`. Only fictional/local data; no credentials, operational database, reference hidden code or human data.
- The browser action was executed by the **independent stimulus driver** `research/cdp_demo_driver.py`, not by REA (REA is a passive observer).
- **Package-specific issue:** on published 6.9.0, `--approved` returned `Unknown flag: --approved`. The test was rerun successfully **without that unsupported flag**, preserving the explicit environment restrictions. Do not copy unreleased flags into frozen protocols.

## Real CLI evidence

| Tool | Evidence | Outcome |
|---|---|---|
| `list-browser-targets` | `targets.json`, provider `rea-cdp-browser` | Local Rota 2 target discovered |
| `inspect-web-page` (2 s, passive baseline) | `inspect.json`, ID `ev_430123544be21c74eaa90f491be1ad22b66da11728cce3a065a7fa4f7e93fa87` | 574 DOM nodes, 672 accessibility nodes; 0 new network requests |
| `inspect-web-page` (10 s, with click) | `filter-inspect.json`, ID `ev_1eb41eed72989a9877492e5c7f404a9a8bac7e2957d4483c344a0506ec99eec5` | **2 browser network requests** linked to the click |
| External CDP stimulus | `filter-driver.json` | Clicked category `Freios`; interface returned **2 products** |

**Observed by REA:** `GET /api/products?category=Freios` → HTTP **200** and `GET /api/products` → HTTP **200**. Both requests identify `/static/app.js` as script initiator. This demonstrates technical observation, **not application reconstruction fidelity or backend source access**.

**Primary content hash:** `filter-inspect.json` SHA-256 `ee089dd20d750ed78def182685cb7f65ee95ef69ef46219726e305794fbe59ce`.

**GitHub artifact:** [rea-wp2-smoke-local-evidence, run 43932452118](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43932452118) (original retention 14 days; archive an authorized local copy with hashes if it must support future replication).

## Capture limitations

REA classified the output as `policy_filtered`. The baseline capture started after page load, so **prior network activity was unavailable**; in the interactive capture only the requests within the 10-second window are observable. REA did not collect response-body JSON shapes (`not_approved`), customer values, storage values, credentials or complete worker network events. It explicitly reports that artifact identity and browser-host architecture were not observed. **No absence-of-event claim** should be made beyond that window.

## Scientific status / next gates

- **Proven:** real official rea-agents **CLI** invocation, CDP target discovery, passive DOM capture, and a network trace correlated to a controlled local UI interaction.
- **Not proven:** REA **MCP tool call from Antigravity**, Windows host behavior, source-hidden isolation, independent external-oracle equivalence, randomized T0–T3 comparison, independent reviewer confirmation, or research-team go/no-go approval.
- **P2 decision:** technical CLI smoke **PASS**, full instrumented-treatment freeze **HOLD / NOT FROZEN** pending client-specific MCP session, scope equality, independent trace review and team sign-off.

This report records a **real engineering validation**, not an experimental outcome to insert into the treatment Results section of M1 v0.4.
