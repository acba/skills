---
name: operar-argos
description: Operar uma fiscalização pelo Argos CLI (`argos <objeto> [<ação>]`): matrizes de planejamento e achados, survey e coleta no LimeSurvey, catálogo de avaliações e avaliação de evidências por IA com revisão humana, ajustes e cenários, auditoria, índices e gráficos, contraditório (comentários do gestor), comunicação com auditados (envio determinístico em lote e sincronização de inbox via AudCom), relatórios e documentos avulsos DOCX/PDF, pipeline, status e backup do controle. Use ao pedir qualquer uma dessas operações ou ao retomar uma execução.
---

# Operar uma fiscalização com Argos

Leia `AGENTS.md`, `README.md` e `fiscalizacao.yml` do projeto. Os comandos têm a
forma `argos <objeto> [<ação>] [VALOR] [--flag valor]`. Resolva o executável
instalado no ambiente e não copie scripts de outra fiscalização para substituir
operações do catálogo.

## Descubra flags pela CLI, não pela memória

Esta skill não lista flags: elas mudam e a CLI é a fonte. Consulte só o que
precisa, em JSON:

- `argos --help --json`: códigos de saída, opções globais e índice das operações (id, comando e resumo);
- `argos <objeto> --help --json`: as ações do objeto com seus parâmetros;
- `argos <objeto> <ação> --help --json`: o contrato de uma operação (`parameters[].flags`, `required`, `choices`, `default`, `positional`, `path`).

Evite `argos --list-operations --json`: traz o catálogo inteiro e ocupa muito contexto.
`argos doctor --json` diagnostica Python, extras, binários, variáveis de ambiente
(sem exibir segredos) e a saúde do workspace (`fiscalizacao.yml`, schema do
`controle.sqlite` somente leitura e integridade de `congelados.yml`, saindo com
código 1 se houver erro). `argos init DESTINO --numero NNN/AAAA --nome "..." --objetivo "..."`
cria o projeto e não faz parte do catálogo. Bancos `controle.sqlite` de schema
antigo (sem tabelas de comunicação) são recusados e exigem workspace novo.

## Leia o resultado pelo envelope e pelo código de saída

Rode as operações com `--json`. Todo desfecho, inclusive erro de linha de comando,
imprime em stdout um único objeto com `ok`, `exit_code`, `status`,
`operation_id`, `id`, `reused`, `result`, `error` e `pending`. O andamento vai
para stderr (`--no-progress` desliga).

| Saída | `status` | O que fazer |
| --- | --- | --- |
| 0 | `completed` | Leia `result.summary`, `result.warnings` e `result.products` (caminho e SHA-256). |
| 1 | `failed`, `unknown` | Leia `error`. `unknown` significa envio externo indeterminado: não repita sem entender. |
| 2 | `not_started` | Nada foi executado; corrija a chamada conforme `error.code`, `error.parameters` e `error.hint`. |
| 3 | `awaiting_input` | Falta insumo ou decisão humana: veja `pending`, resolva e retome com `argos --resume <id>`. |

`error` traz `code` estável (`usage`, `missing_input`, `input_validation`,
`identity_required`, `request_blocked`, `remote_service`, `internal_error`...),
`message` e, quando houver, `line`, `source`, `parameters` e `hint`. Decida pelo
`code`, não pelo texto da mensagem. `reused: true` indica execução idêntica
reaproveitada; `--force` executa de novo.

## Mapa do fluxo

A ordem usual de uma fiscalização, com o objeto de cada etapa:

1. Planejamento: `matriz` (`init`, `validar`, `publicar`, `mapa`, `arvore`) e `planejamento validar` para a validação cruzada entre matriz, questionário, mapa e catálogo;
2. Coleta: `survey` (`gerar`, `coletar`, `baixar-anexos`) e `evidencias preparar`;
3. Avaliação por IA: `catalogo` (`gerar`, `validar`, `aprovar`, `prompts`), `evidencias avaliar` e `revisao` (`exportar`, `decidir`, `importar`, `finalizar`);
4. Execução da auditoria: `ajustar`, `auditar`, `indice`, `comparar` e `graficos`;
5. Contraditório: `contraditorio` (`preparar`, `avaliar`, `consolidar`, `projetar`);
6. Relatórios: `matriz rascunho` e `matriz publicar --tipo achados`, `documento` e suas ações, `documento lint` antes de publicar;
7. Comunicação com auditados: `comunicacao` (ver abaixo);
8. Controle: `status`, `controle` (`backup`, `restaurar`, `limpar`, `avaliacoes`, `congelar`, `camadas`) e `pipeline` para a sequência declarativa.

As especificações de formato estão em `docs/` do projeto (matrizes, SurveyMD,
catálogo de avaliação, DSL de índice e contexto de relatórios); consulte a do
artefato que for editar antes de escrevê-lo.

## Cadastro e caminhos

Na raiz do projeto, execute sem `--project-root` ou `--workspace-root`. Fora
dela, informe só `--project-root <raiz>`. Número, nome, objetivo, processo e
jurisdicionados vêm de `fiscalizacao.yml`; use as flags desses campos só quando
o usuário pedir uma substituição. Templates vêm da seção `templates`. Não
invente jurisdicionados, datas de referência, conclusões ou modelos ausentes.

## Regras de execução

- Confira os insumos e a fase do trabalho antes de executar.
- Originais e bases anteriores são preservados: ajustes criam um cenário filho; use o cenário pedido quando a operação trabalhar com cenários.
- Avaliações de IA, mapas e rascunhos gerados são drafts para revisão humana; não os apresente como conclusão.
- Rode `--preflight` antes de qualquer chamada paga a modelos (`evidencias avaliar`, `contraditorio avaliar`); `--retry-unknown` pode ser cobrado de novo.
- Índices: a memória declara toda a metodologia (`formato: argos-index-dsl/v1`); não selecione comportamento pelo nome do índice nem presuma descontos.
- Credenciais vêm do ambiente ou do `.env` da raiz; nunca as passe por flag, imprima ou grave.

## Comunicação com auditados

Siga sempre a ordem segura:

1. `argos comunicacao status --json`. Sem caixa configurada, oriente `argos comunicacao init --mailbox <email>`; com cache EWS ausente ou expirado, peça ao humano que execute `argos comunicacao auth` (MFA).
2. `argos comunicacao enviar ... --dry-run --preview-dir <dir>` e valide 100% dos destinatários, anexos e o `index.html` gerado (0 erros).
3. `argos comunicacao enviar ... --teste-para <email-do-auditor> --limite 1`.
4. `--enviar` só após autorização explícita do usuário. Reexecutar pula quem já recebeu.
5. Depois do envio: `comunicacao sincronizar`, `comunicacao pendencias` (filtros de ciência, atendimento e prazo), `comunicacao reenviar` para lembretes (sempre `--dry-run` antes de `--enviar`), `comunicacao registrar` para atendimentos manuais ou do LimeSurvey e `comunicacao historico` para o dossiê probatório.

Nunca exponha ou versione `.env` nem `msal_token_cache*.bin`.
