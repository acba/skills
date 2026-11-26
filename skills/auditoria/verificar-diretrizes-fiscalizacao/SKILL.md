---
name: verificar-diretrizes-fiscalizacao
description: Avaliar o cumprimento do DIRETRIZES.md em repositórios de fiscalização, conhecendo o papel das pastas e confrontando dados, scripts, controles, cenários e relatórios. Use quando o usuário pedir diagnóstico de conformidade do projeto, avaliação da organização das pastas, rastreabilidade, atualização dos artefatos, reprocessamento, branches de ajuste ou releases. Produza problemas comprovados, correções concretas e impacto esperado da melhoria, com prioridade e critérios de aceite. Não use para mera redação de relatório, execução de script ou revisão isolada de uma questão sem pedido de diagnóstico do projeto.
metadata:
  requirements: Acesso ao repositório e Python 3.9 ou superior para os utilitários locais; Git e rg quando disponíveis. Referências, modelo e código incluídos; as diretrizes são lidas do projeto avaliado. Não requer rede nem provedores de IA pagos.
---

# Verificar diretrizes de fiscalização

## Resultado e limites

Entregue uma avaliação baseada nas diretrizes vigentes e nas evidências do projeto. Explique **o problema, a correção e o impacto esperado da melhoria**. Produza uma matriz cobrindo todos os requisitos, um mapa funcional das pastas e um plano priorizado e verificável.

Uma avaliação identifica atendimento e lacunas; não garante conformidade sem inspeção suficiente nem certifica atos externos. Não aplique correções, migre pastas, altere decisões ou execute lotes pagos apenas porque encontrou um problema. Quando a implementação estiver solicitada, avance no escopo autorizado e registre a validação. Preserve alterações preexistentes, originais e releases.

## Fontes e recursos obrigatórios

1. Leia o `DIRETRIZES.md` do projeto e as instruções/README disponíveis. Registre caminho, origem, versão e SHA-256. Se o projeto não tiver `DIRETRIZES.md`, pare e informe a ausência; esta skill não mantém uma cópia própria de diretrizes.
2. Leia [papéis das pastas](references/papeis-das-pastas.md) para mapear as responsabilidades do boilerplate Argos e de estruturas equivalentes. A referência orienta a investigação; confirme cada papel no conteúdo e nos scripts.
3. Leia [roteiro de verificações](references/roteiro-verificacoes.md) para selecionar evidências e casos de teste.
4. Use [modelo de relatório](assets/relatorio-avaliacao.md) e o formato JSON gerado pelo utilitário. Leia [contrato das saídas](references/contrato-saidas.md) antes de preencher o JSON.

### Seleção e conciliação das diretrizes

Use esta ordem: arquivo expressamente indicado pelo usuário; `DIRETRIZES.md` da raiz avaliada. Sem diretrizes locais ou indicadas, pare e informe a ausência; não há modelo substituto dentro da skill.

Se houver diretrizes locais ou explicitamente indicadas, a matriz cobre integralmente a fonte selecionada. Faça a conciliação por significado e evidência; coincidência de ID não garante igualdade. Não una regras conflitantes automaticamente nem trate adaptação local como descumprimento sem avaliar aplicabilidade e autoridade. Registre a decisão/limitação sobre o conflito e o efeito no diagnóstico.

Arquivo indicado ou local existente, mas ilegível/malformado, exige registrar o impedimento; não substituí-lo silenciosamente pelo modelo. Pode prosseguir com diagnóstico de referência explicitamente delimitado, preservando a pendência local. Nunca crie ou substitua o DIRETRIZES.md do projeto apenas para executar a avaliação.

Mantenha a versão das diretrizes do projeto e registre sua origem. A skill não mantém nem sincroniza uma cópia própria de regras.

## 1. Preparar a avaliação

Identifique raiz, escopo, fase da fiscalização, destinos de saída, restrições e estado do Git. Distingua avaliação integral de diagnóstico dirigido. Em avaliação dirigida, mantenha todos os requisitos na matriz e marque os fora do exame como `Não verificado`, com justificativa, ou `Não aplicável`, quando efetivamente inaplicáveis.

Use o destino indicado pelo usuário. Sem destino específico, respeite a política local; na ausência dela, use `/tmp/argos-avaliacao-diretrizes/<id>/`. Não escreva controles de avaliação em pastas arbitrárias: se a execução registrar controles no projeto, use o `control_root` autorizado. Não apague saídas existentes.

Resolva `<skill_dir>` como a pasta desta skill e `<python>` como o Python disponível no projeto. Na ausência de um ambiente específico do projeto, use `python3`. Execute:

```text
<python> <skill_dir>/scripts/avaliacao.py preparar --root <raiz> --output <destino-novo>
```

Acrescente `--diretrizes <arquivo>` para selecionar uma fonte expressa. Sem essa opção, o utilitário usa o `DIRETRIZES.md` local e falha se ele não existir. A conciliação substantiva de diferenças continua responsabilidade do avaliador.

O utilitário inventaria caminhos sem ler conteúdos de evidências e gera `inventario.json` e `avaliacao.json`, inicialmente **Não verificado**. Ele não avalia conformidade nem detecta todos os controles. Leia o resultado e complete a inspeção. Não entregue o esqueleto como avaliação concluída.

## 2. Conhecer a função real das pastas

Inventarie pastas de domínio, controles, scripts, documentação, dados externos e arquivos da raiz. Para cada área relevante, registre:

- caminho atual e função observada, com evidência;
- responsabilidade esperada e categoria funcional equivalente;
- entradas, produtos, fontes mantidas e geradores;
- relação com cenários, execução, revisão, congelamento e entrega;
- divergência, impacto e correção necessária, ou equivalência válida.

Mapeie planejamento, coleta, evidências, comentários, cenários, relatórios, publicação, entrega, comunicações, controles e automação. Inclua áreas inesperadas e controles dispersos. Não classifique só pelo nome: `99-Avaliacao_Evidencias` pode conter resultados substantivos, e `docs/` pode conter revisões que precisam de referência central.

Pastas ausentes e nomes distintos não são defeitos por si. Aceite estrutura equivalente que satisfaça responsabilidade, proveniência e operação. Não exija pastas vazias para etapas não aplicáveis. Uma árvore organizada também pode esconder dados desatualizados e regras incoerentes.

## 3. Confrontar os requisitos com evidências

Extraia os identificadores da fonte selecionada. A quantidade não deve ficar fixada no código ou na avaliação. Não omita requisitos novos nem diferenças de conciliação.

Percorra cadeias completas, por diversidade e risco: fonte → ajuste → avaliação → resultado → documento → entrega. Leia fontes determinantes, configurações e funções executoras. Diferencie controle documentado, implementado, exercitado e validado. Marque alcance e amostragem.

Concentre o exame material em:

1. Fonte autorizada, identidade e contratos de dados.
2. Centralização dos controles e consulta de estado recalculado.
3. Dependências, geração individual/lote, invalidação e plano seletivo.
4. Branch antes do ajuste, cenário-pai, isolamento e impacto comparado.
5. Releases com manifesto e proteção efetiva contra sobrescrita.
6. Coerência matriz–mapa–questionário, predicados próprios de situações e aplicabilidade.
7. Avaliação de IA: conversão, critérios, checkpoints, erro separado de conclusão, custo e revisão humana.
8. Comentários, ajustes, painéis, índices e universos.
9. Sincronização de dados, textos, gráficos, anexos e pacotes.
10. Ambiente, testes, qualidade documental e separação por destinatário.

Use `Atende`, `Atende parcialmente`, `Não atende`, `Não verificado` e `Não aplicável` conforme a diretriz. Ausência de evidência não comprova descumprimento; ausência demonstrada de controle aplicável pode comprová-lo. Um `completed` histórico não é atualidade; hash íntegro não é conteúdo correto; branch não isola uma planilha externa; tag sem proteção não garante imutabilidade.

Registre evidências com caminho e função/linha ou chave de registro, versão e alcance. Não reproduza segredos. Hipóteses de causa e impactos potenciais devem ficar explicitamente separados dos fatos. Leia código antes de propor flag ou comando; rotule interfaces futuras como propostas.

## 4. Formular problema, correção e impacto

Consolide problemas por controle ou comportamento observado, vinculando todos os requisitos pertinentes. Na seção 5 do relatório, use o formato enxuto abaixo. Não inclua campos de Causa, Indicador, Preservação, Dependências, Responsável ou Esforço. Essa adaptação da apresentação prevalece sobre a ficha ampliada da seção 22.3 das diretrizes; as verificações substantivas do projeto permanecem aplicáveis.

| Campo | Instrução |
|---|---|
| Problema | Explique comportamento observado e condição em que ocorre |
| Evidência | Localize a comprovação; descreva limite e amostragem |
| Impacto atual | Registre efeito observado; identifique risco potencial separadamente |
| Correção | Indique mudança concreta no arquivo, contrato, componente ou fluxo |
| Impacto da melhoria | Explique o benefício esperado, sem inventar economia |
| Prioridade | P0–P3 com motivo e marco a que se aplica |
| Aceite | Indique teste/confronto que passará depois da correção |
| Estado | Indique se está proposto, em execução, corrigido, validado ou pendente de decisão |

Exemplo: “A consulta imprime somente o último manifesto, sem comparar as fontes atuais. Correção: verificar dependências registradas, expor causa e descendentes e gerar plano sem chamadas pagas. Impacto esperado: reduzir geração de documentos com bases antigas e tempo de identificação do que repetir. Aceite: alterar base de teste após `completed`; consulta marca descendentes desatualizados e preserva avaliações compatíveis.”

Não estime horas ou dinheiro sem medição. Aponte pendências metodológicas para decisão humana. Preserve boas práticas. Priorize correção material e preservação, depois rastreabilidade/visibilidade, depois manutenção e convenções.

## 5. Produzir e validar a entrega

Complete os produtos:

- `relatorio-avaliacao.md`: diagnóstico, problemas, correções, impactos e plano conforme o modelo;
- `avaliacao.json`: metadados, mapa de pastas, todos os requisitos, problemas e boas práticas;
- `inventario.json`: fotografia auxiliar produzida na preparação.

No relatório, inclua a matriz integral ou uma tabela integral anexa com link. Uma avaliação dirigida pode ser curta, mas não esconder itens não examinados. Não calcule nota geral que dilua bloqueadores.

Execute:

```text
<python> <skill_dir>/scripts/avaliacao.py validar --avaliacao <destino>/avaliacao.json
```

Sem `--diretrizes`, o validador usa a fonte registrada na avaliação. Fonte local desaparecida não é substituída automaticamente. Use `--diretrizes` para informar a localização correta e reconcilie eventual mudança de versão.

O validador verifica cobertura, campos, referências e estados. **Ele não confirma a veracidade das evidências nem que o repositório cumpre as regras.** Corrija erros estruturais e revise o conteúdo: cada conclusão deve ter suporte; cada melhoria deve ter benefício e aceite concretos; o Markdown deve refletir o JSON.

Reporte conclusão com principais problemas e melhorias, caminhos gerados, alcance e pendências. Se a implementação foi solicitada, compare antes/depois e só marque como corrigido/validado o que foi efetivamente realizado e conferido.

## Critério de conclusão

Encerre quando todas as diretrizes estiverem explicitamente classificadas; as funções das áreas relevantes estiverem mapeadas; os problemas tiverem evidência, correção e impacto; e a entrega passar pela validação estrutural e revisão de conteúdo. Lacunas de acesso podem permanecer como `Não verificado`, com ação para resolvê-las. Nunca transforme uma lacuna em atestado de conformidade.
