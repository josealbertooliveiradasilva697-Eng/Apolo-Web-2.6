"""Entrada web local. Execute pelo iniciador ou: streamlit run app.py."""
import os
from pathlib import Path
import sqlite3
import streamlit as st
from auth.provider import obter_identidade
from auth.roles import Acao, permitido
from core.catalogo import VERSAO_PROGRAMA
from database.repository import RepositorioSQLite, inspecionar_arquivo
from services.apolo import ServicoApolo
from interface import telas


def main():
    st.set_page_config(page_title="Apolo | Cálculos Aerodinâmicos",page_icon="✈️",layout="wide")
    st.title("Apolo · Cálculos Aerodinâmicos")
    st.caption(f"Base {VERSAO_PROGRAMA} · Primeira versão web local")
    try:
        usuario=obter_identidade()
    except (ValueError,RuntimeError) as exc:
        st.error(str(exc))
        st.stop()
    st.sidebar.subheader("Apolo")
    st.sidebar.caption(f"Perfil de teste: {usuario.papel.value}")
    st.sidebar.info("Modo local de teste, sem login. Integração com Supabase pendente.")
    data_dir=Path(os.environ.get("APOLO_DATA_DIR",str(Path(__file__).parent / "data"))).resolve()
    arquivos=sorted(p.name for p in data_dir.glob("*.db"))
    if not arquivos:
        inicial=RepositorioSQLite(data_dir)
        inicial.criar_novo()
        arquivos=[inicial.path.name]
    principal="Banco_de_Variaveis_Calculo_1_web.db"
    nome=st.sidebar.selectbox("Banco de trabalho",arquivos,index=arquivos.index(principal) if principal in arquivos else 0)
    repo=RepositorioSQLite(data_dir,nome)
    try:
        with repo.conectar() as conn:
            metadata=dict(conn.execute("SELECT chave,valor FROM metadata"))
        # Inspeção completa na primeira abertura por sessão, sem escrituras.
        chave=f"inspecao:{repo.path}:{repo.path.stat().st_mtime_ns}"
        if st.session_state.get("banco_inspecionado")!=chave:
            inspecionar_arquivo(repo.path)
            st.session_state["banco_inspecionado"]=chave
    except (ValueError,sqlite3.Error) as exc:
        st.error(f"Não foi possível abrir o banco: {exc}")
        st.stop()
    if "origem_web" in metadata:
        st.info("Banco novo de teste. O histórico do Google Drive ainda não foi importado.")
    else:
        st.caption("Cópia local de banco importado. O arquivo de origem permanece separado.")
    servico=ServicoApolo(repo,usuario)
    paginas={"Novo cálculo":telas.calculos,"Histórico":telas.historico,"Banco de variáveis":telas.banco}
    if permitido(usuario,Acao.CONFIGURAR):
        paginas["Administração"]=telas.administracao
    if permitido(usuario,Acao.DIAGNOSTICAR):
        paginas["Diagnósticos"]=telas.diagnosticos
    pagina=st.sidebar.radio("Navegação",list(paginas))
    try:
        paginas[pagina](servico)
    except sqlite3.Error:
        st.error("A operação no banco não foi concluída. Tente novamente ou consulte os diagnósticos.")


if __name__ == "__main__":
    main()
