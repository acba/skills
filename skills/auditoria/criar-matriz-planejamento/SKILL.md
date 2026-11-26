---
name: criar-matriz-planejamento
description: Construir, revisar, validar e publicar a Matriz de Planejamento em Markdown, o DOCX/PDF e o mapa de verificação em draft com o Argos CLI, incluindo rastreabilidade F -> IR -> P -> E -> S + C, fontes qualificadas e variantes por público. Use sempre que o usuário pedir para criar, revisar, validar ou converter uma matriz de planejamento, gerar o mapa de verificação ou a árvore de verificação. Para matriz de achados, siga docs/ESPECIFICACAO_MARKDOWN_MATRIZ_ACHADOS.md. Não use para executar procedimentos de auditoria nem para redigir relatórios.
metadata:
  requirements: Argos CLI instalado e um projeto com `fiscalizacao.yml`; template DOCX da matriz em `.templates/`; `--config-fontes` quando o mapa precisar de caminhos/chaves físicos; LibreOffice ou Microsoft Word apenas quando o PDF for solicitado.
---

# Criar a Matriz de Planejamento

## Resultado e limites

Entregue a matriz em Markdown estruturado, validada com o Argos, e o DOCX
publicado a partir dela. Quando solicitado, publique também o PDF, o mapa de
verificação em draft ou a árvore HTML. A matriz declara a estratégia; não
executa procedimentos nem conclui achados. A matriz de achados tem fluxo
próprio em `docs/ESPECIFICACAO_MARKDOWN_MATRIZ_ACHADOS.md`.

Leia a especificação vigente antes de alterar sintaxe:
`docs/ESPECIFICACAO_MARKDOWN_MATRIZ_PLANEJAMENTO.md`. Ela é a fonte única para
gramática, metadados, fontes qualificadas, variantes e geração do mapa.

## Fontes e recursos obrigatórios

1. Leia `fiscalizacao.yml` (número, título, objetivo, processo e
   jurisdicionados) e o template em `.templates/`.
2. Leia a matriz vigente, se existir, e preserve decisões anteriores. Mudanças
   de escopo exigem registro, não sobrescrita silenciosa.
3. Leia o SurveyMD e o mapa de verificação existentes quando a matriz precisar
   manter correspondência com questões, fontes e itens já coletados.
4. Leia `--config-fontes` quando houver. Os caminhos físicos e as chaves
   pertencem ao projeto; a matriz guarda apenas o vínculo lógico.

## 1. Estrutura obrigatória do Markdown

Comece com o front matter obrigatório:

```yaml
---
title: "Nome da fiscalização"
fiscalizacao: "18/2026"
jurisdicionados: "Órgãos abrangidos"
objetivo_auditoria: "Objetivo do trabalho"
tipo_matriz: planejamento
---
```

Depois escreva `questao_geral` no preâmbulo e separe cada questão com
`## Questão NN - Título` (a transversal usa
`## Questão Transversal - Título`). Em cada questão, declare ao menos:

- `questao`;
- `subquestoes`, `riscos`, `fontes_de_informacao`, `informacoes_requeridas`,
  `criterios`, `procedimentos` e `evidencias` como listas identificadas;
- `possiveis_achados` com situações contendo `descricao`, `severidade`,
  `referencias_matriz`, `criterios`,
  `regra_de_identificacao` e `encaminhamento`;
- `o_que_a_analise_permite_dizer` e `limitacoes_e_cautelas`.

A rastreabilidade é `F -> IR -> P -> E -> S + C`: a fonte sustenta a
informação requerida, o procedimento verifica a informação e a evidência
sustenta a situação, ancorada em critérios.

Os IDs de achado e situação são **globais ao documento**, não reiniciam por
questão. Use `A1`, `A2`, `A3`… e `S1.1`, `S2.1`… sem repetir. Um `A1` na
questão 1 e outro `A1` na questão 2 passam na validação estrutural, mas o mapa
falha com “achado duplicado”. Corrija os IDs no Markdown, não no XLSX.

### 1.1 Regras e fontes qualificadas

Prefira qualificar a fonte no átomo quando a regra usar dado externo:

```markdown
      regra_de_identificacao:
        - (questionario:q0101 == Não) |
          (avaliacao_evidencias:avaliacao_documental[q0101] == Não conforme)
```

`fonte:campo` é opcional. Sem prefixo, o vínculo usa `fields` do
`--config-fontes`. Com prefixo, a fonte é registrada automaticamente no mapa.
O config ainda precisa informar `filepath` e `key` para a execução; sem isso o
draft registra pendência e não pode ser aprovado.

Não coloque caminhos na matriz. Não use prefixo vazio/inválido nem valor com
operador lógico dentro de aspas (por exemplo, `"A | B"`); a geração falha.
`campo in [A, B]` é aceito e vira uma ação agrupada.

### 1.2 Variantes

Use `variantes` quando o encaminhamento ou os critérios mudarem por público:

```yaml
      variantes:
        - publico: Empresas estatais
          aplica_se:
            naturezas: [EMPRESA_ESTATAL]
          criterios: [C1, C11]
          tipo_encaminhamento: Recomendação
          encaminhamento: Formalizar o processo.
```

A variante geral é derivada da situação base quando não houver uma `publico:
Geral` explícita. Variantes específicas substituem apenas os atributos que
declaram. Não repita a situação inteira dentro da variante.

## 2. Validar antes de publicar

```text
argos matriz validar 01-Planejamento/.../matriz_planejamento.md
argos matriz validar 01-Planejamento/.../matriz_planejamento.md --strict
```

`matriz validar` não gera produtos. `--strict` transforma avisos em bloqueio.
Corrija o Markdown; nunca edite o DOCX gerado. Use `--json` quando precisar
conferir contagens, erros, avisos e hashes.

Com `--project-root`, caminhos relativos são resolvidos a partir da raiz do
projeto. Para salvar em uma pasta externa, informe caminho absoluto; não presuma
que o diretório atual do terminal será usado.

## 3. Publicar DOCX/PDF

```text
argos matriz publicar caminho/matriz_planejamento.md --output caminho/matriz_planejamento.docx
argos matriz publicar caminho/matriz_planejamento.md --config-layout layout-matriz.yml
argos matriz publicar caminho/matriz_planejamento.md --pdf
```

- O template vem do projeto; confirme que ele corresponde ao tipo de matriz.
- O PDF é derivado do DOCX publicado (`--pdf-output` opcional) e exige
  LibreOffice ou Microsoft Word.
- A apresentação compacta IDs no DOCX sem alterar os IDs canônicos do Markdown.
- `--config-layout` controla apenas espaçamento visual dos critérios, em twips.
  Sem configuração, usa-se o padrão do template.
- Quando houver `larguras_colunas_percentuais`, use as seis chaves do tipo e
  soma exata de 100; sem essa configuração, não invente larguras.

## 4. Gerar e revisar o mapa de verificação

```text
argos matriz mapa caminho/matriz_planejamento.md --output mapa-verificacao.xlsx
argos matriz mapa caminho/matriz_planejamento.md --config-fontes fontes.yml --output mapa-verificacao.xlsx
```

O config mínimo, quando a matriz já usa prefixos, é:

```yaml
sources:
  - id: questionario
    filepath: respostas.xlsx
    key: firstname
  - id: avaliacao_evidencias
    filepath: painel-avaliacao-evidencias.xlsx
    key: Auditado
```

O draft é uma minuta e não executa a auditoria. Se o comando falhar com
`achado duplicado` ou `situação duplicada`, o problema está nos IDs globais
do Markdown. Confira:

- `Critérios de Auditoria` — critérios da matriz e metadados declarados;
- `Variantes de Encaminhamento` — específicas e `.GERAL` derivadas da base;
- `Motivos do Relatório` — minutas `[MINUTA]`, sujeitas a revisão editorial;
- `Fontes de Informação` — fontes referenciadas; caminho/chave ausentes deixam
  pendência;
- `Revisão` e `Pendências` — aprovação humana e itens a resolver.

O gerador agrupa alternativas do mesmo campo, resolve variáveis derivadas e
mantém o achado como **OU** das situações. Não crie ações manualmente nem
edite a planilha para contornar uma regra; corrija a matriz.

Quando o mapa estiver correto, o caminho é:

```text
revisar pendências → aprovar Revisão → executar argos auditar
```

`VerificationMap.compile` recusa fonte sem `filepath` ou `key`; resolva o
config antes de aprovar o mapa.

## 5. Árvore de verificação

```text
argos matriz arvore --mapa mapa-verificacao.xlsx --questionario questionario.md --output arvore.html
```

Gere a árvore apenas depois de o mapa estar revisado. Ela é visualização do
mapa, não substitui a aprovação nem a execução.

## 6. Conferir o resultado

Leia o resumo JSON (`--json`) e confirme:

- `validation.errors` e `validation.warnings`;
- produtos publicados e hashes SHA-256;
- `output` do mapa e contagens de fontes/pendências;
- estado `awaiting_input`, informando qual insumo falta — não invente conteúdo
  para destravar a execução.

Regenere os produtos a partir do Markdown; nunca edite DOCX, XLSX, PDF ou o
mapa manualmente.
