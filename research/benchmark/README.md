# REA — Entrada de um benchmark reservado (WP3/P3/P4)

**Versão da infraestrutura:** v0.1, 16/11/2026. **Estado:** contrato de armazenamento e verificação inicial; **NÃO constitui um benchmark científico oculto nem habilita o piloto T0–T3**.

## Propósito

Após os PRs #4–#7 estabelecerem contratos, captura real de REA CLI no demonstrador, isolamento sintético e transporte agente→avaliador, este módulo introduz a **entrada de ativos controlados pelo avaliador**:

- diretório privado do código-fonte da aplicação de referência;
- arquivo privado JSON contendo os testes comportamentais do avaliador, conforme `research/oracles/suite.schema.json`;
- arquivo privado JSON de política de autorização;
- registro privado de hashes de todos os arquivos de referência e o hash da suíte;
- relatório **público minimizado**, contendo apenas hashes, quantidade de arquivos/casos, data e status **pendente**.

**Se esses materiais forem gerados por `public_fixture.py`, serão um demonstrador público com token aleatório, NÃO uma aplicação de referência independente e desconhecida pelos agentes.** Não misturar o demonstrador com a base científica confirmatória.

## Armazenamento e identidades

O repositório GitHub é público: não colocar código da referência reservado, requisitos ocultos, suites privadas, tokens, banco de dados real, logs privados ou credenciais sob `research/`, `docs/` ou `tests/`. O avaliador deve criar armazenamento e credenciais próprios, sob identidade distinta da identidade usada para executar os agentes. A referência só poderá ser exposta por interface previamente autorizada, nunca por acesso ao repositório de origem.

Apenas manter arquivos de metadados públicos, de forma preferencial sob aprovação explícita da equipe. **Um SHA-256 não prova proveniência, autorização, inexistência de vazamento, isolamento ou qualidade científica.**

## Contrato de política privada `policy.json`

O documento deve declarar:

```json
{
  "schema_version": "1.0",
  "benchmark_id": "IDENTIFICADOR_RESERVADO",
  "reference_owner_id": "PAPEL_REFERENCIA",
  "evaluator_owner_id": "PAPEL_AVALIADOR",
  "authorization_id": "AUTORIZACAO_FORMAL",
  "reference_access": "EVALUATOR_ONLY",
  "oracle_access": "EVALUATOR_ONLY",
  "observability": ["DIRECT", "INDIRECT", "INSTRUMENT_ASSISTED", "UNAVAILABLE"],
  "candidate_applications": [
    {"application_id": "APP_01", "domain": "DOMINIO_A_DEFINIR",
     "agent_target_scope": "OWNED_AUTHORIZED_RUNTIME_ONLY"}
  ],
  "approval_status": "DRAFT"
}
```

Dois rótulos de responsáveis diferentes são apenas **metadados declarados**, não prova de revisão independente. O contrato não aceita `APPROVED`, evitando classificação automática indevida. No futuro, a aprovação precisará ser registrada por processo independente do código do agente e do coletor.

## Procedimento em ambiente do avaliador (não executar com dados privados no CI público)

```bash
# Caminhos ABSOLUTOS fora do checkout e sob a identidade do avaliador
python -m research.benchmark.intake \
  --reference-dir /evaluator-only/reference-source \
  --oracle-suite /evaluator-only/oracle/hidden-suite.json \
  --policy /evaluator-only/policy/benchmark-policy.json \
  --private-record /evaluator-only/records/intake-private.json \
  --public-attestation /evaluator-only/redacted/intake-public.json
```

A entrada exige arquivos reais (não links simbólicos), checa limites de arquivos/bytes, tipos permitidos, contrato sintático dos casos e política, hash do código-fonte e hash da suíte. Proíbe salvar registros ou ativos dentro do repositório e se recusa a sobrescrever arquivos existentes.

**A saída `PENDING_PRIVATE_EVALUATOR_ISOLATION_AND_APPROVAL` é intencional:** mesmo após verificar os hashes, o controle de acesso não foi exercitado de dentro de um agente real.

### Smoke público automatizado

```bash
python -m research.benchmark.public_fixture --destination /tmp/rea-intake-toy
python -m research.benchmark.intake \
  --reference-dir /tmp/rea-intake-toy/reference \
  --oracle-suite /tmp/rea-intake-toy/evaluator/oracle.json \
  --policy /tmp/rea-intake-toy/evaluator/policy.json \
  --private-record /tmp/rea-intake-toy/evaluator/record.json \
  --public-attestation /tmp/rea-intake-public/report.json
python -m pytest -q tests/test_research_benchmark_intake.py
```

O GitHub Actions `.github/workflows/wp3-private-intake-smoke.yml` executa exclusivamente esse **gerador público** em espaço temporário. O único artefato publicado é `intake-redacted.json`. Os tokens criados durante o teste e as suítes de avaliação não são anexados ao GitHub.

## Condições para o verdadeiro benchmark source-hidden

1. Aplicação independente e previamente **não exposta** aos agentes, criada/selecionada por avaliador externo. A Rota 2 pública não atende esse requisito.
2. Requisitos, código, testes e dados reservados fora de qualquer caminho, ferramenta, rede, contexto ou aplicativo acessível ao agente.
3. Referência observável por interface autorizada, mantendo **equivalência de superfície autorizada entre T0–T3**.
4. Prova adversarial de isolamento por filesystem, rede, ferramentas, contas e credenciais **sob identidade de agente real**, com registro de falhas/negativas.
5. Oráculos pré-congelados, verificados por referência, mutantes válidos executados, implementações alternativas corretas e revisão independente.
6. Responsáveis e limiares numéricos P1–P4 formalmente aprovados antes do primeiro piloto.

**Nenhum desses seis requisitos é automaticamente comprovado pelo intake.** Os resultados do smoke não devem ser acrescentados à tabela confirmatória do M1 v0.4.

Veja [Protocolo v1.2](../../docs/research/EXPERIMENTAL_PROTOCOL_v1.2.md), [handoff](../handoff/README.md) e [relatório do checkpoint](../../docs/research/WP3_BENCHMARK_INTAKE_CHECKPOINT_2026-11-16.md).
