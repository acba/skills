# Modelo de template de e-mail (`argos comunicacao enviar`)

Use este modelo como ponto de partida ao criar um novo template de comunicação oficial (TSID01, TSID02, TSID03 ou Termo de Reiteração). Salve em `99-Comunicacoes/<etapa>/email_template/<nome>.md`.

## Front matter YAML + corpo Markdown/Jinja2

```markdown
---
campanha: "tsid03"
prazo_limite: "2026-12-02"
criterio_atendimento: "survey_limesurvey"   # resposta_email | email_com_anexo | survey_limesurvey | manual
assunto: "[{{ auditado }}] Fiscalização TCE-RJ nº {{ fiscalizacao }} — TSID nº 03"
id: "fisc2026-tsid03-{{ auditado | slug }}"
pedir_confirmacao_leitura: true
anexos:
  - caminho: "99-Comunicacoes/06-TSID03/tsid/TSID03 - {{ auditado }}.pdf"
  - caminho: "03-Relatorios/01-Individuais/01-Preliminares/gerados/Relatorio_Preliminar_{{ auditado | slug }}.pdf"
  - caminho: "02-Execucao/07-Comentarios_Gestor/anexos_pdf.zip::Anexo - Questionário ({{ auditado }}).pdf"
    quando: "{{ respondeu }}"
---
Prezado(a) {{ destinatario_nome }},

Encaminhamos, em anexo, o **Termo de Solicitação de Informações e Documentos nº 03 (TSID03)** e o **Relatório Individual Preliminar** referentes à **Fiscalização nº {{ fiscalizacao }}** (Processo nº {{ processo }}).

O prazo para manifestação é **IMPRORROGÁVEL** e se encerra em **{{ data_limite }}**.

{% if respondeu %}
<div style="background:#f8fafc;border-left:4px solid #1b365d;padding:12px 16px;margin:16px 0;border-radius:4px;">
  <p style="margin:0 0 8px 0;"><strong>Questionário eletrônico:</strong> <a href="{{ url_survey }}">{{ url_survey }}</a></p>
  <p style="margin:0;"><strong>Token de acesso:</strong> <code>{{ token }}</code></p>
</div>
{% endif %}

Atenciosamente,

<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:16px;border-collapse:collapse;">
  <tr>
    <td style="vertical-align:middle;border-left:2px solid #cbd5e1;padding-left:16px;font-family:Calibri, Arial, sans-serif;line-height:1.45;">
      <div style="font-size:15px;font-weight:bold;color:#1b365d;">Equipe de Auditoria da Fiscalização nº {{ fiscalizacao }}</div>
      <div style="font-size:13px;color:#374151;">Coordenadoria responsável</div>
      <div style="font-size:13px;margin-top:2px;"><a href="mailto:{{ remetente }}" style="color:#0077b6;font-weight:bold;text-decoration:none;">{{ remetente }}</a></div>
    </td>
  </tr>
</table>
```

## Colunas recomendadas no manifesto `.xlsx`

| Coluna | Obrigatória | Observação |
|---|---|---|
| `auditado` (ou `municipio`) | Sim | Usada no assunto, no `id` com `| slug` e no controle de ciência/prazo |
| `destinatario_nome` | Sim | Nome do ponto focal ou autoridade na saudação |
| `email` | Sim | Um ou mais endereços separados por `;` (deduplicados) |
| `data_limite` | Recomendada | Deve coincidir com `prazo_limite` do front matter e com o texto do TSID |
| `url_survey` / `token` / `respondeu` | Condicional | Necessárias quando a comunicação vincula questionário no LimeSurvey |
