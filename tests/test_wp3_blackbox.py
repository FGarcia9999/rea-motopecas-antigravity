"""WP3 evaluator-engine tests. All suites and behaviors are PUBLIC TOYS, not hidden tests."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from research.oracles import blackbox
from research.oracles.toy_suite import build_public_toy_suite


def _fake_transport():
    calls = []
    def send(port, step, key):
        calls.append((port, step["path"], key))
        if step["path"].startswith("/api/products?category=Freios"):
            return (200, [{"category": "Freios"}, {"category": "Freios"}])
        if step["path"].startswith("/api/products?category=NAO_EXISTE"):
            return (200, [])
        if step["path"] == "/api/health":
            return (200, {"status":"ok","payments":False})
        if step["path"] == "/api/orders":
            previous=sum(x[1]=="/api/orders" for x in calls) > 1
            return (201, {"order_id":"TOY-1", "replayed":previous,
                          "payment_processed":False})
        raise AssertionError("Unexpected test route")
    return send, calls


def test_json_schema_and_valid_public_suite():
    s=build_public_toy_suite()
    blackbox._validate_suite(s)
    assert len(s["cases"])==4


def test_full_public_toy_suite_pass_with_fake_transport(monkeypatch):
    send, calls=_fake_transport()
    monkeypatch.setattr(blackbox,"_send",send)
    result=blackbox.evaluate(build_public_toy_suite(),"http://127.0.0.1:8000",suite_sha256="a"*64,run_id="LOCAL_TOY")
    assert result["result"]=="PASS"
    assert result["passed_cases"]==result["total_cases"]==4
    assert result["critical_failures"]==0
    assert result["raw_response_bodies_in_report"] is False
    assert result["oracle_independent_review_attested"] is False
    assert len(set(c[2] for c in calls if c[1]=="/api/orders"))==1
    assert "TOY-1" not in json.dumps(result)


def test_known_bad_category_is_rejected_not_false_pass(monkeypatch):
    normal,_=_fake_transport()
    def mutated(port,step,key):
        if step["path"]=="/api/products?category=Freios":
            return (200,[])
        return normal(port,step,key)
    monkeypatch.setattr(blackbox,"_send",mutated)
    result=blackbox.evaluate(build_public_toy_suite(),"http://127.0.0.1:8000",suite_sha256="b"*64,run_id="PUBLIC_MUTANT")
    assert result["result"]=="FAIL"
    broken=next(c for c in result["cases"] if c["case_id"]=="PUBLIC_RF03_VALID_CATEGORY")
    assert broken["passed"] is False
    assert broken["failure_code"]=="LENGTH_MISMATCH"


@pytest.mark.parametrize("target",[
    "https://127.0.0.1:8000","http://example.org:8000",
    "http://127.0.0.1:80","http://localhost:8000",
    "http://127.0.0.2:8000","http://127.0.0.1:8000/other",
    "http://user:pass@127.0.0.1:8000",
])
def test_strict_loopback_scope_rejects_non_local_target(target):
    with pytest.raises(blackbox.OracleError):
        blackbox._target_port(target)


@pytest.mark.parametrize("path",[
    "https://example.org/api/products","//evil.example/api/products",
    "/admin","/api/../private","/api/%2e%2e/secrets",
    "/api//products","/api/%2Fetc","/api/products#fragment"
])
def test_untrusted_paths_blocked(path):
    with pytest.raises(blackbox.OracleError):
        blackbox._safe_path(path)


def test_empty_all_equal_is_not_vacuously_accepted():
    check={"op":"all_equal","pointer":"","field_pointer":"/category","value":"Freios"}
    with pytest.raises(blackbox.OracleError,match="ALL_EQUAL"):
        blackbox._check([],check,{})


def test_real_json_pointer_escapes_and_missing():
    assert blackbox._pointer({"a/b":{"c~d":9}},"/a~1b/c~0d")==9
    with pytest.raises(blackbox.OracleError):
        blackbox._pointer({"x":1},"/missing")


def test_duplicate_cases_or_empty_suite_not_permitted():
    s=build_public_toy_suite()
    s["cases"].append(copy.deepcopy(s["cases"][0]))
    with pytest.raises(blackbox.OracleError,match="Duplicate"):
        blackbox._validate_suite(s)
    s["cases"]=[]
    with pytest.raises(blackbox.OracleError):
        blackbox._validate_suite(s)


def test_get_request_body_rejected():
    s=build_public_toy_suite()
    s["cases"][0]["steps"][0]["json"]={"any":"bad"}
    with pytest.raises(blackbox.OracleError,match="GET"):
        blackbox._validate_suite(s)


def test_auth_header_not_permitted():
    s=build_public_toy_suite()
    s["cases"][0]["steps"][0]["headers"]={"Authorization":"Bearer XXXXX"}
    with pytest.raises(blackbox.OracleError):
        blackbox._validate_suite(s)


def test_external_suite_location_enforced():
    with pytest.raises(blackbox.OracleError,match="outside repository"):
        blackbox._external_file(blackbox.REPOSITORY/"README.md",must_exist=True)


def test_report_path_must_be_external():
    with pytest.raises(blackbox.OracleError):
        blackbox._external_file(blackbox.REPOSITORY/"something.json",must_exist=False)


def test_failed_http_status_stays_in_denominator(monkeypatch):
    monkeypatch.setattr(blackbox,"_send",lambda *args:(503,{"detail":"down"}))
    s=build_public_toy_suite()
    result=blackbox.evaluate(s,"http://127.0.0.1:8000",suite_sha256="e"*64,run_id="ERROR_DEMO")
    assert result["total_cases"]==4
    assert result["passed_cases"]==0
    assert all(x["failure_code"]=="HTTP_STATUS_MISMATCH" for x in result["cases"])


def test_invalid_json_document_from_external_file_is_rejected(tmp_path):
    suite=tmp_path/"test.json"
    suite.write_text("not JSON",encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        json.loads(suite.read_bytes())


def test_capture_variable_missing_fails_closed():
    check={"op":"equals_capture","pointer":"/order_id","capture_name":"undefined"}
    with pytest.raises(blackbox.OracleError,match="CAPTURE_NOT_DEFINED"):
        blackbox._check({"order_id":"some-id"},check,{})
