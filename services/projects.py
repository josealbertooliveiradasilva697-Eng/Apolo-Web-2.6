"""Criação/seleção de projetos também passa por autorização."""
from auth.roles import Acao, exigir


class ServicoProjetos:
    def __init__(self, repo, usuario):
        self.repo, self.usuario = repo, usuario

    def listar(self):
        exigir(self.usuario, Acao.CONSULTAR)
        return self.repo.listar()

    def criar(self, nome):
        exigir(self.usuario, Acao.CALCULAR)
        nome = nome.strip()
        if not 1 <= len(nome) <= 120:
            raise ValueError("Nome do projeto deve ter entre 1 e 120 caracteres.")
        return self.repo.criar(nome)

    def selecionar(self, projeto_id):
        exigir(self.usuario, Acao.CONSULTAR)
        return self.repo.obter(projeto_id)
