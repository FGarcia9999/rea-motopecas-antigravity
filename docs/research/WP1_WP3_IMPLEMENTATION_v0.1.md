# WP1–WP3 technical milestone — 2026-11-16

**Result status:** contract/schema implementation, not empirical execution.

## Produced

- \`research/schemas/ground_truth.schema.json\`, \`evidence.schema.json\`, \`run_manifest.schema.json\`, \`treatment.schema.json\`, \`oracle_quality.schema.json\`, \`go_no_go.schema.json\`.
- \`research/contracts.py\`: standardized JSON validation + semantic cross-field checks; observation-coverage and evidence-use summaries (descriptive, not causal); oracle mutation sensitivity and false rejection with denominator protection.
- \`research/treatments/T0.json\`–\`T3.json\`: four syntactically valid **DRAFT** treatment packages, not version-frozen experimental environments.
- \`research/isolation_probe.py\`: an agent-identity filesystem **single-path** access probe; does not establish network/credential isolation.
- \`research/templates/go_no_go.DRAFT.json\`: nine criteria with deliberately null thresholds/owners, pending explicit team agreement.
- \`tests/test_research_contracts.py\`: positive/negative tests including swapped treatment factors, unauthorized REA access, fake observational claims, invalid oracle denominators, duplicate mutations and run-status inconsistencies.

## Immediate scientific decisions required

1. Research team signs off ground-truth schema, controlled target/authorization and epistemic classes (P1).
2. Confirm real REA CLI/MCP package and invocation under explicitly authorized local test system, with version, signed tool/catalog digests and redacted tool-call trace (P2). No tools were invoked in this milestone.
3. Implement evaluator-owned source-hidden targets and real hidden oracles outside public repo (P3/P4); independently validate mutational sensitivity and correct alternatives.
4. Approve numeric no-go thresholds and owners **before** the first pilot run.
5. Pilot only after gate sign-offs; preliminary target is 20 runs, not statistically proven sample size.

**Outcomes not claimed:** completed pilot, actual MCP inspection, reference equivalence, scientific freeze, causality of provenance, independent gate G6/G7 approval. The public code can test the *format* and consistency of a record, but cannot certify that an arbitrary claimed real tool call occurred merely because its JSON is well formed.
