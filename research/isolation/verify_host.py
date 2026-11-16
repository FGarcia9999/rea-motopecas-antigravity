"""Host-side Docker configuration attestation for a synthetic P3 smoke.

Separate from the agent probe. No private evaluator files are read or emitted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def audit(agent: dict, reference: dict, evaluator: dict, probe: dict,
          agent_network: dict, evaluator_network: dict) -> dict:
    a = agent["HostConfig"]
    mounts = {m["Destination"] for m in agent["Mounts"]}
    agent_nets = set(agent["NetworkSettings"]["Networks"])
    ref_nets = set(reference["NetworkSettings"]["Networks"])
    evaluator_nets = set(evaluator["NetworkSettings"]["Networks"])
    checks = {
        "both_bridges_internal": (agent_network["Internal"] is True
                                  and evaluator_network["Internal"] is True
                                  and agent_network["Driver"] == "bridge"
                                  and evaluator_network["Driver"] == "bridge"),
        "agent_only_on_agent_net": agent_nets == {agent_network["Name"]},
        "evaluator_only_on_evaluator_net": evaluator_nets == {evaluator_network["Name"]},
        "reference_on_both_networks": ref_nets == agent_nets | evaluator_nets,
        "all_agent_bind_mounts_read_only": all(m["RW"] is False for m in agent["Mounts"]),
        "agent_nonzero_resource_caps": a["PidsLimit"] > 0 and a["Memory"] > 0,
        "agent_not_privileged": not a["Privileged"],
        "agent_rootfs_readonly": a["ReadonlyRootfs"] is True,
        "agent_dropped_all_capabilities": "ALL" in a["CapDrop"],
        "agent_no_new_privileges": any("no-new-privileges" in s for s in a["SecurityOpt"]),
        "agent_unprivileged_user": agent["Config"]["User"] == "65534:65534",
        "agent_has_no_docker_socket_mount": "/var/run/docker.sock" not in mounts,
        "agent_has_only_allowlisted_mounts": mounts == {"/probe/agent_probe.py", "/restricted/p3-canary"},
        "reference_has_agent_network": bool(agent_nets & ref_nets),
        "evaluator_has_no_shared_agent_network": not (agent_nets & evaluator_nets),
        "evaluator_has_shared_reference_network": bool(evaluator_nets & ref_nets),
        "probe_executed_and_all_checks_passed": probe.get("result") == "PASS_LIMITED_SMOKE"
            and isinstance(probe.get("checks"), dict) and bool(probe["checks"])
            and all(probe["checks"].values()),
        "agent_container_exit_zero": agent["State"]["ExitCode"] == 0,
    }
    success = all(checks.values())
    return {
        "result": "PASS_LIMITED_DOCKER_TOPOLOGY" if success else "FAIL",
        "checks": checks,
        "scope": "DISPOSABLE_PUBLIC_ROTA2_NO_REAL_LLM_OR_HIDDEN_ORACLES",
        "scientific_P3": "NOT_APPROVED",
        "cross_network_policy": "TESTED_SPECIFIC_DOCKER_PATHS_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("agent", "reference", "evaluator", "probe", "agent_network", "evaluator_network"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    data = {k: json.loads(getattr(args, k).read_text()) for k in
            ("agent", "reference", "evaluator", "probe", "agent_network", "evaluator_network")}
    result = audit(**data)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["result"].startswith("PASS_") else 3


if __name__ == "__main__":
    raise SystemExit(main())
