"""Gestão de estoque e pedidos no terminal (sem credenciais administrativas via HTTP)."""
import argparse
from .db import connect, initialize, inventory_ledger_enabled, append_inventory_movement


def main():
    parser = argparse.ArgumentParser(description="Admin local - Rota 2 DEMO")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("orders", help="Listar pedidos demonstrativos")
    stock = subs.add_parser("stock", help="Atualizar estoque por SKU")
    stock.add_argument("sku")
    stock.add_argument("quantity", type=int)
    stock.add_argument("--reason", default="ajuste administrativo local", help="Motivo auditável do ajuste")
    args = parser.parse_args()
    initialize()
    with connect() as db:
        if args.command == "orders":
            for row in db.execute("SELECT id, total_cents, status, created_at FROM orders ORDER BY created_at DESC"):
                print(dict(row))
        elif args.command == "stock":
            if not (0 <= args.quantity <= 99999):
                parser.error("Quantidade inválida (0-99999)")
            if len(args.reason.strip()) < 5:
                parser.error("Motivo do ajuste deve ter pelo menos cinco caracteres")
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute("SELECT id,stock FROM products WHERE sku=?", (args.sku,)).fetchone()
                if row is None:
                    parser.error("SKU não encontrado")
                ledger = inventory_ledger_enabled(db)
                delta = args.quantity - row["stock"]
                if delta:
                    updated = db.execute("UPDATE products SET stock=? WHERE id=?", (args.quantity, row["id"]))
                    if updated.rowcount != 1:
                        raise RuntimeError("Atualização inesperada de estoque")
                    if ledger:
                        append_inventory_movement(
                            db, product_id=row["id"], delta_qty=delta,
                            movement_type="ADJUSTMENT", reason=args.reason,
                        )
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise
            print(f"{args.sku}: estoque atualizado para {args.quantity} (delta {delta})")

if __name__ == "__main__":
    main()
