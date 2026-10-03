import os
from typing import Protocol
from .roles import Identidade, Papel


class ProvedorIdentidade(Protocol):
    def identificar(self) -> Identidade: ...


class ProvedorLocal:
    """Perfil de teste configurado no servidor. Não é autenticação de usuários."""

    def identificar(self) -> Identidade:
        papel = Papel(os.environ.get("APOLO_LOCAL_ROLE", "operador"))
        return Identidade("local-teste", papel, "Teste local")


def obter_identidade() -> Identidade:
    modo = os.environ.get("APOLO_AUTH_MODE", "local")
    if modo != "local":
        raise RuntimeError("O provedor de autenticação ainda não está integrado. Use o modo local para testes.")
    return ProvedorLocal().identificar()
