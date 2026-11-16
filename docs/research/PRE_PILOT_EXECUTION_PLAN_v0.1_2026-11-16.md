# REA — Plano executivo pré-piloto v0.1 (16/11/2026)

**Situação: DRAFT / HOLD.** Documento operacional derivado do [Protocolo Experimental v1.2](EXPERIMENTAL_PROTOCOL_v1.2.md), [Diretriz Científica v1.1](RESEARCH_DIRECTIVE_v1.1.md), [Roadmap v2.2](ROADMAP_v2.2.md) e [registro P1–P4](PILOT_P1_P4_READINESS_2026-11-16.md). Não altera esses instrumentos; exige aprovação expressa da equipe para congelamento. **Não há benchmark privado real homologado nem execuções T0–T3 realizadas.**

## 1. Questão causal e desenho preservados

W = workflow estruturado; I = observação REA via ferramentas reais autorizadas. Tratamentos: T0=(W0,I0), T1=(W1,I0), T2=(W0,I1), T3=(W1,I1). Contraste principal: **E[Y(T3)] − E[Y(T1)]**, em que Y é a proporção de testes comportamentais externos e previamente fixados aprovados **por execução completa**. Contraste secundário: T2−T0. Efeitos fatoriais W, I e W×I: suplementares. A intervenção I é um *pacote de observação instrumentada*; não identifica o efeito isolado do protocolo de transporte MCP. Utilização de evidência é medida descritiva pós-tratamento, não mediador causal randomizado.

A unidade independente de análise é a **execução integral**, com sessão, workspace e estado inicial novos. Testes dentro de uma mesma execução são correlacionados. Registrar todas as execuções, incluindo falhas, timeouts, bloqueios e excesso de orçamento, de acordo com uma convenção de escore pré-congelada.

## 2. Sequência e dependências

| Marco | Pacote e papel responsável A DESIGNAR | Entradas e produtos exigidos | Aceite / condição de saída |
|---|---|---|---|
| **M00** | Custódia e autorização — líder científico + administrador do avaliador | Inventário de ferramentas, contas e riscos; autorização do alvo; identidades separadas; política de retenção e redigibilidade | Repositório/armazenamento privado criado por identidade avaliadora, permissões testadas, sem conexão com ferramentas do agente |
| **M01** | Referência independente — custodiante da aplicação | Aplicação nova ou independente, nunca fornecida como fonte ao agente; requisitos e estado inicial; hashes privados | Referência executa em serviço autorizado; fonte/ground truth permanecem privados; escopo observável fixo |
| **M02** | Instrumentação real — operador de Antigravity/MCP | Release rea-agents fixo, catálogo e parâmetros, permissões por tratamento, versões de modelo, browser/CDP, chamadas e traces | Pelo menos captura real, revisada, no cliente e ambiente designados; setup/doctor não contam como execução |
| **M03** | Isolamento efetivo — revisor técnico de segurança | Agente real, todos os conectores e credenciais; probes por FS/rede/GitHub/MCP; canário inacessível | Negativas explícitas verificadas, auditoria de rotas alternativas e documentação de limitações |
| **M04** | Oráculos independentes — avaliador + adjudicador | Suíte privada congelada, referência PASS, mutantes válidos executados, alternativas corretas, regras metamórficas | Métricas e denominadores definidos e revisados; decisões divergentes adjudicadas; nenhum teste oculto no repo público |
| **M05** | Congelamento P1–P4 — líder científico + coautor + avaliador | Nove critérios no-go com limites e responsáveis; T0–T3, prompts, budgets e política de falhas versionados | Aprovação humana **externa ao agente** e registro inviolável com data/versões; qualquer falha implica HOLD |
| **M06** | Piloto exploratório WP4 — operador experimental | Plano de alocação balanceada e randomizada, 5 execuções por tratamento = 20 previstas; ambientes novos | Logs completos e redigidos, sem descarte seletivo; 20 é meta de planejamento, não tamanho de amostra justificado |
| **M07** | Revisão do piloto e congelamento confirmatório — estatístico + equipe | Distribuições de fidelidade, custos, atrito, categorias de erro, variabilidade e parecer de precisão/poder | Decisão GO/REVISE/HOLD, desenho confirmatório e plano estatístico congelados **antes** da amostra principal |

**Caminho crítico:** M00 → M01 → M03/M04; M00 → M02; M02+M03+M04 → M05 → M06 → M07. A priorização não autoriza trabalhar com código ou testes privados sob o mesmo principal dos agentes.

## 3. Nove critérios de não prosseguimento — preencher antes de qualquer piloto

Os nove IDs oficiais continuam: MCP_LIVE_CALL, TRACE_COMPLETENESS, SOURCE_ISOLATION, AUTHORIZATION_EQUIVALENCE, ORACLE_MUTATION_DETECTION, ORACLE_FALSE_REJECTION, MAX_COST, MAX_ATTRITION e HUMAN_INTERVENTIONS. Todos permanecem sem limiar aprovado e sem dono nomeado no arquivo público DRAFT.

**Não adotar limiares numéricos neste plano.** O avaliador deverá apresentar definição operacional, unidade, denominador, custo de erro, limiar e responsável para cada critério, com assinatura e carimbo temporal em registro sob custódia privada. Jamais definir ou mudar thresholds após visualizar resultados.

## 4. Protocolo operacional do piloto — sujeito ao gate

- **Antes de cada execução:** registrar app/task, estado inicial da aplicação, digest dos oráculos no avaliador, tratamento atribuído, ID do modelo e configuração, prompt/Skills/catalogo de ferramentas, seed quando disponível, limites de tempo/tokens/custos e autorização.
- **Durante:** capturar interações, tool calls realmente executadas (identificador, versão, argumentos/resultados redigidos e hashes), timestamps, erros, bloqueios, resets, retries e intervenções humanas; não transferir fonte reservada.
- **Após:** encerrar a identidade/agente e transferir apenas código candidato e metadados por handoff com SHA-256; avaliador verifica pacote e testa em sandbox descartável sem execução automática do ZIP.
- **Avaliação:** executar a suíte privada fixa; computar Y por execução conforme regras previamente assinadas; tratar timeout/falha/correto=0 e ausências sem exclusão seletiva; guardar razões detalhadas em custodiante privado e emitir apenas agregado redigido após liberação.
- **Randomização:** gerar ordem sob responsabilidade independente, balancear 5 por braço, evitar efeitos de ordem, vazamento entre sessões e contaminação de prompts/testes; se uma única aplicação for usada no piloto, não inferir validade entre domínios.
- **Segurança:** credenciais do avaliador nunca montadas em contêineres dos agentes; egress allowlist, nenhum segredo em logs/PRs/artefatos de CI público, perfil de navegador descartável e permissão explícita da aplicação.

## 5. Quadro de recursos e custos — variáveis ainda não orçadas

Por execução: custo = consumo do LLM (entrada/saída + cached quando aplicável) + ferramentas/infraestrutura + tempo de preparação + mão de obra humana + armazenamento/auditoria + retrabalho. Registrar unidade monetária, versão de tabela de preços, uso real, timeout e custo dos casos malsucedidos. Custo/funcionalidade correta exige convenção separada para denominador zero. O orçamento máximo deve ser aprovado antes do piloto.

Amostra principal sugerida no Protocolo v1.2: **4 aplicações × 4 tratamentos × 5 repetições × 2 famílias de modelos = 160 execuções possíveis**, ainda hipotéticas. Revisar com variabilidade/poder após piloto; não afirmar significância antecipadamente. Considerar, quando exequível, baseline de LLM aberto; documentar eventuais impossibilidades.

## 6. Riscos decisivos e medidas

1. **Contaminação:** modelo ter visto código público ou soluções semelhantes; selecionar referência independente, registrar exposição prévia, usar canários controlados e reconhecer opacidade de dados de treinamento.
2. **Instrumentação desigual:** ferramentas concedem privilégios extras, não apenas nova representação; mapear autorização idêntica entre braços e registrar diferenças de observação.
3. **Dependência de fornecedor:** versões de modelo e Antigravity mudam; fixar versões/ID, parâmetros e capturas, registrar datas/limites de reprodução.
4. **Viés dos oráculos:** suite mede equivalência de implementação em vez de comportamento; executar alternativas corretas, mutações válidas e dupla adjudicação.
5. **Pseudorreplicação:** testes aninhados não contam como execuções independentes; estimar contrastes na unidade de execução, com incerteza agrupada.
6. **Vazamento:** Git ignore/CI scanner não inspecionam integralmente histórico/forks/artefatos; usar custódia privada isolada e revisão humana de publicação.
7. **Mudança de escopo:** não alterar M1/Resultados para acompanhar êxitos de infraestrutura; distinguir evidência de viabilidade de fidelidade experimental.

## 7. Aprovações e próximos atos

Os nomes efetivos dos responsáveis, as autorizações do alvo, a custódia, os limiares, os custos e as decisões da equipe estão **por definir**. O primeiro passo operacional é designar custodiante e revisor independentes e escolher a solução privada. Não iniciar M06 sem documentação externa de liberação dos gates P1–P4.

**Estado documental:** Diretriz v1.1, Protocolo v1.2, Roadmap v2.2 e manuscrito M1 v0.4 mantidos, sem resultados novos. Plano e JSON em DRAFT são publicáveis; **fonte e testes reservados, não**.

### Referências de apoio
- Baltes, S. et al. *Guidelines for empirical studies in software engineering involving large language models.* Empirical Software Engineering 32, article 64 (2027), published online 3 Nov 2026. DOI: https://doi.org/10.1007/s10664-026-10922-3 (modelo, versão, prompts, rastros, baselines, avaliação humana, limitações).
- GitHub Docs, *Secure use reference*: https://docs.github.com/en/actions/reference/security/secure-use (workflows e conteúdo não confiável).
