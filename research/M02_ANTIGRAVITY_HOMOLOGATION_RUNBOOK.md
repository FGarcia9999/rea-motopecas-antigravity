# REA M02 — roteiro de homologação Windows / Antigravity

**PROPOSTO, NÃO EXECUTADO NO ANTIGRAVITY.** O teste Linux com cliente MCP Python está comprovado, mas não representa uma sessão de agente Antigravity.

## 1. Precondições
Usar apenas a Rota 2 demonstrativa em http://127.0.0.1:8000, com SQLite descartável, Chrome/Edge em perfil temporário, CDP loopback e conta de laboratório autorizada. Não conceder a essa identidade acesso a repositório privado, código de referência desconhecido, suíte oculta ou credenciais institucionais. Nomear operador e revisor independente no registro privado.

## 2. Verificar e aprovar configuração
No PowerShell, com Node suportado (22.23.4+, 24.22.1+ ou 26.12.1+):

~~~powershell
node --version
npm --version
$REA_VERSION = '6.9.0'
npx.cmd -y "rea-agents@$REA_VERSION" --version
npx.cmd -y "rea-agents@$REA_VERSION" setup --client antigravity --dry-run
~~~

**Somente após aprovação humana** das mudanças propostas e com backup das configurações:

~~~powershell
# npx.cmd -y "rea-agents@$REA_VERSION" setup --client antigravity
# Reinicie Antigravity. Depois, confira ferramentas no cliente real e rode:
# npx.cmd -y "rea-agents@$REA_VERSION" doctor --client antigravity --json
~~~

Dry-run, setup, doctor e ferramenta visível não provam execução real. Não usar @latest em protocolo congelado nem flags de desenvolvimento não suportadas.

## 3. Restrições da sessão
As variáveis devem estar no ambiente do PROCESSO QUE INICIA O SERVIDOR MCP, não apenas em um PowerShell isolado:

~~~powershell
$env:REA_BROWSER_OBSERVE_ENABLED = 'true'
$env:REA_BROWSER_CDP_ENDPOINTS_JSON = '["http://127.0.0.1:9222"]'
$env:REA_BROWSER_ALLOWED_ORIGINS_JSON = '["http://127.0.0.1:8000"]'
$env:REA_MCP_TOOL_FAMILIES = 'browser'
$env:REA_MCP_OUTPUT_SCHEMA_PROFILE = 'off'
~~~

Verificar que a configuração registrada do Antigravity herda os valores; modificar o cliente somente após aprovação e reiniciá-lo. A origem autorizada e o catálogo precisam ser idênticos aos do controle instrumental planejado. Não copiar material do avaliador.

## 4. Teste observado pelo Antigravity
Com o navegador de laboratório já aberto em Rota 2, solicitar ao agente:

> Execute a ferramenta MCP rea list_browser_targets exclusivamente na página local autorizada. Use o target_id recebido para chamar inspect_web_page por um intervalo delimitado. Descreva um comportamento visível da filtragem por categoria fundamentado no Evidence retornado; não substitua a chamada por resultados CLI, dados de fonte, navegador de terceiros ou suposições.

O prefixo exibido na UI pode variar: usar o nome EFETIVO da ferramenta. Guardar, **em espaço privado**, prova de (a) cliente Antigravity e sua versão, (b) entrada da chamada e resposta real, (c) IDs e SHA-256 dos Evidence, (d) catálogo e schema digest, (e) permissões/target, (f) decisão baseada na evidência, e (g) falhas e limitações. Publicar somente relatório minimizado aprovado pela equipe.

## 5. Semântica de aceite

| Nível | Comprovação | Classificação |
|---|---|---|
| INSTALLED | Pacote existe | Não é MCP |
| CONFIGURED | Setup/doctor concluído | Não é tool call |
| VISIBLE | Ferramenta anunciada pelo Antigravity | Não garante execução |
| EXECUTED | Request/response de ferramenta sob Antigravity | Evidência técnica P2 a revisar |
| DECISION_USEFUL | Evidência vinculada a requisito ou decisão auditável | Requer adjudicação independente |

**P2 científico continua HOLD até** atribuir operadores, congelar versões/catálogo, comparar permissões T0–T3, medir custos e auditar autenticamente as chamadas e sua utilização. Não anunciar piloto.

Fontes: https://github.com/morluto/rea/blob/main/docs/getting-started/installation.md ; https://github.com/morluto/rea/blob/main/docs/reference/mcp-contracts.md ; https://github.com/morluto/rea/blob/main/docs/guides/web/browser-observation.md
