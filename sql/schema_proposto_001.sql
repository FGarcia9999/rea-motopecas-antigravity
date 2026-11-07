-- PROPOSTA DE MIGRAÇÃO 001. Aplicação segura/idempotente pelo script Python.
-- Atenção: NÃO execute isoladamente em produção; exige baseline + integração API/CLI.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS schema_migrations(
 version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS inventory_movements(
 id INTEGER PRIMARY KEY,
 product_id INTEGER NOT NULL REFERENCES products(id),
 delta_qty INTEGER NOT NULL CHECK(delta_qty <> 0),
 movement_type TEXT NOT NULL CHECK(movement_type IN ('OPENING','SALE','ADJUSTMENT','RETURN')),
 order_id TEXT REFERENCES orders(id),
 reason TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(order_id,product_id,movement_type)
);
CREATE INDEX IF NOT EXISTS ix_compat_bike ON compatibility(bike_id,product_id);
CREATE INDEX IF NOT EXISTS ix_products_category ON products(category,id);
CREATE INDEX IF NOT EXISTS ix_movements_product ON inventory_movements(product_id,id);
-- Saldo de abertura é registrado uma vez e sob transação pelo script migração.
-- Regra de conservação: products.stock = SUM(inventory_movements.delta_qty) por product_id.