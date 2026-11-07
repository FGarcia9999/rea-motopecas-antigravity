"""API de uma loja didática. Não coleta dados pessoais nem processa pagamento."""
from __future__ import annotations

from contextlib import asynccontextmanager
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3

from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .catalog import BIKES
from .db import connect, initialize, inventory_ledger_enabled, append_inventory_movement

BASE = Path(__file__).resolve().parent.parent
STATIC = BASE / "static"
BIKE_IDS = {b["id"]: b for b in BIKES}

class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1, le=10)

class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[Item] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def no_duplicate_products(self):
        ids = [i.product_id for i in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Um produto não pode aparecer duas vezes")
        return self

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize()
    yield


def make_app() -> FastAPI:
    app = FastAPI(title="Rota 2 | API Motopeças", version="1.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
        )
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "public, max-age=300"
        return response

    @app.get("/api/health")
    def health():
        with connect() as db:
            db.execute("SELECT 1").fetchone()
        return {"status": "ok", "mode": "demo", "payments": False}

    @app.get("/api/bikes")
    def bikes():
        return BIKES

    @app.get("/api/categories")
    def categories():
        with connect() as db:
            return [x[0] for x in db.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()]

    def serialize_product(row: sqlite3.Row, db: sqlite3.Connection):
        result = dict(row)
        result["bikes"] = [r[0] for r in db.execute(
            "SELECT bike_id FROM compatibility WHERE product_id = ? ORDER BY bike_id", (row["id"],)
        ).fetchall()]
        return result

    @app.get("/api/products")
    def products(q: str = Query("", max_length=80), category: str = Query("", max_length=40),
                 bike: str = Query("", max_length=40), year: int | None = Query(None, ge=1990, le=2100)):
        if bike and bike not in BIKE_IDS:
            raise HTTPException(422, "Modelo de motocicleta não reconhecido")
        if year is not None and not bike:
            raise HTTPException(422, "Selecione um modelo antes do ano")
        if bike and year is not None:
            lo, hi = BIKE_IDS[bike]["years"]
            if not (lo <= year <= hi):
                return []
        sql = "SELECT p.* FROM products p WHERE 1=1"
        args: list = []
        if q.strip():
            sql += " AND (LOWER(p.name) LIKE ? OR LOWER(p.sku) LIKE ? OR LOWER(p.description) LIKE ?)"
            term = "%" + q.strip().lower().replace("%", "\\%").replace("_", "\\_") + "%"
            # LIKE escapes: backslash must be declared explicitly.
            sql = sql.replace("LIKE ?", "LIKE ? ESCAPE '\\'")
            args.extend([term, term, term])
        if category:
            sql += " AND p.category = ?"
            args.append(category)
        if bike:
            sql += " AND EXISTS(SELECT 1 FROM compatibility c WHERE c.product_id=p.id AND c.bike_id=?)"
            args.append(bike)
        sql += " ORDER BY p.id LIMIT 100"
        with connect() as db:
            return [serialize_product(r, db) for r in db.execute(sql, args).fetchall()]

    @app.get("/api/products/{product_id}")
    def product(product_id: int):
        with connect() as db:
            row = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            if not row:
                raise HTTPException(404, "Produto não encontrado")
            return serialize_product(row, db)

    @app.post("/api/orders", status_code=201)
    def place_order(payload: OrderRequest,
                    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=100)):
        if not all(c.isalnum() or c in "-_" for c in idempotency_key):
            raise HTTPException(400, "Idempotency-Key inválida")
        normalized = sorted((i.product_id, i.quantity) for i in payload.items)
        digest = hashlib.sha256(json.dumps(normalized).encode("utf-8")).hexdigest()
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                prior = db.execute("SELECT id, request_digest, total_cents FROM orders WHERE idempotency_key=?", (idempotency_key,)).fetchone()
                if prior:
                    if prior["request_digest"] != digest:
                        raise HTTPException(409, "Chave de idempotência reutilizada com itens diferentes")
                    db.execute("COMMIT")
                    return {"order_id": prior["id"], "total_cents": prior["total_cents"],
                            "status": "SIMULADO", "payment_processed": False, "replayed": True}

                ledger = inventory_ledger_enabled(db)  # inside transaction; read-only on legacy DB
                total = 0
                lines = []
                for product_id, quantity in normalized:
                    r = db.execute("SELECT id, stock, price_cents FROM products WHERE id=?", (product_id,)).fetchone()
                    if not r:
                        raise HTTPException(404, f"Produto {product_id} não existe")
                    if r["stock"] < quantity:
                        raise HTTPException(409, f"Estoque insuficiente para produto {product_id}")
                    total += r["price_cents"] * quantity
                    lines.append((product_id, quantity, r["price_cents"]))
                order_id = "DEMO-" + secrets.token_hex(6).upper()
                db.execute("INSERT INTO orders(id,idempotency_key,request_digest,total_cents) VALUES (?,?,?,?)",
                           (order_id, idempotency_key, digest, total))
                for pid, qty, cents in lines:
                    updated = db.execute("UPDATE products SET stock=stock-? WHERE id=? AND stock>=?", (qty, pid, qty))
                    if updated.rowcount != 1:
                        raise HTTPException(409, "Estoque alterado durante o pedido")
                    db.execute("INSERT INTO order_items(order_id,product_id,quantity,unit_price_cents) VALUES (?,?,?,?)",
                               (order_id, pid, qty, cents))
                    if ledger:
                        append_inventory_movement(
                            db, product_id=pid, delta_qty=-qty,
                            movement_type="SALE", order_id=order_id,
                            reason="pedido demonstrativo confirmado",
                        )
                db.execute("COMMIT")
                return {"order_id": order_id, "total_cents": total, "status": "SIMULADO",
                        "payment_processed": False, "replayed": False}
            except Exception:
                db.execute("ROLLBACK")
                raise

    @app.get("/api/metrics")
    def metrics():
        with connect() as db:
            p = db.execute("SELECT COUNT(*), COALESCE(SUM(stock),0) FROM products").fetchone()
            o = db.execute("SELECT COUNT(*), COALESCE(SUM(total_cents),0) FROM orders").fetchone()
            return {"products": p[0], "units_in_stock": p[1], "demo_orders": o[0], "demo_total_cents": o[1]}

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app

app = make_app()
