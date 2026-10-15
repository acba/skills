---
name: criar-termos-auditoria
description: Elaborar, revisar e atualizar Termos de Auditoria para planejamento de auditorias e fiscalizações; estruturar objeto, problema, riscos, critérios, evidências, escopo, asseguração, entregas e cronograma. Use também quando o usuário pedir um canvas ou painel dos termos, ou uma minuta de ata da reunião de planejamento. Produz Markdown e, com o script incluído, SVG, PNG e DOCX.
---

# Criar Termos de Auditoria

## Insumos e decisão editorial

Leia os documentos do trabalho e o pedido do usuário. Use `assets/modelo-termos-auditoria.md` como estrutura inicial; `assets/01-Termos de auditoria.md.txt` é apenas um exemplo específico de LGPD no TCE-RJ. Consulte `references/formato.md` para a sintaxe e `references/qualidade.md` para a revisão. Preserve as fontes e a terminologia institucional do trabalho. Se já houver termos, revise o arquivo existente e registre as mudanças relevantes.

Produza primeiro **Termos de Auditoria em Markdown**, com frontmatter YAML e as 12 seções abaixo. Diferencie informações documentadas, propostas e pendências. Onde faltar dado essencial, use `[PENDENTE: especificar ...]` e indique ao usuário o que precisa ser confirmado. Não crie número de processo, unidade, norma, data, participante, decisão ou prazo. Não converta riscos hipotéticos em achados nem trate o painel como conclusão de auditoria.

## Estrutura obrigatória

1. Objeto
2. Critérios
3. Evidências
4. Problema de Auditoria
5. Riscos da Fiscalização
6. Stakeholders
7. Nível de Asseguração
8. Objetivo
9. Não Escopo
10. Escopo
11. Entregas
12. Datas e Ausências

Use os títulos `## 1. Objeto` até `## 12. Datas e Ausências`, nessa ordem. Renumere subtítulos internos ao reorganizar material legado. Em `Datas e Ausências`, registre tanto marcos temporais conhecidos quanto ausências conhecidas; mantenha pendências explícitas se não houver informação. O nível de asseguração deve corresponder aos procedimentos e limitações documentados.

## Revisão antes da geração

Verifique a ligação entre objeto, problema, riscos, objetivo e escopo. Confira se critérios são aplicáveis, se evidências podem sustentar os procedimentos, se escopo e não escopo são coerentes e se entregas e datas são viáveis. Identifique lacunas e contradições sem resolvê-las por suposição. O script verifica formato e presença de campos; a revisão técnica do conteúdo cabe ao agente e à equipe de auditoria.

## Arquivos de saída

Com as dependências de `requirements.txt` instaladas, execute a partir da pasta da skill:

```bash
python scripts/build_terms.py /caminho/para/termos.md --validate-only
python scripts/build_terms.py /caminho/para/termos.md --output-dir /caminho/para/saida
```

O comando copia o Markdown validado para `Termos de Auditoria.md`, renderiza o painel `Termos de auditoria.svg` e `.png`, e cria `Ata de Reunião.docx`. Para incluir identidade visual, passe `--logo /caminho/logo.png` **somente** se o usuário fornecer ou autorizar o logo dessa instituição. O logo do TCE-RJ incluído em `assets/` não se aplica a outros órgãos.

Inspecione o PNG gerado para identificar texto cortado, sobreposto ou ilegível; corrija o conteúdo ou o renderizador e gere novamente. Se houver ferramenta de visualização de DOCX, confira também a minuta. O DOCX é sempre uma **minuta**: preencha `participantes`, `data_reuniao`, `horario_reuniao`, `local_reuniao` e `decisoes_reuniao` apenas a partir de registros reais. A pauta baseada nos termos não demonstra que houve reunião, discussão ou aprovação. Entregue os arquivos com uma lista curta das pendências de confirmação.
