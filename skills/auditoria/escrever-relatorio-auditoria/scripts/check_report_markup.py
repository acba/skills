#!/usr/bin/env python3
"""Lightweight checks for TCE-RJ Markdown/Pandoc/Jinja report files.

Erros (código de saída 1): figura ou tabela sem a fonte `(Fonte: ...)` imediatamente
abaixo, fonte em mais de uma linha, rodapé sem definição, `\\newpage` fora de linha própria e
defeitos de Jinja e de fragmentos de achado.

Avisos (não alteram o código de saída, salvo com `--estrito`): fonte com mais de
`--max-fonte` caracteres (padrão 220), nota de rodapé com mais de 4 linhas ou mais de
`--max-nota` caracteres (padrão 600) e ponto e vírgula em texto corrido. O ponto e vírgula é
admitido em listas, em tabelas, em citações (linhas iniciadas por `>`) e em blocos de código.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SOURCE_PREFIX = '<div custom-style="FonteImagem">(Fonte:'
SOURCE_RE = re.compile(r'^<div custom-style="FonteImagem">\(Fonte:.*\)</div>$')
LIST_ITEM_RE = re.compile(r"^([-*+]|\d+[.)]|\([ivxlc]+\)|[a-z][.)])\s")
FIG_RE = re.compile(r"!\[[^\]]+\]\([^)]+\).*\{#fig:[A-Za-z0-9_-]+#\}")
TBL_CAPTION_RE = re.compile(r"^:\s+.+\{#tbl:[A-Za-z0-9_-]+#\}\s*$")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([A-Za-z0-9_.-]+)\]:", re.MULTILINE)
FOOTNOTE_REF_RE = re.compile(r"\[\^([A-Za-z0-9_.-]+)\](?!:)")
JINJA_TAG_RE = re.compile(r"{%\s*(.*?)\s*%}")
ACHADO_HEADING = "## Achado {{ achado.numero }} – {{ achado.nome }}"


def next_nonempty(lines: list[str], start: int) -> tuple[int, str] | None:
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index, lines[index].strip()
    return None


def is_source(line: str) -> bool:
    return line.startswith(SOURCE_PREFIX)


def check_figures(lines: list[str], path: Path) -> list[str]:
    errors: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("!["):
            continue
        if not FIG_RE.search(stripped):
            errors.append(f"{path}:{index + 1}: figura sem label {{#fig:...#}}")
        source = next_nonempty(lines, index + 1)
        if source is None or not is_source(source[1]):
            errors.append(f"{path}:{index + 1}: figura sem fonte imediatamente abaixo")
        elif source[1].startswith(SOURCE_PREFIX) and not SOURCE_RE.match(source[1]):
            errors.append(f"{path}:{source[0] + 1}: fonte deve caber em uma linha: (Fonte: ...)")
    return errors


def check_tables(lines: list[str], path: Path) -> list[str]:
    errors: list[str] = []
    for index, line in enumerate(lines):
        if not TBL_CAPTION_RE.match(line.strip()):
            continue
        table_start = next_nonempty(lines, index + 1)
        if table_start is None or not table_start[1].startswith("|"):
            errors.append(f"{path}:{index + 1}: legenda de tabela sem tabela logo abaixo")
            continue
        found_source = False
        scan_limit = min(len(lines), index + 80)
        for scan in range(table_start[0] + 1, scan_limit):
            stripped = lines[scan].strip()
            if is_source(stripped):
                found_source = True
                if not SOURCE_RE.match(stripped):
                    errors.append(f"{path}:{scan + 1}: fonte deve caber em uma linha: (Fonte: ...)")
                break
            if scan > table_start[0] + 3 and stripped.startswith("#"):
                break
            if scan > table_start[0] + 3 and TBL_CAPTION_RE.match(stripped):
                break
        if not found_source:
            errors.append(f"{path}:{index + 1}: tabela sem bloco de fonte após o corpo")
    return errors


def check_footnotes(text: str, path: Path) -> list[str]:
    defs = set(FOOTNOTE_DEF_RE.findall(text))
    refs = set(FOOTNOTE_REF_RE.findall(text))
    errors: list[str] = []
    for ref in sorted(refs - defs):
        errors.append(f"{path}: rodapé referenciado sem definição: [^{ref}]")
    return errors


def check_avisos(lines: list[str], path: Path, max_fonte: int, max_nota: int) -> list[str]:
    """Avisos de estilo: fonte longa, nota longa e ponto e vírgula em texto corrido."""
    avisos: list[str] = []
    em_codigo = False
    em_nota = False
    nota_inicio = 0
    nota_linhas = 0
    nota_tamanho = 0

    def fechar_nota() -> None:
        if em_nota and (nota_linhas > 4 or nota_tamanho > max_nota):
            avisos.append(
                f"{path}:{nota_inicio}: nota de rodapé longa ({nota_linhas} linhas, {nota_tamanho} caracteres); "
                "mover a definição para o corpo ou para nota metodológica"
            )

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            fechar_nota()
            em_nota = False
            em_codigo = not em_codigo
            continue
        if em_codigo:
            continue
        if FOOTNOTE_DEF_RE.match(line):
            fechar_nota()
            em_nota, nota_inicio, nota_linhas, nota_tamanho = True, index + 1, 1, len(stripped)
        elif em_nota and (line.startswith("    ") or line.startswith("\t")) and stripped:
            nota_linhas += 1
            nota_tamanho += len(stripped)
        elif em_nota and not stripped:
            nota_tamanho += 0
        elif em_nota:
            fechar_nota()
            em_nota = False
        if stripped.startswith(SOURCE_PREFIX):
            if len(stripped) > max_fonte:
                avisos.append(f"{path}:{index + 1}: fonte longa ({len(stripped)} caracteres); manter até cerca de 200 e mover o restante para nota de rodapé")
            continue
        if ";" not in stripped:
            continue
        if (
            stripped.startswith(("|", ">", "{%", "{#", "<", "#", "!["))
            or LIST_ITEM_RE.match(stripped)
            or FOOTNOTE_DEF_RE.match(line)
        ):
            continue
        if em_nota:
            avisos.append(f"{path}:{index + 1}: ponto e vírgula em nota de rodapé; usar ponto final ou vírgula")
            continue
        avisos.append(f"{path}:{index + 1}: ponto e vírgula em texto corrido; usar ponto final, vírgula ou reestruturar")
    fechar_nota()
    return avisos


def check_newpage(lines: list[str], path: Path) -> list[str]:
    errors: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if "newpage" in stripped and stripped != r"\newpage":
            errors.append(f"{path}:{index + 1}: quebra de página deve ser linha isolada '\\newpage'")
    return errors


def check_jinja_balance(lines: list[str], path: Path) -> list[str]:
    stack: list[tuple[str, int]] = []
    errors: list[str] = []
    for index, line in enumerate(lines):
        for tag in JINJA_TAG_RE.findall(line):
            normalized = tag.strip().strip("-").strip()
            token = normalized.split(None, 1)[0] if normalized else ""
            if token in {"if", "for"}:
                stack.append((token, index + 1))
            elif token == "endif":
                if not stack or stack[-1][0] != "if":
                    errors.append(f"{path}:{index + 1}: endif sem if correspondente")
                else:
                    stack.pop()
            elif token == "endfor":
                if not stack or stack[-1][0] != "for":
                    errors.append(f"{path}:{index + 1}: endfor sem for correspondente")
                else:
                    stack.pop()
    for token, line_number in stack:
        closing = "endif" if token == "if" else "endfor"
        errors.append(f"{path}:{line_number}: bloco Jinja '{token}' sem '{closing}'")
    return errors


def first_nonempty_lines(lines: list[str], count: int) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            result.append((index, stripped))
            if len(result) == count:
                break
    return result


def has_line(lines: list[str], expected: str) -> bool:
    return any(line.strip() == expected for line in lines)


def check_achado_fragment(lines: list[str], path: Path) -> list[str]:
    text = "\n".join(lines)
    if "auditado.get_achado_por_nome(nome_achado)" not in text and "## Achado {{ achado.numero }}" not in text:
        return []

    errors: list[str] = []
    first_lines = first_nonempty_lines(lines, 3)
    expected_prefix = [
        "{% set nome_achado = '",
        "{% set achado = auditado.get_achado_por_nome(nome_achado) %}",
        "{% if achado %}",
    ]
    if len(first_lines) < 3 or not first_lines[0][1].startswith(expected_prefix[0]):
        errors.append(f"{path}: achado deve iniciar com definição de nome_achado")
    if len(first_lines) < 3 or first_lines[1][1] != expected_prefix[1]:
        errors.append(f"{path}: segunda linha útil deve definir achado via auditado.get_achado_por_nome(nome_achado)")
    if len(first_lines) < 3 or first_lines[2][1] != expected_prefix[2]:
        errors.append(f"{path}: terceira linha útil deve abrir '{{% if achado %}}'")

    required_lines = [
        r"\newpage",
        ACHADO_HEADING,
        "### Critérios",
        "### Evidências",
        "### Situação encontrada",
        "#### Conclusão",
        "### Propostas de Encaminhamento",
    ]
    for required in required_lines:
        if not has_line(lines, required):
            errors.append(f"{path}: achado sem linha obrigatória: {required}")

    required_snippets = [
        "{% for evidencia in achado.evidencias %}",
        "achado.situacoes_encontradas",
        "{% for e in achado.encaminhamentos %}",
        "**Comunicação com {{ e.tipo }}** para que {{ e.encaminhamento }};",
        "{# Final do Achado -",
    ]
    for snippet in required_snippets:
        if snippet not in text:
            errors.append(f"{path}: achado sem trecho obrigatório: {snippet}")

    try:
        situacao_index = next(i for i, line in enumerate(lines) if line.strip() == "### Situação encontrada")
        conclusao_index = next(i for i, line in enumerate(lines) if line.strip() == "#### Conclusão")
    except StopIteration:
        return errors

    if conclusao_index <= situacao_index:
        errors.append(f"{path}: '#### Conclusão' deve vir após '### Situação encontrada'")
    else:
        specific_headings = [
            line.strip()
            for line in lines[situacao_index + 1 : conclusao_index]
            if line.strip().startswith("#### ")
        ]
        if not specific_headings:
            errors.append(f"{path}: achado deve ter ao menos uma subseção específica '#### ...' antes da conclusão")

    if not lines[-1].strip() == "{% endif %}":
        errors.append(f"{path}: achado deve terminar com '{{% endif %}}'")

    return errors


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    errors.extend(check_figures(lines, path))
    errors.extend(check_tables(lines, path))
    errors.extend(check_footnotes(text, path))
    errors.extend(check_newpage(lines, path))
    errors.extend(check_jinja_balance(lines, path))
    errors.extend(check_achado_fragment(lines, path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Markdown report files to check")
    parser.add_argument("--max-fonte", type=int, default=220, help="tamanho máximo da linha de fonte antes do aviso")
    parser.add_argument("--max-nota", type=int, default=600, help="tamanho máximo de nota de rodapé antes do aviso")
    parser.add_argument("--estrito", action="store_true", help="trata os avisos como erros")
    parser.add_argument("--sem-avisos", action="store_true", help="não executa os avisos de estilo")
    args = parser.parse_args()

    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    errors: list[str] = []
    avisos: list[str] = []
    for path in args.files:
        if not path.exists():
            errors.append(f"{path}: arquivo não encontrado")
            continue
        errors.extend(check_file(path))
        if not args.sem_avisos:
            avisos.extend(
                check_avisos(path.read_text(encoding="utf-8").splitlines(), path, args.max_fonte, args.max_nota)
            )

    if errors:
        print("\n".join(errors), file=sys.stderr)
    if avisos:
        print("\n".join(f"aviso: {a}" for a in avisos), file=sys.stderr)
    if errors or (avisos and args.estrito):
        return 1
    print("OK" + (f" ({len(avisos)} avisos)" if avisos else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
