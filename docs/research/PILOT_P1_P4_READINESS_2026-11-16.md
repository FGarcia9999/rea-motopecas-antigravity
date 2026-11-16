# REA — Controle de publicação e prontidão do piloto T0–T3

**Marco:** 16/11/2026 • **Estado:** INFRAESTRUTURA PÚBLICA EM REVISÃO; **PILOTO BLOQUEADO**.

Este registro mantém o alinhamento ao Protocolo Experimental v1.2, à Diretriz Científica v1.1, ao Roadmap v2.2 e ao manuscrito M1 v0.4. Não substitui atas ou aprovações dos coautores.

## Duas fronteiras distintas

**Fronteira de publicação:** o repositório `FGarcia9999/rea-motopecas-antigravity` pode conter códigos de infraestrutura, esquemas públicos, testes sintéticos, relatórios redigidos e hashes aprovados para divulgação. Não pode conter código de aplicações de referência reservadas, suítes de oráculos ocultos, ground truth experimental, credenciais, tráfego HAR/PCAP, logs brutos ou dados pessoais.

**Fronteira experimental:** o agente implementador vê a superfície funcional autorizada e seu próprio workspace, **não** fonte, requisitos reais nem oráculos do avaliador. A equipe avaliadora recebe um pacote SHA-256 do candidato, verifica seus metadados sem executá-lo automaticamente e realiza ensaios em sandbox separada.

O `scripts/check_research_public_boundary.py` impede algumas inclusões inadvertidas **no conjunto Git rastreado** (diretórios/arquivos reservados, documentos JSON privados e indicadores de segredos conhecidos). A regra é implementada no CI e testada com amostras sintéticas. Ela é **defesa em profundidade, não prova de inexistência de vazamentos**. Os históricos já publicados, contas conectadas, mensagens, screenshots e objetos de outros serviços ficam fora de seu escopo.

## Registro de prontidão P1–P4

| Gate | Evidência técnica hoje | Condição ainda não comprovada | Estado |
|---|---|---|---|
| P1 — contratos e thresholds | JSON Schemas e T0–T3 em DRAFT, nove critérios definidos | Valores mensuráveis, donos, congelamento e aprovação explícita | HOLD |
| P2 — observação instrumental | REA CLI 6.9.0 observou a Rota 2 local em GitHub Actions | Sessão real de Antigravity/MCP, catálogos, permissões e revisão independente | HOLD |
| P3 — acesso segregado | Smoke em Docker com agente de sondagem e redes internas | Agente LLM real, ferramentas/contas ligadas e referência genuinamente source-hidden | HOLD |
| P4 — qualidade do oráculo | Engine público, uma implementação alternativa e um mutante didático | Oráculos ocultos independentes, mutações válidas, alternativas corretas, adjudicação | HOLD |

**Execução do bloqueio programático:**

```bash
python scripts/check_research_public_boundary.py
python -m research.gates.readiness
python -m research.gates.readiness --require-ready
```

O último comando deve terminar com código 3 enquanto a pesquisa estiver bloqueada. A aprovação do CI não altera esse fato.

## Contratos de aprovação que a equipe precisa completar

1. Identificar responsáveis reais pela execução dos agentes, custódia da fonte, elaboração dos oráculos, revisão independente, gerenciamento de custos e controle de LGPD/segurança.
2. Selecionar a custódia **privada e fora do repositório público**, preferencialmente com acesso segregado por identidade e log de leitura.
3. Pré-registrar requisitos e oráculos privados, aplicáveis ao mesmo conjunto de comportamentos autorizados em T0–T3.
4. Congelar modelo e versões de ferramenta, configuração de Antigravity/MCP, prompts/Skills, hashes, orçamentos, critérios de timeout e intervenção humana.
5. Fixar limiares e regras de decisão dos nove critérios no arquivo **privado de aprovação** do estudo, com dupla verificação e evidência de aceite; o JSON público em DRAFT não vale como aprovação.
6. Demonstrar negados explícitos (e não apenas NOT_FOUND) para acessos indevidos a código, suíte e credenciais usando a identidade **efetiva** do agente.
7. Validar os oráculos em referência, mutações realmente executadas e alternativas verificadas corretas. Registrar falsas rejeições e inconsistências com dupla revisão.
8. Antes do WP4, produzir registro imutável de liberação, escopo de autorização, data, revisores e hashes; a liberação do piloto não será feita por script do agente implementador.

## Saída para o manuscrito

A infraestrutura pode apoiar o capítulo **Method/Experimental Setup** ou o suplemento de reprodutibilidade, com a classificação correta de *feasibility engineering*. Não inserir esses testes públicos ou classificações de CI como observações T0–T3 ou evidência de causalidade no manuscrito M1 v0.4.

**Decisão editorial e científica atual:** manter o estudo confirmatório em HOLD até que os responsáveis completem os controles e aprovações externos.
