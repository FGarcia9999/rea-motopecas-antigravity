# REA WP3 — Marco de entrada de ativos de benchmark reservado

**Data:** 16/11/2026. **Natureza:** infraestrutura de reprodutibilidade / preparação de benchmark. **Não existem resultados experimentais T0–T3, suíte privada registrada, aprovação científica ou benchmark independente demonstrado nesta etapa.**

## Encadeamento e motivação

O projeto já dispõe, nos PRs de pesquisa precedentes, de contratos de tratamento e evidências, captura real do REA CLI no exemplo Rota 2, motor de oráculos comportamentais em caixa-preta, teste sintético de isolamento em Docker e transferência de artefatos com hashes. Para que esses controles sirvam a um artigo científico, o avaliador precisa possuir **ativos concretos próprios e não públicos**, imutáveis durante cada experimento, sem conceder acesso ao agente.

Este marco implementa o **contrato inicial de entrada e compromisso criptográfico de conteúdo (SHA-256)**, diferenciando:
- fonte de referência **privada**: hash por arquivo e hash canônico do conjunto, guardados no registro privado;
- oráculos reservados **privados**: validação estrutural e SHA-256;
- política de acesso **privada**: campos obrigatórios, rótulos de responsáveis distintos, contrato de observabilidade, escopo de autorização e status DRAFT;
- relatório público **minimizado**: somente SHA-256, números de arquivos/casos, tamanho total e **negação explícita** de aprovação P1–P4, isolamento e experimento.

## Segurança e integridade

O módulo `research/benchmark/intake.py` exige diretórios externos ao checkout, bloqueia links simbólicos, arquivos inesperados, arquivos muito grandes, sobrescritas e tentativas de registrar políticas como `APPROVED`. Os testes negativos verificam modificação de conteúdo, incompatibilidade entre IDs de aplicação, credenciais/escopos não permitidos por contrato, ausência dos campos da suíte e vazamento de nomes privados.

O `public_fixture.py` **não é benchmark reservado real**: é uma receita pública que produz conteúdo sintético e um token aleatório em armazenamento temporário para verificar que o relatório redigido não os expõe. O mecanismo não inspeciona semanticamente a qualidade dos casos nem assegura que a fonte seja desconhecida de um agente.

## Evidência de engenharia

- Workflow: `.github/workflows/wp3-private-intake-smoke.yml`.
- Testes: `tests/test_research_benchmark_intake.py`.
- Artefatos do CI: apenas resumo público minimizado; não inclui código, oráculos, políticas ou tokens sintéticos.
- Aprovação do CI: confirmar pelo link do GitHub Actions da branch no momento de revisão.

## Situação dos gates

| Controle | Estado após este marco |
|---|---|
| WP3 — formato e hash de fonte/testes avaliador | IMPLEMENTADO / TESTE SINTÉTICO |
| P1 — critérios e contratos formalmente aprovados | PENDENTE |
| P2 — execução real MCP no Antigravity | PENDENTE, apesar de CLI REA demonstrada |
| P3 — agente real sem acesso à referência/oráculos | PENDENTE, apesar do smoke Docker |
| P4 — oráculos independentes válidos de benchmark privado | PENDENTE, apesar dos controles públicos |
| WP4 — piloto planejado de 20 execuções | NÃO INICIADO |

## Encaminhamento prioritário

**Definir a custódia privada dos ativos** (repositório privado separado ou armazenamento institucional controlado) e o responsável avaliador. Somente após autorização de alvo e dos responsáveis, cadastrar a primeira aplicação independente e construir sua suíte de oráculos reservada; repetir o teste de isolamento sob a identidade do agente real antes de permitir qualquer execução T0–T3.

**O manuscrito M1 v0.4 permanece inalterado em suas seções de Resultados**, evitando confundir prontidão técnica com eficácia do método.
