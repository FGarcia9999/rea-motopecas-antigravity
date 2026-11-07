# Rota 2 Motopeças — evolução SQLite REV05 (Opção A)

**Fontes do docente:** slides 86–95 da apresentação REV05 e **Anexo A** do Guia Didático REV05. Projeto didático sem dados pessoais ou pagamentos. **Não é prova de execução do Antigravity/REA/MCP.**

## Estado real e escopo

O legado tinha 4 tabelas (products, compatibility, orders, order_items), pedidos com BEGIN IMMEDIATE e replay idempotente, mas apenas o saldo corrente de estoque. A nova implementação preserva os contratos e acrescenta uma migração **explícita** (001_inventory_ledger): schema_migrations e inventory_movements.

| Módulo | Alteração | Garantia/limite |
|---|---|---|
| app/db.py | Detecta migração, insere movimentos na transação do chamador e reconcilia | Falha fechada para migração incompleta; nunca migra no startup |
| app/main.py | Em pedido novo: saldo, order_items e SALE dentro do mesmo BEGIN IMMEDIATE | Rollback de todos os efeitos; replay não duplica evento |
| app/manage.py | stock com motivo opcional (--reason), ADJUSTMENT na mesma transação | Administração exclusivamente local, sem endpoint HTTP |
| scripts/lab_db_extension.py | init/backup/restore/migrate/adjust/verify do docente | Aceita **somente lab_*.db**; uso operacional expressamente proibido |
| sql/schema_proposto_001.sql | DDL conceitual original do docente | Não executar sozinho no banco operacional |
| tests/test_db_rev05.py | Testes de contrato e regressão | Verificação local/CI, **não** revisão independente por agente |

**Compatibilidade:** se o banco não foi migrado, API e CLI continuam atendendo os contratos legados, sem gerar movimentos. Se a migração foi aplicada, **toda nova venda e ajuste pelas rotas implementadas** gera lançamento atômico no ledger. Alterações SQL manuais não são bloqueadas por esta versão, mas podem ser detectadas pela conciliação.

## Windows — laboratório isolado

Na raiz do clone, com Python 3.11, executar **antes** de qualquer pedido na base de laboratório:

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/lab_db_extension.py init --db data/lab_rota2.db
.\.venv\Scripts\python.exe scripts/lab_db_extension.py backup --db data/lab_rota2.db
.\.venv\Scripts\python.exe scripts/lab_db_extension.py restore --db data/lab_rota2.db
.\.venv\Scripts\python.exe scripts/lab_db_extension.py migrate --db data/lab_rota2.db
.\.venv\Scripts\python.exe scripts/lab_db_extension.py verify --db data/lab_rota2.db
~~~

Na mesma cópia da aplicação, para operações após a migração:

~~~powershell
$env:MOTO_DB_PATH = (Resolve-Path 'data/lab_rota2.db').Path
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# Em outro PowerShell, configurar a mesma variável de ambiente:
$env:MOTO_DB_PATH = (Resolve-Path 'data/lab_rota2.db').Path
.\.venv\Scripts\python.exe -m app.manage stock R2-FR-001 25 --reason "Inventario didatico conferido"
.\.venv\Scripts\python.exe scripts/lab_db_extension.py verify --db data/lab_rota2.db
~~~

O lançamento OPENING representa o estoque **no momento T0 da migração**. Não é reconstituição de vendas anteriores. Não utilizar scripts laboratoriais em data/motopecas.db. A cópia de segurança é realizada por sqlite3.Connection.backup(), não pela cópia direta do arquivo aberto.

## Gates de dados REV05

- **G-DB1:** products.stock = SUM(inventory_movements.delta_qty) por produto, desde T0; divergência bloqueia avanço.
- **G-DB2:** PRAGMA integrity_check='ok', foreign_key_check vazio, CHECK(stock >= 0), CHECK(delta_qty <> 0).
- **G-DB3:** falha na gravação SALE provoca rollback de saldo, pedido e itens; corrida por 1 unidade permite só um pedido.
- **G-DB4:** Idempotency-Key repetida com o mesmo payload retorna pedido anterior sem novo débito/evento; payload diferente gera conflito.
- **G-DB5:** alteração CLI registra ADJUSTMENT com motivo; invalidação ou delta zero não grava movimento espúrio.
- **Revisão independente e aprovação humana:** permanecem separadas de CI; não declarar G6/G7 como PASS sem a evidência correspondente.

O teste TDD **RED** foi reproduzido usando o app/main.py original após migração (sem INSERT de SALE): falhou em 0 == 1. O **GREEN**, depois de instrumentar a transação, passou. Ver [registro local](evidence/DB_REV05_VALIDATION.md). O teste não foi realizado pelo Antigravity.

## Segurança e decisões posteriores

- Nenhuma migração automática no startup, nenhuma base operacional alterada, nenhuma ativação automática de WAL.
- SQLite usa um escritor por vez; WAL só após homologar versão, concorrência, backup e manutenção.
- PostgreSQL não foi implementado: exigir PoC, p95, SQLITE_BUSY, carga real, custos, backup e rollback.
- Reconciliador detecta SQL manual não instrumentado; não garante controle de acesso em nível de SGBD.
- Contratos da API e catálogo fictício de 12 produtos continuam preservados.

Consulte [ADR-001](adr/ADR-001-SQLite-Inventory-Ledger-REV05.md), [matriz DB-REV05](traceability_db_rev05.csv), [originais e hashes](materials/REV05_SOURCES.sha256).

**Fontes:** SQLite Backup API (https://sqlite.org/backup.html), Foreign Keys (https://sqlite.org/foreignkeys.html), WAL (https://sqlite.org/wal.html); OWASP Database Security; NIST SP 800-218.
