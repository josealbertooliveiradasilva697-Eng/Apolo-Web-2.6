"""PostgREST com JWT individual; escrita atômica por RPC autorizado."""
from uuid import UUID

from core.catalogo import CATALOGO_CALCULOS, CATALOGO_VARIAVEIS
from integrations.supabase_http import ErroSupabase


def uuid_valido(valor):
    try:
        return str(UUID(str(valor)))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Identificador inválido.") from None


class RepositorioProjetosSupabase:
    def __init__(self, cliente, usuario):
        self.cliente, self.usuario = cliente, usuario

    def listar(self):
        return self.cliente.request("GET", "/rest/v1/projects", query={
            "select": "id,nome,owner_id,created_at",
            "owner_id": f"eq.{uuid_valido(self.usuario.id)}",
            "order": "created_at.asc,id.asc",
        })

    def criar(self, nome):
        return self.cliente.request("POST", "/rest/v1/projects",
            payload={"nome": nome, "owner_id": uuid_valido(self.usuario.id)})[0]

    def obter(self, projeto_id):
        rows = self.cliente.request("GET", "/rest/v1/projects", query={
            "select": "id,nome,owner_id",
            "id": f"eq.{uuid_valido(projeto_id)}",
            "owner_id": f"eq.{uuid_valido(self.usuario.id)}",
        })
        if len(rows) != 1:
            raise PermissionError("Projeto ausente ou não autorizado.")
        return rows[0]


class RepositorioSupabase:
    def __init__(self, cliente, usuario, projeto_id):
        self.cliente, self.usuario = cliente, usuario
        self.projeto_id = uuid_valido(projeto_id)
        RepositorioProjetosSupabase(cliente, usuario).obter(self.projeto_id)

    @property
    def contexto(self):
        return f"supabase:{self.usuario.id}:{self.projeto_id}"

    def variaveis(self):
        definitions = self.cliente.request("GET", "/rest/v1/variables", query={
            "select": "*", "order": "eh_saida.asc,categoria.asc,nome.asc",
        })
        values = self.cliente.request("GET", "/rest/v1/project_values", query={
            "select": "id_variavel,valor_real,valor_texto,atualizado_em",
            "project_id": f"eq.{self.projeto_id}",
        })
        current = {r["id_variavel"]: r for r in values}
        # Detecta catalogo/migration incompleto em vez de retornar defaults fictícios.
        if set(current) != {m["id_variavel"] for m in CATALOGO_VARIAVEIS.values()}:
            raise ErroSupabase("Projeto ou catálogo incompleto. Confira as migrations.")
        if {r["id_variavel"] for r in definitions} != set(current):
            raise ErroSupabase("Catálogo online incompatível com esta versão.")
        return [{**r, **current[r["id_variavel"]]} for r in definitions]

    def salvar_execucao(self, id_calculo, entradas, saidas):
        result = self.cliente.request("POST", "/rest/v1/rpc/apolo_save_execution", payload={
            "p_project_id": self.projeto_id, "p_id_calculo": id_calculo,
            "p_entradas": entradas, "p_saidas": saidas,
        })
        return uuid_valido(result)

    def configurar(self, nome, valor):
        if nome not in CATALOGO_VARIAVEIS or CATALOGO_VARIAVEIS[nome]["eh_saida"]:
            raise ValueError("Somente variáveis de entrada podem ser configuradas.")
        self.cliente.request("POST", "/rest/v1/rpc/apolo_configure", payload={
            "p_project_id": self.projeto_id, "p_nome": nome, "p_valor": valor,
        })

    def historico(self, limite=200):
        if not isinstance(limite, int) or not 1 <= limite <= 200:
            raise ValueError("Limite deve estar entre 1 e 200.")
        rows = self.cliente.request("GET", "/rest/v1/executions", query={
            "select": "id_execucao:id,id_calculo,executado_em,status,mensagem",
            "project_id": f"eq.{self.projeto_id}", "order": "executado_em.desc,id.desc",
            "limit": limite,
        })
        return [{**r, "nome": CATALOGO_CALCULOS[r["id_calculo"]]["nome"]} for r in rows]

    def detalhe(self, id_execucao):
        identificador = uuid_valido(id_execucao)
        # Contexto de projeto também importa quando dois projetos são do mesmo usuário.
        rows = self.cliente.request("GET", "/rest/v1/executions", query={
            "select": "id", "id": f"eq.{identificador}",
            "project_id": f"eq.{self.projeto_id}",
        })
        if not rows:
            return []
        values = self.cliente.request("GET", "/rest/v1/execution_values", query={
            "select": "id_execucao:execution_id,id_variavel,papel,valor_real,valor_texto,unidade_si",
            "execution_id": f"eq.{identificador}", "order": "papel.asc,id_variavel.asc",
        })
        names = {m["id_variavel"]: name for name, m in CATALOGO_VARIAVEIS.items()}
        return [{**r, "nome": names[r["id_variavel"]]} for r in values]

    def diagnostico(self):
        return self.cliente.request("POST", "/rest/v1/rpc/apolo_diagnostics",
            payload={"p_project_id": self.projeto_id})
