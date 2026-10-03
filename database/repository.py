from contextlib import contextmanager
from datetime import datetime
import hashlib
import math
from pathlib import Path
import re
import sqlite3

from core.catalogo import CATALOGO_VARIAVEIS, CATALOGO_CALCULOS, SCHEMA_VERSION, VERSAO_PROGRAMA

SCHEMA = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")


def agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def assinatura_schema(conn):
    """Compara colunas, chaves e índices; ignora tabelas extras do legado."""
    expected = sqlite3.connect(":memory:")
    expected.executescript(SCHEMA)
    try:
        result = {}
        for (nome,) in expected.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (nome,)).fetchone():
                raise ValueError(f"Tabela obrigatória ausente: {nome}.")
            result[nome] = {}
            for pragma in ("table_info", "foreign_key_list", "index_list"):
                want = sorted(tuple(r) for r in expected.execute(f'PRAGMA {pragma}("{nome}")'))
                got = sorted(tuple(r) for r in conn.execute(f'PRAGMA {pragma}("{nome}")'))
                if want != got:
                    raise ValueError(f"Schema incompatível em {nome}: {pragma}. Importação cancelada.")
                result[nome][pragma] = got
            for index in result[nome]["index_list"]:
                index_name = index[1]
                want = list(expected.execute(f'PRAGMA index_info("{index_name}")'))
                got = [tuple(r) for r in conn.execute(f'PRAGMA index_info("{index_name}")')]
                if want != got:
                    raise ValueError(f"Índice incompatível: {index_name}.")
            # Confere também CHECK e demais restrições não descritas pelos PRAGMAs.
            def ddl(db):
                sql=db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?",(nome,)).fetchone()[0]
                return re.sub(r"\s+"," ",sql).strip()
            if ddl(conn)!=ddl(expected):
                raise ValueError(f"Restrições de tabela incompatíveis: {nome}.")
        return result
    finally:
        expected.close()


def inspecionar_arquivo(path: Path):
    path = path.resolve(strict=True)
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as conn:
        integridade = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integridade != "ok":
            raise ValueError("O banco não passou no teste de integridade.")
        if conn.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("O banco contém referências inválidas.")
        schema = assinatura_schema(conn)
        metadata = dict(conn.execute("SELECT chave, valor FROM metadata"))
        if metadata.get("schema_version") != str(SCHEMA_VERSION):
            raise ValueError("Versão de schema diferente de 2.")
        for nome, meta in CATALOGO_VARIAVEIS.items():
            row = conn.execute("SELECT nome, unidade_si, unidade_codigo, tipo, eh_saida FROM variaveis WHERE id_variavel=?", (meta["id_variavel"],)).fetchone()
            if row != (nome, meta["unidade_si"], meta["unidade_codigo"], meta["tipo"], meta["eh_saida"]):
                raise ValueError(f"Catálogo incompatível: {nome}.")
        for id_calc, meta in CATALOGO_CALCULOS.items():
            row = conn.execute("SELECT nome, versao, formula FROM calculos WHERE id_calculo=?", (id_calc,)).fetchone()
            if row != (meta["nome"], meta["versao"], meta["formula"]):
                raise ValueError(f"Definição de cálculo incompatível: {id_calc}.")
            rows = conn.execute("SELECT id_variavel, papel FROM dependencias_calculo WHERE id_calculo=? ORDER BY ordem", (id_calc,)).fetchall()
            expected = [(CATALOGO_VARIAVEIS[n]["id_variavel"], p) for p, names in (("entrada",meta["entradas"]),("saida",meta["saidas"])) for n in names]
            if rows != expected:
                raise ValueError(f"Dependências incompatíveis: {id_calc}.")
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        counts = {n: conn.execute('SELECT COUNT(*) FROM "' + n.replace('"','""') + '"').fetchone()[0] for n in tables}
    return {"arquivo": path.name, "sha256":hashlib.sha256(path.read_bytes()).hexdigest(), "metadata":metadata,"contagens":counts,"schema":schema,"integridade":integridade}


class RepositorioSQLite:
    @property
    def contexto(self):
        return f"sqlite:{self.path}"

    def diagnostico(self):
        return inspecionar_arquivo(self.path)

    def __init__(self, data_dir: Path, nome: str = "Apolo_teste.db"):
        if not re.fullmatch(r"[A-Za-z0-9_-]+\.db", nome):
            raise ValueError("Nome do banco inválido.")
        self.data_dir = data_dir.resolve()
        self.path = (self.data_dir / nome).resolve()
        if self.path.parent != self.data_dir:
            raise ValueError("O banco deve ser uma cópia na pasta de trabalho.")
        # Arquivos em originals nunca são usados para gravação.
        if "originals" in (p.lower() for p in self.path.parts):
            raise ValueError("Não é permitido gravar na pasta de originais.")

    @contextmanager
    def conectar(self):
        # Verifica novamente para rejeitar links trocados após a construção.
        if self.path.resolve().parent != self.data_dir:
            raise ValueError("Caminho do banco alterado.")
        conn = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 15000")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def criar_novo(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            inspecionar_arquivo(self.path)
            return
        # x cria exclusivamente; nunca substitui arquivo existente.
        with self.path.open("xb"):
            pass
        conn = sqlite3.connect(self.path)
        try:
            conn.executescript(SCHEMA)
            with conn:
                timestamp = agora()
                conn.executemany("INSERT INTO metadata(chave,valor) VALUES(?,?)", [
                    ("programa", "Programa para cálculos Aerodinâmicos"),
                    ("versao_programa",VERSAO_PROGRAMA),("schema_version",str(SCHEMA_VERSION)),
                    ("origem_web","Banco novo para testes locais; não contém o histórico do Drive."),
                ])
                for meta in CATALOGO_VARIAVEIS.values():
                    conn.execute("INSERT INTO variaveis VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                        meta["id_variavel"],meta["nome"],meta["padrao"] if meta["tipo"]=="REAL" else None,
                        meta["padrao"] if meta["tipo"]=="TEXT" else None,meta["unidade_si"],meta["unidade_codigo"],
                        meta["tipo"],meta["categoria"],meta["eh_saida"],meta["descricao"],timestamp))
                for id_calc, meta in CATALOGO_CALCULOS.items():
                    conn.execute("INSERT INTO calculos VALUES(?,?,?,?,?,?,1,?,?)",(id_calc,meta["nome"],meta["versao"],meta["formula"],meta["unidade_saida"],meta["descricao"],timestamp,timestamp))
                    ordem = 1
                    for papel,names in (("entrada",meta["entradas"]),("saida",meta["saidas"])):
                        for nome in names:
                            conn.execute("INSERT INTO dependencias_calculo VALUES(?,?,?,?)",(id_calc,CATALOGO_VARIAVEIS[nome]["id_variavel"],papel,ordem))
                            ordem += 1
        finally:
            conn.close()

    def variaveis(self):
        with self.conectar() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM variaveis ORDER BY eh_saida, categoria, nome")]

    def valores(self):
        return {r["nome"]: r["valor_real"] if r["tipo"]=="REAL" else r["valor_texto"] for r in self.variaveis()}

    def _atualizar(self, conn, nome, valor):
        meta = CATALOGO_VARIAVEIS[nome]
        if meta["tipo"]=="REAL":
            real, texto = float(valor), None
            if not math.isfinite(real):
                raise ValueError("O valor deve ser finito.")
        else:
            real, texto = None, str(valor)
        cur = conn.execute("UPDATE variaveis SET valor_real=?,valor_texto=?,atualizado_em=? WHERE id_variavel=?",(real,texto,agora(),meta["id_variavel"]))
        if cur.rowcount != 1:
            raise ValueError(f"Variável ausente: {nome}.")
        return real,texto,meta

    def salvar_execucao(self, id_calculo, entradas, saidas):
        with self.conectar() as conn:
            cur = conn.execute("INSERT INTO execucoes(id_calculo,executado_em,status,mensagem) VALUES(?,?,'SUCESSO',NULL)",(id_calculo,agora()))
            id_execucao = cur.lastrowid
            for papel,values in (("entrada",entradas),("saida",saidas)):
                for nome,valor in values.items():
                    real,texto,meta = self._atualizar(conn,nome,valor)
                    conn.execute("INSERT INTO execucao_valores VALUES(?,?,?,?,?,?)",(id_execucao,meta["id_variavel"],papel,real,texto,meta["unidade_si"]))
            return id_execucao

    def configurar(self, nome, valor):
        if nome not in CATALOGO_VARIAVEIS or CATALOGO_VARIAVEIS[nome]["eh_saida"]:
            raise ValueError("Somente variáveis de entrada podem ser configuradas.")
        with self.conectar() as conn:
            self._atualizar(conn,nome,valor)

    def historico(self, limite=200):
        with self.conectar() as conn:
            return [dict(r) for r in conn.execute("SELECT e.*,c.nome FROM execucoes e JOIN calculos c USING(id_calculo) ORDER BY id_execucao DESC LIMIT ?",(limite,))]

    def detalhe(self, id_execucao):
        with self.conectar() as conn:
            return [dict(r) for r in conn.execute("SELECT v.nome,ev.* FROM execucao_valores ev JOIN variaveis v USING(id_variavel) WHERE id_execucao=? ORDER BY papel,nome",(id_execucao,))]
