---
name: rea-build
description: Implementa requisitos da loja web reconstruída por REA com Python FastAPI, JavaScript, TDD, segurança por padrão, diff pequeno e gates executáveis.
---

# Agente de engenharia REA

1. Ler `.agents/rules/rea.md` e os requisitos que deseja implementar em `docs/traceability.csv`.
2. Selecionar **um requisito** e explicitar o critério de aceite.
3. **TDD RED**: criar teste reproduzindo comportamento faltante e executá-lo para observar falha esperada.
4. **TDD GREEN**: implementar menor alteração que satisfaz o teste. Garantir que dados de preço são calculados no servidor.
5. **REFACTOR**: manter contrato e remover duplicações. Não importar assets da loja de referência.
6. Rodar `python scripts/gate.py`, revisar o relatório, atualizar o status da matriz conforme evidência real.
7. Separar PR/commit por mudança; nunca publicar automaticamente nem alterar configurações do repositório sem revisão humana.

Para checkout: testar stock >= quantity, rollback completo e idempotência. Para front-end: texto da API com `textContent`, CSP, responsividade, controle de teclado e estado vazio. Para catálogo real: exigir aprovação e fichas técnicas.

**Falhas:** compilação/testes incorretos -> REWORK; exigência fora do escopo -> UNSUPPORTED_CAPABILITY; ação administrativa, credenciais ou deploy -> NEEDS_HUMAN / FAIL_CLOSED.
