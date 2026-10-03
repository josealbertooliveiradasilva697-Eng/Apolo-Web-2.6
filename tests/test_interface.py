from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from database.repository import RepositorioSQLite

APP=Path(__file__).resolve().parents[1]/"app.py"


@pytest.fixture
def app(monkeypatch,tmp_path):
    monkeypatch.setenv("APOLO_DATA_DIR",str(tmp_path/"data"))
    monkeypatch.setenv("APOLO_AUTH_MODE","local")
    monkeypatch.setenv("APOLO_LOCAL_ROLE","operador")
    return AppTest.from_file(str(APP),default_timeout=30)


def test_operador_calcula_e_consulta_historico(app):
    app.run()
    assert not app.exception
    assert "Administração" not in app.sidebar.radio[0].options
    app.selectbox[0].select("CAL_NEWTON").run()
    app.number_input[0].set_value(1000)
    app.number_input[1].set_value(2)
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value=="2000 N"
    app.sidebar.radio[0].set_value("Histórico").run()
    assert not app.exception
    assert len(app.dataframe)==2


def test_breguet_invalido_mostra_erro_sem_historico(app):
    app.run()
    app.selectbox[0].select("CAL_BREG").run()
    app.button[0].click().run()
    assert not app.exception
    assert len(app.error)==1
    app.sidebar.radio[0].set_value("Histórico").run()
    assert not app.exception
    assert len(app.dataframe)==0


@pytest.mark.parametrize("papel",["admin","desenvolvedor"])
def test_paginas_por_papel(app,monkeypatch,papel):
    monkeypatch.setenv("APOLO_LOCAL_ROLE",papel)
    app.run()
    assert not app.exception
    assert "Administração" in app.sidebar.radio[0].options
    assert ("Diagnósticos" in app.sidebar.radio[0].options)==(papel=="desenvolvedor")
    app.sidebar.radio[0].set_value("Administração").run()
    assert not app.exception
    app.selectbox[0].select("gravidade").run()
    app.number_input[0].set_value(9.8)
    app.button[0].click().run()
    assert not app.exception
    assert len(app.success)==1


def test_provedor_futuro_falha_fechado(app,monkeypatch):
    monkeypatch.setenv("APOLO_AUTH_MODE","supabase")
    app.run()
    assert not app.exception
    assert len(app.error)==1
    assert len(app.number_input)==0


def test_sessoes_tem_formularios_independentes(app):
    app.run()
    other=AppTest.from_file(str(APP),default_timeout=30).run()
    app.number_input[0].set_value(1.225)
    app.number_input[1].set_value(50)
    app.number_input[2].set_value(10)
    app.number_input[3].set_value(0.8)
    app.button[0].click().run()
    assert not app.exception
    assert other.number_input[0].value==0.0
    assert len(other.metric)==0


def test_banco_grafico_e_filtros(app):
    app.run()
    app.sidebar.radio[0].set_value("Banco de variáveis").run()
    assert not app.exception
    assert len(app.dataframe[0].value)==23
    app.checkbox[2].check().run()
    assert not app.exception
    app.selectbox[0].select("N").run()
    assert not app.exception
    app.checkbox[0].uncheck().run()
    assert not app.exception
    assert len(app.dataframe[0].value)==6
    app.checkbox[1].uncheck().run()
    assert not app.exception
    assert len(app.dataframe[0].value)==0
