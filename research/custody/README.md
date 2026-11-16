# REA — M00: contrato de custódia e prova sintética de acesso

**Estado:** prova técnica de alcance limitado, não liberação científica. **P1–P4 e o piloto T0–T3 continuam HOLD.**

## 1. O que este módulo acrescenta

- `access_matrix.DRAFT.json`: recursos e papéis autorizados/proibidos **propostos** para agente implementador, operador, custodiante da fonte, avaliador dos oráculos e revisor independente. As identidades, as contas e as permissões efetivas **ainda não foram designadas nem comprovadas**.
- `preflight.py`: sonda de **um único arquivo-canário sintético**, exatamente denominado `rea_m00_synthetic_canary.txt`, sob a identidade atual do processo. Lê no máximo 1 byte **sem divulgar conteúdo nem caminho**. Verifica também a disponibilidade de um endpoint HTTP local explicitamente permitido.
- `tests/test_research_custody.py`: testes de ACL proposta e falhas adversariais, inclusive origem externa, symlink, `NOT_FOUND`, UID não verificado, canário legível e serviço indisponível.
- `.github/workflows/m00-custody-preflight.yml`: contêiner sem root, rede interna Docker, serviço de treinamento temporário sem dados reais e arquivo-canário inacessível por permissões; conserva somente resultado público redigido.

## 2. Semântica dos resultados

| Situação | Resultado | Significado |
|---|---|---|
| Arquivo-canário existe e a abertura gera `PermissionError` | `DENIED` | Acesso negado **a este arquivo e identidade** |
| O arquivo não existe | `NOT_FOUND` | **Não é** prova de acesso negado |
| Arquivo é legível | `ACCESSIBLE` | Falha de isolamento no escopo testado |
| Não há prova do UID efetivo não-root | `INCOMPLETE_OR_UNSAFE` | Sem atesto de identidade |
| URL sai da allowlist `127.0.0.1:8000` / `m00-reference:8000` | `REJECTED` | Nenhuma sondagem da URL externa é realizada |

`PASS_ONE_SCOPE` somente indica `DENIED` + interface local acessível + UID esperado. Ainda assim, `real_llm_or_antigravity_identity_attested=false`, `all_network_mcp_and_connector_scopes_checked=false` e `scientific_P3=HOLD`.

**Nunca aponte a sonda para arquivos reais de código, oráculos ou credenciais.** A pasta da equipe avaliadora deve possuir um canário **inofensivo e criado especificamente** para a verificação. O programa **não procura** caminhos privados e não se conecta a IPs externos.

### Execução de laboratório Linux (somente ambientes próprios)

Em um contêiner/conta de laboratório previamente autorizados, com o arquivo sintético acima montado e inacessível ao UID esperado:

```bash
python research/custody/preflight.py \
  --canary-file /protected/rea_m00_synthetic_canary.txt \
  --runtime-url http://127.0.0.1:8000/ \
  --expected-uid 65534
```

A versão CI executa a mesma verificação contra o hostname `m00-reference` da rede Docker interna. Sem Linux `geteuid`, a execução retorna incompleta, **não** aprovada por omissão; em Windows/Antigravity será necessário um atesto de identidade real separado.

## 3. Evidência executada

- [GitHub Actions — M00 canary smoke](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43964685926): sonda real, sintética e limitada, no contêiner de teste.
- O relatório contém apenas classes de resultado/booleanos; jamais nome absoluto de path, conteúdo do canário ou endereço de recurso privado.
- O script executado no CI é um **processo Python de teste**, não um agente LLM, não o cliente Antigravity, nem o conjunto de ferramentas MCP real.

## 4. Trabalho necessário para concluir M00

1. Designar nominalmente, **fora do repositório público quando apropriado**, responsáveis distintos por fonte, oráculos, segurança e revisão.
2. Provisionar armazenamento privado sob identidade sem tokens acessíveis aos agentes. Uma pasta dentro do GitHub público, `.gitignore` ou repositório privado acessível ao mesmo conector não asseguram separação.
3. Documentar autorização de alvos, contratos de licença/uso, riscos, privacidade, retenção e revogação.
4. Testar controles **efetivos** com identidades reais, inclusive ferramentas GitHub/MCP, filesystem, rede, browser e credenciais.
5. Registrar aprovações, recusas e hashes privados sob custodiante; não usar CI público como repositório de evidências confidenciais.

Consulte também o [checkpoint M00](../../docs/research/M00_CUSTODY_ACCESS_CHECKPOINT_2026-11-16.md) e [SOP de custódia](../../docs/research/EVALUATOR_CUSTODY_SOP_v0.1_2026-11-16.md) trazem a classificação e as decisões pendentes.
