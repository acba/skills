# Roteiro de verificações por risco

Use o DIRETRIZES.md vigente como regra. Esta referência seleciona testes, sem substituir a matriz integral.

| Tema | Ler/inspecionar | Verificação e efeito esperado |
|---|---|---|
| Controle central | Configuração de caminhos, registro de execuções e logs | Rotina individual e lote aparecem no mesmo controle, sem fonte paralela |
| Atualidade | Função de consulta e dependências declaradas | Mudar entrada depois de `completed` revela descendentes desatualizados |
| Geração seletiva | CLI, filtros, orquestrador e plano | Individual e lote compartilham núcleo; escopo incompleto é explicitado |
| Cenários | Branches/commits, manifestos e ledger de ajustes | Novo ajuste parte do pai; dados externos ficam isolados |
| Releases | Manifesto, geradores e armazenamento | Tentativa de sobrescrita em cópia de teste falha sem mudança |
| Regras | Matriz, mapa, executor e casos | Situação falsa não ocorre por achado verdadeiro ou motivo isolado |
| Questionário | Fonte, versão nativa publicada e exportação | IDs/relevâncias reais preservados; reconstrução identificada |
| Coleta | Bruto, cadastro, inventário e seleção | Arquivo e resposta pertencem ao auditado correto; duplicidades explicadas |
| Ajustes | Valores anteriores/propostos/aplicados e aprovação | Registro sem mudança não entra na contagem de alterações |
| IA | Conversão, catálogo, checkpoint, tratamento de erro e revisão | Prompt/contexto alterado invalida análise; timeout não vira conclusão |
| Custo | Tentativas, plano, usage e política de limites | Repetições têm motivo; estimativas separadas de realizado |
| Comentários | Seções, decisões, ajustes e painel | Mapeamento seguro evita chamadas redundantes e recriação de situação saneada |
| Cálculos | Pesos, denominadores e coorte | Populações reconciliadas; oficial e comparável distinguidos |
| Sincronização | Bases, JSON, contextos, MD/DOCX/PDF e ZIP | Mesmos dados e regras para a finalidade; hash não mascara texto antigo |
| Documento | Recursos, campos, conversor e PDF renderizado | Sem perda de conteúdo, imagens, notas ou tabelas pertinentes |
| Entrega | Especificação, conjuntos de IDs e conteúdo | Quantidade correta com destinatário duplicado/faltante é rejeitada |
| Ambiente | Dependências e comandos documentados | Ferramentas e flags existem; ambiente testado pode ser reproduzido |

Registre quando um teste só foi analisado estaticamente, quando foi executado e quando foi validado no conteúdo. Não simule implementação de controle ausente para declará-lo atendido. Não rode modelos pagos para diagnosticar estrutura ou mudar redação. Todos os testes com escrita usam cópias ou áreas isoladas e mantêm os originais.

Prioridades seguem DIRETRIZES.md: P0 bloqueio material comprovado; P1 lacuna de controle a corrigir antes do marco pertinente; P2 manutenção/retrabalho; P3 convenção incremental. Fundamente a consequência e não atribua gravidade pelo nome da pasta.
