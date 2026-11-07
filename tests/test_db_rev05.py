"""REV05: pytest integration contracts for opt-in SQLite inventory ledger."""
from __future__ import annotations

import concurrent.futures
import os
import sqlite3
import subprocess
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

from app.db import connect, inventory_ledger_enabled, reconcile_inventory
from app.main import make_app
from scripts import lab_db_extension


@pytest.fixture
def lab(tmp_path, monkeypatch):
    path = tmp_path / "lab_rota2.db"
    monkeypatch.setenv("MOTO_DB_PATH", str(path))
    with TestClient(make_app()) as client:
        with connect() as db:
            assert not inventory_ledger_enabled(db)
        lab_db_extension.migrate(path)
        yield client, path


def order(client, pid=1, qty=2, key=None):
    return client.post(
        "/api/orders",
        json={"items": [{"product_id": pid, "quantity": qty}]},
        headers={"Idempotency-Key": key or str(uuid.uuid4())},
    )


def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "app.manage", *args],
        capture_output=True, text=True, env=os.environ.copy(), check=False,
    )


def test_migration_is_idempotent_and_opening_balances(lab):
    _, path = lab
    with connect() as db:
        assert inventory_ledger_enabled(db)
        assert db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 12
        assert db.execute("SELECT COUNT(*) FROM inventory_movements").fetchone()[0] == 12
        assert reconcile_inventory(db) == []
    lab_db_extension.migrate(path)
    with connect() as db:
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM inventory_movements").fetchone()[0] == 12
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_sale_debits_and_records_in_same_transaction(lab):
    client, _ = lab
    old = client.get("/api/products/1").json()["stock"]
    r = order(client)
    assert r.status_code == 201
    with connect() as db:
        rows = db.execute(
            "SELECT product_id, delta_qty, order_id, movement_type FROM inventory_movements "
            "WHERE movement_type='SALE'"
        ).fetchall()
        assert len(rows) == 1
        assert tuple(rows[0]) == (1, -2, r.json()["order_id"], "SALE")
        assert reconcile_inventory(db) == []
    assert client.get("/api/products/1").json()["stock"] == old - 2


def test_idempotency_replay_does_not_duplicate_sale(lab):
    client, _ = lab
    key = "rev05-" + uuid.uuid4().hex
    r1 = order(client, pid=3, qty=2, key=key)
    r2 = order(client, pid=3, qty=2, key=key)
    assert r1.status_code == r2.status_code == 201
    assert r2.json()["replayed"] is True
    assert r1.json()["order_id"] == r2.json()["order_id"]
    assert order(client, pid=3, qty=1, key=key).status_code == 409
    with connect() as db:
        assert db.execute(
            "SELECT COUNT(*) FROM inventory_movements WHERE movement_type='SALE'"
        ).fetchone()[0] == 1
        assert reconcile_inventory(db) == []


def test_failed_ledger_insert_rolls_back_order_and_stock(lab):
    client, _ = lab
    old = client.get("/api/products/1").json()["stock"]
    with connect() as db:
        db.execute("""CREATE TRIGGER reject_sale BEFORE INSERT ON inventory_movements
            WHEN NEW.movement_type='SALE'
            BEGIN SELECT RAISE(ABORT, 'simulated ledger failure'); END""")
    with pytest.raises(sqlite3.IntegrityError, match="simulated ledger failure"):
        order(client, qty=1)
    with connect() as db:
        assert db.execute("SELECT stock FROM products WHERE id=1").fetchone()[0] == old
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
        assert reconcile_inventory(db) == []


def test_insufficient_stock_has_no_side_effects(lab):
    client, _ = lab
    assert order(client, pid=12, qty=10).status_code == 409
    with connect() as db:
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
        assert db.execute(
            "SELECT COUNT(*) FROM inventory_movements WHERE movement_type='SALE'"
        ).fetchone()[0] == 0
        assert reconcile_inventory(db) == []


def test_cli_stock_adjustment_and_reason(lab):
    client, _ = lab
    old = client.get("/api/products/1").json()["stock"]
    r = cli("stock", "R2-FR-001", str(old + 4), "--reason", "Inventario de laboratorio")
    assert r.returncode == 0, r.stderr
    with connect() as db:
        row = db.execute(
            "SELECT delta_qty,reason FROM inventory_movements "
            "WHERE movement_type='ADJUSTMENT'"
        ).fetchone()
        assert (row["delta_qty"], row["reason"]) == (4, "Inventario de laboratorio")
        assert reconcile_inventory(db) == []


def test_cli_noop_does_not_create_zero_delta(lab):
    client, _ = lab
    n = client.get("/api/products/1").json()["stock"]
    assert cli("stock", "R2-FR-001", str(n)).returncode == 0
    with connect() as db:
        assert db.execute(
            "SELECT COUNT(*) FROM inventory_movements WHERE movement_type='ADJUSTMENT'"
        ).fetchone()[0] == 0


def test_cli_invalid_stock_and_reason_do_not_write(lab):
    client, _ = lab
    old = client.get("/api/products/1").json()["stock"]
    for args in (
        ("R2-FR-001", "-1"),
        ("NAO-EXISTE", "10"),
        ("R2-FR-001", "30", "--reason", "bad"),
    ):
        assert cli("stock", *args).returncode != 0
    assert client.get("/api/products/1").json()["stock"] == old
    with connect() as db:
        assert reconcile_inventory(db) == []


def test_online_backup_restore_integrity(lab):
    client, path = lab
    assert order(client).status_code == 201
    lab_db_extension.backup(path)
    lab_db_extension.restore(path)
    restored = path.with_name("lab_rota2_restored.db")
    with sqlite3.connect(restored) as db:
        db.row_factory = sqlite3.Row
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert reconcile_inventory(db) == []


def test_manual_tampering_is_detected(lab):
    with connect() as db:
        db.execute("UPDATE products SET stock=stock+1 WHERE id=1")
        errors = reconcile_inventory(db)
    assert len(errors) == 1 and errors[0]["sku"] == "R2-FR-001"


def test_partial_schema_fails_closed(lab):
    client, _ = lab
    with connect() as db:
        db.execute("DELETE FROM schema_migrations")
    with pytest.raises(RuntimeError, match="Migração não registrada"):
        order(client)


def test_lab_only_path_validation(tmp_path):
    with pytest.raises(SystemExit, match="lab_"):
        lab_db_extension.safe_path(tmp_path / "motopecas.db")
    with pytest.raises(SystemExit, match="lab_"):
        lab_db_extension.safe_path(tmp_path / "lab_ok.sql")


def test_concurrent_orders_never_oversell(lab):
    client, _ = lab
    assert cli("stock", "R2-FR-001", "1").returncode == 0
    keys = ["concurrent-" + uuid.uuid4().hex for _ in range(2)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(lambda k: order(client, qty=1, key=k).status_code, keys))
    assert sorted(statuses) == [201, 409]
    with connect() as db:
        assert db.execute("SELECT stock FROM products WHERE id=1").fetchone()[0] == 0
        assert db.execute(
            "SELECT COUNT(*) FROM inventory_movements WHERE movement_type='SALE'"
        ).fetchone()[0] == 1
        assert reconcile_inventory(db) == []
