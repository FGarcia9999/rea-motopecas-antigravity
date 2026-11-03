---
name: rea-verify
description: Executa revisão independente de comportamento, segurança, teste e evidências da loja REA, proibindo autoaprovação e reportando PASS, FAIL ou NOT VERIFIED.
---

# Auditor independente REA

## Pré-condição

Executar como **agente ou conversa distinta** do implementador, com acesso somente de leitura quando possível. Não aceitar relato do implementador como prova de qualidade. Não alterar código nem `gate-report.json` durante a auditoria.

## Roteiro

1. Ler critérios originais e hipóteses (`docs/discovery.md`, `docs/traceability.csv`, `docs/threat-model.md`).
2. Calcular hashes próprios e comparar com `docs/evidence/gate-report.json` **após** execução local do gate, se disponível.
3. Executar `python -m pytest -q tests`, verificar que os casos importantes não usam fixture que contorne as regras.
4. Provar com testes independentes: SQLi, XSS, alteração de preço pelo cliente, falta de estoque, duas requisições idênticas e reenvio com payload diferente.
5. Fazer smoke test responsivo e acessibilidade no browser **se ferramenta disponível**; marcar NOT VERIFIED se não puder abrir.
6. Verificar ausência de dados reais, segredos, tracking e dependências sem licença; executar `pip-audit` quando disponível.
7. Produzir `docs/evidence/independent-review.md` com veredito por gate, evidência concreta, falhas e recomendações. Não criar PASS global se qualquer gate crítico estiver pendente.
8. Entregar ao responsável humano a recomendação de release. **Não publicar nem alterar visibilidade de repo.**

## Decisão

- `PASS` se requisito observado, teste passa e evidência é reproduzível.
- `FAIL_CORRECTABLE` para defeito que retorna ao implementador.
- `NOT VERIFIED` para instrumento indisponível, sem evidência ou avaliação pendente.
- `NEEDS_HUMAN / FAIL_CLOSED` para segurança não autorizada, segredos ou publicação.
