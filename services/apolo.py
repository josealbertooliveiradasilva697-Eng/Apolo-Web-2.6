from auth.roles import Acao, Identidade, exigir
from core.calculos import calcular
from core.catalogo import CATALOGO_CALCULOS
from database.contracts import RepositorioCalculos


class ServicoApolo:
    def __init__(self, repo: RepositorioCalculos, usuario: Identidade):
        self.repo, self.usuario = repo, usuario

    def consultar(self):
        exigir(self.usuario, Acao.CONSULTAR)
        return self.repo.variaveis()

    def executar(self, id_calculo, entradas):
        exigir(self.usuario, Acao.CALCULAR)
        # Canonicaliza somente entradas declaradas; ignora campos externos.
        meta = CATALOGO_CALCULOS.get(id_calculo)
        if meta is None:
            raise ValueError("Cálculo desconhecido.")
        saidas = calcular(id_calculo, entradas)
        snapshot = {nome:float(entradas[nome]) for nome in meta["entradas"]}
        id_execucao = self.repo.salvar_execucao(id_calculo, snapshot, saidas)
        return {"id_execucao":id_execucao,"id_calculo":id_calculo,"entradas":snapshot,"saidas":saidas}

    def configurar(self, nome, valor):
        exigir(self.usuario, Acao.CONFIGURAR)
        self.repo.configurar(nome, valor)

    def historico(self):
        exigir(self.usuario, Acao.CONSULTAR)
        return self.repo.historico()

    def detalhe(self, id_execucao):
        exigir(self.usuario, Acao.CONSULTAR)
        return self.repo.detalhe(id_execucao)

    def diagnosticar(self):
        exigir(self.usuario, Acao.DIAGNOSTICAR)
        return self.repo.diagnostico()
