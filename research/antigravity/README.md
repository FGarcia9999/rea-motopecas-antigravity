# REA M02 — kit de evidências Antigravity reais, sob custódia privada

**Estado:** preparação e validação de integridade; não é o cliente Antigravity, não chama ferramentas MCP e **não comprova** o uso do agente. O teste anterior [M02 por stdio](../../docs/research/M02_REAL_MCP_STDIO_CHECKPOINT_2026-11-16.md) usou um cliente Python independente, não Windows.

## Preparar a pasta privada no Windows

No checkout local deste projeto, no PowerShell:

~~~powershell
powershell -File .\research\antigravity\Prepare-M02-Windows.ps1 -PrivateDir 'C:\REA-M02-PRIVATE\session-001'
~~~

O comando cria a pasta **fora do repositório e fora da área acessível a agentes**, `session.DRAFT.json`, `PRIVATE_README.txt` e a subpasta `evidence`. Registra versões locais de Node/npm, quando encontradas. Não modifica settings, não instala REA, não executa Antigravity ou o servidor MCP. Usa uma pasta nova para cada sessão, recusando sobrescritas.

Somente se o operador desejar e autorizar a inspeção do pacote oficial, adicionar `-InspectRea` em uma **nova pasta**. Esse opt-in pode baixar/cachear `rea-agents@6.9.0` e executa somente `--version` e `setup --client antigravity --dry-run`, **não aplica configuração**. O [runbook de homologação](../M02_ANTIGRAVITY_HOMOLOGATION_RUNBOOK.md) aborda o passo seguinte com aprovação humana.

A documentação oficial da Google distingue **Antigravity 2.0, Antigravity IDE e Antigravity CLI**. Confira seu produto antes de seguir os menus [MCP — Google](https://antigravity.google/docs/mcp).

## Capturar somente registros reais gerados pelo cliente

A referência deve ser a Rota 2 local autorizada, com Chrome/Edge e CDP em perfil descartável, sem dados reais ou contas institucionais. Se o Antigravity efetivamente invocar ferramentas REA, guardar os registros nativos do cliente (ou screenshots **redigidas**) em uma destas formas por papel:

- `evidence/tool-catalog.txt` ou `evidence/tool-catalog.png` — catálogo observado na sessão real.
- `evidence/targets-call.txt` ou `evidence/targets-call.png` — chamada real `list_browser_targets`, argumento e resultado.
- `evidence/inspection-call.txt` ou `evidence/inspection-call.png` — chamada real `inspect_web_page` e Evidence, com ID de alvo proveniente da chamada anterior.
- `evidence/decision-record.txt` ou `evidence/decision-record.png` — decisão/requisito fundamentado na evidência, com timestamp.

**Não criar arquivos inventados, vazios ou provenientes da execução Linux por Python** fingindo que pertencem ao Antigravity. Uma captura isolada da UI não é atesto criptográfico de origem. Nunca copiar cookies, HAR bruto, PII, credenciais, código de referência, requisitos ocultos ou oráculos privados. Retenha material integral apenas sob custódia privada, com acesso segregado.

Editar `session.DRAFT.json` para indicar qual produto é utilizado (`ANTIGRAVITY_2_0`, `ANTIGRAVITY_IDE` ou `ANTIGRAVITY_CLI`), versão real e confirmações verdadeiras do operador. Mesmo marcando essas confirmações como true, isso **não** autentica a sessão.

## Verificar hashes sem executar arquivos

~~~powershell
python -m research.antigravity.session audit --private-dir 'C:\REA-M02-PRIVATE\session-001'
~~~

O comando computa hashes SHA-256 de até quatro arquivos (2 MiB cada), verifica tipo regular, rejeita links simbólicos, duplicidade e extensões não previstas, sem executar arquivos ou publicar conteúdo. Gera, dentro da pasta privada:

- `audit-private.json`: hashes individuais e resumo para revisão independente;
- `audit-redacted-candidate.json`: somente contagens/estado, **candidato** a divulgação após revisão humana.

Se todos os registros estiverem presentes e o operador tiver feito as declarações completas, o máximo é `FILES_PRESENT_AWAIT_INDEPENDENT_AUTHENTICATION`. Isso não prova que os dados são autênticos: o revisor precisa verificar o registro no produto original, ferramenta, input/output, timestamps, permissões e o vínculo Evidence→decisão.

**P2 e P1–P4 continuam HOLD; T0–T3 não iniciados.** Nunca enviar os arquivos de evidência ao repositório público nem considerá-los resultados confirmatórios do manuscrito M1 v0.4.
