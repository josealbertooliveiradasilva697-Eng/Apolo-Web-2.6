"""Integração em PostgreSQL real, exclusivo de banco de teste vazio.

CI configura um container dedicado. Nunca executar contra banco de produção.
O bootstrap simula apenas auth.users/auth.uid; não simula RLS/grants/transações.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DSN = os.environ.get("APOLO_TEST_POSTGRES_DSN")
pytestmark = pytest.mark.skipif(not DSN, reason="PostgreSQL de teste não configurado.")


@pytest.fixture(scope="module")
def postgres():
    if os.environ.get("APOLO_TEST_POSTGRES_ISOLATED") != "1":
        pytest.fail("Exige APOLO_TEST_POSTGRES_ISOLATED=1 e banco dedicado vazio.")
    import psycopg
    with psycopg.connect(DSN, autocommit=True) as conn:
        if conn.execute("select to_regclass('public.profiles')").fetchone()[0]:
            pytest.fail("Banco de teste já contém profiles; nada foi apagado.")
        conn.execute("""
            create role anon nologin;
            create role authenticated nologin;
            create schema auth;
            create table auth.users(
                id uuid primary key, email text, raw_user_meta_data jsonb default '{}'
            );
            create function auth.uid() returns uuid language sql stable as
              $$ select nullif(current_setting('request.jwt.claim.sub',true),'')::uuid $$;
            grant usage on schema auth to authenticated,anon;
            grant execute on function auth.uid() to authenticated,anon;
        """)
        for path in sorted((RAIZ / "supabase" / "migrations").glob("*.sql")):
            conn.execute(path.read_text(encoding="utf-8"))
    yield


@pytest.fixture
def db(postgres):
    import psycopg
    with psycopg.connect(DSN) as conn:
        yield conn
        conn.rollback()


def usuario(conn, role="operador"):
    uid = uuid4()
    conn.execute("insert into auth.users(id,email,raw_user_meta_data) values(%s,%s,%s::jsonb)",
        (uid, "teste@example.invalid", json.dumps({"nome": "Teste", "role": "desenvolvedor"})))
    # Promoção só pelo administrador de banco; cliente não tem UPDATE.
    if role != "operador":
        conn.execute("update public.profiles set role=%s where id=%s", (role, uid))
    return uid


@contextmanager
def autenticado(conn, uid=None, role="authenticated"):
    assert role in {"authenticated", "anon"}
    conn.execute(f"set local role {role}")
    conn.execute("select set_config('request.jwt.claim.sub',%s,true)", (str(uid) if uid else "",))
    try:
        yield
    finally:
        conn.execute("reset role")


def projeto(conn, uid):
    with autenticado(conn, uid):
        return conn.execute("insert into public.projects(nome,owner_id) values('Projeto',%s) returning id",
            (uid,)).fetchone()[0]


def salvar(conn, pid, entradas=None, saidas=None):
    return conn.execute("select public.apolo_save_execution(%s,'CAL_NEWTON',%s::jsonb,%s::jsonb)",
        (pid, json.dumps(entradas or {"Massa da aeronave": 1000, "Aceleração": 2}),
         json.dumps(saidas or {"Força resultante": 2000}))).fetchone()[0]


def test_novo_profile_ignora_promocao_em_metadata(db):
    uid = usuario(db)
    assert db.execute("select role from public.profiles where id=%s", (uid,)).fetchone()[0] == "operador"
    pid = projeto(db, uid)
    with autenticado(db, uid):
        assert db.execute("select count(*) from public.project_values where project_id=%s", (pid,)).fetchone()[0] == 23


def test_isolamento_usuario_e_grants_diretos(db):
    from psycopg.errors import InsufficientPrivilege
    a, b = usuario(db), usuario(db)
    pa, pb = projeto(db, a), projeto(db, b)
    with autenticado(db, a):
        execution = salvar(db, pa)
    with autenticado(db, b):
        for table in ("projects", "project_values", "executions", "execution_values", "profiles"):
            rows = db.execute(f"select * from public.{table}").fetchall()
            # profiles/projetos/valores de B existem; execuções/valores de A são invisíveis.
            if table in {"executions", "execution_values"}:
                assert rows == []
        assert db.execute("select count(*) from public.projects where id=%s", (pa,)).fetchone()[0] == 0
        assert db.execute("select count(*) from public.project_values where project_id=%s", (pa,)).fetchone()[0] == 0
        assert db.execute("select count(*) from public.profiles where id=%s", (a,)).fetchone()[0] == 0
        with pytest.raises(InsufficientPrivilege), db.transaction():
            salvar(db, pa)
        with pytest.raises(InsufficientPrivilege), db.transaction():
            db.execute("update public.profiles set role='desenvolvedor' where id=%s", (b,))
        with pytest.raises(InsufficientPrivilege), db.transaction():
            db.execute("update public.project_values set valor_real=99 where project_id=%s", (pb,))
        with pytest.raises(InsufficientPrivilege), db.transaction():
            db.execute("insert into public.projects(nome,owner_id) values('Outro',%s)", (a,))
        with pytest.raises(InsufficientPrivilege), db.transaction():
            db.execute("insert into public.executions(project_id,user_id,id_calculo,status) values(%s,%s,'CAL_NEWTON','SUCESSO')", (pb,b))


@pytest.mark.parametrize("role", ["operador", "admin", "desenvolvedor"])
def test_configuracao_e_diagnostico_por_papel_no_banco(db, role):
    from psycopg.errors import InsufficientPrivilege
    uid = usuario(db, role)
    pid = projeto(db, uid)
    with autenticado(db, uid):
        salvar(db, pid)
        statement = "select public.apolo_configure(%s,'gravidade','9.8'::jsonb)"
        if role == "operador":
            with pytest.raises(InsufficientPrivilege), db.transaction():
                db.execute(statement, (pid,))
        else:
            db.execute(statement, (pid,))
            assert db.execute("select valor_real from public.project_values where project_id=%s and id_variavel='G_m_s2'", (pid,)).fetchone()[0] == 9.8
        if role == "desenvolvedor":
            result = db.execute("select public.apolo_diagnostics(%s)", (pid,)).fetchone()[0]
            assert result["execucoes"] == 1
        else:
            with pytest.raises(InsufficientPrivilege), db.transaction():
                db.execute("select public.apolo_diagnostics(%s)", (pid,))


def test_anon_sem_leitura_ou_rpc(db):
    from psycopg.errors import InsufficientPrivilege
    uid = usuario(db)
    pid = projeto(db, uid)
    with autenticado(db, role="anon"):
        with pytest.raises(InsufficientPrivilege), db.transaction():
            db.execute("select * from public.projects")
        with pytest.raises(InsufficientPrivilege), db.transaction():
            salvar(db, pid)


def test_rollback_snapshot_invalido(db):
    from psycopg.errors import InvalidParameterValue
    uid = usuario(db)
    pid = projeto(db, uid)
    with autenticado(db, uid):
        before = db.execute("select id_variavel,valor_real,valor_texto from public.project_values where project_id=%s order by id_variavel", (pid,)).fetchall()
        with pytest.raises(InvalidParameterValue), db.transaction():
            salvar(db, pid, saidas={"Força resultante": "texto"})
        assert db.execute("select count(*) from public.executions").fetchone()[0] == 0
        assert db.execute("select id_variavel,valor_real,valor_texto from public.project_values where project_id=%s order by id_variavel", (pid,)).fetchall() == before


def test_600_snapshots_equivalentes_persistidos(db):
    from core.calculos import calcular
    referencia = json.loads((RAIZ / "tests" / "fixtures" / "equivalencia_apolo_26.json").read_text(encoding="utf-8"))
    uid = usuario(db)
    pid = projeto(db, uid)
    with autenticado(db, uid):
        for caso in referencia["casos"]:
            outputs = calcular(caso["id_calc"], caso["entradas"])
            assert outputs == caso["saidas"]
            eid = db.execute("select public.apolo_save_execution(%s,%s,%s::jsonb,%s::jsonb)",
                (pid,caso["id_calc"],json.dumps(caso["entradas"]),json.dumps(outputs))).fetchone()[0]
            persisted = dict(db.execute("""
                select v.nome,ev.valor_real from public.execution_values ev
                join public.variables v using(id_variavel)
                where ev.execution_id=%s and ev.papel='saida'
            """, (eid,)).fetchall())
            assert persisted == caso["saidas"]
        assert db.execute("select count(*) from public.executions").fetchone()[0] == 600
