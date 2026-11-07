# ADR-001 — Livro-razão incremental em SQLite (REV05)

**Status:** implementado em branch de revisão; **não implantado no banco operacional**.
**Origem:** Rota 2 Motopeças, apresentação REV05 (86–95) e Guia Didático (Anexo A).

## Contexto

O banco já possui orders, order_items e stock transacional, porém saldo não é explicado por eventos de ajuste/venda. Não há evidências mensuradas para justificar substituir o SQLite por PostgreSQL agora.

## Decisão

Evoluir o esquema **aditivamente**, por migração explícita 001_inventory_ledger: schema_migrations e inventory_movements. Inserir OPENING para saldos existentes no marco T0, sem alegar retroatividade. Quando migrado, API/CLI gravam SALE/ADJUSTMENT na **mesma transação** da alteração; em esquema parcial, operações falham fechadas. Bancos legados sem migração mantêm a operação original.

## Alternativas

| Escolha | Benefício | Custo/limite |
|---|---|---|
| Somente saldo atual | Simplicidade | Nenhuma trilha de alteração |
| Ledger aditivo SQLite (escolhida) | Reconciliação e poucas alterações aos contratos | Um escritor, migração coordenada com código |
| PostgreSQL imediato | Papéis/concorrência centralizada | Infraestrutura e TCO sem necessidade comprovada |

## Verificação e limites

Testes para replay idempotente, transações, rollback por trigger de falha, CLI, validação de motivo, backup/restauração, conciliação e 2 pedidos simultâneos. Migração operacional e aprovação humana não foram realizadas. Nenhum endpoint administrativo HTTP ou mecanismo de pagamento foi criado.

Critérios G-DB1 a G-DB5 detalhados em [DB REV05](../DB_REV05_IMPLEMENTATION.md). A versão embarcada do SQLite deve ser verificada antes de considerar WAL.
