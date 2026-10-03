import os
from typing import Protocol
from .roles import Identidade, Papel
from config import Configuracao


class ProvedorIdentidade(Protocol):
    def identificar(self) -> Identidade: ...


class ProvedorLocal:
    """Perfil de teste configurado no servidor. Não é autenticação de usuários."""

    def identificar(self) -> Identidade:
        if Configuracao.carregar().auth_mode != "local":
            raise RuntimeError("Provider local disponível somente em desenvolvimento SQLite.")
        papel = Papel(os.environ.get("APOLO_LOCAL_ROLE", "operador"))
        return Identidade("local-teste", papel, "Teste local")


def obter_identidade() -> Identidade:
    modo = os.environ.get("APOLO_AUTH_MODE", "local")
    if modo != "local":
        raise RuntimeError("obter_identidade é exclusivo do modo local. Para login online, use ProvedorSupabase.")
    return ProvedorLocal().identificar()
