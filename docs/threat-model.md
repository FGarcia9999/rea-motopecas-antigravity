# Modelo de ameaças / risco residual — MVP didático

| Ativo | Ameaça | Medida presente | Risco residual |
|---|---|---|---|
| Pedidos e estoque | Concorrência / venda além do estoque | `BEGIN IMMEDIATE`, `UPDATE ... stock>=qty`, transação e rollback | Teste de estresse concorrente pendente |
| API de catálogo | SQL injection | Parâmetros vinculados; testes com payloads | Revisão SAST externa pendente |
| Página e JavaScript | XSS / recursos externos | `textContent` para dados, CSP `script-src 'self'`, sem scripts externos | Teste DAST e browser automatizado pendentes |
| Valores de pedido | Preço adulterado no cliente | API ignora preço informado, calcula total do catálogo | Catálogo demo, sem tributos/frete |
| API de pedido | Spam / automação maliciosa | Tamanho/quantidade limitada, idempotência | **Sem rate limiting**; não expor à internet |
| Dados pessoais | Uso indevido de dados do cliente | Sem captura de PII, CPF, e-mail ou cartão | Logs de infraestrutura precisam ser avaliados antes do deploy |
| Administração | Acesso indevido ao inventário | Gestão apenas por CLI local; sem endpoint admin público | Operador do host deve proteger acesso aos arquivos |
| Banco | Perda de persistência | SQLite local e transações | Sem backup/HA; não é arquitetura de produção |
| Agente LLM/MCP | Prompt injection e exfiltração | Skills com guardrails e ferramenta de leitura limitada | Requer políticas reais de MCP no Antigravity |
| Software de terceiros | Dependência vulnerável | CI inclui `pip-audit` | Auditoria depende da resolução de versões e internet |
| Reutilização indevida | Marca/autorais/compatibilidade falsa | Identidade e SVG originais; dados sintéticos; aviso | Exige revisão humana antes de disponibilização comercial |

**Critérios de liberação para uso real (não satisfeitos):** identidade comercial, homologação de compatibilidade, banco operacional/backup, autenticação, autorização, LGPD e base legal, HTTPS e headers de borda, rate limiting, antifraude, integração com PSP tokenizado, cálculo de frete, tributos, política de troca, CDC e conformidade consumerista.

Referência: https://asvs.owasp.org/ (OWASP ASVS 5.0).
