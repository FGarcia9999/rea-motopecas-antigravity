# REA — M02: prova real do protocolo MCP sobre stdio

**Data:** 16/11/2026. **Estatuto:** execução real de ferramentas MCP usando cliente independente e alvo local sintético. **Antigravity/Windows NÃO HOMOLOGADO; P2 científico HOLD; nenhum experimento T0–T3 executado.**

## O que mudou em relação ao CLI

Antes, [WP2 CLI](../../research/WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md) já havia comprovado comandos reais do pacote oficial REA. Agora, em [GitHub Actions run 43968147964 — SUCCESS](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43968147964), um cliente Python distinto conectou-se por stdio ao servidor oficial executado por npx -y rea-agents@6.9.0 mcp.

A sequência **realmente executada** foi: initialize → notifications/initialized → tools/list → tools/call(list_browser_targets) → tools/call(inspect_web_page). A primeira chamada obteve do navegador um ID de alvo real e autorizado; a segunda executou inspeção de página por 1.500 ms. Ambas retornaram Evidence com provedor rea-cdp-browser, operation, evidence_id e normalized_result. Os testes verificam identificadores sem expor valores brutos. Isso é **mais forte que registro ou doctor**, mas **não comprova uso no Antigravity**.

## Contrato e restrições

| Parâmetro | Configuração |
|---|---|
| Pacote | rea-agents@6.9.0, identidade npm consultada no workflow |
| Alvo | Rota 2 fictícia em http://127.0.0.1:8000 |
| CDP | Chrome headless, perfil descartável, http://127.0.0.1:9222 |
| Transporte | MCP JSON-RPC 2.0 stdio, sessão inicializada |
| Família visível | REA_MCP_TOOL_FAMILIES=browser |
| Output schema | REA_MCP_OUTPUT_SCHEMA_PROFILE=off (validação do servidor permanece ativa) |
| Evidência pública | Apenas hashes de catálogo/schema/ID, metadados, versões e status |
| Arquivos privados | Nenhuma referência oculta, segredo, HAR bruto ou oracle real no GitHub |
| Intervenção agente LLM | Não há; o cliente foi automatizado em Python |
| Decisão científica | HOLD: sem Antigravity Windows nem revisão independente |

A família browser restringe a superfície de ferramentas e reduz o catálogo anunciado. Para validade causal, seu conjunto e custo de contexto precisarão ser congelados de forma idêntica em T2 e T3, com autorização comparável nos braços não instrumentados.

## Interpretação rigorosa

- **Comprovado:** o npm release oficial funciona como **servidor MCP real**, com negociação, catálogo e duas ferramentas de observação invocadas em localhost; geração de Evidence real no CDP.
- **Não comprovado:** agente Antigravity/Windows chamar as ferramentas; sua decisão depender do Evidence; referência com fonte inacessível; qualidade de oráculos independentes; superioridade de T3−T1; registro/assinatura humana de P2.
- O navegador foi observado passivamente, não manipulado pela ferramenta; a janela de 1,5 s não atesta eventos anteriores ou posteriores.
- [Artefato minimizado do CI](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43968147964) é sujeito à retenção do GitHub Actions; guardar cópia controlada e seus hashes sob custodiante antes da expiração.

**Próximo passo:** [homologação específica Antigravity](../../research/M02_ANTIGRAVITY_HOMOLOGATION_RUNBOOK.md), sob autorização, conta isolada e revisão externa. O manuscrito M1 v0.4 continua sem resultados experimentais.
