from dataclasses import dataclass
from enum import Enum


class Papel(str, Enum):
    OPERADOR = "operador"
    ADMIN = "admin"
    DESENVOLVEDOR = "desenvolvedor"


@dataclass(frozen=True)
class Identidade:
    id: str
    papel: Papel
    nome: str


class Acao(str, Enum):
    CONSULTAR = "consultar"
    CALCULAR = "calcular"
    CONFIGURAR = "configurar"
    DIAGNOSTICAR = "diagnosticar"
    IMPORTAR_BANCO = "importar_banco"


PERMISSOES = {
    Papel.OPERADOR: frozenset({Acao.CONSULTAR, Acao.CALCULAR}),
    Papel.ADMIN: frozenset({Acao.CONSULTAR, Acao.CALCULAR, Acao.CONFIGURAR}),
    Papel.DESENVOLVEDOR: frozenset(Acao),
}


def permitido(usuario: Identidade, acao: Acao) -> bool:
    return acao in PERMISSOES.get(usuario.papel, frozenset())


def exigir(usuario: Identidade, acao: Acao) -> None:
    if not permitido(usuario, acao):
        raise PermissionError("Seu perfil não permite esta operação.")
