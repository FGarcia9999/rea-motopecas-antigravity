"""P3 topology assertions on synthetic JSON only, not a real LLM isolation audit."""
from __future__ import annotations

import copy
from io import StringIO

import pytest

from research.isolation.agent_probe import _has_default_route
from research.isolation.verify_host import audit


@pytest.fixture
def demo():
    agent = {
        "HostConfig": {
            "Privileged": False,
            "ReadonlyRootfs": True,
            "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges:true"],
            "PidsLimit": 64,
            "Memory": 201326592,
        },
        "Mounts": [
            {"Destination": "/probe/agent_probe.py", "RW": False},
            {"Destination": "/restricted/p3-canary", "RW": False},
        ],
        "Config": {"User": "65534:65534"},
        "NetworkSettings": {"Networks": {"p3-agent-net": {"NetworkID": "n1"}}},
        "State": {"ExitCode": 0},
    }
    reference = {"NetworkSettings": {"Networks": {
        "p3-agent-net": {}, "p3-evaluator-net": {},
    }}}
    evaluator = {"NetworkSettings": {"Networks": {"p3-evaluator-net": {}}}}
    probe = {"result": "PASS_LIMITED_SMOKE", "checks": {
        "synthetic_reference_api_accessible": True,
        "evaluator_dns_access_blocked": True,
        "evaluator_direct_ip_access_blocked": True,
        "explicitly_mounted_canary_read_denied": True,
        "reference_source_not_mounted": True,
        "evaluator_private_store_not_mounted": True,
        "docker_control_socket_not_mounted": True,
        "non_root_agent_uid": True,
        "no_ipv4_default_route": True,
    }}
    agent_network = {"Name": "p3-agent-net", "Driver": "bridge", "Internal": True}
    evaluator_network = {"Name": "p3-evaluator-net", "Driver": "bridge", "Internal": True}
    return {"agent": agent, "reference": reference, "evaluator": evaluator,
            "probe": probe, "agent_network": agent_network,
            "evaluator_network": evaluator_network}


def test_p3_smoke_not_scientific_approval(demo):
    result = audit(**demo)
    assert result["result"] == "PASS_LIMITED_DOCKER_TOPOLOGY"
    assert result["scientific_P3"] == "NOT_APPROVED"
    assert all(result["checks"].values())


@pytest.mark.parametrize("change,failed_check", [
    (lambda d: d["agent"]["HostConfig"].update(Privileged=True), "agent_not_privileged"),
    (lambda d: d["agent"]["HostConfig"].update(ReadonlyRootfs=False), "agent_rootfs_readonly"),
    (lambda d: d["agent"]["HostConfig"].update(CapDrop=[]), "agent_dropped_all_capabilities"),
    (lambda d: d["agent"]["HostConfig"].update(PidsLimit=0), "agent_nonzero_resource_caps"),
    (lambda d: d["agent"]["HostConfig"].update(SecurityOpt=[]), "agent_no_new_privileges"),
    (lambda d: d["agent"]["Mounts"][0].update(RW=True), "all_agent_bind_mounts_read_only"),
    (lambda d: d["agent"]["Mounts"].append({"Destination":"/var/run/docker.sock","RW":False}),
     "agent_has_no_docker_socket_mount"),
    (lambda d: d["agent"]["Config"].update(User="0:0"), "agent_unprivileged_user"),
    (lambda d: d["agent"]["State"].update(ExitCode=3), "agent_container_exit_zero"),
    (lambda d: d["agent_network"].update(Internal=False), "both_bridges_internal"),
    (lambda d: d["agent"]["NetworkSettings"]["Networks"].update({"p3-evaluator-net": {}}),
     "agent_only_on_agent_net"),
    (lambda d: d["evaluator"]["NetworkSettings"]["Networks"].update({"p3-agent-net": {}}),
     "evaluator_only_on_evaluator_net"),
    (lambda d: d["probe"]["checks"].update(evaluator_direct_ip_access_blocked=False),
     "probe_executed_and_all_checks_passed"),
])
def test_reject_insecure_topology(demo, change, failed_check):
    unsafe = copy.deepcopy(demo)
    change(unsafe)
    result = audit(**unsafe)
    assert result["result"] == "FAIL"
    assert result["checks"][failed_check] is False


def test_private_file_not_mounted_does_not_mean_access_denied(demo):
    """A missing file is weaker than a real PermissionError on a mounted canary."""
    demo["probe"]["checks"]["explicitly_mounted_canary_read_denied"] = False
    demo["probe"]["checks"]["evaluator_private_store_not_mounted"] = True
    assert audit(**demo)["result"] == "FAIL"


def test_network_route_parser_no_default_route(monkeypatch):
    route = "Iface Destination Gateway Flags RefCnt Use Metric Mask\neth0 000010AC 00000000 0001 0 0 0 00FFFFFF\n"
    monkeypatch.setattr("builtins.open", lambda *a, **k: StringIO(route))
    assert _has_default_route() is False


def test_network_route_parser_detects_default_route(monkeypatch):
    route = "Iface Destination Gateway Flags RefCnt Use Metric Mask\neth0 00000000 010010AC 0003 0 0 0 00000000\n"
    monkeypatch.setattr("builtins.open", lambda *a, **k: StringIO(route))
    assert _has_default_route() is True
