"""O serviço precisa funcionar sem conexão ou caminho de SQLite."""

import pytest

from auth.roles import Identidade, Papel
from services.apolo import ServicoApolo


class RepositorioMemoria:
    contexto = "projeto:teste"

    def __init__(self):
        self.execucoes = []

    def salvar_execucao(self, id_calculo, entradas, saidas):
        self.execucoes.append((id_calculo, entradas, saidas))
        return "id-remoto"

    def diagnostico(self):
        return {"execucoes": len(self.execucoes)}

    def configurar(self, nome, valor):
        pytest.fail("Operador não pode alcançar a persistência para configurar.")


def test_servico_nao_exige_arquivo_e_preserva_snapshot():
    repo = RepositorioMemoria()
    servico = ServicoApolo(repo, Identidade("u", Papel.OPERADOR, "Teste"))
    resultado = servico.executar(
        "CAL_NEWTON", {"Massa da aeronave": 1000, "Aceleração": 2, "externo": 99}
    )
    assert resultado["id_execucao"] == "id-remoto"
    assert repo.execucoes == [
        ("CAL_NEWTON", {"Massa da aeronave": 1000.0, "Aceleração": 2.0},
         {"Força resultante": 2000.0})
    ]
    with pytest.raises(PermissionError):
        servico.configurar("gravidade", 9.8)
    with pytest.raises(PermissionError):
        servico.diagnosticar()


def test_diagnostico_so_para_desenvolvedor():
    servico = ServicoApolo(
        RepositorioMemoria(), Identidade("u", Papel.DESENVOLVEDOR, "Teste")
    )
    assert servico.diagnosticar() == {"execucoes": 0}
