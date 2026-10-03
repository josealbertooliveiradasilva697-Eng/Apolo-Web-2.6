"""Supabase Auth real via endpoints oficiais. Tokens ficam apenas na sessão."""
from dataclasses import dataclass, field
import time
from uuid import UUID

from auth.roles import Identidade, Papel
from integrations.supabase_http import ClienteSupabase, ErroSupabase, SessaoExpirada


@dataclass(frozen=True)
class Sessao:
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_at: float

    @classmethod
    def da_resposta(cls, data):
        try:
            access, refresh = data["access_token"], data["refresh_token"]
            expires = float(data.get("expires_at") or (time.time() + float(data["expires_in"])))
            if not isinstance(access, str) or not access or not isinstance(refresh, str) or not refresh:
                raise ValueError
            if not time.time() < expires < time.time() + 86400:
                raise ValueError
            return cls(access, refresh, expires)
        except (KeyError, TypeError, ValueError, OverflowError):
            raise ErroSupabase("Resposta de autenticação inválida.") from None


class ProvedorSupabase:
    def __init__(self, config, factory=None):
        self.config = config
        self.factory = factory or ClienteSupabase

    def cliente(self, sessao=None):
        return self.factory(self.config, sessao.access_token if sessao else None)

    def entrar(self, email, senha):
        if not email.strip() or not senha:
            raise ValueError("Informe email e senha.")
        try:
            data = self.cliente().request("POST", "/auth/v1/token",
                payload={"email": email.strip(), "password": senha},
                query={"grant_type": "password"})
        except ErroSupabase as exc:
            if exc.status in {400, 401, 422}:
                raise ValueError("Não foi possível entrar. Confira email, senha e confirmação da conta.") from None
            raise
        return Sessao.da_resposta(data)

    def restaurar(self, sessao):
        if not isinstance(sessao, Sessao):
            raise SessaoExpirada("Entre novamente.")
        if sessao.expires_at <= time.time() + 30:
            try:
                data = self.cliente().request("POST", "/auth/v1/token",
                    payload={"refresh_token": sessao.refresh_token},
                    query={"grant_type": "refresh_token"})
            except ErroSupabase as exc:
                if exc.status in {400, 401, 422}:
                    raise SessaoExpirada("Sua sessão expirou. Entre novamente.") from None
                raise
            sessao = Sessao.da_resposta(data)
        client = self.cliente(sessao)
        # Não identifica usuário decodificando um JWT sem verificar sua assinatura.
        data = client.request("GET", "/auth/v1/user")
        try:
            uid = str(UUID(data["id"]))
        except (KeyError, TypeError, ValueError, AttributeError):
            raise SessaoExpirada("Usuário não confirmado pelo Supabase.") from None
        profiles = client.request("GET", "/rest/v1/profiles", query={
            "select": "id,nome,role", "id": f"eq.{uid}",
        })
        if len(profiles) != 1 or profiles[0].get("id") != uid:
            raise PermissionError("Perfil ausente. Confira a configuração da conta.")
        try:
            papel = Papel(profiles[0]["role"])
        except (KeyError, ValueError):
            raise PermissionError("Perfil não autorizado.") from None
        return sessao, Identidade(uid, papel, profiles[0]["nome"])

    def sair(self, sessao):
        try:
            self.cliente(sessao).request("POST", "/auth/v1/logout", query={"scope": "local"})
        except SessaoExpirada:
            pass
