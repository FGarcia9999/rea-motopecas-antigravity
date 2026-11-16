# REA — Estado de prontidão P1–P4

Ferramenta de leitura do protocolo experimental; **não emite autorização científica**.

```bash
python -m research.gates.readiness
# Apenas para verificar que o piloto ainda está bloqueado:
python -m research.gates.readiness --require-ready
```

A primeira execução produz JSON com os contratos conferidos, as lacunas e `pilot_authorized=false`. A segunda termina com código **3** enquanto não existir procedimento de verificação independente de aprovações e isolamento. O CI normal apenas registra o estado; não deve falhar por existir uma pesquisa ainda não autorizada.

Os critérios numéricos estão no `research/templates/go_no_go.DRAFT.json` e os tratamentos em `research/treatments/T0.json` até `T3.json`. Não inserir nomes fictícios, valores derivados dos resultados piloto, assinaturas presumidas ou estados `APPROVED` para fazer o teste passar. Uma alteração textual desse arquivo não comprova autorização humana.

P1 requer limiares mensuráveis, owners e congelamento; P2 exige chamada MCP real sob Antigravity e permissão documentada; P3 necessita de agente real e referência verdadeiramente reservada; P4 requer oráculos ocultos independentes, referência PASS, mutantes válidos e alternativas corretas revisadas. Posteriormente, outro processo controlado por principal independente poderá verificar aprovações autenticamente assinadas, sem expor segredos ao agente.

A existência do código e a aprovação do GitHub Actions não satisfazem esses gates. O resultado confirmatório M1 v0.4 continua reservado até a realização dos experimentos.
