"""Extensão didática para SQLite da Rota 2. NÃO substitui app/db.py.

Execute da raiz do repositório, somente com banco cujo nome começa por lab_:
  python scripts/lab_db_extension.py init --db data/lab_rota2.db
  python scripts/lab_db_extension.py migrate --db data/lab_rota2.db
  python scripts/lab_db_extension.py adjust --db data/lab_rota2.db --sku R2-FR-001 --quantity 25 --reason inventario-aula
  python scripts/lab_db_extension.py verify --db data/lab_rota2.db
  python scripts/lab_db_extension.py backup --db data/lab_rota2.db

IMPORTANTE: até modificar app/main.py e app/manage.py para registrar eventos na MESMA
transação do estoque, NÃO execute pedidos via API nesse banco após migrate. Caso contrário,
a conciliação detectará corretamente diferenças. Migração NÃO retroage sobre pedidos antigos.
"""
from __future__ import annotations
import argparse
import hashlib
import os
import sqlite3
import sys
from pathlib import Path
# Permite importar app/ quando este arquivo é executado como scripts/lab_db_extension.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import datetime, timezone

MIGRATION_ID = '001_inventory_ledger'


def safe_path(s):
    p = Path(s).expanduser().resolve()
    if not p.name.lower().startswith('lab_') or p.suffix.lower() not in ('.db','.sqlite','.sqlite3'):
        raise SystemExit('SEGURANÇA: use banco lab_*.db, separado de data/motopecas.db')
    p.parent.mkdir(parents=True,exist_ok=True)
    return p


def conn_for(p):
    db=sqlite3.connect(str(p), timeout=15, isolation_level=None)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=15000')
    return db


def baseline(p):
    os.environ['MOTO_DB_PATH'] = str(p)
    from app.db import initialize
    initialize()
    with conn_for(p) as db:
        print('Base pronta:',db.execute('SELECT COUNT(*) FROM products').fetchone()[0],'produtos')


def backup(p):
    target=p.with_name(p.stem+'_backup'+p.suffix)
    if target.exists():
        raise SystemExit('Backup existente: renomeie-o antes de executar novo backup')
    with conn_for(p) as source, sqlite3.connect(target) as target_db:
        source.backup(target_db)
    print('Backup completo:',target, 'sha256:',hashlib.sha256(target.read_bytes()).hexdigest())


def restore(p):
    """Exercício de recuperação em NOVO arquivo lab_..., sem sobrescrever a base."""
    source=p.with_name(p.stem+'_backup'+p.suffix)
    target=p.with_name(p.stem+'_restored'+p.suffix)
    if not source.exists():raise SystemExit('Backup ausente; execute backup primeiro')
    if target.exists():raise SystemExit('Restauração já existe; não sobrescrever')
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dest:
        src.backup(dest)
        status=dest.execute('PRAGMA integrity_check').fetchone()[0]
        dest.execute('PRAGMA foreign_keys=ON')
        fk=dest.execute('PRAGMA foreign_key_check').fetchall()
        products=dest.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    if status!='ok' or fk:raise SystemExit('Falha ao validar restauração: '+status)
    print('RESTORE PASS:',target,'produtos:',products,'FK violadas:',len(fk))


def migrate(p):
    if not p.exists(): raise SystemExit('Use init primeiro')
    with conn_for(p) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            db.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            already=db.execute('SELECT 1 FROM schema_migrations WHERE version=?',(MIGRATION_ID,)).fetchone()
            if already:
                db.execute('COMMIT');print('Migração já aplicada; sem alterações');return
            db.execute("""CREATE TABLE IF NOT EXISTS inventory_movements(
              id INTEGER PRIMARY KEY,
              product_id INTEGER NOT NULL REFERENCES products(id),
              delta_qty INTEGER NOT NULL CHECK(delta_qty <> 0),
              movement_type TEXT NOT NULL CHECK(movement_type IN ('OPENING','SALE','ADJUSTMENT','RETURN')),
              order_id TEXT REFERENCES orders(id),
              reason TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              UNIQUE(order_id, product_id, movement_type)
            )""")
            db.execute('CREATE INDEX IF NOT EXISTS ix_compat_bike ON compatibility(bike_id,product_id)')
            db.execute('CREATE INDEX IF NOT EXISTS ix_products_category ON products(category,id)')
            db.execute('CREATE INDEX IF NOT EXISTS ix_movements_product ON inventory_movements(product_id,id)')
            # Baseline means inventory as it exists NOW; historical sales are not reconstructed.
            db.execute("INSERT INTO inventory_movements(product_id,delta_qty,movement_type,reason) SELECT id,stock,'OPENING','saldo no instante da migração' FROM products WHERE stock <> 0")
            db.execute('INSERT INTO schema_migrations(version) VALUES (?)',(MIGRATION_ID,))
            db.execute('COMMIT')
        except:
            db.execute('ROLLBACK');raise
    print('Migração aplicada. ATENÇÃO: API e CLI devem ser instrumentadas antes de novas transações.')


def adjust(p,sku,quantity,reason):
    if not reason or len(reason.strip())<5: raise SystemExit('Motivo obrigatório (mínimo 5 caracteres)')
    if quantity <0 or quantity >99999:raise SystemExit('Estoque fora de 0..99999')
    with conn_for(p) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            row=db.execute('SELECT id,stock FROM products WHERE sku=?',(sku,)).fetchone()
            if not row: raise ValueError('SKU não encontrado')
            if not db.execute('SELECT 1 FROM schema_migrations WHERE version=?',(MIGRATION_ID,)).fetchone(): raise ValueError('Migração pendente')
            delta=quantity-row['stock']
            if delta:
                db.execute('UPDATE products SET stock=? WHERE id=?',(quantity,row['id']))
                db.execute('INSERT INTO inventory_movements(product_id,delta_qty,movement_type,reason) VALUES (?,?,?,?)',(row['id'],delta,'ADJUSTMENT',reason.strip()))
            db.execute('COMMIT')
        except:
            db.execute('ROLLBACK');raise
    print('SKU:',sku,'de:',row['stock'],'para:',quantity,'delta:',delta)


def verify(p):
    with conn_for(p) as db:
        valid=db.execute('PRAGMA integrity_check').fetchone()[0]
        fk=db.execute('PRAGMA foreign_key_check').fetchall()
        rows=db.execute("""SELECT p.sku,p.stock,COALESCE(SUM(m.delta_qty),0) AS balance
          FROM products p LEFT JOIN inventory_movements m ON m.product_id=p.id
          GROUP BY p.id HAVING p.stock<>COALESCE(SUM(m.delta_qty),0)""").fetchall()
        print('SQLite:',sqlite3.sqlite_version,'integrity:',valid,'FK violations:',len(fk),'ledger discrepancies:',len(rows))
        for row in rows:print(dict(row))
        if valid!='ok' or fk or rows:raise SystemExit(2)
    print('PASS: conciliação e integridade. Este PASS não prova integração com API/CLI.')


def main():
    a=argparse.ArgumentParser(description='Laboratório de evolução SQLite — só banco lab_*.db')
    a.add_argument('action',choices=['init','backup','restore','migrate','adjust','verify'])
    a.add_argument('--db',required=True)
    a.add_argument('--sku')
    a.add_argument('--quantity',type=int)
    a.add_argument('--reason',default='')
    z=a.parse_args();p=safe_path(z.db)
    if z.action=='init':baseline(p)
    elif z.action=='backup':backup(p)
    elif z.action=='restore':restore(p)
    elif z.action=='migrate':migrate(p)
    elif z.action=='verify':verify(p)
    elif z.action=='adjust':
        if z.sku is None or z.quantity is None:a.error('--sku e --quantity são obrigatórios para adjust')
        adjust(p,z.sku,z.quantity,z.reason)

if __name__=='__main__':main()