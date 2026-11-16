# WP3 — External black-box oracle, v0.1

Date: 2026-11-16. Status: executable public evaluator and demonstrator only. No hidden oracle dataset, independent reviewer approval, or T0–T3 comparative experiment has been completed.

## Scientific purpose

The evaluation engine is published; the substantive hidden tests and ground-truth contracts must be authored by independent evaluators, kept outside the public repository, and technically inaccessible to implementing agents. Merely placing a JSON file outside Git does NOT establish source or oracle isolation.

Primary study outcome remains the run-level proportion of independent external behavioral tests passed. The public example here is deliberately visible and may NOT be used as confirmatory data.

## Components

- blackbox.py: local-only HTTP evaluator with JSON Schema validation, allowlisted loopback target and /api/ endpoints, multi-step behaviors, typed JSON Pointer checks, per-case capture variables, zero response-body publication, timeout/failure retention, and suite hash.
- suite.schema.json: public contract for externally owned test suites.
- toy_suite.py: public sample for RF-03, missing categories, health, and two-step idempotency of a synthetic order.
- toy_mutant.py: intentionally faulty local server returning an empty Freios category.
- tests/test_wp3_blackbox.py: positive and negative tests for fail-closed URLs, forbidden headers, duplicated cases, invalid suites, counters, and report minimization.
- wp3-public-oracle-smoke.yml: CI runs the public toy suite on local Rota 2, then verifies that the known-bad mutant fails for a behavioral reason. It does not access private evaluator material.

## Run in an owned isolated demo environment

First install requirements-dev.txt and run the Rota 2 API in an **isolated temporary database** on 127.0.0.1:8000. In a separate shell on Linux:

    mkdir -p /tmp/rea-wp3-evaluator
    python -m research.oracles.toy_suite --output /tmp/rea-wp3-evaluator/public.json
    python -m research.oracles.blackbox --suite /tmp/rea-wp3-evaluator/public.json \
      --target http://127.0.0.1:8000 --run-id PUBLIC_SMOKE_01 \
      --report /tmp/rea-wp3-evaluator/report.json

Windows: generate the suite in a separate authorized evaluator directory outside the Git checkout and provide absolute paths. No external target IP is permitted. No new production routes or customer data are used.

The engine prints results as PASS/FAIL for the *supplied* suite only, with run ID and suite SHA-256; it never reproduces raw API response bodies in the report. Case failures and timeouts remain in the run denominator. Independence, isolation and human approvals remain false in the report.

## Required before the real WP3 / pilot gate

1. Define and freeze evaluator-owned source-hidden applications and a ground-truth contract, with authorization records, independent evaluators, release hashes and observability classes.
2. Restrict the actual agent's filesystem, network, tool and credential access. Audit isolation from the agent identity. Prompt instructions or separate directories alone are not sufficient.
3. Build private hidden oracle suites before agents start implementation; ensure they PASS on the reference and can detect VALID, EXECUTED behavior-changing mutants. Include independently verified correct alternative implementations and adjudication to quantify false rejection.
4. Freeze criteria, thresholds and reviewers with P1–P4 sign-off BEFORE the exploratory 20-run pilot.
5. Keep all failed executions, timeouts, tool blocks and resource costs. Do not report public toy pass rates as study efficacy.

## Important limitations

This v0.1 evaluator supports only JSON API workflows; it does not test pixel fidelity, UI rendering, concurrent consistency, browser state or private database records directly. Capturing idempotency through the public sample only exercises a disposable synthetic application.

No statistical interpretation of T3−T1, provenance causality, independent review completion or reference equivalence is justified by these tests.

See docs/research/EXPERIMENTAL_PROTOCOL_v1.2.md and research/WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md.
