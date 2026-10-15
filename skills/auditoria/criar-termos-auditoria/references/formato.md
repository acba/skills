# Formato dos Termos de Auditoria

O insumo é Markdown UTF-8. O frontmatter YAML deve ser um mapa. `fiscalizacao`, `processo_paag` e `objetivo_auditoria` são exigidos para renderização; quando o número do processo não existir, registre uma pendência explícita. Campos de reunião são opcionais e só devem conter fatos documentados.

```yaml
---
title: Termos de Auditoria
orgao: "Órgão responsável"
secretaria: ""
unidade: ""
fiscalizacao: "[PENDENTE: número da fiscalização]"
processo_paag: "[PENDENTE: número do processo]"
jurisdicionados: ""
objetivo_auditoria: "Objetivo fundamentado nos documentos do trabalho"
data_reuniao: ""
horario_reuniao: ""
local_reuniao: ""
participantes: []
decisoes_reuniao: []
---
```

Depois vêm exatamente as seções `## 1. Objeto` até `## 12. Datas e Ausências`, em ordem. `###` cria subtítulos; `-` cria itens; parágrafos em linhas contíguas são unidos no painel. O Markdown permanece como registro textual completo; o painel é uma apresentação da mesma fonte. Tabelas Markdown simples são renderizadas como linhas de texto no painel. A minuta de ata reproduz a pauta, mas não atesta que a reunião ocorreu.
