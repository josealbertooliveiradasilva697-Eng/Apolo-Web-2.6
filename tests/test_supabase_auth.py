"""Auth consulta o servidor e usa somente o profile protegido."""
import time
from uuid import uuid4

import pytest
from auth.roles import Papel
from auth.supabase_provider import ProvedorSupabase, Sessao
from config import Configuracao
from integrations.supabase_http import ErroSupabase, SessaoExpirada

UID = str(uuid4())
CFG = Configuracao("development", "supabase", "supabase", "https://example.com", "publica")


class API:
    def __init__(self, *respostas):
        self.responses = iter(respostas)
        self.calls = []
        self.tokens = []

    def factory(self, config, token):
        self.tokens.append(token)
        return self

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return result


def sessao():
    return Sessao("access-secreto", "refresh-secreto", time.time() + 3600)


def token_data():
    return {"access_token": "access-novo", "refresh_token": "refresh-novo", "expires_in": 3600}


def test_refresh_usa_token_novo_e_papel_do_profile():
    api = API(token_data(), {"id": UID, "user_metadata": {"role": "desenvolvedor"}},
        [{"id": UID, "role": "operador", "nome": "Usuário"}])
    novo, user = ProvedorSupabase(CFG, api.factory).restaurar(
        Sessao("access-antigo", "refresh-antigo", time.time() - 1))
    assert novo.access_token == "access-novo"
    assert user.papel is Papel.OPERADOR
    assert api.tokens == [None, "access-novo"]
    assert api.calls[0][1]["query"] == {"grant_type": "refresh_token"}
    assert api.calls[0][1]["payload"] == {"refresh_token": "refresh-antigo"}


@pytest.mark.parametrize("profiles", [[], [{"id": UID, "role": "superadmin", "nome": ""}],
    [{"id": str(uuid4()), "role": "operador", "nome": ""}]])
def test_sem_profile_protegido_nao_ha_identidade(profiles):
    api = API({"id": UID}, profiles)
    with pytest.raises(PermissionError):
        ProvedorSupabase(CFG, api.factory).restaurar(sessao())


def test_sessao_revogada_falha_fechada():
    api = API(SessaoExpirada("Expirada", 401))
    with pytest.raises(SessaoExpirada):
        ProvedorSupabase(CFG, api.factory).restaurar(sessao())
    assert len(api.calls) == 1


def test_refresh_rejeitado_exige_login():
    api = API(ErroSupabase("Refresh rejeitado", 400))
    with pytest.raises(SessaoExpirada):
        ProvedorSupabase(CFG, api.factory).restaurar(
            Sessao("a", "r", time.time() - 1))


def test_indisponibilidade_nao_vira_credencial_invalida():
    api = API(ErroSupabase("Servidor indisponível", 500))
    with pytest.raises(ErroSupabase, match="indisponível"):
        ProvedorSupabase(CFG, api.factory).entrar("teste@example.com", "senha")


def test_login_rejeitado_sem_detalhes_do_servidor():
    api = API(ErroSupabase("segredo", 400))
    with pytest.raises(ValueError) as exc:
        ProvedorSupabase(CFG, api.factory).entrar("teste@example.com", "senha")
    assert "segredo" not in str(exc.value)


def test_logout_revogado_nao_impede_limpeza_local():
    api = API(SessaoExpirada("Expirada", 401))
    ProvedorSupabase(CFG, api.factory).sair(sessao())
    assert api.calls[0][1]["query"] == {"scope": "local"}


def test_tokens_nao_aparecem_no_repr():
    assert "access-secreto" not in repr(sessao())
    assert "refresh-secreto" not in repr(sessao())
