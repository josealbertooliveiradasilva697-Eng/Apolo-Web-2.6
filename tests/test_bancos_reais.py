import hashlib
from pathlib import Path
import sqlite3
import pytest
from auth.roles import Identidade, Papel
from core.calculos import calcular
from database.repository import RepositorioSQLite, inspecionar_arquivo
from tools.importar_banco import importar
from services.apolo import ServicoApolo

ORIGINALS=Path(__file__).resolve().parents[1]/"originals"


@pytest.mark.parametrize("filename,execucoes",[("Banco_de_Variaveis_Calculo_1.db",1),("123.db",7)])
def test_historico_real_e_importacao_preservados(filename,execucoes,tmp_path):
    source=ORIGINALS/filename
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    assert inspecionar_arquivo(source)["contagens"]["execucoes"]==execucoes
    conn=sqlite3.connect(source.as_uri()+"?mode=ro",uri=True)
    try:
        for id_exec, id_calc in conn.execute("SELECT id_execucao,id_calculo FROM execucoes WHERE status='SUCESSO'"):
            rows=conn.execute("SELECT v.nome,ev.papel,ev.valor_real FROM execucao_valores ev JOIN variaveis v USING(id_variavel) WHERE id_execucao=?",(id_exec,)).fetchall()
            entries={n:v for n,p,v in rows if p=="entrada"}
            outputs={n:v for n,p,v in rows if p=="saida"}
            assert calcular(id_calc,entries)==outputs
    finally:
        conn.close()
    repo=RepositorioSQLite(tmp_path/"copies","Copia.db")
    user=Identidade("teste",Papel.DESENVOLVEDOR,"Teste")
    importar(source,repo,user)
    assert len(repo.historico())==execucoes
    ServicoApolo(repo,user).executar("CAL_NEWTON",{"Massa da aeronave":1000,"Aceleração":2})
    assert len(repo.historico())==execucoes+1
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
