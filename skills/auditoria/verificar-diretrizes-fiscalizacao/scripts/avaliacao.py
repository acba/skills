#!/usr/bin/env python3
"""Prepare inventário neutro e valide a estrutura de avaliações de diretrizes."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re


ESTADOS = {"Atende", "Atende parcialmente", "Não atende", "Não verificado", "Não aplicável"}
ESTADOS_PROBLEMA = {"Proposto", "Em execução", "Corrigido", "Validado", "Pendente de decisão"}
EXCLUIDOS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}
CAMPOS_PROBLEMA = (
    "problema", "impacto_atual", "justificativa_prioridade", "correcao",
    "impacto_melhoria", "aceite",
)

def selecionar_diretrizes(root, explicitas=None):
    if explicitas is not None:
        return explicitas.resolve(), "indicadas"
    locais = root.resolve() / "DIRETRIZES.md"
    if os.path.lexists(locais):
        return locais, "projeto"
    raise ValueError("DIRETRIZES.md não encontrado no projeto; informe --diretrizes.")


def fonte_para_validacao(dados, explicitas=None):
    if explicitas is not None:
        return explicitas.resolve()
    meta = dados.get("metadata", {}) if isinstance(dados, dict) else {}
    if not isinstance(meta, dict) or not isinstance(meta.get("diretrizes_path"), str):
        raise ValueError("Fonte ausente nos metadados; informe --diretrizes.")
    registrada = Path(meta["diretrizes_path"])
    if os.path.lexists(registrada):
        return registrada
    raise ValueError("Diretrizes locais/indicadas indisponíveis; informe sua localização com --diretrizes.")


def ler_diretrizes(path):
    conteudo = path.read_bytes()
    texto = conteudo.decode("utf-8")
    itens = re.findall(r"^\*\*(DIR-\d+)\s+[—–-]\s+(.+?)\.\*\*", texto, re.MULTILINE)
    if not itens or len({item[0] for item in itens}) != len(itens):
        raise ValueError("Diretrizes sem requisitos DIR-... reconhecíveis ou com IDs duplicados.")
    return itens, hashlib.sha256(conteudo).hexdigest()


def gravar(path, dados):
    with path.open("x", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")


def preparar(root, diretrizes, output):
    root, output = root.resolve(), output.resolve()
    diretrizes, origem = selecionar_diretrizes(root, diretrizes)
    if not root.is_dir():
        raise ValueError("Raiz inexistente ou não é diretório.")
    if output == root or root.is_relative_to(output):
        raise ValueError("Destino deve ser área própria, nunca raiz ou ancestral do projeto.")
    itens, digest = ler_diretrizes(diretrizes)
    if output.exists():
        raise ValueError("Destino já existe; escolha área nova para preservar a avaliação anterior.")
    arquivos, pastas, links, erros = [], [], [], []

    def erro_os(erro):
        erros.append({"path": str(erro.filename), "erro": str(erro)})

    for base, dirs, files in os.walk(root, followlinks=False, onerror=erro_os):
        pasta = Path(base)
        selecionadas = []
        for nome in sorted(dirs):
            caminho = pasta / nome
            if nome in EXCLUIDOS or caminho.resolve() == output:
                continue
            relativo = caminho.relative_to(root).as_posix()
            if caminho.is_symlink():
                links.append(relativo)
                continue
            selecionadas.append(nome)
            pastas.append(relativo)
        dirs[:] = selecionadas
        for nome in sorted(files):
            caminho = pasta / nome
            relativo = caminho.relative_to(root).as_posix()
            if caminho.is_symlink():
                links.append(relativo)
            else:
                arquivos.append(relativo)
    contagens = Counter(path.split("/")[0] if "/" in path else "<raiz>" for path in arquivos)
    inventario = {
        "root": str(root), "data_utc": datetime.now(timezone.utc).isoformat(),
        "metodo": "Caminhos, sem leitura de conteúdo; symlinks não percorridos; nenhuma conclusão de conformidade.",
        "exclusoes": sorted(EXCLUIDOS), "arquivos": arquivos, "pastas": pastas,
        "symlinks_nao_percorridos": links, "erros_leitura": erros,
        "arquivos_por_area": dict(sorted(contagens.items())),
    }
    avaliacao = {
        "schema_version": "1.0",
        "metadata": {
            "root": str(root), "diretrizes_path": str(diretrizes),
            "diretrizes_origem": origem,
            "diretrizes_sha256": digest, "data_utc": inventario["data_utc"],
            "escopo": "Preencher após delimitar a avaliação",
            "limitacoes": ["Esqueleto de preparação; inspeção substantiva ainda não realizada."],
        },
        "pastas": [],
        "requisitos": [
            {"id": codigo, "titulo": titulo, "estado": "Não verificado", "evidencias": [],
             "justificativa": "Inspeção pendente", "alcance": "Não examinado", "problemas": []}
            for codigo, titulo in itens
        ],
        "problemas": [], "boas_praticas": [],
    }
    output.mkdir(parents=True, exist_ok=False)
    gravar(output / "inventario.json", inventario)
    gravar(output / "avaliacao.json", avaliacao)
    return {"output": str(output), "requisitos": len(itens), "arquivos": len(arquivos),
            "aviso": "Complete a inspeção: esqueleto não é avaliação concluída."}


def validar(dados, itens, digest):
    erros = []

    def exigir(condicao, mensagem):
        if not condicao:
            erros.append(mensagem)

    def texto(valor):
        return isinstance(valor, str) and bool(valor.strip())

    def lista_textos(valor, vazia=True):
        return isinstance(valor, list) and all(texto(v) for v in valor) and (vazia or bool(valor))

    if not isinstance(dados, dict):
        return ["Avaliação deve ser objeto JSON."]
    exigir(dados.get("schema_version") == "1.0", "schema_version deve ser 1.0.")
    meta = dados.get("metadata")
    if not isinstance(meta, dict):
        erros.append("metadata inválido.")
    else:
        for campo in ("root", "diretrizes_path", "data_utc", "escopo"):
            exigir(texto(meta.get(campo)), f"metadata.{campo} obrigatório.")
        exigir(meta.get("diretrizes_sha256") == digest, "Hash das diretrizes incompatível; reconcilie a versão.")
        exigir(lista_textos(meta.get("limitacoes")), "metadata.limitacoes deve ser lista de textos.")

    def objetos(chave):
        valor = dados.get(chave)
        if not isinstance(valor, list) or not all(isinstance(v, dict) for v in valor):
            erros.append(f"{chave} deve ser lista de objetos.")
            return []
        return valor

    requisitos = objetos("requisitos")
    problemas = objetos("problemas")
    pastas = objetos("pastas")
    boas = objetos("boas_praticas")
    esperados = dict(itens)
    ids = [r.get("id") for r in requisitos]
    exigir(all(isinstance(i, str) for i in ids), "IDs dos requisitos devem ser textos.")
    ids_validos = [i for i in ids if isinstance(i, str)]
    exigir(len(ids_validos) == len(set(ids_validos)), "Requisitos duplicados.")
    exigir(set(ids_validos) == set(esperados), "Cobertura deve conter todos e somente os requisitos vigentes.")
    problema_ids = [p.get("id") for p in problemas]
    exigir(all(isinstance(i, str) and re.fullmatch(r"PROB-\d+", i) for i in problema_ids), "IDs de problema inválidos.")
    problemas_validos = {p["id"]: p for p in problemas if isinstance(p.get("id"), str)}
    exigir(len(problemas_validos) == len(problemas), "Problemas duplicados ou sem ID.")
    requisitos_validos = {r["id"]: r for r in requisitos if isinstance(r.get("id"), str)}
    for req in requisitos:
        codigo = req.get("id")
        exigir(req.get("titulo") == esperados.get(codigo) if isinstance(codigo, str) else False,
               f"{codigo}: título divergente da diretriz.")
        exigir(req.get("estado") in ESTADOS if isinstance(req.get("estado"), str) else False,
               f"{codigo}: estado inválido.")
        for campo in ("justificativa", "alcance"):
            exigir(texto(req.get(campo)), f"{codigo}: {campo} obrigatório.")
        avaliado = req.get("estado") in ("Atende", "Atende parcialmente", "Não atende")
        exigir(lista_textos(req.get("evidencias"), vazia=not avaliado), f"{codigo}: evidências inválidas/ausentes.")
        refs = req.get("problemas")
        exigir(lista_textos(refs), f"{codigo}: problemas deve ser lista de IDs.")
        if not lista_textos(refs):
            continue
        if req.get("estado") in ("Atende parcialmente", "Não atende"):
            exigir(bool(refs), f"{codigo}: lacuna exige problema associado.")
        for ref in refs:
            exigir(ref in problemas_validos, f"{codigo}: problema {ref} inexistente.")
            if ref in problemas_validos:
                exigir(codigo in problemas_validos[ref].get("diretrizes", [])
                       if isinstance(problemas_validos[ref].get("diretrizes"), list) else False,
                       f"{codigo}/{ref}: associação sem retorno.")
    for prob in problemas:
        codigo = prob.get("id")
        for campo in CAMPOS_PROBLEMA:
            exigir(texto(prob.get(campo)), f"{codigo}: {campo} obrigatório.")
        exigir(lista_textos(prob.get("evidencias"), vazia=False), f"{codigo}: evidência obrigatória.")
        exigir(prob.get("prioridade") in ("P0", "P1", "P2", "P3"), f"{codigo}: prioridade inválida.")
        exigir(prob.get("estado") in ESTADOS_PROBLEMA if isinstance(prob.get("estado"), str) else False,
               f"{codigo}: estado inválido.")
        refs = prob.get("diretrizes")
        exigir(lista_textos(refs, vazia=False), f"{codigo}: diretrizes obrigatórias.")
        if isinstance(refs, list):
            for ref in refs:
                exigir(isinstance(ref, str) and ref in esperados, f"{codigo}: diretriz {ref} inexistente.")
                if isinstance(ref, str) and ref in requisitos_validos:
                    exigir(codigo in requisitos_validos[ref].get("problemas", [])
                           if isinstance(requisitos_validos[ref].get("problemas"), list) else False,
                           f"{codigo}/{ref}: associação sem retorno.")
    exigir(bool(pastas), "Mapeie ao menos uma área/pasta relevante.")
    for pasta in pastas:
        for campo in ("caminho", "funcao_observada", "funcao_esperada", "conclusao"):
            exigir(texto(pasta.get(campo)), f"Pasta: {campo} obrigatório.")
        exigir(lista_textos(pasta.get("evidencias"), vazia=False), "Pasta exige evidência de inspeção.")
    for boa in boas:
        exigir(texto(boa.get("descricao")) and texto(boa.get("preservacao")), "Boa prática exige descrição/preservação.")
        exigir(lista_textos(boa.get("evidencias"), vazia=False), "Boa prática exige evidência.")
    return erros


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    prep = comandos.add_parser("preparar", help="Inventariar e gerar esqueleto não avaliado.")
    prep.add_argument("--root", type=Path, required=True)
    prep.add_argument("--diretrizes", type=Path, help="Opcional: prioridade sobre a fonte local do projeto.")
    prep.add_argument("--output", type=Path, required=True)
    val = comandos.add_parser("validar", help="Validar cobertura/contrato; não certifica conformidade.")
    val.add_argument("--diretrizes", type=Path, help="Opcional: localização da fonte usada na avaliação.")
    val.add_argument("--avaliacao", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.comando == "preparar":
            resultado = preparar(args.root, args.diretrizes, args.output)
            status = 0
        else:
            dados = json.loads(args.avaliacao.read_text(encoding="utf-8"))
            fonte = fonte_para_validacao(dados, args.diretrizes)
            itens, digest = ler_diretrizes(fonte)
            erros = validar(dados, itens, digest)
            resultado = {"estrutura_valida": not erros, "erros": erros,
                         "limite": "Validação estrutural; não confirma evidências nem conformidade do projeto."}
            status = 1 if erros else 0
    except (OSError, ValueError) as erro:
        resultado, status = {"erro": str(erro)}, 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
