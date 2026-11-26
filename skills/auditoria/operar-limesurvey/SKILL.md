---
name: operar-limesurvey
description: Operar a instância LimeSurvey do TCE-RJ (limesurvey-novo) pelo navegador real via CLI `browse` (`~/.local/bin/browse`) para importar arquivos `.lss`, inicializar e importar participantes/tokens em CSV, pré-visualizar telas e grupos (`previewgroup`), testar lógica condicional e upload obrigatório, extrair participantes de surveys de referência e configurar notificações/confirmações. Use sempre que o usuário pedir para importar, testar, pré-visualizar, configurar participantes/tokens ou inspecionar um survey diretamente no LimeSurvey web. Para elaborar o SurveyMD/LSS no repositório ou coletar respostas via Argos, use `elaborar-survey-limesurvey` ou `operar-argos`.
metadata:
  requirements: CLI `browse` conectado à extensão no navegador (`browse status`), sessão autenticada no LimeSurvey do TCE-RJ e permissão de escrita em `/tmp` para uploads.
---

# Operar o LimeSurvey do TCE-RJ via `browse`

## Por que usar `browse` e não RemoteControl

Na instância do TCE-RJ (`https://www.tcerj.tc.br/limesurvey-novo`, LimeSurvey 3.23), a API RemoteControl 2 está desabilitada (requisições `GET` ou `POST` JSON-RPC a `/index.php/admin/remotecontrol` retornam `HTTP 200` com `Content-Length: 0`). Além disso, `argos contraditorio` e `argos survey` operam apenas a geração local e a coleta via cookies de sessão. Portanto, importação de `.lss`, criação e carga de participantes/tokens e pré-visualização interativa devem ser feitas pela interface web autenticada usando o CLI `browse`.

## Salvaguardas obrigatórias

- **Nunca** ative um survey, dispare e-mails de convite/lembrete nem apague surveys existentes sem pedido explícito do usuário. Todo survey recém-importado deve permanecer **inativo**.
- Se o navegador redirecionar para login ou apresentar CAPTCHA/2FA, pare imediatamente e peça ao usuário via `browse handoff` (ou informe no chat). Nunca tente contornar autenticação.
- Remova de `/tmp` as cópias temporárias de `.lss` e `.csv` ao concluir a operação.

## Pré-requisitos e regras do CLI `browse`

1. Verifique a conexão antes de começar:
   ```bash
   browse status
   ```
2. **Raiz permitida para upload:** `browse upload` aceita **apenas** caminhos absolutos dentro de `/tmp`. Copie o `.lss` ou `.csv` para `/tmp/` antes de chamar `browse upload` com `--tab <TAB> --ref <REF> --files /tmp/...`.
3. **Abas e ciclos de espera:**
   - Abra uma aba com `browse navigate "<URL>"` (retorna `tab`) e reutilize `--tab <TAB>` nos comandos seguintes. Se a aba tiver sido fechada no navegador, `navigate` sem `--tab` abre outra.
   - Após cliques que disparam navegação, aguarde com `browse wait_for --tab <TAB> --load settle --timeout 30000`. Após cliques reativos em JS (ex.: ExpressionScript em rádio/checkbox), aguarde `browse wait_for --tab <TAB> --ms 400`.
4. **Inspeção confiável:**
   - Use `browse snapshot --tab <TAB>` para obter os refs atuais (`e11`, `e78`, etc.) sempre que mudar de tela ou aba interna.
   - Use `browse eval --tab <TAB> --expression '<js>'` (a flag obrigatória é `--expression`).
   - Para conferir renderização visual, capture `browse screenshot --tab <TAB> --output /tmp/<nome>.png --fullPage true` e inspecione com leitura de imagem.

## Mapa de URLs do LimeSurvey (`limesurvey-novo`)

Base: `https://www.tcerj.tc.br/limesurvey-novo/index.php`

- **Importar novo survey:** `/admin/survey/sa/newsurvey` (clicar na aba `Import`)
- **Resumo/visão geral do survey:** `/admin/survey/sa/view/surveyid/<SID>`
- **Inicializar tabela de participantes:** `/admin/tokens/sa/index/surveyid/<SID>`
- **Importar participantes via CSV:** `/admin/tokens/sa/import/surveyid/<SID>`
- **Listar participantes (paginado):** `/admin/tokens?surveyid=<SID>&sa=browse&TokenDynamic_page=<N>`
- **Pré-visualizar survey (tela inicial):**
  - Sem tabela de tokens: `/survey/index/sid/<SID>/newtest/Y`
  - Com tabela de tokens inicializada: `/survey/index/sid/<SID>/token/<TOKEN>/newtest/Y` (sem token o LimeSurvey exibirá a tela de digitação do token e não substituirá `{TOKEN:FIRSTNAME}`).
- **Pré-visualizar um grupo específico:** `/survey/index/action/previewgroup/sid/<SID>/gid/<GID>`

## Fluxo 1 — Importar arquivo `.lss`

1. Copie o `.lss` para `/tmp/<arquivo>.lss`.
2. Navegue para `/admin/survey/sa/newsurvey`, faça `snapshot` e clique na aba `Import`.
3. Faça `snapshot` da aba de importação, anexe `/tmp/<arquivo>.lss` no botão de arquivo (`browse upload --tab <TAB> --ref <REF> --files /tmp/<arquivo>.lss`) e clique em `Import survey`.
4. Aguarde `settle` (`--timeout 30000`) e confira o quadro `Survey structure import summary`:
   - Deve exibir `Success` e `Import of survey is completed.`, além das contagens esperadas de grupos, questões, atributos, respostas e subquestões.
5. Clique em `Go to survey` e registre o `<NEW_SID>` da URL `/admin/survey/sa/view/surveyid/<NEW_SID>`, conferindo: título, descrição, administrador, e-mail, data de expiração e `questionindex` (índice incremental).

## Fluxo 2 — Pré-visualizar e testar regras no navegador

### Particularidades do LimeSurvey 3.23 (tema `fruity`)

- **Upload obrigatório (`type="|"`):** a validação exige `mandatory="Y"` **e** o atributo de questão `min_num_of_files="1"`. Quando ativos, a pergunta exibe `*` e o alerta vermelho `Por favor, carregar um arquivo`.
- **Cabeçalho HTML (Bootstrap 3):** `align-items-center` do Bootstrap 4 não surte efeito. Use `<h1>` (`font-size:16px;font-weight:bold;margin-top:20px`) para a primeira linha institucional ao lado do logotipo e `<p>` (`font-size:12px`) para as linhas subordinadas.
- **Placeholders:** `TOKEN:FIRSTNAME` (em caixa alta com acentos, exatamente igual ao nome do auditado nas regras `grelevance`) só é substituído quando o preview é aberto com `?token=<TOKEN>` válido.

### Sequência de verificação

1. Na visão geral `/admin/survey/sa/view/surveyid/<SID>`, colete via `eval` os links `a[href*="gid/"]` para mapear os `<GID>` dos grupos (ex.: `Identificação`, `Achado 3 — Situação 1`, `Ciência`).
2. Abra a tela de boas-vindas (com `/token/<TOKEN>/newtest/Y` se já houver participantes) e capture screenshot para validar logotipo, cabeçalho, saudação, processo, prazos e e-mail de contato.
3. Abra `previewgroup/sid/<SID>/gid/<GID>` dos grupos representativos:
   - Teste as alternativas de rádio/decisão (ex.: marcar a opção de cumprimento integral e depois a de discordância) e verifique com `eval` no DOM `.question-container` se os campos condicionais exibem exatamente os textos e a flag `mandatory` esperados.

## Fluxo 3 — Extrair, preparar e importar participantes (CSV)

### Extrair participantes de um survey de referência

Quando precisar reaproveitar cadastro e tokens de um survey anterior (ex.: survey do questionário principal), extraia todas as páginas usando `fetch` dentro de `browse eval` na aba autenticada (o padrão `pageSize` da grade é 10):

```javascript
async () => {
  const parseRows = (doc) => [...doc.querySelectorAll("#token-grid tbody tr")].map(tr => {
    const tds = [...tr.querySelectorAll("td")].map(td => td.innerText.trim());
    return {tid: tds[2], firstname: tds[3], lastname: tds[4], email: tds[5], emailstatus: tds[6], token: tds[7], language: tds[8]};
  });
  let all = [], seen = new Set();
  for (let p = 1; p <= 20; p++) {
    const html = await (await fetch(`/limesurvey-novo/index.php/admin/tokens?surveyid=<REF_SID>&sa=browse&TokenDynamic_page=${p}`)).text();
    const rows = parseRows(new DOMParser().parseFromString(html, "text/html"));
    const fresh = rows.filter(r => r.tid && !seen.has(r.tid));
    if (!fresh.length) break;
    fresh.forEach(r => { seen.add(r.tid); all.push(r); });
  }
  return all;
}
```

### Regras do CSV de importação

- **Codificação e colunas:** UTF-8, separado por vírgula (`,`), cabeçalho `firstname,lastname,email,emailstatus,token,language,usesleft`.
- **Chave crítica (`firstname`):** deve coincidir caractere a caractere (maiúsculas e acentos) com o valor usado nas equações `TOKEN:FIRSTNAME == "..."` do `.lss`.
- **Múltiplos e-mails (`;`):** o LimeSurvey 3.23 aceita nativamente vários endereços separados por ponto e vírgula (`a@x;b@y`) no campo `email` (envia para todos). Deduplique endereços repetidos no mesmo campo (case-insensitive, preservando a ordem) antes de gerar o CSV para evitar envios duplicados.
- **Filtro por escopo:** inclua apenas os auditados que devem responder ao survey (ex.: apenas os respondentes quando os não respondentes não participam da coleta).

### Passos de importação na UI

1. Copie o CSV para `/tmp/<participantes>.csv`.
2. Acesse `/admin/tokens/sa/index/surveyid/<SID>` e clique em `Initialise participant table`.
3. Acesse `/admin/tokens/sa/import/surveyid/<SID>`, faça `snapshot` e:
   - Anexe `/tmp/<participantes>.csv` (`browse upload`).
   - **Selecione explicitamente o separador `Comma`** (nunca deixe `Automatic` quando houver `;` dentro da coluna `email`, pois o detector automático pode confundir o delimitador).
   - Mantenha `Filter blank email addresses` e `Filter duplicate records` marcados e `Allow invalid email addresses` desmarcado.
   - Clique em `Upload`.
4. Confira no resultado `Uploaded CSV file successfully` que o número de `records imported` coincide com o total de linhas do CSV, depois abra `/admin/tokens/sa/browse/surveyid/<SID>` para conferir acentuação UTF-8, e-mails e tokens.

## Fluxo 4 — E-mail de confirmação para o respondente do Grupo 1

- A confirmação padrão do LimeSurvey (`sendconfirmation: Y`) envia apenas para o(s) e-mail(s) da tabela de participantes.
- Para enviar confirmação também ao e-mail digitado no formulário (ex.: pergunta de código `email` no Grupo 1):
  1. Em *Notifications & data*, preencha **Send basic admin notification email to** (`emailnotificationto`) com `{email.NAOK}`.
  2. Em *Email templates*, substitua obrigatoriamente o assunto e o corpo do template **Basic admin notification** pelo texto institucional de confirmação ao gestor — removendo links internos (`{VIEWRESPONSEURL}`, `{EDITRESPONSEURL}`, `{STATISTICSURL}`) antes de ativar o survey.

## Encerramento

Ao concluir qualquer operação com esta skill:
1. Remova os arquivos temporários em `/tmp/` usados para upload.
2. Retorne a aba aberta para `/admin/survey/sa/view/surveyid/<SID>` mantendo o survey inativo (salvo pedido contrário).
3. Informe ao usuário o `<SID>` criado/operado, as contagens confirmadas na interface (grupos/questões/participantes importados) e os links exatos validados.
