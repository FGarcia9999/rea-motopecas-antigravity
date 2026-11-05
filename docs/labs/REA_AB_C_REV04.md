# Laboratório REV04 — A, B e C (Windows / PowerShell)

**Público:** 8º período de Sistemas de Informação. **Alvo:** somente a aplicação didática Rota 2 Motopeças executada em `127.0.0.1`. **Natureza:** roteiro planejado, não execução registrada.

## Princípio de decisão

- **A — workflow agêntico:** Antigravity + LLM + Rules + Skills próprias; manutenção/TDD/gates. **Não exige `rea-agents`**.
- **B — REA oficial:** `rea-agents` via CLI ou servidor MCP; instrumenta a observação de um alvo autorizado. **Não é prova de reconstrução**.
- **C — integração:** evidenciação de B aceita por decisão humana → requisito/aceite → teste RED → código GREEN → gate → verificação independente. C só se justifica se B reduzir uma dúvida real de engenharia.

## 0. Preparação

Em PowerShell, a partir de um diretório limpo e autorizado:

```powershell
git clone https://github.com/FGarcia9999/rea-motopecas-antigravity.git rota2-lab
cd rota2-lab
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/gate.py
```

Não altere a `main` durante a aula. Registre commit SHA, ambiente, hora, comando e saída. O comando `git clone` baixa o projeto **já implementado**; exercícios nele avaliam manutenção evolutiva, e não reconstrução independente.

## A — TDD controlado para RF-03

1. Abrir a pasta completa como workspace no Antigravity. Conferir `AGENTS.md`, `.agents/rules/rea.md` e `.agents/skills/rea-*/SKILL.md`.
2. Executar `/rea-discovery`, solicitando matriz observação/hipótese/requisito/teste, sem alterar código.
3. Em branch própria, escolher melhoria pequena em RF-03. Executar **teste RED antes de implementação**, reter log com saída não zero; então GREEN e gate.
4. Em nova conversa/revisor, `/rea-verify` deve testar o contrato sem aceitar o relato do implementador como prova. Guardar parecer independente.
5. Conferir `tests/test_rf03_contract.py`; categorias locais incluem **Freios** e **Filtros**, mas **não** `capacetes`. `GET /api/products?category=capacetes` pode retornar HTTP 200 com lista vazia; isso **não** comprova filtro funcional.

## B — instalação homologada do software REA

**Pré-condições:** autorização para alterar configuração do cliente; Node/npm em versão compatível com o release homologado; ambiente de laboratório sem segredos. Conferir https://github.com/morluto/rea/blob/main/docs/installation.md.

```powershell
node -v
npm -v
# Preencher com uma versão efetivamente homologada, sem os caracteres <>:
$REA_VERSION = "VERSAO-HOMOLOGADA"
npx.cmd -y "rea-agents@$REA_VERSION" --version
npx.cmd -y "rea-agents@$REA_VERSION" setup --client antigravity --dry-run
# Somente com aprovação das alterações previstas:
npx.cmd "rea-agents@$REA_VERSION" setup --client antigravity
# Reiniciar o Antigravity e conferir manualmente a lista de ferramentas vivas:
npx.cmd -y "rea-agents@$REA_VERSION" doctor --client antigravity --json
```

**Atenção:** doctor saudável demonstra diagnóstico local, não tool call. Instalação pode afetar o perfil do usuário e outros projetos; revisar o plano. Na configuração real, usar as opções/documentação do release instalado; nunca copiar segredos ou logs não redigidos para Git.

Em terminais separados:

```powershell
# Terminal 1 — aplicação didática
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — perfil descartável, apenas loopback
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) { $edge = "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe" }
& $edge --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir="$env:TEMP\rea-browser-lab" http://127.0.0.1:8000

# Terminal 3 — descobrir target
npx.cmd -y "rea-agents@$REA_VERSION" list-browser-targets http://127.0.0.1:9222 --json
```

Copie o ID da aba local retornado pela ferramenta, sem presumir identificador. Antes de executar, confira `--help` do **mesmo release** e os controles de observação/allowlist que ele exigir.

```powershell
# Substituir ID_REAL pelo ID obtido; iniciar captura ANTES do clique
npx.cmd -y "rea-agents@$REA_VERSION" inspect-web-page http://127.0.0.1:9222 ID_REAL --observation-ms 10000 --include-accessibility-text --include-json-body-shapes --json
```

Durante a janela, clicar na categoria **Freios**. Capturar URL, método, status, estrutura JSON, horário, target, nome da ferramenta, argumentos, versão, saída, limitações e hash. Depois fechar o navegador descartável. Não afirmar que uma captura não realizada ocorreu. Em MCP, exigir tool name + args + result da chamada **viva**, não apenas o arquivo de configuração.

## C — juntar evidência e implementação

1. Escolha `EV-B-001` **somente como identificador a preencher após coleta verdadeira**; não há Evidence embutida nesta documentação.
2. Classifique OBSERVADO/INFERIDO/DESCONHECIDO/INDISPONÍVEL; o servidor SQL não pode ser inferido apenas da interface de terceiros.
3. Decisão humana: aceitar/rejeitar/reformular a observação e vincular ao RF-03 em `docs/traceability.csv` ou registro derivado.
4. Escrever teste reproduzindo comportamento faltante; guardar RED → GREEN, diff, gate e revisão independente.
5. Resultado: cadeia **evidência → requisito → teste → implementação → gate → aprovação**. Não carimbar PASS global se qualquer elo estiver NOT VERIFIED.

## 5 níveis de prova

| Nível | Mínimo verificável |
|---|---|
| 1. Instalação | Binário/package reporta versão fixa |
| 2. Configuração | Doctor identifica registro do cliente |
| 3. Disponibilidade | Agente lista ferramenta REA na sessão |
| 4. Execução | Log mostra nome, argumentos, resultado e target |
| 5. Utilidade | Evidência muda uma decisão de requisito/teste, com limites |

**Fontes:** https://rea.tools/guides/browser/ · https://rea.tools/get-started/ · https://github.com/morluto/rea/blob/main/docs/installation.md.
