"""Interface online com API controlada: login, papéis, projetos, seis cálculos."""
from pathlib import Path
import time
from uuid import uuid4

import pytest
from streamlit.testing.v1 import AppTest

from auth.roles import Identidade, Papel
from auth.supabase_provider import Sessao
from core.catalogo import CATALOGO_CALCULOS, CATALOGO_VARIAVEIS

APP = Path(__file__).resolve().parents[1] / "app.py"


class API:
    def __init__(self, uid):
        self.uid = uid
        self.projects = [{"id": str(uuid4()), "nome": "Projeto A", "owner_id": uid}]
        self.values = {n: m["padrao"] for n,m in CATALOGO_VARIAVEIS.items()}
        self.executions = []
        self.snapshots = {}
        self.calls = []

    def request(self, method, path, payload=None, query=None):
        self.calls.append((method, path, payload, query))
        if path == "/rest/v1/projects":
            if method == "POST":
                item = {"id": str(uuid4()), **payload}
                self.projects.append(item)
                return [item]
            if "id" in query:
                return [p for p in self.projects if query["id"] == "eq." + p["id"]]
            return self.projects
        if path == "/rest/v1/variables":
            return sorted(CATALOGO_VARIAVEIS.values(),
                key=lambda v:(v["eh_saida"], v["categoria"], v["nome"]))
        if path == "/rest/v1/project_values":
            return [{"id_variavel": m["id_variavel"],
                "valor_real": self.values[n] if m["tipo"] == "REAL" else None,
                "valor_texto": self.values[n] if m["tipo"] == "TEXT" else None,
                "atualizado_em": "2026-10-03"} for n,m in CATALOGO_VARIAVEIS.items()]
        if path == "/rest/v1/rpc/apolo_save_execution":
            eid = str(uuid4())
            self.executions.append({"id_execucao": eid, "id": eid,
                "id_calculo": payload["p_id_calculo"], "project_id": payload["p_project_id"],
                "executado_em": "2026-10-03", "status": "SUCESSO", "mensagem": None})
            self.values.update(payload["p_entradas"])
            self.values.update(payload["p_saidas"])
            self.snapshots[eid] = [
                {"id_execucao": eid, "id_variavel": CATALOGO_VARIAVEIS[n]["id_variavel"],
                 "papel": papel, "valor_real": v, "valor_texto": None,
                 "unidade_si": CATALOGO_VARIAVEIS[n]["unidade_si"]}
                for papel,data in [("entrada",payload["p_entradas"]),("saida",payload["p_saidas"])]
                for n,v in data.items()
            ]
            return eid
        if path == "/rest/v1/executions":
            rows = [e for e in self.executions if query["project_id"] == "eq." + e["project_id"]]
            if "id" in query:
                return [e for e in rows if query["id"] == "eq." + e["id"]]
            return rows[::-1]
        if path == "/rest/v1/execution_values":
            return self.snapshots[query["execution_id"][3:]]
        raise AssertionError((method,path))


@pytest.fixture
def online_app(monkeypatch, tmp_path):
    import auth.supabase_provider as providers
    uid = str(uuid4())
    user = Identidade(uid, Papel.OPERADOR, "Usuário")
    api = API(uid)

    class Provider:
        def entrar(self, email, senha):
            return Sessao("access", "refresh", time.time() + 3600)

        def restaurar(self, sessao):
            return sessao, user

        def cliente(self, sessao):
            return api

        def sair(self, sessao):
            pass

    monkeypatch.setattr(providers, "ProvedorSupabase", lambda config: Provider())
    for key,value in {
        "APOLO_ENV":"development", "APOLO_AUTH_MODE":"supabase",
        "APOLO_REPOSITORY_MODE":"supabase", "SUPABASE_URL":"https://example.supabase.co",
        "SUPABASE_PUBLISHABLE_KEY":"sb_publishable_test",
        "APOLO_DATA_DIR":str(tmp_path / "sem_sqlite"),
    }.items():
        monkeypatch.setenv(key,value)
    monkeypatch.delenv("RENDER", raising=False)
    app = AppTest.from_file(str(APP), default_timeout=30)
    return app,api,tmp_path


def entrar(app):
    app.run()
    assert not app.exception
    assert [t.label for t in app.text_input] == ["Email", "Senha"]
    app.text_input[0].set_value("teste@example.com")
    app.text_input[1].set_value("senha")
    app.button[0].click().run()
    assert not app.exception


@pytest.mark.parametrize("calc,values,expected", [
    ("CAL_SUST",[1.225,50,10,0.8],12250.0),
    ("CAL_ARR",[1.225,50,10,0.04],612.5),
    ("CAL_EMP",[10,500,100],4000.0),
    ("CAL_NEWTON",[1000,2],2000.0),
    ("CAL_BER",[101325,1.225,50,9.81,100],104057.975),
    ("CAL_BREG",[100,0.0002,20000,1000,100000,80000],2231435.5131420977),
])
def test_seis_calculos_online_sem_arquivo_sqlite(online_app, calc, values, expected):
    app,api,tmp_path = online_app
    entrar(app)
    app.selectbox[0].select(calc).run()
    for widget,value in zip(app.number_input,values):
        if not widget.disabled:
            widget.set_value(value)
    next(b for b in app.button if b.label == "Calcular e salvar").click().run()
    assert not app.exception
    assert app.metric[0].value.startswith(f"{expected:.10g} ")
    calls = [c for c in api.calls if c[1] == "/rest/v1/rpc/apolo_save_execution"]
    assert len(calls) == 1
    assert calls[0][2]["p_project_id"] == api.projects[0]["id"]
    assert not (tmp_path / "sem_sqlite").exists()
    app.sidebar.radio[0].set_value("Histórico").run()
    assert not app.exception
    assert len(app.dataframe) == 2


def test_logout_remove_tokens_e_resultados(online_app):
    app,_,_ = online_app
    entrar(app)
    assert "auth_session" in app.session_state
    next(b for b in app.sidebar.button if b.label == "Sair").click().run()
    assert not app.exception
    assert "auth_session" not in app.session_state
    assert "ultimo_resultado" not in app.session_state
    assert [t.label for t in app.text_input] == ["Email", "Senha"]


def test_criar_projeto_operador(online_app):
    app,api,_ = online_app
    entrar(app)
    app.sidebar.text_input[0].set_value("Projeto B")
    next(b for b in app.sidebar.button if b.label == "Criar projeto").click().run()
    assert not app.exception
    assert api.projects[-1]["nome"] == "Projeto B"
    assert app.sidebar.selectbox[0].value == api.projects[-1]["id"]
