# REV04 — auditoria de alinhamento dos materiais e do repositório

**Data-base:** 2026-11-04. **Commit de referência:** `93a453da219dcd3311e274c63fd68c78f82dd8fc`.

Este registro compara o projeto Rota 2 Motopeças com a apresentação **Engenharia de Software → IA → REA — REV04** (85 lâminas), o **Guia Didático — Laboratório REA — REV04** (19 páginas) e o HTML interativo anexados pelo docente. A presença deste relatório **não atesta** que o Antigravity ou o REA oficial tenham sido executados.

## Materiais-fonte fornecidos pelo docente

| Arquivo recebido | Tamanho (bytes) | SHA-256 | Condição |
|---|---:|---|---|
| `REA_Engenharia_Software_IA_GOVERNANCA_2026_REV04.pdf` | 5348312 | `3629ef9f3d67313c` (prefixo) | 85 páginas, fonte para a trilha conceitual |
| `Guia Didático - Laboratório - REA - REV04.pdf` | 1313928 | `d4a0c59373012ea8` (prefixo) | 19 páginas, fonte dos laboratórios A/B/C |
| `REA_Engenharia_Software_IA_REA_REV04_Apresentacao_Interativa (este).html` | 8736753 | `333ed66aae95480b` (prefixo) | 85 slides; ainda com rótulos REV03 no HTML original |

**Observação:** os arquivos binários originais não estão adicionados a este repositório por esta atualização textual. Para preservação integral ou distribuição oficial, arquivar os originais separadamente e verificar seus SHA-256 completos. Prefixos são identificadores de conferência curta, não substituem hash completo.

## Matriz de aderência

| Componente | Estado auditável | Ajuste realizado nesta revisão |
|---|---|---|
| Aplicação Python/FastAPI/SQLite e front-end | Implementação presente no commit-base | Preservada; não declarar paridade com a loja externa |
| A — workflow com Antigravity, Rules, Skills, pytest, gates | Skills e testes presentes | Documentar como fluxo proposto; separar configuração de execução |
| B — `rea-agents` oficial por CLI/MCP | Sem artefato de sessão real no commit-base | Manual específico + Skill auxiliar `rea-instrument`; checklist da instalação à execução |
| C — integração A+B | Sem evidência viva integrada no commit-base | Roteiro da cadeia observação → requisito → teste → código → gate → aprovação |
| RF-03 — filtro | Endpoint e teste básico existentes | Adicionar testes não-vazios, combinação, estados vazios, ordem e casos-limite |
| CLI administrativa | `tests/test_cli.py` no CI aprovado | Corrigir classificação na matriz: testes automatizados não equivalem a smoke manual |
| G1–G7 | Processo descrito; CI avalia subconjunto | Explicitar que G5/G6/G7 dependem de outras evidências e autorização |
| Segurança/LGPD | Modelo de ameaças inicial | Registrar CDP loopback, política de egress, segredo em HAR/logs, MCP e LLM externo |
| HTML do docente | 85 slides, conteúdo REV04 | Errata: metadados e nome de CSV citavam REV03; correção do HTML deve ser entregue como artefato docente separado |
| Guia, exemplo RF-03 | `category=capacetes` é inadequado ao catálogo fictício | Nos roteiros do repositório usar `category=Freios`; no material original sinalizar errata |

## Classificação das evidências

- **OBSERVADO NO GITHUB:** árvore, fontes, testes, execução de CI e arquivos versionados, na revisão indicada.
- **VERIFICADO PELO CI ORIGINAL:** compilação, pytest e pip-audit no job `REA Quality Gates` de 2026-11-03, execução `41660716506`. Isto não comprova ambiente Windows, browser/CDP ou integração REA/MCP.
- **NÃO VERIFICADO:** configuração viva do Antigravity, lista de tools reais, observação no navegador via REA, execução de Skill, teste diferencial contra referência, revisão independente e aprovação humana de release.
- **EXEMPLO DIDÁTICO:** IDs `EV-B-001`, URLs/respostas de captura e datas ilustrativas no guia não são evidência executada.

## Critérios para fechar a sincronização

1. Executar suíte/testes e CI no commit final; guardar links de job, SHA e artefatos novos.
2. Homologar versão exata do pacote `rea-agents` e Node; registrar `--version`, doctor e schemas CLI vivos.
3. Realizar laboratório B em navegador descartável e apenas no alvo `127.0.0.1`; preservar Evidence real sem dados sensíveis.
4. Executar C somente quando B trouxer informação que altere uma decisão de engenharia; registrar vínculo com RF-03.
5. Fazer revisão independente em sessão separada; registrar resultado e decisão humana. Sem esses passos, manter G6/G7 como NOT VERIFIED.

**Referências primárias:** https://rea.tools/get-started/ · https://rea.tools/guides/browser/ · https://github.com/morluto/rea/blob/main/docs/installation.md · https://antigravity.google/docs/skills · https://csrc.nist.gov/pubs/sp/800/218/final.
