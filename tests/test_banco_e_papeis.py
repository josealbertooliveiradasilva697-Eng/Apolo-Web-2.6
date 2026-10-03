import hashlib
import json
from pathlib import Path
import sqlite3
import re
from concurrent.futures import ThreadPoolExecutor
import pytest
from auth.roles import Acao, Identidade, Papel, exigir
from core.catalogo import CATALOGO_CALCULOS
from database.repository import RepositorioSQLite, inspecionar_arquivo
from services.apolo import ServicoApolo
from tools.importar_banco import importar


RAIZ = Path(__file__).resolve().parents[1]
FIXTURE_SCHEMA = RAIZ / "tests" / "fixtures" / "schema_apolo_26.json"


with FIXTURE_SCHEMA.open("r", encoding="utf-8") as arquivo:
    REFERENCIA_SCHEMA = json.load(arquivo)


@pytest.fixture
def repo(tmp_path):
    repository=RepositorioSQLite(tmp_path/"data")
    repository.criar_novo()
    return repository


def user(papel=Papel.OPERADOR):
    return Identidade("teste",papel,"Teste")


def entradas_newton():
    return dict(zip(CATALOGO_CALCULOS["CAL_NEWTON"]["entradas"],[1000,2]))


def test_schema_idêntico_ao_original(repo):
    assert len(REFERENCIA_SCHEMA["objetos"]) == 11
    assert REFERENCIA_SCHEMA["proveniencia"]["sha256"] == (
        "b06d2d4e064fdafd8c2edae0130435175022da7c62dc2221ee881edb1ae949e7"
    )
    query="SELECT type,name,tbl_name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
    def normalize(rows):
        return [(kind,name,table,re.sub(r"\s+"," ",sql).strip()) for kind,name,table,sql in rows]

    expected = [
        (
            objeto["tipo"],
            objeto["nome"],
            objeto["tabela"],
            objeto["sql"],
        )
        for objeto in REFERENCIA_SCHEMA["objetos"]
    ]

    with repo.conectar() as conn:
        assert normalize(conn.execute(query)) == expected


def test_snapshot_e_valores_persistidos(repo):
    s=ServicoApolo(repo,user())
    result=s.executar("CAL_NEWTON",entradas_newton())
    assert result["saidas"]=={"Força resultante":2000.0}
    assert len(s.detalhe(result["id_execucao"]))==3
    assert repo.valores()["Força resultante"]==2000
    s.executar("CAL_NEWTON",{**entradas_newton(),"Aceleração":3})
    assert next(r["valor_real"] for r in s.detalhe(1) if r["nome"]=="Aceleração")==2


def test_reabertura_sem_alterar_dados(repo):
    ServicoApolo(repo,user()).executar("CAL_NEWTON",entradas_newton())
    before=repo.path.read_bytes()
    repo.criar_novo()
    assert repo.path.read_bytes()==before


def test_transacao_rollback(repo):
    valores=repo.valores()
    with pytest.raises(KeyError):
        repo.salvar_execucao("CAL_NEWTON",entradas_newton(),{"Variável desconhecida":2000})
    assert repo.historico()==[]
    assert repo.valores()==valores


def test_invalido_nao_grava_parcial(repo):
    before=repo.valores()
    with pytest.raises(ValueError):
        ServicoApolo(repo,user()).executar("CAL_BREG",dict(zip(CATALOGO_CALCULOS["CAL_BREG"]["entradas"],[100,0,20000,1000,100000,80000])))
    assert repo.valores()==before
    assert repo.historico()==[]


def test_operador_nao_configura_mesmo_fora_da_tela(repo):
    with pytest.raises(PermissionError):
        ServicoApolo(repo,user()).configurar("gravidade",9.8)
    assert repo.valores()["gravidade"]==9.81


def test_admin_configura_mas_nao_importa(repo,tmp_path):
    admin=user(Papel.ADMIN)
    ServicoApolo(repo,admin).configurar("gravidade",9.8)
    assert repo.valores()["gravidade"]==9.8
    with pytest.raises(PermissionError): importar(repo.path,RepositorioSQLite(tmp_path/"copies"),admin)


@pytest.mark.parametrize("papel",list(Papel))
def test_papeis(papel):
    exigir(user(papel),Acao.CALCULAR)
    if papel!=Papel.DESENVOLVEDOR:
        with pytest.raises(PermissionError): exigir(user(papel),Acao.DIAGNOSTICAR)


def test_importacao_preserva_origem_e_schema(repo,tmp_path):
    ServicoApolo(repo,user()).executar("CAL_NEWTON",entradas_newton())
    before=hashlib.sha256(repo.path.read_bytes()).hexdigest()
    copia=RepositorioSQLite(tmp_path/"copies","Importado.db")
    report=importar(repo.path,copia,user(Papel.DESENVOLVEDOR))
    assert report["origem_preservada"]
    assert hashlib.sha256(repo.path.read_bytes()).hexdigest()==before
    assert copia.valores()==repo.valores()
    assert copia.historico()==repo.historico()
    assert inspecionar_arquivo(copia.path)["schema"]==inspecionar_arquivo(repo.path)["schema"]
    with pytest.raises(FileExistsError): importar(repo.path,copia,user(Papel.DESENVOLVEDOR))


def test_importacao_incompativel_nao_cria_copia(tmp_path):
    path=tmp_path/"legado.db"
    with sqlite3.connect(path) as conn: conn.execute("CREATE TABLE variaveis(chave TEXT,valor TEXT)")
    copia=RepositorioSQLite(tmp_path/"copies")
    with pytest.raises(ValueError): importar(path,copia,user(Papel.DESENVOLVEDOR))
    assert not copia.path.exists()


def test_caminhos_fora_da_copia_rejeitados(tmp_path):
    with pytest.raises(ValueError): RepositorioSQLite(tmp_path,"../fonte.db")
    with pytest.raises(ValueError): RepositorioSQLite(tmp_path/"originals","fonte.db")


def test_duas_execucoes_concorrentes_mantem_snapshots(repo):
    def run(a):
        return ServicoApolo(repo,user()).executar("CAL_NEWTON",{**entradas_newton(),"Aceleração":a})
    with ThreadPoolExecutor(max_workers=2) as executor:
        results=list(executor.map(run,[2,3]))
    for r in results:
        detalhe=repo.detalhe(r["id_execucao"])
        assert next(v["valor_real"] for v in detalhe if v["nome"]=="Aceleração")==r["entradas"]["Aceleração"]
        assert next(v["valor_real"] for v in detalhe if v["nome"]=="Força resultante")==r["saidas"]["Força resultante"]
