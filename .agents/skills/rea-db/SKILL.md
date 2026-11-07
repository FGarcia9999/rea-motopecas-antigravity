---
name: rea-db
description: Evolução audível e incremental da persistência SQLite na Opção A, com migrações opt-in, TDD, reconciliação e gates de dados.
---

# Skill própria REV05 — banco de dados da Rota 2

1. Ler AGENTS.md, .agents/rules/rea.md, docs/DB_REV05_IMPLEMENTATION.md e ADR-001; nunca executar DDL em banco não autorizado.
2. Inventariar esquema atual e classificar OBSERVADO / INFERIDO / NÃO VERIFICADO. Não inferir dados de terceiros.
3. Elaborar DER, invariantes G-DB1 a G-DB5 e plano de migração, backup/restore/rollback antes de mudar o esquema.
4. Usar **somente lab_*.db** na atividade; não migrar data/motopecas.db, não habilitar WAL automaticamente, não instalar servidor externo.
5. Demonstrar teste RED real com log; então a menor implementação GREEN. API e CLI devem lançar movimentos com o UPDATE na mesma transação.
6. Testar replay idempotente, concorrência, limites, falhas de inserção e conciliação; executar pytest e scripts/gate.py.
7. Solicitar auditoria em sessão independente e aprovação humana. CI verde não substitui a decisão de G6/G7.
8. Nunca comitar arquivos .db, dados privados, dumps, credenciais ou resultados não verificados.
