# REA — Decisões abertas para pré-registro e congelamento estatístico (v0.1)

**DRAFT / HOLD.** Documento de decisões a resolver antes do piloto ou do estudo principal, não um pré-registro aprovado. Não antecipar resultados nem recalcular hipóteses conforme sua direção.

## Matriz de decisões

| ID | Decisão a registrar | Orientação já contida no Protocolo v1.2 | Pendente |
|---|---|---|---|
| D01 | Definição completa da unidade experimental | A execução integral é a unidade, não cada teste oculto | Seleção de apps, tarefas/estados, população-alvo |
| D02 | Contraste primário e direção | E[Y(T3)]−E[Y(T1)] | Precisar universo de generalização e escala de Y |
| D03 | Contrastes secundários | T2−T0; efeitos W, I e W×I suplementares | Multiplicidade, intervalos, prioridades e modelo |
| D04 | Randomização | Sessões frescas e ordem randomizada/contrabalanceada | Gerador/seed, bloqueio por aplicação e família do modelo |
| D05 | Falhas, custos e timeouts | Reter todas as execuções; regras precongeladas | Escore em fail/timeout, tentativas e desvios protocolados |
| D06 | Denominadores dos testes | Suíte externa fixa aplicável por execução | Ausentes, inconclusivos, funcionalidades UNAVAILABLE |
| D07 | Qualidade dos oráculos | Referência PASS, mutantes válidos, alternativas corretas | Taxas mínimas/máximas, auditoria e IC, adjudicação |
| D08 | Qualidade de evidência e instrumentação | Separar cobertura, uso de evidência e fidelidade | Regras de deduplicação, traces válidos, limites REA |
| D09 | Economia e recursos | Contar LLM, ferramentas, infraestrutura e intervenção | Moeda, tabela de preços/versões, custo de zero-correct |
| D10 | Modelos e baseline aberto | Versions, parâmetros e reprodutibilidade | Famílias/IDs e justificativa de baseline aberto ou omissão |
| D11 | Análise e precisão | Hierárquico binomial ou bootstrap agrupado pós-diagnóstico do piloto | Critério de escolha, tamanhos e poder do estudo principal |
| D12 | Ética, segurança e divulgação | Fonte/testes ocultos não compartilhados | Licenças, LGPD, retenção, risco de contaminação, divulgação |
| D13 | LLM e ferramentas | W/I ortogonais em T0–T3 | Controle de prompts/Skills/MCP e escopo igual |
| D14 | Protocol deviations | HOLD/REVISE se gate falhar | Política de emendas, ordem de decisões e assinaturas |

## Piloto planejado vs. confirmatório

- **WP4:** 5 execuções previstas em cada tratamento, total 20, exploratórias e independentes quando a infraestrutura permitir. O piloto estima viabilidade, latência, custos, atrito, variação e risco de medição. Não usar a mesma amostra como evidência confirmatória após escolher o método com base nela.
- **WP5:** referência de dimensionamento preliminar 4 apps × 4 tratamentos × 5 repetições × 2 modelos = 160 execuções possíveis. Isso é um **cenário para cálculo de viabilidade**, não compromisso de execução ou poder garantido; justificar n por precisão, dispersão intra-app e custo.
- A análise deve considerar clustering de execuções dentro de aplicativos e modelos, além da correlação dos testes dentro de cada execução. Testes não podem inflar artificialmente n independente.
- O contraste principal mede o **pacote de instrumentação REA/MCP** sob workflow W=1. Não atribuir causalidade a proveniência (RQ5), que é observacional pós-tratamento.

## Checklist de reporte para Empirical Software Engineering

Conforme Baltes et al. (online 3 Nov 2026, DOI https://doi.org/10.1007/s10664-026-10922-3), a equipe deverá declarar, além das estatísticas: papéis dos LLMs, releases/IDs e parâmetros, arquitetura e prompts/Skills, ferramentas e chamadas reais, traces, baselines e benchmarks, validação humana, limites, ameaças à validade e recursos de replicação. Considerar baseline LLM aberto se tecnicamente possível; justificar exceções.

**Antes do pré-registro:** resolver D01–D14 com decisões explícitas de responsável e data; registrar protocolo/versão estatística, aprovação humana e hashes em custodiante independente. Não divulgar decisões internas com credenciais ou detalhes dos testes ocultos no GitHub público.

## Estado atual

Todos os itens acima são **pendências de decisão**, não resultados. Os scripts de prontidão do projeto permanecem em HOLD, e o manuscrito M1 v0.4 não recebeu dados empíricos novos.
