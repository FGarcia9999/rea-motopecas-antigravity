"""Gestão de estoque e pedidos no terminal (sem credenciais administrativas via HTTP)."""
import argparse
from .db import connect, initialize


def main():
    parser = argparse.ArgumentParser(description="Admin local - Rota 2 DEMO")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("orders", help="Listar pedidos demonstrativos")
    stock = subs.add_parser("stock", help="Atualizar estoque por SKU")
    stock.add_argument("sku")
    stock.add_argument("quantity", type=int)
    args = parser.parse_args()
    initialize()
    with connect() as db:
        if args.command == "orders":
            for row in db.execute("SELECT id, total_cents, status, created_at FROM orders ORDER BY created_at DESC"):
                print(dict(row))
        elif args.command == "stock":
            if not (0 <= args.quantity <= 99999):
                parser.error("Quantidade inválida (0-99999)")
            cursor = db.execute("UPDATE products SET stock=? WHERE sku=?", (args.quantity, args.sku))
            if not cursor.rowcount:
                parser.error("SKU não encontrado")
            print(f"{args.sku}: estoque atualizado para {args.quantity}")

if __name__ == "__main__":
    main()
