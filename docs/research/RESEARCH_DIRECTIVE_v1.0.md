# Diretriz de desenvolvimento e pesquisa REA — v1.0 (11/11/2026)

**Estado: draft para aprovação formal do grupo de pesquisa.** A presente diretriz **não** autoriza execução em alvos externos, abertura de portas, publicação de dados, merge na main, alteração de bancos operacionais ou submissão científica. Baseada nas revisões do Protocolo Experimental REA v1.0, Manuscrito M1 v0.2 e Roadmap v2.0 fornecidos em 11/11/2026; mudanças consolidadas em [Protocol v1.1](EXPERIMENTAL_PROTOCOL_v1.1.md) e [Decision Register](DECISION_REGISTER_2026-11-11.md).

## Contribuição científica (não é resultado)

Problema: estimar o valor incremental de observação instrumentada REA CLI/MCP para reconstrução funcional de aplicações web com código-fonte de referência oculto. O objeto **não é** provar que uma loja foi criada autonomamente nem que o REA oficial orquestra o SDLC.

- **W** = workflow estruturado com regras, Skills, TDD, gates e aprovação.
- **I** = instrumentação REA CLI/MCP/CDP autorizada, com prova de `tool call` real.
- **T0** = agente genérico + browser; **T1** = W sem I (Opção A); **T2** = I sem W; **T3** = W + I (Opção C).
- **Estimando confirmatório primário** = média run-level Y(T3) − Y(T1) na proporção de testes comportamentais externos aprovados; **secundário** = T2 − T0. Efeitos W, I e W×I são complementares, com escala, intervalos de confiança e correção de multiplicidade pré-definidos.
- **RQ5 sobre proveniência**: somente descritiva/associacional; atribuir causalidade à proveniência exigiria ablação randomizada específica além dos fatores W e I.

## Directives de implementação

1. **Isolamento real**: referência, ground truth e testes ocultos não acessíveis aos agentes. Aplicar controles por filesystem, rede e credenciais; prompts isolados não bastam. O repositório público Rota 2 é apenas demonstrador/piloto e não constitui benchmark confirmatório inédito.
2. **Tratamento informacional justo**: todas as condições dispõem do mesmo alvo e superfície autorizada. Ferramentas podem fornecer **representações diferentes** do comportamento; registrar quando houver informação privilegiada adicional, sem mascarar o fator instrumental.
3. **Congelamento**: versões e hashes de código, rea-agents, servidor MCP, catálogo de ferramentas, SO, Node/Python, browser/CDP, LLM, prompts, Skills, permissões, orçamento e critérios de parada. Doctor/setup **não** comprovam chamadas executadas.
4. **Proveniência**: registro de evidence_id, origem, hora, instrumento, versão, argumentos/resultado, hash, estado OBSERVED/INFERRED/UNKNOWN/UNAVAILABLE, requisito, oracle_id, teste, commit, gate, revisão independente e decisão humana. Distinguir evidência coletada de evidência que realmente alterou decisão.
5. **Oráculos**: testes externos elaborados por avaliador separado, validados contra referência. Metaavaliar com mutantes válidos e executados, versões alternativas funcionalmente corretas, propriedades metamórficas e anotação dupla de amostra estratificada. Proibir que testes ocultos ou ground truth sejam publicados antecipadamente.
6. **Métrica e amostragem**: a unidade experimental primária é uma reconstrução completa, não cada teste isolado. Guardar toda falha, timeout, intervenção, comando bloqueado e custo no denominador conforme política pré-congelada; ajustar o cenário de 20 pilotos / 160 confirmatórios após diagnóstico e planejamento de precisão/poder.
7. **Gates**: não declarar superioridade, equivalência global ou revisão independente apenas por pytest/CI. Separar validade funcional, origem, segurança, revisão de outra sessão/agente e aprovação humana.
8. **Segurança/ética**: somente alvos próprios ou expressamente autorizados, CDP em loopback/perfil descartável, sem PII/segredos/HAR bruto público, allowlist de rede e least privilege.
9. **REA vs ASF**: preservar perguntas, benchmarks e dados próprios para cada estudo; qualquer método reutilizado deve ser explicitado na redação científica.

## Governança por pacotes

| WP | Produto de saída | Status inicial |
|---|---|---|
| WP1 | Definições, contratos de ground truth e observabilidade, protocolo assinado | DRAFT |
| WP2 | Tratamentos T0–T3 versionados, autenticação, tools reais, freeze de recursos | NOT VERIFIED |
| WP3 | Aplicações source-hidden e oráculos validados | NOT IMPLEMENTED |
| WP4 | 20 execuções de piloto com rastros auditáveis | NOT EXECUTED |
| WP5 | Estudo confirmatório e análise estatística congelada | NOT STARTED |
| WP6 | Manuscrito, suplemento, DOI, declarações e submissão | NOT READY |

**Go/no-go**: antes do primeiro piloto, o grupo deve escolher métricas e limiares objetivos para viabilidade de MCP, isolamento, informação/autorizações, detecção por oráculo, falsas rejeições, custos e attrition. Falha → **HOLD/REVISE** documentado; é proibido escolher limiares depois de ver resultados.

**Controle de mudanças**: diretivas via PR de pesquisa e revisão humana. `main` e PRs #1/#2 não devem ser integrados por automatismo. Estas políticas não são execução experimental.
