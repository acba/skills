---
name: operar-argos
description: Operar uma fiscalização pelo Argos CLI (`argos <objeto> [<ação>]`): matrizes de planejamento e achados, survey e coleta no LimeSurvey, catálogo de avaliações e avaliação de evidências por IA com revisão humana, ajustes e cenários, auditoria, índices e gráficos, contraditório (comentários do gestor), comunicação com auditados (envio determinístico em lote e sincronização de inbox via AudCom), relatórios e documentos avulsos DOCX/PDF, pipeline, status e backup do controle. Use ao pedir qualquer uma dessas operações ou ao retomar uma execução.
---

# Operar uma fiscalização com Argos

Leia `AGENTS.md`, `README.md` e `fiscalizacao.yml` do projeto. Os comandos têm a
forma `argos <objeto> [<ação>]`; descubra objetos, ações e parâmetros com
`argos --list-operations` e `argos <objeto> --help`. Cada ação tem só os seus
parâmetros. `argos init` é o bootstrap e não aparece no catálogo de operações. Resolva o
executável instalado no ambiente; evite copiar scripts de outra fiscalização
para substituir operações do catálogo de operações.

## Comandos por objeto

Os caminhos e flags abaixo são exemplos; o `README.md` traz o fluxo completo.

- `init <destino> --numero NNN/AAAA --nome "..." --objetivo "..."`: cria o projeto e o controle SQLite;
- `status [--produto ID] [--json]`: integridade e atualidade dos produtos e execuções;
- `controle backup|restaurar|limpar|avaliacoes|congelar`: `backup --output b.sqlite`; `restaurar b.sqlite --output novo.sqlite` (recusa destino existente); `limpar` retira do controle produtos com arquivo ausente ou substituídos; `avaliacoes [--modelo M --estado E --limite N]` (também `--provider`, `--tipo`, `--caso`) lista as avaliações de IA gravadas; `congelar [--id MARCO --motivo "..." --tag TAG --caminhos ... | --verificar | --listar]` congela artefatos em `99-Gestao_e_Controle/congelados.yml` com hashes SHA-256 e valida integridade em disco;
- `planejamento validar --matriz m.md --questionario q.md --mapa mapa.xlsx --catalogo cat.yml [--estrito] [--output rel.json]`: validação cruzada única entre Matriz, Questionário (SurveyMD), Mapa de Verificação e Catálogo de Evidências (exige ao menos dois artefatos);
- `matriz init|rascunho|validar|publicar|mapa|arvore`: `init [--tipo planejamento|achados]`; `validar matriz.md [--strict]` não gera produtos; `publicar matriz.md [--pdf] [--html-output x.html]` valida antes de gerar o DOCX; `mapa matriz.md --output mapa-draft.xlsx [--config-fontes f.yml]`; `arvore --mapa revisado.xlsx --questionario q.md --output arvore.html`; `rascunho resultado.json` cria o draft da matriz de achados, que depois segue `validar`/`publicar` com `--tipo achados` (e `--resultado-auditoria r.json` para o modo enriquecido). O front matter da matriz precisa declarar `title`, `fiscalizacao`, `jurisdicionados` e `objetivo_auditoria`; para controlar colunas, `larguras_colunas_percentuais` com soma exata de 100. Consulte `docs/ESPECIFICACAO_MARKDOWN_MATRIZ_PLANEJAMENTO.md`, `docs/ESPECIFICACAO_MARKDOWN_MATRIZ_ACHADOS.md` e `docs/ESPECIFICACAO_UNIFICADA_MATRIZES_V1_3.md`;
- `survey gerar|coletar|baixar-anexos`: `gerar q.md [--guia] [--pdf]`; `coletar --survey-id ID --output-dir pasta/ [--dry-run]` (API do LimeSurvey); `baixar-anexos respostas.xlsx --output-dir anexos/`;
- `catalogo gerar|validar|aprovar|prompts`: o catálogo de avaliações (prompts) da avaliação de evidências, sem chamar modelos; provider remoto exige o catálogo aprovado;
- `evidencias preparar|avaliar`: `preparar --coleta pasta/ --respostas r.xlsx --output-dir evidencias/` monta a árvore de forma idempotente; `avaliar --catalogo C.yml --questionario q.md --respostas r.xlsx --raiz-evidencias evidencias/ --avaliadores provider:modelo[:perfil][@nivel] [--preflight]` executa avaliadores e juiz com deduplicação semântica no SQLite (`--avaliadores` é obrigatório; `--provider-juiz`/`--modelo-juiz` escolhem o juiz; `--casos`, `--auditados`, `--questoes` restringem o escopo). `@nivel` define o nível de raciocínio e o provider recusa antes da chamada o que não suporta. As chaves vêm do ambiente ou do `.env` da raiz; o andamento sai em stderr (`--no-progress` desliga) e `--preflight` planeja sem chamar modelo. `--retry-failed` reenvia falhas confirmadas e `--retry-unknown` reenvia chamadas `unknown`, que podem ser cobradas de novo;
- `revisao exportar|decidir|importar|finalizar`: revisão humana por `run_id`, de evidências ou de contraditório; `exportar --run-id ID --formato json|xlsx --output r.xlsx`, `importar r.xlsx`; `decidir --acao confirmar|substituir|adiar` (a coluna `action` do lote usa os mesmos valores); `finalizar --run-id ID [--output final.xlsx] [--painel-output painel.xlsx]` gera o painel que é a fonte `aevi:` da matriz;
- `ajustar --respostas base.xlsx --ajustes ajustes.xlsx [--scenario-id ID]`: aplica ajustes sem sobrescrever a base e registra cenário filho imutável;
- `auditar --base-auditados b.xlsx --mapa mapa.xlsx --fontes r.xlsx [--mapa-fontes id=caminho] [--matriz matriz.md] --output resultado.json`: executa os procedimentos do mapa e resolve a aplicabilidade da matriz; `--validar-insumos --exportacao-survey s.xlsx` valida os insumos antes;
- `comparar --resultado-anterior antes.json --resultado-auditoria depois.json --output impactos.json`: impactos por auditado (o `--impactos` dos relatórios e dos gráficos);
- `contraditorio preparar|avaliar|consolidar|projetar`: `preparar --resultado-auditoria r.json --lss-output c.lss --anexos-output a.zip` gera o survey de comentários do gestor; `avaliar --comentarios survey-comentarios.xlsx [--escopo situacao|item|ambos] ...` avalia os comentários exportados do survey (padrão `ambos`, com plano e `--max-model-requests` sobre a soma; `--mapeamento` e `--respostas` (a base de respostas atual) valem só com `ambos`); `consolidar` (depois da revisão das prioridades) gera propostas de ajuste, contexto e painel em draft; `projetar --contexto c.json --scenario FILHO --contexto-output aplicado.json` projeta o contexto pelos ajustes já aplicados no cenário filho (com `--painel` e `--painel-output`, também o painel). `--preflight` em `avaliar` planeja sem gastar;
- `comunicacao init|auth|status|enviar|sincronizar|pendencias|reenviar|registrar|importar-historico|historico`: `init --mailbox caixa@orgao.gov.br` configura a caixa remetente (obrigatória no primeiro acesso, sem remetente padrão hardcoded) e protege o `.gitignore`; `auth` executa EWS/MFA; `status` exibe diagnóstico sanitizado, resumo de envios e campanhas no `controle.sqlite`; `enviar --template t.md --manifest m.xlsx [--remetente R] [--campanha C] [--prazo-limite DATA] [--criterio-atendimento resposta_email|email_com_anexo|survey_limesurvey|manual] [--preview-dir dir/] [--dry-run | --teste-para email | --enviar]` valida 100% do lote (inclusive anexos e `arquivo.zip::membro` com `quando:`), gera `index.html` e aplica idempotência tripla (`controle.sqlite` + JSONL + Exchange); `sincronizar [--caixa C] [--dias N] [--exportar inbox.jsonl]` sincroniza caixas monitoradas e cruza recibos de leitura e respostas contra `comunicacao_envio`; `pendencias [--campanha C] [--sem-ciencia | --sem-atendimento | --somente-vencidos] [--exportar p.xlsx]` acompanha ciência, atendimento e violações de prazo; `reenviar --campanha C [--sem-ciencia | --sem-atendimento] [--prefixo "[LEMBRETE] "] [--dry-run | --teste-para email | --enviar]` envia lembretes dentro do prazo com idempotência por rodada (`#lembrete-N`); `registrar --campanha C [--do-survey resp.csv | --tipo ciencia|atendimento --auditado A]` registra ciência/atendimento manual ou do LimeSurvey; `importar-historico --campanha C` faz backfill retroativo de envios já gravados no controle; `historico --auditado A [--campanha C] [--exportar dossie.md]` exibe a linha do tempo completa do auditado (envios, SHA-256 dos anexos, lembretes, bounces, auto-respostas, ciências e atendimento) e exporta dossiê probatório em Markdown;
- `indice --memoria indice.yaml --respostas r.xlsx [--output resultado.json|.xlsx|.csv] [--rastreio-output rastreio.json]`: compila `argos-index-dsl/v1` e calcula os nós sobre XLSX ou CSV; `indice lote --memorias lote.json --respostas r.xlsx [--output combinado.json] [--xlsx-output combinado.xlsx]` calcula várias memórias sobre a mesma base;
- `graficos --resultado-auditoria r.json [--avaliacoes aval.json] [--output-dir analises]`: tabelas, gráficos PNG e `analises/manifest.json`;
- `documento <arquivo.md>`, `documento relatorio-individual|relatorio-auditoria|anexo-evidencias`: `documento nota.md [--contexto c.json] [--pdf]` publica um Markdown avulso; `relatorio-individual --resultado-auditoria r.json --template m.md --output-dir dir/ [--fase preliminar|final]` gera um DOCX por auditado; `relatorio-auditoria ... --output consolidado.docx` o consolidado; `anexo-evidencias ... --output anexo.docx` o anexo (modelo em `templates.anexo_evidencias`). `--ativos analises/manifest.json` inclui imagens;
- `pipeline [--plan-file pipeline.json] [--until-stage <etapa>] [--dry-run]`: executa a sequência declarativa de etapas; cada etapa usa um id do catálogo de operações (`objeto.acao`).

## Cadastro e caminhos

Na raiz do projeto, execute o comando sem `--project-root` ou `--workspace-root`.
Fora dela, informe somente `--project-root <raiz>`. O banco padrão é o arquivo
declarado em `caminhos.control_db`.

Número, nome, objetivo, processo e jurisdicionados vêm de `fiscalizacao.yml`.
Use flags desses campos quando o usuário pedir uma substituição na execução.
Templates vêm da seção `templates` e ficam em `.templates/`. Não invente
jurisdicionados, datas de referência, conclusões ou modelos ausentes.

## Cálculo de índices

Use uma memória YAML com `formato: argos-index-dsl/v1`. Ela declara conversores,
regras, nós, operações, referências, pesos, seletores e faixas de maturidade.
Não selecione comportamento pelo nome do índice e não presuma descontos: cada
metodologia deve estar declarada no grafo. Definições em formato legado falham
com orientação para migração; não existe fallback silencioso.

Use `--config-estatisticas` para apontar, separadamente, um YAML
`argos.report-config/v1` de estatísticas/comparações e informe também
`--contexto-output` ou `--contexto-json-output`. `--rastreio-output` publica a explicação
por nó e componente sem copiar as respostas originais. Resultados e erros estão
documentados em `docs/INDEX_DSL_V1_RESULTADOS.md`; exemplos normativos ficam em
`docs/index-dsl-v1/exemplos/`.

## Execução

Confira os insumos e a fase do trabalho antes de executar. Use o identificador
de cenário solicitado quando a operação trabalhar com cenários. Originais e
bases anteriores devem ser preservados. Ajustes criam um cenário filho;
avaliações automáticas e mapas gerados são drafts para revisão humana.

Rode `--preflight` antes de qualquer chamada paga a modelos (`evidencias avaliar`,
`contraditorio avaliar`).

## Comunicação com auditados

Para enviar comunicações com `argos comunicacao`, siga sempre a ordem segura:

1. Verifique a configuração com `argos comunicacao status`. Se não houver caixa configurada, oriente `argos comunicacao init --mailbox <email>`; se o cache EWS estiver ausente ou expirado, peça ao humano que execute `argos comunicacao auth` (MFA).
2. Rode `argos comunicacao enviar --template <md> --manifest <xlsx|csv|json> --remetente <email> --preview-dir <dir> --dry-run` e valide 100% dos destinatários, anexos e previews HTML (`index.html`).
3. Teste o envio real para o auditor com `--teste-para <email> --limite 1` (ou `--filtro-id ...`).
4. Só execute `--enviar` após autorização explícita do usuário. Nunca exponha ou versione `.env` nem `msal_token_cache*.bin`.
5. Para acompanhar ciência e prazo após o envio: rode `argos comunicacao sincronizar --dias 14`, depois `argos comunicacao pendencias --campanha <id> [--sem-ciencia | --somente-vencidos] [--exportar pendencias.xlsx]`. Dentro do prazo, reenvie lembretes com `argos comunicacao reenviar --campanha <id> --sem-ciencia --prefixo "[LEMBRETE] "` (validando com `--dry-run` antes de `--enviar`). Para campanhas de survey, cruze atendimentos com `argos comunicacao registrar --campanha <id> --do-survey <respostas.csv>`. Após o prazo, exporte `--somente-vencidos` para subsidiar o Termo de Reiteração.

Inspecione o resultado: diferencie `completed`, `awaiting_input`, `failed` e
pendências de revisão. `--json` produz saída estruturada para leitura de
estado, produtos e avisos.
