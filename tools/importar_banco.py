"""python -m tools.importar_banco origem.db --nome Projeto.db [--audit-only]."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
from database.repository import RepositorioSQLite, inspecionar_arquivo
from auth.roles import Acao, exigir


def importar(origem, repo, usuario):
    exigir(usuario,Acao.IMPORTAR_BANCO)
    origem=Path(origem).resolve(strict=True)
    if origem==repo.path or repo.path.exists():
        raise FileExistsError("Escolha um nome novo para a cópia de trabalho.")
    before=hashlib.sha256(origem.read_bytes()).hexdigest()
    report=inspecionar_arquivo(origem)
    repo.data_dir.mkdir(parents=True,exist_ok=True)
    with repo.path.open("xb"):
        pass
    try:
        src=sqlite3.connect(origem.as_uri()+"?mode=ro",uri=True)
        dst=sqlite3.connect(repo.path)
        try:
            src.backup(dst)
        finally:
            src.close()
            dst.close()
        inspecionar_arquivo(repo.path)
        if before!=hashlib.sha256(origem.read_bytes()).hexdigest():
            raise RuntimeError("O banco de origem mudou durante a importação.")
    except Exception:
        # Remove exclusivamente a cópia nova incompleta criada nesta operação.
        repo.path.unlink(missing_ok=True)
        raise
    return {"origem":report,"copia_trabalho":repo.path.name,"origem_preservada":True}


def main():
    from auth.provider import obter_identidade
    parser=argparse.ArgumentParser(description="Audita e importa uma cópia; não altera a origem.")
    parser.add_argument("origem",type=Path)
    parser.add_argument("--nome",default="Banco_importado.db")
    parser.add_argument("--audit-only",action="store_true")
    args=parser.parse_args()
    if args.audit_only:
        report=inspecionar_arquivo(args.origem)
    else:
        repo=RepositorioSQLite(Path(__file__).resolve().parents[1]/"data",args.nome)
        report=importar(args.origem,repo,obter_identidade())
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
