---
name: elaborar-survey-limesurvey
description: Elaborar e publicar o questionário SurveyMD como importação LimeSurvey (.lss) e guia do respondente (DOCX/PDF), além do survey de comentários do gestor e da coleta de respostas e evidências. Use quando o usuário pedir para criar, revisar ou converter um questionário, gerar o LSS, gerar o guia em DOCX/PDF, montar o survey de comentários ou coletar respostas do LimeSurvey. Não use para avaliar evidências nem redigir relatórios.
metadata:
  requirements: Argos CLI instalado e um projeto com `fiscalizacao.yml`; credenciais do LimeSurvey apenas em variáveis de ambiente quando houver coleta; LibreOffice ou Microsoft Word apenas quando o PDF for solicitado.
---

# Elaborar o survey LimeSurvey

## Resultado e limites

Entregue o SurveyMD validado, o `.lss` importável e o guia DOCX/PDF do
respondente (`argos survey gerar`). Quando solicitado, gere também o survey de
comentários do gestor (`argos contraditorio preparar`) e colete respostas e
anexos do LimeSurvey (`argos survey coletar` e `argos survey baixar-anexos`). O survey
coleta declarações e evidências; ele não julga conformidade nem conclui
achados — isso pertence a `argos evidencias avaliar` e `argos auditar`.

## Fontes e recursos obrigatórios

1. Leia a matriz de planejamento vigente para manter correspondência entre
   questões de auditoria, informações requeridas e itens do questionário.
2. Leia o SurveyMD atual e preserve códigos de questão já respondidos; mudar um
   código em coleta ativa quebra a rastreabilidade das respostas.
3. Leia a escala de adoção padrão (`naoad`, `adfor`, `admen`, `adpar`, `admai`,
   `naoap`) antes de propor novas escalas.

## 1. Gramática SurveyMD

Antes de criar ou revisar o Markdown, consulte a
[especificação normativa completa do SurveyMD v1](../../docs/SURVEYMD_V1.md).
Ela define gramática, metadados, diretivas e aliases aceitos, tipos, condições,
macros, defaults, limites e exemplos verificados. Use essa referência como fonte
única para decidir a sintaxe; não invente atributos específicos do LimeSurvey
no arquivo autoral. Os exemplos executáveis ficam em
<code>../../docs/surveymd-v1/examples/</code>.

Forma básica: front matter YAML opcional, escalas em <code>## Escala: &lt;id&gt;</code>, grupos
em <code>## Grupo: &lt;id&gt; | Nome</code> e questões em <code>### &lt;codigo&gt; [&lt;tipo&gt;]</code>. Alternativas
usam <code>- codigo | Rótulo</code>; declare diretivas em linhas <code>nome: valor</code> e consulte
a especificação para compatibilidade por tipo e expansão de macros.

## 2. Validar e publicar

```text
argos survey gerar questionario.md --guia
argos survey gerar questionario.md --output questionario.lss --docx-output guia.docx --pdf
```

O `.lss` sai em `<questionario>.lss` (ou em `--output`); `--guia` gera também o
guia DOCX (`<questionario>.docx` ou `--docx-output`), e `--pdf` deriva o PDF do
guia (`--pdf-output` opcional; `--estilos` troca o DOCX de estilos) e exige
LibreOffice ou Microsoft Word. A ação
valida a gramática antes de publicar; corrija o Markdown — nunca edite o `.lss`
ou o DOCX gerados.

## 3. Survey de comentários do gestor

```text
argos contraditorio preparar --resultado-auditoria resultado_auditoria.json \
  --questionario questionario.md --lss-output comentarios.lss --anexos-output anexos.zip
```

O survey de comentários nasce do resultado preliminar da auditoria e dos
ajustes aplicados (`--ajustes`); os anexos DOCX são individuais por auditado e
usam `--template-anexos` (padrão: `templates.comentarios_gestor` do projeto).
`--config-comentarios` troca as perguntas e os textos, e `--data-final`,
`--nome-administrador` e `--email-administrador` preenchem o prazo e o contato.
Use `--sem-lss` ou `--sem-anexos` para publicar apenas uma das partes.

## 4. Coletar respostas e evidências

```text
argos survey coletar --survey-id 123456 --output-dir 02-Execucao/01-Coleta/01-Questionario --dry-run
argos survey coletar --survey-id 123456 --output-dir 02-Execucao/01-Coleta/01-Questionario
```

Para baixar apenas os anexos de um XLSX de respostas já exportado do LimeSurvey:

```text
argos survey baixar-anexos respostas-exportadas.xlsx --output-dir 02-Execucao/01-Coleta/anexos
```

- `--output-dir` é a pasta de **um** survey; use uma pasta por survey.
- A coleta cria `exportacoes_brutas/<timestamp>-<execucao>/`, `auditados/` e
  `manifesto-geral.xlsx`. Os anexos correntes usam nomes fixos:
  `auditados/<auditado>-r<id>/respostas.pdf` e `evidencias.zip`.
- `--dry-run` valida a configuração localmente, sem rede; use-o antes de
  qualquer coleta real.
- Credenciais do LimeSurvey vêm exclusivamente de variáveis de ambiente;
  nunca as grave em produtos, logs ou no SQLite.
- Repetições sem mudança reutilizam os anexos; versões antigas vão para
  `auditados/.versoes/`. `--refresh` força nova consulta dos anexos.
- A extração é opcional e desativada por padrão; com `--extract true` ela vai
  para `derivados/`, nunca para junto do ZIP corrente.
- `--coluna-auditado` indica a coluna que identifica o auditado (padrão:
  `firstname`) e `--nome-consolidado` o nome-base das cópias consolidadas.
- O `argos status` verifica os manifestos e produtos, mas não os PDFs/ZIPs
  gerenciados correntes. Preserve os arquivos baixados; não os edite.

## 5. Conferir o resultado

Leia o resumo JSON (`--json`) e confirme os produtos publicados, o `sid` e os
hashes. Em `awaiting_input`, informe qual insumo falta. Mudanças no SurveyMD
depois de uma coleta ativa exigem decisão explícita do auditor: prefira um novo
cenário ou uma nova versão do questionário a editar respostas existentes.
