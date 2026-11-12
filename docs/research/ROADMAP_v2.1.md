# REA Research Roadmap v2.1 — 2026-11-11

**Decision:** keep REA scientifically separate from ASF. Reuse of conceptual infrastructure (e.g., oracles/provenance) is allowed only with transparent attribution; do not reuse the same independent results as a second finding.

| Priority | WP | Next output | Release / stop criterion |
|---|---|---|---|
| 1 | WP1 Definitions | Editable protocol v1.1, approved observability contract, locked RQ1–RQ5/estimands | Human sign-off before pilot |
| 2 | WP2 Instrumentation | Treatment packages T0–T3, versioned MCP tools and permissions | Demonstrable real tool calls; reproducible environment |
| 3 | WP3 Benchmarks / oracles | Ground truth and hidden tests stored away from agent workspace; mutant/alternative tests | Oracle false-rejection/fault detection gates approved |
| 4 | WP4 Pilot | 20 independent, randomized/counterbalanced executions with full logs | Feasibility and variance study; hold if no-go triggered |
| 5 | WP5 Main experiment | Multiple applications and models, finalized sampling and analysis | Full source-hidden evaluation on frozen design |
| 6 | WP6 Submission | M1 results, uncertainty, ethics, supplements, archival DOI | Human author approvals and journal compliance |

## No-go / non-conformance

Stop/revise if real REA/MCP cannot be used reliably; access rights differ materially across treatments; hidden code or oracles leak; oracle false rejection/fault detection is unacceptable; time/cost precludes meaningful replication; or reproducibility logs are incomplete. **Set objective thresholds before pilot starts.**

## Manuscript update policy

- Working manuscript M1 v0.3 (DOCX) contains proposed methods, no measured treatment outcomes.
- Pilot data and confirmatory results will remain separate; all failures and timeouts retained according to prespecified policy.
- Rewrite the title/abstract only if supported by data; remove internal appendix/revision notes before submission.
- Verify and disclose real LLM product/model versions, prompts, roles and use; never claim that ChatGPT or Antigravity ran tests without primary logs.
- Benchmark ground-truth content and hidden tests are **not to be committed to this public Git repository**.
- Review draft PR #1 then PR #2 before merging to main; the research PR is stacked on #2 and requires separate review.
