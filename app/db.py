"""SQLite com estoque transacional e idempotência de pedidos demonstrativos."""
from __future__ import annotations

import os
from contextlib import contextmanager
import sqlite3
from pathlib import Path

from .catalog import PRODUCTS

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "motopecas.db"


def path() -> Path:
    return Path(os.environ.get("MOTO_DB_PATH", str(DEFAULT_DB)))


@contextmanager
def connect():
    dbpath = path()
    dbpath.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(dbpath), timeout=15, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    try:
        yield conn
    finally:
        conn.close()


def initialize() -> None:
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                image TEXT NOT NULL,
                price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS compatibility (
                product_id INTEGER NOT NULL REFERENCES products(id),
                bike_id TEXT NOT NULL,
                PRIMARY KEY(product_id, bike_id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL UNIQUE,
                request_digest TEXT NOT NULL,
                total_cents INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'SIMULADO'
            );
            CREATE TABLE IF NOT EXISTS order_items (
                order_id TEXT NOT NULL REFERENCES orders(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price_cents INTEGER NOT NULL,
                PRIMARY KEY(order_id, product_id)
            );
        """)
        # Seed só na primeira execução: reiniciar app não restaura estoque consumido.
        if db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            db.execute("BEGIN IMMEDIATE")
            try:
                for sku, name, category, image, cents, stock, description, bikes in PRODUCTS:
                    cur = db.execute(
                        "INSERT INTO products (sku,name,category,image,price_cents,stock,description) VALUES (?,?,?,?,?,?,?)",
                        (sku, name, category, image, cents, stock, description),
                    )
                    db.executemany("INSERT INTO compatibility (product_id,bike_id) VALUES (?,?)", [(cur.lastrowid, b) for b in bikes])
                db.execute("COMMIT")
            except Exception:
                db.execute("ROLLBACK")
                raise
