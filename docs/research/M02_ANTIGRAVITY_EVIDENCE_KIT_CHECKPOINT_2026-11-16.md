# REA — M02: kit de coleta e integridade de evidências no Antigravity/Windows

**Data:** 16/11/2026 • **Estado:** IMPLEMENTAÇÃO DE INFRAESTRUTURA; **não é um atesto de chamada real pelo Antigravity**. O gate científico P2 e o piloto T0–T3 continuam HOLD.

## Objetivo

O [checkpoint anterior de servidor MCP](M02_REAL_MCP_STDIO_CHECKPOINT_2026-11-16.md) comprovou duas chamadas JSON-RPC MCP executadas por um cliente Python independente em Linux/CI. Ainda falta comprovar que **o cliente Google Antigravity real**, sob a identidade e a configuração do operador, executa REA MCP e utiliza os resultados para uma decisão auditável. Esta entrega não tenta simular o Antigravity nem substitui esse requisito.

## Entregas de implementação

| Componente público | Escopo |
|---|---|
| research/antigravity/session.py | Criação e auditoria de pasta privada externa ao Git, validação de campos/escopo, hash SHA-256 de arquivos de evidência, sumários privados/redigidos |
| research/antigravity/Prepare-M02-Windows.ps1 | Preparo conservador no Windows: coleta de versões locais e, **apenas com opt-in**, inspeção do release REA fixado e dry-run de setup |
| research/antigravity/README.md | Procedimento de laboratório e quatro classes de evidências a fornecer após chamadas verdadeiras no cliente |
| tests/test_research_antigravity_session.py | Negativos: nenhum arquivo, sessão com claims falsos, duplicidade, symlink, tamanho excessivo, URL não autorizada, release latest, pasta dentro do Git, sobrescrita |
| .github/workflows/m02-windows-private-kit.yml | Teste nativo Windows do **empacotador**, sem invocar Antigravity nem iniciar piloto; nenhum material privado carregado como artefato |

## Resultados permitidos e não permitidos

- Um relatório de sessão criado sem arquivos retorna INCOMPLETE_PRIVATE_RECORD, mesmo se a pasta privada existir.
- Quatro arquivos presentes, mesmo acompanhados de declarações positivas do operador, retornam no máximo FILES_PRESENT_AWAIT_INDEPENDENT_AUTHENTICATION. A integridade dos bytes **não autentica o produto que os produziu**, nem prova que o agente usou a observação.
- O programa recusa incluir referência/oráculos reais e não lê caminhos fora dos nomes de evidência explicitamente permitidos; grava resultados na pasta privada.
- Nenhum teste no GitHub poderá marcar antigravity_client_real_tool_use_independently_verified=true ou pilot_authorized=true. Esse reconhecimento requer revisão independente dos registros do cliente original, com permissão e proveniência.
- **Nunca publicar** screenshots sem revisão, logs brutos de MCP, tráfego, credenciais, ground truth ou materiais de avaliação em branch GitHub.

## Critério científico ainda pendente

1. Operador de laboratório e revisor independente designados.
2. Cliente específico (Antigravity 2.0, IDE ou CLI) e release registrado e autorizado.
3. Catálogo MCP real e input/output de tools/call list_browser_targets e inspect_web_page capturados no próprio cliente.
4. Cadeia evidence_id → requisito/decisão documentada e adversarialmente verificada.
5. Versões, custo de contexto, limites, permissões T0–T3 e no-go P2 congelados.
6. Atesto externo sob custódia privada, sem conferência pelo agente implementador.

## Próxima decisão

O teste local do kit torna a execução **pelo operador no Windows** mais reprodutível, mas não remove a pendência de acesso ao computador onde o Antigravity real está instalado. Até que a sessão exista, a equipe poderá continuar no M01 com desenho de aplicação independente sob custódia privada, sem expor o código a agentes.

**Não acrescentar estes resultados demonstrativos à seção Results do M1 v0.4.**

Fonte de configuração do cliente: [Google — Antigravity MCP](https://antigravity.google/docs/mcp); [REA — documentação oficial](https://rea.tools/get-started/).
