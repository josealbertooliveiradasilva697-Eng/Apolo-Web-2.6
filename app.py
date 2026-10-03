"""Entrada Streamlit: SQLite local ou Supabase autenticado, por configuração."""
import os
from pathlib import Path
import sqlite3

import streamlit as st

from auth.provider import obter_identidade
from auth.roles import Acao, permitido
from auth.supabase_provider import ProvedorSupabase
from config import Configuracao
from core.catalogo import VERSAO_PROGRAMA
from database.repository import RepositorioSQLite, inspecionar_arquivo
from database.supabase_repository import RepositorioProjetosSupabase, RepositorioSupabase
from integrations.supabase_http import ErroSupabase, SessaoExpirada
from interface import telas
from services.apolo import ServicoApolo
from services.projects import ServicoProjetos


def login(provider):
    st.subheader("Entrar no Apolo")
    with st.form("login", clear_on_submit=True):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        enviar = st.form_submit_button("Entrar", type="primary")
    if enviar:
        try:
            sessao = provider.entrar(email, senha)
            sessao, _ = provider.restaurar(sessao)
        except (ValueError, PermissionError, ErroSupabase) as exc:
            st.error(str(exc))
        else:
            st.session_state.clear()
            st.session_state["auth_session"] = sessao
            st.rerun()
    st.caption("Use a conta cadastrada pelo administrador do Apolo.")


def repositorio_local():
    data_dir = Path(os.environ.get("APOLO_DATA_DIR", str(Path(__file__).parent / "data"))).resolve()
    arquivos = sorted(p.name for p in data_dir.glob("*.db"))
    if not arquivos:
        inicial = RepositorioSQLite(data_dir)
        inicial.criar_novo()
        arquivos = [inicial.path.name]
    principal = "Banco_de_Variaveis_Calculo_1_web.db"
    nome = st.sidebar.selectbox("Banco de trabalho", arquivos,
        index=arquivos.index(principal) if principal in arquivos else 0)
    repo = RepositorioSQLite(data_dir, nome)
    chave = f"inspecao:{repo.path}:{repo.path.stat().st_mtime_ns}"
    if st.session_state.get("banco_inspecionado") != chave:
        inspecionar_arquivo(repo.path)
        st.session_state["banco_inspecionado"] = chave
    return repo


def online(config):
    provider = ProvedorSupabase(config)
    if "auth_session" not in st.session_state:
        if st.session_state.pop("aviso_logout", None):
            st.warning("Você saiu neste navegador. A revogação remota não foi confirmada; tente novamente quando a conexão voltar.")
        login(provider)
        st.stop()
    try:
        sessao, usuario = provider.restaurar(st.session_state["auth_session"])
    except (SessaoExpirada, PermissionError) as exc:
        st.session_state.clear()
        st.error(str(exc))
        login(provider)
        st.stop()
    st.session_state["auth_session"] = sessao
    st.sidebar.caption(f"{usuario.nome} · {usuario.papel.value}")
    if st.sidebar.button("Sair"):
        falhou = False
        try:
            provider.sair(sessao)
        except (ErroSupabase, PermissionError):
            falhou = True
        finally:
            st.session_state.clear()
        if falhou:
            st.session_state["aviso_logout"] = True
        st.rerun()
    client = provider.cliente(sessao)
    projetos = ServicoProjetos(RepositorioProjetosSupabase(client, usuario), usuario)
    with st.sidebar.form("novo_projeto", clear_on_submit=True):
        nome = st.text_input("Nome do novo projeto")
        criar = st.form_submit_button("Criar projeto")
    if criar:
        try:
            criado = projetos.criar(nome)
        except (ValueError, PermissionError) as exc:
            st.sidebar.error(str(exc))
        else:
            st.session_state[f"projeto:{usuario.id}"] = criado["id"]
            st.rerun()
    lista = projetos.listar()
    if not lista:
        st.info("Crie seu primeiro projeto para começar.")
        st.stop()
    nomes = {p["id"]: p["nome"] for p in lista}
    chave = f"projeto:{usuario.id}"
    if st.session_state.get(chave) not in nomes:
        st.session_state.pop(chave, None)
    projeto_id = st.sidebar.selectbox("Projeto", list(nomes), format_func=nomes.get, key=chave)
    projetos.selecionar(projeto_id)
    repo = RepositorioSupabase(client, usuario, projeto_id)
    return usuario, repo


def main():
    st.set_page_config(page_title="Apolo | Cálculos Aerodinâmicos", page_icon="✈️", layout="wide")
    st.title("Apolo · Cálculos Aerodinâmicos")
    st.caption(f"Base {VERSAO_PROGRAMA}")
    st.sidebar.subheader("Apolo")
    try:
        config = Configuracao.carregar()
        if config.auth_mode == "local":
            usuario = obter_identidade()
            st.sidebar.caption(f"Perfil de teste: {usuario.papel.value}")
            st.sidebar.info("Modo local de desenvolvimento, sem login.")
            repo = repositorio_local()
        else:
            usuario, repo = online(config)
    except (ValueError, PermissionError, sqlite3.Error, ErroSupabase) as exc:
        st.error(str(exc))
        st.stop()
    servico = ServicoApolo(repo, usuario)
    paginas = {
        "Novo cálculo": telas.calculos,
        "Histórico": telas.historico,
        "Banco de variáveis": telas.banco,
    }
    if permitido(usuario, Acao.CONFIGURAR):
        paginas["Administração"] = telas.administracao
    if permitido(usuario, Acao.DIAGNOSTICAR):
        paginas["Diagnósticos"] = telas.diagnosticos
    pagina = st.sidebar.radio("Navegação", list(paginas))
    try:
        paginas[pagina](servico)
    except SessaoExpirada:
        st.session_state.clear()
        st.error("Sua sessão expirou. Entre novamente.")
        st.rerun()
    except PermissionError as exc:
        st.error(str(exc))
    except ErroSupabase as exc:
        st.error(str(exc))
    except sqlite3.Error:
        st.error("A operação no banco não foi concluída. Tente novamente.")


if __name__ == "__main__":
    main()
