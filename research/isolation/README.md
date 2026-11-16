# Research P3 — isolated synthetic agent/evaluator smoke

This directory implements a **bounded engineering validation**, not an LLM experiment. It is a public synthetic demonstration using the Rota 2 reference in a disposable GitHub-hosted runner.

Files: `Dockerfile.reference` builds the educational Rota 2 service; `evaluator_service.py` runs a health-only evaluator on a separate internal bridge; `agent_probe.py` tests explicitly authorized target connectivity and forbidden evaluator access; `verify_host.py` independently inspects Docker permissions, mounts and networks.

Run from GitHub Actions using `.github/workflows/p3-isolation-smoke.yml`. **Never execute this workflow against operational infrastructure, production browsers, third-party sites or real evaluator secrets.** The workflow creates no published Docker ports and uses internal networks. Reports contain only booleans and a classification indicating that P3 is not approved.

A true hidden-benchmark isolation gate additionally requires: a real implementation-agent identity with its configured tools and credentials, a reference whose code is genuinely inaccessible, an evaluator controlled by a different principal, failure-mode/alternative-route probes, review by another researcher, and frozen go/no-go thresholds. It must also avoid giving the agent access to this public source as its supposed hidden reference.

See [P3 checkpoint](../../docs/research/P3_ISOLATION_CHECKPOINT_2026-11-16.md), [Research Protocol v1.2](../../docs/research/EXPERIMENTAL_PROTOCOL_v1.2.md), and [P4 oracle engine](../oracles/README.md).
