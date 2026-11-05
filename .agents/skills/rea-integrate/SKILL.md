---
name: rea-integrate
description: Integra uma evidência real do REA oficial ao workflow de engenharia A, mediante decisão humana, requisito, TDD, revisão independente e gate controlado.
---

# Integração didática — Opção C

**Pré-condição:** domínio demonstrado da Opção A e pelo menos uma evidência real, autorizada e útil da Opção B. Não executar C por ritual quando a instrumentação não muda decisão de engenharia.

1. Ler `AGENTS.md`, `.agents/rules/rea.md`, `docs/labs/REA_AB_C_REV04.md` e `docs/traceability.csv`.
2. Pedir registro B autêntico com origem, versão da ferramenta, data, alvo, log, hash, limitações e estado epistemológico. Recusar `EV-B-001` como evidência se ainda for apenas exemplo.
3. Documentar qual incerteza A não resolveu, qual tool B esclareceu e qual requisito/critério foi efetivamente alterado; submeter a decisão humana.
4. Em branch isolada: requisito RF-03 → teste RED com log → menor implementação GREEN → refactor → `python scripts/gate.py` e diff.
5. Encaminhar a uma conversa/agente de revisão independente, sem acesso ao histórico de justificativas do implementador. Receber PASS/FAIL/NOT VERIFIED por gate.
6. Não alterar logs de execução anteriores, não declarar equivalência global, não acessar backend de terceiros, não publicar automaticamente.
7. Entregar cadeia rastreável: `evidence_id → requirement_id → test_id → commit_sha → CI_run → independent_review → human_decision`. Preencher pendências como `NOT VERIFIED`.
