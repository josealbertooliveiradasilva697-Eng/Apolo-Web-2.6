"""Contrato REST, isolamento de contexto e configuração que falha fechada."""
from io import BytesIO
from urllib.error import HTTPError, URLError
from uuid import uuid4

import pytest
from auth.roles import Identidade, Papel
from config import Configuracao
from core.catalogo import CATALOGO_VARIAVEIS
from database.supabase_repository import RepositorioSupabase, RepositorioProjetosSupabase
from integrations.supabase_http import ClienteSupabase, ErroSupabase, SessaoExpirada
from services.projects import ServicoProjetos

UID = str(uuid4())
PROJECT = str(uuid4())
USER = Identidade(UID, Papel.OPERADOR, "Teste")


class Respostas:
    def __init__(self, *respostas):
        self.respostas = iter(respostas)
        self.calls = []

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return next(self.respostas)


@pytest.mark.parametrize("env", [
    {"APOLO_ENV": "production"},
    {"RENDER": "true"},
    {"RENDER": "true", "APOLO_ENV": "development"},
    {"APOLO_AUTH_MODE": "supabase", "SUPABASE_URL": "http://example.com", "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_test"},
    {"APOLO_AUTH_MODE": "supabase", "SUPABASE_URL": "https://example.com", "SUPABASE_PUBLISHABLE_KEY": "sb_secret_test"},
    {"APOLO_AUTH_MODE": "local", "APOLO_REPOSITORY_MODE": "supabase"},
])
def test_configuracao_recusa_combinacao_insegura(env):
    with pytest.raises(ValueError):
        Configuracao.carregar(env)


def test_config_chave_nao_aparece_no_repr():
    c = Configuracao.carregar({"APOLO_AUTH_MODE": "supabase",
        "SUPABASE_URL": "https://example.supabase.co", "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_test"})
    assert "sb_publishable_test" not in repr(c)


def test_repository_rejeita_projeto_invisivel():
    with pytest.raises(PermissionError):
        RepositorioSupabase(Respostas([]), USER, PROJECT)


def test_detalhe_nao_le_valores_de_outro_projeto():
    fake = Respostas([{"id": PROJECT}], [])
    repo = RepositorioSupabase(fake, USER, PROJECT)
    assert repo.detalhe(str(uuid4())) == []
    assert len(fake.calls) == 2
    assert fake.calls[-1][1]["query"]["project_id"] == f"eq.{PROJECT}"


def test_snapshot_enviado_em_uma_unica_operacao():
    execution = str(uuid4())
    fake = Respostas([{"id": PROJECT}], execution)
    repo = RepositorioSupabase(fake, USER, PROJECT)
    assert repo.salvar_execucao("CAL_NEWTON", {"Massa da aeronave": 1, "Aceleração": 2},
        {"Força resultante": 2}) == execution
    assert len(fake.calls) == 2
    assert fake.calls[-1][0] == ("POST", "/rest/v1/rpc/apolo_save_execution")
    assert fake.calls[-1][1]["payload"]["p_project_id"] == PROJECT


def test_variaveis_exigem_projeto_completo():
    fake = Respostas([{"id": PROJECT}], list(CATALOGO_VARIAVEIS.values()), [])
    with pytest.raises(ErroSupabase):
        RepositorioSupabase(fake, USER, PROJECT).variaveis()


def test_projeto_operador_valida_nome_antes_do_banco():
    fake = Respostas([{"id": PROJECT}])
    service = ServicoProjetos(RepositorioProjetosSupabase(fake, USER), USER)
    with pytest.raises(ValueError):
        service.criar(" " * 20)
    with pytest.raises(ValueError):
        service.criar("x" * 121)
    assert not fake.calls


class Opener:
    def __init__(self, status=None):
        self.status = status
        self.request = None

    def open(self, req, timeout):
        self.request = req
        if self.status:
            raise HTTPError(req.full_url, self.status, "segredo-do-servidor", {}, BytesIO(b"senha-token"))
        return BytesIO(b'{"ok":true}')


def test_http_jwt_individual_e_sem_vazamento_de_corpo():
    config = Configuracao("development", "supabase", "supabase",
        "https://example.supabase.co", "sb_publishable_test")
    a, b = Opener(), Opener()
    ClienteSupabase(config, "token-A", a).request("GET", "/rest/v1/projects")
    ClienteSupabase(config, "token-B", b).request("GET", "/rest/v1/projects")
    assert a.request.get_header("Authorization") == "Bearer token-A"
    assert b.request.get_header("Authorization") == "Bearer token-B"
    for status, error in [(401, SessaoExpirada), (403, PermissionError), (500, ErroSupabase)]:
        with pytest.raises(error) as exc:
            ClienteSupabase(config, "token-A", Opener(status)).request("GET", "/rest/v1/projects")
        assert "senha-token" not in str(exc.value)
        assert "segredo-do-servidor" not in str(exc.value)


def test_http_recusa_nan_antes_da_rede():
    config = Configuracao("development", "supabase", "supabase", "https://example.com", "publica")
    opener = Opener()
    with pytest.raises(ValueError):
        ClienteSupabase(config, opener=opener).request("POST", "/rest/v1/projects", {"v": float("nan")})
    assert opener.request is None
