---
name: rea-instrument
description: Prepara e verifica de forma controlada a instrumentação do REA oficial via CLI ou MCP em alvo local autorizado, sem confundir setup, doctor e chamada executada.
---

# Instrumentação didática — Opção B

**Esta é uma Skill PRÓPRIA do projeto Rota 2, não a skill oficial instalada por rea-agents.** Não executa o REA por si; requer autorização, runtime compatível, instalação/configuração real e tools disponíveis.

1. Ler `.agents/rules/rea.md`, `docs/labs/REA_AB_C_REV04.md`, o escopo e a documentação do release homologado.
2. Registrar versão exata do `rea-agents`, Node/npm, client e commit; não selecionar `@latest` sem decisão de homologação.
3. Apresentar plano `setup --client antigravity --dry-run` para aprovação humana. Não aplicar modificações globais sem autorização.
4. Distinguir: (a) package instalado, (b) doctor/configuração saudável, (c) tool visível no Antigravity, (d) chamada real com parâmetros/saída, (e) utilidade demonstrada.
5. Restringir CDP ao `127.0.0.1:9222` em perfil descartável e alvo próprio `127.0.0.1:8000`. Validar regras de observação/allowlist da versão utilizada; não navegar em perfil com credenciais.
6. Experimentar RF-03 em `category=Freios`, não `capacetes`; verificar HTTP 200 **e retorno não vazio** quando o catálogo local estiver saudável.
7. Gerar registro segundo `docs/evidence/rea-observation-template.md`, com comando, tool, versão, hora, target, status HTTP, evidência original, hash e limites. Nunca falsificar captura.
8. Marcar `NOT VERIFIED` se alguma tool não estiver disponível; não substituir evidência de REA por output de browser nativo sem declarar diferença.
