# WP3/P4 — Agent-to-evaluator handoff (research infrastructure)

**Status, 2026-11-16:** executable transport format and public integration smoke. **NOT** a scientific source-hidden benchmark, isolated evaluator attestation, or independent human approval.

## Why a separate handoff?

The implementing agent has access only to an **authorized running reference application** and its own writable output workspace. The independent assessor owns the hidden requirement contract, reference source code, frozen behavioral tests, adjudication and the evaluation account. After the agent finishes or fails its run, it submits a versioned archive of its implementation; **the evaluator must never grant the agent access to the evaluator workspace**.

The existing P3 Docker smoke tests a scripted principal, not a real LLM. The handoff here adds an explicit artifact path and immutable per-file digest, but it **does not create a trust boundary by itself**. Actual separation requires distinct principals, filesystem/network controls, independent reviewer and frozen trial rules.

## Public implementation

`bundle.py` generates a deterministic ZIP with `handoff-manifest.json` (run ID, treatment T0–T3 and SHA-256/byte count of each file) plus allowed candidate source files. It rejects symlinks, dotfiles, traversal, unexpected extensions, oversize archives, duplicate ZIP entries, unsafe absolute paths, corrupt payloads and output overwrite. The evaluator verifies checksums and **only then** extracts into a previously nonexistent folder with restricted file modes. It **never executes candidate code**.

Limitations: accepted sources are limited to `src/...` Python, `web/...` JS/CSS/HTML/JSON, and `assets/...` SVG/PNG/JPG/WEBP. Broader or compiled applications require a reviewed format revision, not ad-hoc extensions. Hashes provide **integrity**, not authorship, attestation or safety. ZIP content should be handled as hostile and, if executed, must be executed only in a separately controlled container with egress restrictions, read-only base image, resource caps and no evaluator/ground-truth mounts.

### Synthetic local demonstration

Use two directories outside the repository: an agent-output folder containing `src/service.py` and an evaluator-owned storage location.

```bash
python -m research.handoff.bundle pack --workspace /tmp/rea-candidate   --archive /tmp/rea-transfer/output.zip --run-id PUBLIC_DEMO --treatment T3
python -m research.handoff.bundle verify --archive /tmp/rea-transfer/output.zip   --inbox /tmp/rea-evaluator/received --extract
```

Use the actual non-overlapping paths on your host. Output `FORMAT_AND_HASHES_VERIFIED_NO_EXECUTION_OR_AUTHORSHIP_ATTESTATION` means only data integrity. Do not reuse `PUBLIC_DEMO` as an experimental run.

### Private assessor contract — **not supplied in this public repository**

Before any confirmatory task:
1. Independent assessor creates **private, source-hidden** application and locked behavior contract (ground truth and hidden oracle suite), and records immutable hashes **without revealing code or oracle contents** to the agent.
2. Team documents permission equivalence across T0–T3, including the exact REA/MCP tool catalog and any extra information available to instrumented arms.
3. Reference lives in evaluator-only storage and is deployed as an authorized observable service. Agent source and oracles are unreachable from all agent tools, filesystem paths and network endpoints.
4. Agent writes a candidate into its workspace and is terminated. A trusted external operator captures the handoff ZIP. Treat any output as untrusted.
5. Evaluator independently verifies the archive, tests it in its own disposable sandbox against frozen hidden oracles, retains every failure/timeout and signs an adjudication. Test results leave the evaluator only as approved redacted metadata.
6. An independent researcher inspects the environment attestation, correctness alternatives, executed mutants and all nine approved no-go thresholds.
7. Only then is a pilot execution eligible for scientific analysis. **The 20-run pilot remains unstarted**.

Never commit hidden tests, private reference code, credentials or full HAR traces here. The public GitHub Actions checks **only public synthetic data**.

## Controls and CI

`tests/test_research_handoff.py` checks deterministic output, hashes, traversal, malformed/duplicate ZIPs, symlinks, oversized payloads, output overwrite and no code execution. `p4-public-evaluator-smoke.yml` validates one synthetic handoff and the three public oracle controls (original, deliberately wrong mutant, alternate correct for four public cases).

**Interpretation of sample metrics:** one tested mutant detected and one alternate correct implementation accepted only show that the engine distinguishes these **two handcrafted controls**; they are NOT estimators of population mutation sensitivity or false rejection.

See [P4 checkpoint](../../docs/research/P4_EVALUATOR_CHECKPOINT_2026-11-16.md), [protocol v1.2](../../docs/research/EXPERIMENTAL_PROTOCOL_v1.2.md) and [P3 isolation checkpoint](../../docs/research/P3_ISOLATION_CHECKPOINT_2026-11-16.md).
