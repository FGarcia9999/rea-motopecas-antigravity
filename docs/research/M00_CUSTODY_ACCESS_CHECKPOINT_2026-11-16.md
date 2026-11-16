# REA — M00: primeiro controle executável de custódia e autorização

**Data:** 16/11/2026 • **Versão:** 0.1 • **Estatuto:** engenharia demonstrativa, **NÃO** liberação experimental.

## Objetivo e conexão com o estudo

O [Plano Pré-Piloto v0.1](PRE_PILOT_EXECUTION_PLAN_v0.1_2026-11-16.md) definiu M00 como requisito para preparar referência independente, oráculos ocultos e sessões T0–T3. Este checkpoint executa **um controle técnico de permissão**, de alcance delimitado, e estrutura a matriz proposta de papéis. Não substitui designação de pessoas, assinatura, controle efetivo das contas conectadas ou aprovação P1–P4.

O estudo permanece regido pela [Diretriz v1.1](RESEARCH_DIRECTIVE_v1.1.md), [Protocolo v1.2](EXPERIMENTAL_PROTOCOL_v1.2.md), [Roadmap v2.2](ROADMAP_v2.2.md) e manuscrito M1 v0.4, sem dados de eficácia.

## Entregas e observação

| Item | Implementação ou evidência | Interpretação |
|---|---|---|
| Matriz de acesso | `research/custody/access_matrix.DRAFT.json`: cinco papéis, nove recursos; explícitos `allow`/`deny`; nenhuma identidade atribuída | Contrato público proposto, não ACL efetivamente aplicada |
| Sonda sintética | `research/custody/preflight.py`: leitura de 1 byte de canário **inofensivo**, sem imprimir valores | `DENIED` prova bloqueio apenas no escopo do arquivo |
| Controle positivo | Serviço temporário HTTP na mesma rede interna permitido ao processo não-root | Conectividade autorizada de teste preservada |
| Controles negativos | Canário legível, não encontrado, symlink, caminho fora do escopo, URL fora da allowlist, UID divergente | Verificador falha fechado |
| Testes e CI | `tests/test_research_custody.py` e workflow `m00-custody-preflight.yml` | Evidência reproduzível de engenharia pública |

**Execução efetiva:** [GitHub Actions run 43964685926](https://github.com/FGarcia9999/rea-motopecas-antigravity/actions/runs/43964685926), com contêiner Linux descartável, UID 65534 e recurso protegido. O serviço de teste foi acessível e a leitura do canário recebeu `PermissionError`; o resultado `PASS_ONE_SCOPE` foi produzido sem revelar conteúdo ou caminho. **É uma sonda Python, não uma sessão real de LLM/Antigravity.**

## Decisões humanas abertas

| Referência | Decisão necessária | Estado |
|---|---|---|
| M00-A | Pessoa/identidade responsável pela aplicação de referência e autorização | NÃO DESIGNADA |
| M00-B | Pessoa/identidade independente responsável por oráculos e ground truth | NÃO DESIGNADA |
| M00-C | Auditor responsável por escopo, conta, ferramentas, redes e incidentes | NÃO DESIGNADO |
| M00-D | Armazenamento privado com segregação de contas, acesso e auditoria | NÃO PROVISIONADO |
| M00-E | Licença, finalidade, anonimização, retenção, revogação e plano de resposta | NÃO APROVADOS |
| M00-F | Atesto adversarial **na identidade real** do agente e ferramentas REA/MCP | NÃO EXECUTADO |

**Condição de saída de M00:** a equipe deverá documentar responsáveis reais, autorização, custódia efetiva, verificação de não acesso e aceite independente em armazenamento controlado pelo avaliador. O scanner de arquivos públicos e esse smoke com canário não satisfazem essas condições por si.

## Próxima execução planejada

Assim que as identidades e o ambiente privado forem definidos: executar a validação de acesso a um canário inofensivo sob a **identidade real do agente**, junto de probes de filesystem, redes, ferramentas conectadas e contas GitHub/Antigravity; documentar acessos negados e superfícies que permanecem acessíveis. Se qualquer recurso privado puder ser lido por agente, registrar **HOLD/REVISE**, corrigir o ambiente e repetir a prova.

O M01 (referência independente) só pode ser considerado efetivamente implantado após fonte genuinamente reservada e custódia adequada; nenhuma implementação real foi publicada ou simulada neste checkpoint. O WP4 (20 execuções exploratórias previstas) **não começou**.

### Segurança de publicação

Nenhuma referência científica reservada, teste oculto, segredo, código de oráculo ou log confidencial foi acrescentado ao GitHub público. O artefato do CI contém somente status sintéticos; resultados científicos permanecerão sob custódia independente e divulgação aprovada.
