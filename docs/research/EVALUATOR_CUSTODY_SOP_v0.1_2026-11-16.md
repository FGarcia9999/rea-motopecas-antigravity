# REA — SOP v0.1: custódia independente de referência e oráculos

**Status: PROCEDIMENTO PROPOSTO / NÃO EXECUTADO SOBRE DADOS REAIS.** Este documento é público; nenhum local privado, conta, URL secreta ou nome de arquivo reservado deve ser acrescentado a ele.

## 1. Zonas de confiança

| Zona | Identidade | Pode acessar | Não deve acessar |
|---|---|---|---|
| PÚBLICO | GitHub do projeto REA | Código metodológico, estruturas JSON, sintéticos, relatório agregado revisado | Requisitos ocultos, fontes/fixtures reais, tokens e logs brutos |
| AGENTE | Conta/container de execução T0–T3 | Aplicação de referência em interface **autorizada** e próprio workspace, ferramentas por tratamento | Repositório privado, credenciais avaliadoras, testes ocultos, fonte |
| CUSTODIANTE | Conta segregada da fonte de referência | Fonte, autorização, deploy controlado, hashes privados | Agente e ferramentas de implementação |
| AVALIADOR | Conta segregada de oráculos e revisão | Suíte oculta, ambiente de avaliação, manifestos privados e relatórios de casos | Contexto do agente implementador |
| AUDITOR | Revisão independente autorizada | Provas mínimas de acesso/negação, hashes e atas de decisões | Acesso desnecessário a credenciais de produção |

Um repositório privado associado à **mesma conta cujo token/connector GitHub é disponibilizado ao agente** não assegura isolamento. Exigir identidades e tokens segregados e verificar permissões efetivas de conectores, MCP, shell, contas e rede; credenciais não devem ser disponibilizadas a workflows do repositório público.

## 2. Sequência de provisionamento sob responsabilidade humana

1. Formalizar autorização, aplicação, finalidade, responsáveis por referência, avaliador e custodiante de dados.
2. Escolher cofre institucional/servidor isolado ou repositório **privado sob principal segregado**, com 2FA, menor privilégio, trilha de acesso, backup/retention e política de exclusão.
3. Criar a fonte independente e seu estado inicial privado; gerar identificador e manifesto SHA-256 privado, com processo de assinatura/atesto externo ao agente.
4. Elaborar ground truth e suítes ocultas por avaliadores independentes; testar a referência antes de qualquer agente executar; precongelar valores e critérios.
5. Implantar só o endpoint funcional autorizado; não expor /admin, APIs internas do avaliador, mounts privados, credenciais, Docker socket ou ferramentas de execução de testes.
6. Fazer sondas adversariais com a **identidade do agente real**, testando filesystem, rede, endpoints alternativos, MCP, GitHub, navegador, variáveis e credenciais. Negativas explícitas `DENIED` valem para escopos específicos; `NOT_FOUND` sozinho não prova isolamento.
7. Após execução, operador confiável encerra o agente e entrega artefatos via `research/handoff/bundle.py`; validação do hash **não executa** o código. Avaliação roda em sandbox descartável com egress controlado, CPU/memória/tempo fixos.
8. Auditor independente confirma compatibilidade do alvo, thresholds, variáveis, orçamento, assinatura e revisão de oráculos antes de autorizar piloto.
9. Divulgar apenas metadados aprovados. Hash SHA-256 de ativos secretos pode permitir correlação com arquivos já conhecidos; publicar digests individuais **somente após decisão de divulgação da equipe**.

## 3. Materiais privados necessários

- Pacote de autorização e propriedade/licença de referência.
- Fonte da referência, snapshot de dados sintéticos e manifesto assinado.
- Ground truth por comportamento, com classe DIRECT/INDIRECT/INSTRUMENT_ASSISTED/UNAVAILABLE.
- Suítes ocultas versionadas e resultados de referência PASS, mutantes válidos e alternativas corretas.
- Matriz de permissões T0–T3 e ambientes isolados por execução.
- Atesto externo da liberação ou recusa do piloto e registros de divergências/adjudicação.

**Não usar CI público para executar suíte oculta.** Mesmo artefatos não versionados podem persistir em logs de workflow, cache ou uploads acidentais. Nunca criar PR público a partir de branch privada que contenha arquivos ocultos.

## 4. Política de incidentes e vazamentos

Se um segredo for encontrado no GitHub público, parar publicação, **revogar/rotacionar credenciais** quando aplicável e comunicar custodiante e equipe de segurança. Apenas apagar o arquivo na última revisão não remove necessariamente o histórico, clones, forks ou referências em PRs. Procedimentos de saneamento devem considerar as instruções do GitHub e eventual suporte da plataforma; não reescrever histórico em massa sem avaliação dos efeitos nos PRs e colaboradores.

Referência: GitHub Docs — https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

## 5. Limite do SOP

O controle de acesso só está **comprovado** após auditoria por principal independente. O scanner atual do repositório e o smoke de contêineres são ferramentas auxiliares; nenhum deles autoriza M06 nem indica que houve execução no Antigravity real.

O responsável pela custódia e o revisor devem registrar em ambiente privado o aceite do SOP, escopo e plano de resposta; nenhum nome/assinatura é presumido neste documento público.
