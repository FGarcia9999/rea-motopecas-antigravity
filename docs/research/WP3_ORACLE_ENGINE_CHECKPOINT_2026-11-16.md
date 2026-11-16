# WP3 — First executable oracle checkpoint (2026-11-16)

**Scientific label:** an *engineering feasibility check using public toy cases*, not the confirmatory T0–T3 comparison, not independent source-hidden review, and not P4 approval.

## Provenance

- GitHub Actions demonstration: https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43943444066
- Configured Quality Gates: https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43943558636
- Software: public Rota 2 educational FastAPI/SQLite application in an ephemeral GitHub-hosted Ubuntu runner; evaluator tests run in the same CI job, NOT in an isolated trust principal.
- Test-suite contract: research/oracles/suite.schema.json. The publicly readable toy suite is constructed by research/oracles/toy_suite.py **in runner temporary storage outside the checkout**. That location is not proof of secrecy or process isolation.
- Evaluation engine: research/oracles/blackbox.py; outputs report metadata only and refuses non-loopback URLs.

## Public positive / negative controls

| Control | Observed job outcome | Scientific interpretation |
|---|---|---|
| Positive: Rota 2 reference with 4 public sample cases | PASS (4/4) | The engine can evaluate this known public behavior |
| Negative: known-bad synthetic local server, category Freios returns [] with HTTP 200 | FAIL; RF-03 raises LENGTH_MISMATCH | The engine distinguishes a behavior defect from HTTP success |
| Replay same Idempotency-Key in a synthetic order | Included in the four-case public reference PASS | Basic multi-step capability; no concurrency guarantee |
| Arbitrary external target, traversal, auth header, empty suite | Unit tests reject | Fail-closed API evaluator inputs, not a security penetration test |
| Manifest, compileall, pytest, dependency audit | SUCCESS for final code state at first checkpoint | Engineering configuration quality only |

**Neither 4/4 nor 1/1 is an estimate of benchmark behavioral fidelity, mutation sensitivity or false rejection.** One known faulty toy implementation cannot provide a confidence interval or generalizable mutation score. The evaluator suite is not hidden; there is no blinded assessor, independent application, alternative correct implementation study, or signed gate.

## Preservation of required boundaries

- Only localhost IP 127.0.0.1 and ports 8000–8999 are admitted. The runner never targets third-party sites.
- Reports include suite digest, case IDs, failure categories and durations, but no full API response bodies, order IDs or credentials.
- Hidden tests, reference source, research ground truth and private evaluator notes must remain outside the repository and implementing-agent workspace, under separately enforced filesystem/network/tool isolation. The public engine alone cannot guarantee that.
- No PR is merged to main. PR #4 is the preceding research WP1–WP3 scaffold; this extension is staged independently.

## Next scientific deliverables

1. **P3 isolation evidence:** provision distinct agent/evaluator identities and workspaces with network and tool permission controls; attempt adversarial access from the agent identity and record DENIED, not merely NOT_FOUND.
2. **P4 real independent oracles:** generate a private benchmark target with evaluator-only source and reference requirements, predeclare behavior suite and time/state resets, validate reference PASS, varied valid mutants and verified-correct alternatives, and obtain independent reviewer adjudication.
3. **P1/P2 freeze:** agree numeric go/no-go thresholds and authors' approvals; complete a true Antigravity client MCP tool call on an authorized host, building on the separate real CLI smoke evidence already available.
4. **WP4 pilot:** only after signed P1–P4 gates; the suggested 20 runs are a *planning target*, not an executed sample.

**Manuscript M1 v0.4 impact:** this milestone can support a technical feasibility subsection or supplementary engineering log. It must not populate the confirmatory Results table or justify a claim that REA/MCP outperforms a baseline.
