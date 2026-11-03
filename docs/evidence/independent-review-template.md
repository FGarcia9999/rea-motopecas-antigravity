# Parecer de validação semântica independente — TEMPLATE

**STATUS: NOT EXECUTED.** Este arquivo é um formulário para futura execução, **não** um atestado de revisão já realizada.

- Commit SHA auditado: PENDENTE
- Agente revisor: PENDENTE
- Modelo/versão do LLM: PENDENTE
- Data UTC / ambiente: PENDENTE
- Gate G1 — escopo/identidade: NOT VERIFIED
- Gate G2 — descoberta e fonte: NOT VERIFIED
- Gate G3 — requisitos e rastreabilidade: NOT VERIFIED
- Gate G4 — testes adversariais independentes: NOT VERIFIED
- Gate G5 — segurança e privacidade: NOT VERIFIED
- Gate G6 — evidência/proveniência/hash: NOT VERIFIED
- Gate G7 — entrega/autorização: NOT VERIFIED

## Procedimento mínimo

1. Rodar `python scripts/gate.py` em ambiente limpo.
2. Examinar a diferença entre requisitos, código, testes e execução real.
3. Escrever casos adversariais **independentes** dos do agente construtor.
4. Auditar artefatos, dependências, assets e modelo de ameaças.
5. Registrar achados com severidade, arquivo/linha, caso reproduzível e recomendação.
6. Solicitar decisão humana para publicação e gates de risco.

**Proibição:** não converter este template em `PASS` sem evidências concretas e sem outra conversa/agente executor.
