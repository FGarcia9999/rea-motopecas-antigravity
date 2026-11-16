# REA P3 — Controlled isolation smoke checkpoint

**Date:** 16 November 2026. **Scientific classification:** engineering feasibility evidence for an isolated synthetic topology; **NOT P3 approval, NOT a hidden benchmark, NOT a T0–T3 trial**.

## Evidence and reproducibility

- [GitHub Actions restricted agent/evaluator validation — SUCCESS](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43946136046), commit `9dcdf7add3397cf27ea7316a2774ed12a3b63363`.
- Source: `research/isolation/` and `.github/workflows/p3-isolation-smoke.yml`.
- Private synthetic filesystem canary is generated at runtime by CI and never printed. Only sanitized test results are uploaded (14-day retention); no hidden oracles or research ground truth are stored in this public repository.

### Network and identity design

```text
GitHub-hosted runner (trusted Docker daemon; temporary)
     +---------------- INTERNAL Docker bridge: p3-agent-net ----------------+
     |  scripted non-root "agent" ---- HTTP only ----> Rota2 reference       |
     |  no source code mount, no Docker socket, read-only root FS           |
     +----------------------------+-----------------------------------------+
                                  | Reference is dual-homed
     +---------------- INTERNAL Docker bridge: p3-evaluator-net ------------+
     |  evaluator demo health service <---> reference                       |
     |  private evaluator fixture mounted only in evaluator                 |
     +----------------------------------------------------------------------+
```

The agent probe tests authorized access to `p3-reference:8000/api/health`, negative reachability by evaluator DNS and direct IP, a deliberately mounted unreadable canary yielding `PermissionError`, lack of source/evaluator mounts, absent Docker socket, unprivileged UID, and absent IPv4 default route.

The separate **host audit** checks the actual `docker inspect` state: both bridges `Internal=true`, exact network memberships, no shared agent–evaluator network, all agent bind mounts read-only, `cap-drop ALL`, `no-new-privileges`, non-root UID, read-only root filesystem and nonzero resource limits. The synthetic app itself runs with temporary SQLite under `/tmp`; no existing operational database is used.

**Observed:** all defined checks passed in [run 43946136046](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43946136046). A subsequent unit-test suite additionally rejects non-internal networks, escalated privileges, shared networks, writable mounts, Docker socket exposure and missing negative controls.

## Important limits and threats to validity

1. **Agent identity is only a scripted Python probe**, not Antigravity, a real LLM or the T3 toolset. A future real agent's filesystem, linked tools, MCP catalog, network exposure and credentials require separate audit.
2. **Rota 2 is public-source** and the reference service uses the project's code, so this is not a source-hidden confirmatory application. Lack of a bind mount in a container is not evidence the agent has never seen public code.
3. The reference service is deliberately connected to both networks to be observable by the evaluator. A compromised dual-homed reference or trusted Docker daemon is outside this limited test's threat model. Stronger P3 deployment should use separate trust principals/hosts and verified restrictions.
4. `NOT_FOUND` does not establish access denial. Only the explicit canary file was tested for `PermissionError`. DNS/IP negative probes cover the selected evaluator endpoint, not all conceivable tool interfaces or alternative routes.
5. The runtime image and Python dependencies have **not been frozen for the scientific pilot**. The CI records the commit and repeatable steps, but exact image digests, network setup, scopes and external tool versions must be frozen and archived before confirmatory experiments.
6. This test does **not** establish oracle quality (P4) or data validity and does not license editing any empirical results table in Manuscript M1 v0.4.

## Updated project gate register

| Gate | State | Required next evidence |
|---|---|---|
| P1 | DRAFT | Research-team approval of thresholds and operational data contracts |
| P2 | CLI proof obtained; MCP client NOT VERIFIED | Real authorized Antigravity/MCP call with versioned trace and independent check |
| P3 | **TECHNICAL ISOLATION SMOKE PASS — FULL GATE HOLD** | Same topology with real agent/tool identity and independent source-hidden target |
| P4 | Demonstration-only oracle engine | Evaluator-owned hidden tests, reference PASS, verified mutants, correct alternatives and reviewer adjudication |
| P5/P6 | NOT EXECUTED | Only after prior gates and analysis freeze |

The engineering evidence can support the **feasibility/method-implementation** narrative, but it cannot support a claim of causal improvement, general security, or stronger reference fidelity.

Sources: [Docker internal networks](https://docs.docker.com/reference/cli/docker/network/create/), [bridge isolation](https://docs.docker.com/engine/network/drivers/bridge/), [no-new-privileges](https://docs.docker.com/reference/cli/docker/container/run/).
