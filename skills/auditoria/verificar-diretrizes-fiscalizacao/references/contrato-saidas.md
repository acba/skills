# Contrato das saídas

`preparar` gera um esqueleto. Complete os campos com inspeção humana/agente. `validar` retorna exit code 0 apenas para estrutura consistente; não certifica conteúdo.

## avaliacao.json

- `schema_version`: `1.0`.
- `metadata`: `root`, `diretrizes_path`, `diretrizes_origem` (`indicadas` ou `projeto`), `diretrizes_sha256`, `data_utc`, `escopo`, `limitacoes` (lista). O hash deve ser o da fonte realmente lida. Avaliações antigas sem origem continuam válidas quando a fonte registrada ou explicitamente informada está acessível.
- `pastas`: lista de objetos com `caminho`, `funcao_observada`, `funcao_esperada`, `evidencias` (lista de textos localizáveis), `conclusao`. Incluir áreas de domínio e equivalências, não apenas falhas.
- `requisitos`: uma linha por identificador da fonte vigente, com `id`, `titulo`, `estado`, `evidencias` (lista), `justificativa`, `alcance`, `problemas` (lista de IDs `PROB-...`). Estados: `Atende`, `Atende parcialmente`, `Não atende`, `Não verificado`, `Não aplicável`.
- `problemas`: objetos com os campos abaixo.
- `boas_praticas`: lista de objetos com `descricao`, `evidencias` (lista) e `preservacao`.

## Cada problema

Use o formato enxuto da seção 5 do relatório. Causa, indicador, preservação, dependências, responsável e esforço não são exigidos nem devem ser acrescentados como campos nessa seção. JSONs antigos que contenham esses campos continuam aceitos pelo validador; novos produtos devem seguir o modelo abaixo.

```json
{
  "id": "PROB-001",
  "diretrizes": ["DIR-13", "DIR-15"],
  "problema": "Comportamento observado em condição explícita",
  "evidencias": ["scripts/status.py: função status; confronto com entrada alterada"],
  "impacto_atual": "Efeito observado; risco potencial identificado como tal",
  "prioridade": "P1",
  "justificativa_prioridade": "Risco e marco em que deve ser tratado",
  "correcao": "Componente, contrato ou fluxo que muda",
  "impacto_melhoria": "Benefício esperado sem economia inventada",
  "aceite": "Teste ou confronto que comprova a correção",
  "estado": "Proposto"
}
```

Estados do problema: `Proposto`, `Em execução`, `Corrigido`, `Validado`, `Pendente de decisão`. Prioridades: P0, P1, P2, P3. Links entre problemas e requisitos são bidirecionais. Um requisito parcialmente/não atendido exige problema associado com evidência. `Não verificado` e `Não aplicável` exigem justificativa, mas não inventam defeito. Evidências de atendimento devem identificar o suporte e o alcance. Boas práticas podem ser lista vazia se não houve constatação suficiente; não inventar para equilibrar o relatório.

O mapa de pastas pode conter função não comprovada se a conclusão registra esse limite e a evidência identifica exatamente o que foi consultado. Não apresentar suposição como observação.
