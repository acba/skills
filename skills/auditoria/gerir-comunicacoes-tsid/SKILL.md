---
name: gerir-comunicacoes-tsid
description: Conduzir o ciclo completo de comunicações oficiais com auditados (TSID01, TSID02, TSID03, ofícios e Termos de Reiteração) via `argos comunicacao` e `argos controle congelar`: configurar remetente e autenticação EWS/MFA, preparar template Markdown/Jinja2 e manifesto de destinatários, validar 100% dos anexos em prévia HTML (`--dry-run`), enviar amostra de teste (`--teste-para`), disparar lote oficial idempotente (`--enviar`), sincronizar caixa de entrada para capturar recibos de leitura, respostas, devoluções (bounces/NDR) e auto-respostas, reenviar lembretes dentro do prazo (`[LEMBRETE]`), registrar atendimento manual ou via LimeSurvey, exportar inadimplentes vencidos para Termo de Reiteração e gerar dossiê probatório com hashes SHA-256. Use sempre que o usuário pedir para enviar TSIDs/e-mails em lote, acompanhar ciência ou prazo de comunicações, checar bounces, reenviar lembretes, emitir lista para Termo de Reiteração ou gerar dossiê de comunicações. Não use para criar ou editar o questionário no LimeSurvey (use `elaborar-survey-limesurvey` ou `operar-limesurvey`) nem para redigir relatórios de auditoria (use `escrever-relatorio-auditoria`).
---

# Gerir Comunicações Oficiais e TSIDs (`argos comunicacao`)

Conduz comunicações em lote com auditados via `argos comunicacao` (integrado ao `audcom` e ao `controle.sqlite`) com rastreabilidade integral, proteção contra duplicidade e controle separado de **ciência**, **entregas com falha (bounce)** e **atendimento ao prazo**.

## Salvaguardas obrigatórias (e o porquê de cada uma)

- **Nunca execute `--enviar` sem autorização explícita do usuário.** Um disparo oficial atinge dezenas de órgãos jurisdicionados simultaneamente e não pode ser desfeito após entregue pelo Exchange.
- **Sempre valide 100% do lote com `--dry-run --preview-dir` e envie 1 amostra com `--teste-para` antes do disparo real.** Isso garante que nenhum anexo está faltando, nenhuma data divergiu entre TSID/anexo/e-mail e a renderização HTML (assinatura, links, tokens) está íntegra.
- **Nunca exponha, imprima ou versione `.env`, senhas ou `msal_token_cache*.bin`.** O cache OAuth concede acesso direto à caixa institucional; se expirar ou faltar, peça ao humano que rode `argos comunicacao auth` (MFA).
- **Congele os artefatos enviados (`argos controle congelar`) após o disparo.** Como o `controle.sqlite` registra o hash SHA-256 de cada PDF anexado ao e-mail, sobrescrever depois o PDF no repositório quebraria a cadeia probatória.

## Fluxo operacional completo

### Fase 1 — Preparar ambiente e conferir pré-requisitos

1. Verifique caixa configurada e cache EWS:
   ```bash
   argos comunicacao status
   ```
   - Se não houver caixa configurada: oriente `argos comunicacao init --mailbox <caixa-institucional>` (não existe remetente padrão hardcoded).
   - Se `Cache EWS: AUSENTE` ou token expirado: peça ao usuário para executar `argos comunicacao auth` (device code + MFA).
2. Confirme o escopo do manifesto de destinatários (`.xlsx`, `.csv` ou `.json`):
   - Deduplique e-mails por auditado preservando a ordem;
   - Confirme se não respondentes devem ou não constar da lista (ex.: em etapa de comentários de survey, não respondentes normalmente ficam fora do lote do formulário);
   - Garanta coerência de **data limite** entre o TSID PDF, o anexo do survey, a planilha de destinatários e o template de e-mail.
3. Monte o template Markdown com front matter YAML declarando a campanha, o prazo único de atendimento e o critério de cumprimento. Para estrutura completa, assinatura institucional e anexos dentro de `.zip` (`arquivo.zip::membro` + condição `quando:`), consulte `references/modelo-template-email.md`.

### Fase 2 — Validar, pré-visualizar e testar (antes de enviar)

1. **Validação fail-fast e prévia HTML (`--dry-run`):**
   ```bash
   argos comunicacao enviar \
     --template 99-Comunicacoes/<etapa>/email_template/<modelo>.md \
     --manifest 99-Comunicacoes/<etapa>/email_template/<destinatarios>.xlsx \
     --remetente <caixa@orgao.gov.br> \
     --preview-dir /tmp/preview_comunicacao \
     --dry-run
   ```
   - Exija `erros: 0` e confira o número esperado de destinatários (`simulados`).
   - Se o usuário quiser revisar visualmente o e-mail antes de aprovar, suba um servidor local somente em `127.0.0.1` (`python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/preview_comunicacao`), informe `http://127.0.0.1:8765/index.html` e encerre o servidor ao terminar.
2. **Teste real direcionado (`--teste-para`):**
   ```bash
   argos comunicacao enviar \
     --template <modelo>.md --manifest <destinatarios>.xlsx \
     --remetente <caixa@orgao.gov.br> \
     --teste-para <email-do-auditor> --limite 1
   ```
   - O modo teste usa prefixo `[TESTE]` e **não** grava o item como enviado definitivo no `controle.sqlite`. Peça ao auditor para confirmar o recebimento e abrir todos os anexos.

### Fase 3 — Disparo oficial e congelamento

1. **Somente após autorização expressa**, dispare o lote real:
   ```bash
   argos comunicacao enviar \
     --template <modelo>.md --manifest <destinatarios>.xlsx \
     --remetente <caixa@orgao.gov.br> \
     --enviar
   ```
   - O comando tem **idempotência tripla** (`controle.sqlite` + log JSONL + *Itens Enviados* do Exchange): se houver queda de rede no meio, basta reexecutar o mesmo comando — quem já recebeu é pulado automaticamente.
2. Congele os documentos enviados em `99-Gestao_e_Controle/congelados.yml`:
   ```bash
   argos controle congelar \
     --id <marco-envio> \
     --motivo "<descrição e data do envio>" \
     --tag congelamento-<marco>-<YYYY-MM-DD> \
     --caminhos <pasta-relatorios-ou-tsids>
   ```

### Fase 4 — Acompanhar ciência, tratar bounces e enviar lembretes

Ciência e atendimento são dimensões independentes: **ciência** indica que o auditado recebeu/leu ou respondeu ao e-mail; **atendimento** indica o cumprimento da solicitação dentro do `prazo_limite` (`resposta_email`, `email_com_anexo`, `survey_limesurvey` ou `manual`).

1. **Sincronizar inbox** (detecta automaticamente as caixas das campanhas no `controle.sqlite`):
   ```bash
   argos comunicacao sincronizar --dias 14
   ```
   - Recibos de leitura (`Read:`/`Lida:`) e respostas na thread confirmam **ciência** (basta 1 destinatário do auditado).
   - **Auto-respostas** (*Out of Office*/férias) são registradas como `AUTO_RESPOSTA` e **não** marcam ciência nem atendimento.
   - **Devoluções (NDR)** são registradas como `BOUNCE` e aparecem destacadas em `status` e `pendencias` — priorize corrigir o endereço dos auditados com `BOUNCE` antes de esperar o prazo vencer.
2. **Consultar painel e exportar pendências:**
   ```bash
   argos comunicacao status
   argos comunicacao pendencias --campanha <id> --sem-ciencia --exportar 99-Comunicacoes/<etapa>/acompanhamento.xlsx
   ```
3. **Reenviar lembrete dentro do prazo** (respeitando o mesmo fluxo `--dry-run` → `--enviar`):
   ```bash
   argos comunicacao reenviar --campanha <id> --sem-ciencia --prefixo "[LEMBRETE] " --dry-run
   argos comunicacao reenviar --campanha <id> --sem-ciencia --prefixo "[LEMBRETE] " --enviar
   ```
   - Cada rodada gera IDs derivados (`<id>#lembrete-1`, `#lembrete-2`), mantendo proteção anti-duplicidade. O Argos bloqueia lembretes após o `prazo_limite` (salvo `--permitir-vencidos`), porque após o vencimento o instrumento adequado é o Termo de Reiteração.

### Fase 5 — Registrar atendimento, emitir reiteração e gerar dossiê probatório

1. **Registrar atendimentos** (em lote via exportação do LimeSurvey ou individualmente para ofício/e-TCE):
   ```bash
   argos comunicacao registrar --campanha <id> --do-survey <respostas_limesurvey.csv>
   argos comunicacao registrar --campanha <id> --tipo atendimento --auditado "<NOME>" --obs "Protocolo e-TCE nº ..."
   ```
2. **Listar violações de prazo para Termo de Reiteração:**
   ```bash
   argos comunicacao pendencias --campanha <id> --somente-vencidos --exportar 99-Comunicacoes/<etapa>/inadimplentes_reiteracao.xlsx
   ```
   - A partir dessa planilha, gere os Termos de Reiteração e inicie uma nova campanha independente (ex.: `--campanha TSID02-TR01`) com o novo `prazo_limite`.
3. **Emitir dossiê probatório de um auditado** (para instruir reiteração ou representação por descumprimento):
   ```bash
   argos comunicacao historico --auditado "<NOME>" --exportar dossie_<slug>.md
   ```
   - O Markdown gerado traz a linha do tempo cronológica em horário local, `Internet-Message-ID`, `Conversation-ID` e tabela de integridade (SHA-256) de todos os anexos enviados; pode ser publicado em PDF via `argos documento dossie_<slug>.md --pdf`.

## Referências locais

- `references/modelo-template-email.md`: leia ao criar ou revisar um template de e-mail institucional com front matter YAML, anexos condicionais em `.zip` e assinatura HTML.
