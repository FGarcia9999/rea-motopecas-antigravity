"""PUBLIC demonstrator suite generator for Rota 2.

The test cases are visible by design, so this is NOT a hidden oracle and its
results may not enter the study's confirmatory outcome table.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .blackbox import REPOSITORY, OracleError


def build_public_toy_suite() -> dict:
    return {
        "schema_version": "1.0", "suite_id": "PUBLIC_R2_SMOKE",
        "application_id": "ROTA2_PUBLIC_DEMO",
        "cases": [
            {"case_id": "PUBLIC_RF03_VALID_CATEGORY", "criticality": "MAJOR",
             "steps": [{"method": "GET", "path": "/api/products?category=Freios", "expected_status": 200,
                        "checks": [
                            {"op": "length", "pointer": "", "value": 2},
                            {"op": "all_equal", "pointer": "", "field_pointer": "/category", "value": "Freios"},
                        ]}]},
            {"case_id": "PUBLIC_RF03_EMPTY_CATEGORY", "criticality": "MINOR",
             "steps": [{"method": "GET", "path": "/api/products?category=NAO_EXISTE", "expected_status": 200,
                        "checks": [{"op": "length", "pointer": "", "value": 0}]}]},
            {"case_id": "PUBLIC_HEALTH", "criticality": "MAJOR",
             "steps": [{"method": "GET", "path": "/api/health", "expected_status": 200,
                        "checks": [
                            {"op": "equals", "pointer": "/status", "value": "ok"},
                            {"op": "equals", "pointer": "/payments", "value": False},
                        ]}]},
            {"case_id": "PUBLIC_ORDER_IDEMPOTENCY", "criticality": "CRITICAL",
             "steps": [
                 {"method": "POST", "path": "/api/orders", "expected_status": 201,
                  "headers": {"Idempotency-Key": "$RUN_KEY"},
                  "json": {"items": [{"product_id": 1, "quantity": 1}]},
                  "checks": [
                      {"op": "equals", "pointer": "/payment_processed", "value": False},
                      {"op": "equals", "pointer": "/replayed", "value": False},
                  ],
                  "capture": {"first_order": "/order_id"}},
                 {"method": "POST", "path": "/api/orders", "expected_status": 201,
                  "headers": {"Idempotency-Key": "$RUN_KEY"},
                  "json": {"items": [{"product_id": 1, "quantity": 1}]},
                  "checks": [
                      {"op": "equals", "pointer": "/replayed", "value": True},
                      {"op": "equals_capture", "pointer": "/order_id", "capture_name": "first_order"},
                  ]},
             ]},
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(REPOSITORY):
        raise OracleError("Toy suite files must be generated outside the implementing repository")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_public_toy_suite(), indent=2, ensure_ascii=False)+"\n")
    print("PUBLIC_TOY_SUITE_ONLY_NO_HIDDEN_TESTS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
