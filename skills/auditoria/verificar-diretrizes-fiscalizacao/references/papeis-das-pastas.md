# Papéis das pastas do projeto

Use o cadastro e as fontes para confirmar responsabilidades. Nomes diferentes
podem representar a mesma função; não conclua conformidade apenas pela árvore.

| Local padrão | Responsabilidade |
|---|---|
| `fiscalizacao.yml` | Identificação, objetivo, jurisdicionados, caminhos e templates |
| `.templates/` | Modelos editáveis; dados específicos vêm do cadastro e das fontes |
| `.agents/skills/` | Instruções e recursos locais para agentes |
| `00-Estudos_Preliminares/` | Antecedentes, referências externas e análise de riscos |
| `01-Planejamento/` | Termos, estratégia, plano, matriz e instrumentos de coleta |
| `02-Execucao/01-Coleta/` | Exportações e anexos originais, separados por instrumento e organização |
| `02-Execucao/02-Avaliacoes/` | Avaliações e pareceres, identificados por instrumento e execução |
| `02-Execucao/03-Cenarios/` | Bases e ajustes por cenário; relação com o cenário-pai |
| `02-Execucao/04-Execucao_Procedimentos/` | Insumos e resultados dos procedimentos por cenário |
| `02-Execucao/05-Matriz_Achados/` | Consolidação e rastreabilidade dos achados |
| `03-Relatorios/` | Relatórios individuais e consolidado, com anexos |
| `04-Publicacao/` | Produtos para publicação, quando prevista |
| `05-Entrega/releases/` | Conjuntos congelados, manifestos e documentos de entrega |
| `99-Comunicacoes/` | Comunicações formais e fontes originais |
| `99-Gestao_e_Controle/controle.sqlite` | Cadastro operacional, execuções, cenários, produtos e revisão |
| `99-Gestao_e_Controle/01-Logs/` | Logs legíveis por execução |
| `99-Gestao_e_Controle/02-Exportacoes/` | Exportações derivadas do controle |
| `99-Gestao_e_Controle/03-Backups/` | Snapshots consistentes do controle |
| `docs/` | Documentação de operação e arquitetura |
| `scripts/` | Extensões locais, quando necessárias, e seus testes |

A estrutura completa pode conter pastas vazias de bootstrap. Pastas com IDs
surgem quando há produtos a organizar. Examine divergências de responsabilidade,
duplicações de fontes, controles fora do local declarado, produtos antigos e
dependências externas não registradas. Uma pasta vazia, sozinha, não é defeito.

O `control_root` e o caminho do SQLite são os declarados no cadastro. Um banco
ativo paralelo na raiz precisa ser investigado; backups identificados não são
um segundo controle ativo. Templates e skills copiados na criação são fontes
locais: alterações posteriores no Argos não os atualizam automaticamente.
