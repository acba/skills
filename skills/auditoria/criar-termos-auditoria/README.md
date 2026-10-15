# Criar Termos de Auditoria

Skill para redigir e revisar Termos de Auditoria em Markdown e gerar um painel SVG/PNG e uma minuta de ata DOCX. O conteúdo técnico deve ser elaborado com base nos documentos de cada trabalho; o script valida a estrutura e renderiza os arquivos.

## Uso local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_terms.py /caminho/para/termos.md --validate-only
python scripts/build_terms.py /caminho/para/termos.md --output-dir /caminho/para/saida
```

Comece por `assets/modelo-termos-auditoria.md`. O arquivo `assets/01-Termos de auditoria.md.txt` é um exemplo específico do TCE-RJ, não um modelo genérico. Para usar o logo institucional, informe `--logo /caminho/logo.png`. Sem esse argumento, o painel não inclui logo.

Saídas: `Termos de Auditoria.md`, `Termos de auditoria.svg`, `Termos de auditoria.png` e `Ata de Reunião.docx`. A ata permanece uma minuta com pendências até que dados reais da reunião sejam fornecidos.
