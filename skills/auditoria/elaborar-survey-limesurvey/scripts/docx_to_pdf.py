#!/usr/bin/env python3
"""Converte um DOCX em PDF com Word no Windows ou LibreOffice no Linux.

O arquivo de entrada e a saída podem conter espaços ou caracteres não ASCII.
A conversão ocorre em uma pasta temporária com nomes simples para evitar
problemas de carregamento dos conversores em diferentes instalações.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_docx", type=Path, help="DOCX a converter.")
    parser.add_argument(
        "output_pdf",
        type=Path,
        nargs="?",
        help="PDF de saída. Se omitido, usa o mesmo nome-base do DOCX.",
    )
    parser.add_argument(
        "--libreoffice",
        type=Path,
        help="Caminho explícito para libreoffice/soffice ou soffice.exe.",
    )
    parser.add_argument(
        "--engine",
        choices=("auto", "word", "libreoffice"),
        default="auto",
        help=(
            "Motor de conversão. Em auto, prioriza Microsoft Word no Windows "
            "e usa LibreOffice no Linux (padrão: auto)."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Tempo máximo da conversão, em segundos (padrão: 180).",
    )
    return parser.parse_args()


def _windows_candidates() -> list[Path]:
    candidates: list[Path] = []
    for executable in ("soffice.exe", "libreoffice.exe", "soffice", "libreoffice"):
        resolved = shutil.which(executable)
        if resolved:
            candidates.append(Path(resolved))

    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432"):
        base = os.environ.get(variable)
        if base:
            candidates.append(Path(base) / "LibreOffice" / "program" / "soffice.exe")
    return candidates


def find_libreoffice(explicit: Path | None = None) -> Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"Executável do LibreOffice não encontrado: {candidate}")

    if os.name == "nt":
        candidates = _windows_candidates()
    else:
        candidates = [
            Path(resolved)
            for name in ("libreoffice", "soffice")
            if (resolved := shutil.which(name))
        ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    if os.name == "nt":
        detail = (
            "Instale o LibreOffice, adicione a pasta 'program' ao PATH ou informe "
            "--libreoffice \"C:\\Program Files\\LibreOffice\\program\\soffice.exe\"."
        )
    else:
        detail = "Instale o LibreOffice Writer e confirme que 'libreoffice' ou 'soffice' está no PATH."
    raise FileNotFoundError(detail)


def validate_pdf(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError("O motor de conversão não gerou um PDF válido.")
    with path.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise RuntimeError("A saída gerada não possui um cabeçalho PDF válido.")


def convert_with_word(source: Path, target: Path, *, timeout: int) -> str:
    if os.name != "nt":
        raise RuntimeError("A conversão pelo Microsoft Word está disponível apenas no Windows.")

    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        raise FileNotFoundError("PowerShell não encontrado para acionar o Microsoft Word.")

    script = r"""
$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($env:SURVEY_DOCX_INPUT, $false, $true)
    $document.ExportAsFixedFormat($env:SURVEY_PDF_OUTPUT, 17)
} finally {
    if ($null -ne $document) {
        $document.Close($false) | Out-Null
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) | Out-Null
    }
    if ($null -ne $word) {
        $word.Quit() | Out-Null
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
"""
    environment = os.environ.copy()
    environment["SURVEY_DOCX_INPUT"] = str(source)
    environment["SURVEY_PDF_OUTPUT"] = str(target)
    try:
        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Timeout após {timeout}s na conversão pelo Microsoft Word.") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"Microsoft Word encerrou com o código {result.returncode}{suffix}")
    validate_pdf(target)
    return "Microsoft Word"


def convert_with_libreoffice(
    source: Path,
    target: Path,
    *,
    libreoffice: Path,
    timeout: int,
) -> str:
    command = [
        str(libreoffice),
        "--headless",
        "--nologo",
        "--nodefault",
        "--nofirststartwizard",
        "--norestore",
        "--nolockcheck",
        "--convert-to",
        "pdf:writer_pdf_Export",
        "--outdir",
        str(target.parent),
        str(source),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Timeout após {timeout}s na conversão pelo LibreOffice.") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"LibreOffice encerrou com o código {result.returncode}{suffix}")
    validate_pdf(target)
    return f"LibreOffice ({libreoffice})"


def convert_docx_to_pdf(
    input_docx: Path,
    output_pdf: Path,
    *,
    engine: str,
    libreoffice: Path | None,
    timeout: int,
) -> str:
    source = input_docx.expanduser().resolve()
    target = output_pdf.expanduser().resolve()

    if not source.is_file():
        raise FileNotFoundError(f"DOCX não encontrado: {source}")
    if source.suffix.casefold() != ".docx":
        raise ValueError(f"A entrada deve possuir extensão .docx: {source}")
    if target.suffix.casefold() != ".pdf":
        raise ValueError(f"A saída deve possuir extensão .pdf: {target}")
    if timeout <= 0:
        raise ValueError("O timeout deve ser maior que zero.")

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="survey-pdf-") as temp_dir:
        temp = Path(temp_dir)
        local_docx = temp / "document.docx"
        local_pdf = temp / "document.pdf"
        shutil.copyfile(source, local_docx)

        if engine == "word":
            used_engine = convert_with_word(local_docx, local_pdf, timeout=timeout)
        elif engine == "libreoffice":
            executable = find_libreoffice(libreoffice)
            used_engine = convert_with_libreoffice(
                local_docx,
                local_pdf,
                libreoffice=executable,
                timeout=timeout,
            )
        elif os.name == "nt":
            try:
                used_engine = convert_with_word(local_docx, local_pdf, timeout=timeout)
            except (FileNotFoundError, RuntimeError, OSError) as word_error:
                local_pdf.unlink(missing_ok=True)
                try:
                    executable = find_libreoffice(libreoffice)
                    used_engine = convert_with_libreoffice(
                        local_docx,
                        local_pdf,
                        libreoffice=executable,
                        timeout=timeout,
                    )
                except (FileNotFoundError, RuntimeError, OSError) as libreoffice_error:
                    raise RuntimeError(
                        "Falha nos motores disponíveis. "
                        f"Microsoft Word: {word_error}; LibreOffice: {libreoffice_error}"
                    ) from libreoffice_error
        else:
            executable = find_libreoffice(libreoffice)
            used_engine = convert_with_libreoffice(
                local_docx,
                local_pdf,
                libreoffice=executable,
                timeout=timeout,
            )

        validate_pdf(local_pdf)
        staged_pdf = target.with_name(f".{target.name}.tmp")
        shutil.copyfile(local_pdf, staged_pdf)
        os.replace(staged_pdf, target)
        return used_engine


def main() -> int:
    args = parse_args()
    source = args.input_docx
    target = args.output_pdf or source.with_suffix(".pdf")
    try:
        used_engine = convert_docx_to_pdf(
            source,
            target,
            engine=args.engine,
            libreoffice=args.libreoffice,
            timeout=args.timeout,
        )
        final_target = target.expanduser().resolve()
        print(f"Sistema: {sys.platform}")
        print(f"Motor: {used_engine}")
        print(f"PDF: {final_target}")
        print(f"Tamanho: {final_target.stat().st_size} bytes")
        return 0
    except (FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
