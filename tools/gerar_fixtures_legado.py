import ast
import hashlib
import json
import math
import random
import re
import sqlite3
from pathlib import Path
from types import SimpleNamespace

from core.catalogo import CATALOGO_CALCULOS


RAIZ = Path(__file__).resolve().parents[1]

SOURCE = RAIZ / "originals" / "Apolo_2_6_exportado.py"
DESTINO = RAIZ / "tests" / "fixtures"

MAPPING = {
    "CAL_SUST": "calcular_sustentacao",
    "CAL_ARR": "calcular_arrasto",
    "CAL_EMP": "calcular_Empuxo_de_Motor_a_Jato",
    "CAL_NEWTON": "calcular_Newton",
    "CAL_BER": "calcular_Bernoulli",
    "CAL_BREG": "calcular_Breguet",
}


if not SOURCE.exists():
    raise FileNotFoundError(
        f"Arquivo legado não encontrado: {SOURCE}"
    )


CODIGO_FONTE = SOURCE.read_text(encoding="utf-8")
TREE = ast.parse(CODIGO_FONTE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def executar_original(id_calc, entradas):
    """
    Executa somente a função de cálculo correspondente do Apolo 2.6,
    sem inicializar Colab, Google Drive ou banco de dados real.
    """

    callbacks = []
    resultados = []

    class Button:
        def __init__(self, **kwargs):
            pass

        def on_click(self, callback):
            callbacks.append(callback)

    widgets = SimpleNamespace(
        Button=Button,
        HTML=lambda **kwargs: SimpleNamespace(value=""),
        Label=lambda **kwargs: None,
        VBox=lambda valores: valores,
    )

    ambiente = {
        "math": math,
        "widgets": widgets,
        "display": lambda *args: None,
        "criar_float_widget": (
            lambda nome, *args: SimpleNamespace(value=entradas[nome])
        ),
        "ler_variavel_float": (
            lambda nome, *args: entradas[nome]
        ),
        "atualizar_resultado": lambda *args: None,
        "salvar_variavel": lambda *args: None,
        "registrar_execucao": (
            lambda *args, **kwargs: resultados.append(kwargs["saidas"])
        ),
    }

    nome_funcao = MAPPING[id_calc]

    node = next(
        n
        for n in TREE.body
        if isinstance(n, ast.FunctionDef)
        and n.name == nome_funcao
    )

    modulo = ast.Module(
        body=[node],
        type_ignores=[],
    )

    exec(
        compile(modulo, str(SOURCE), "exec"),
        ambiente,
    )

    ambiente[node.name]()

    if not callbacks:
        raise RuntimeError(
            f"Nenhum callback encontrado em {nome_funcao}"
        )

    callbacks[0](None)

    return resultados[0] if resultados else None


def gerar_casos_equivalencia():
    casos = []

    for id_calc in MAPPING:
        for seed in range(100):
            rng = random.Random(seed)

            nomes = CATALOGO_CALCULOS[id_calc]["entradas"]

            entradas = {
                nome: rng.uniform(-100, 1000)
                for nome in nomes
            }

            # Breguet exige condições específicas para produzir
            # entradas matematicamente válidas.
            if id_calc == "CAL_BREG":
                entradas[nomes[1]] = rng.uniform(0.00001, 0.1)
                entradas[nomes[3]] = rng.uniform(0.1, 10000)
                entradas[nomes[4]] = rng.uniform(1000, 100000)

                entradas[nomes[5]] = (
                    entradas[nomes[4]]
                    * rng.uniform(0.05, 0.99)
                )

            resultado = executar_original(
                id_calc,
                entradas,
            )

            if resultado is None:
                raise RuntimeError(
                    f"O legado não produziu resultado: "
                    f"{id_calc}, seed={seed}"
                )

            casos.append(
                {
                    "id_calc": id_calc,
                    "seed": seed,
                    "entradas": entradas,
                    "saidas": resultado,
                }
            )

    return casos


def gerar_breguet_invalidos():
    nomes = CATALOGO_CALCULOS["CAL_BREG"]["entradas"]

    configuracoes = [
        (5, 0),
        (5, 100000),
        (1, 0),
        (1, -1),
        (3, 0),
    ]

    casos = []

    for indice, valor in configuracoes:
        valores = [
            100,
            0.0002,
            20000,
            1000,
            100000,
            80000,
        ]

        valores[indice] = valor

        entradas = dict(zip(nomes, valores))

        resultado = executar_original(
            "CAL_BREG",
            entradas,
        )

        if resultado is not None:
            raise RuntimeError(
                "Caso esperado como inválido pelo legado "
                f"produziu resultado: {entradas}"
            )

        casos.append(
            {
                "entradas": entradas,
                "esperado_invalido": True,
            }
        )

    return casos


def gerar_schema_original():
    funcao = next(
        n
        for n in TREE.body
        if isinstance(n, ast.FunctionDef)
        and n.name == "criar_esquema_novo"
    )

    ambiente = {}

    modulo = ast.Module(
        body=[funcao],
        type_ignores=[],
    )

    exec(
        compile(modulo, str(SOURCE), "exec"),
        ambiente,
    )

    conn = sqlite3.connect(":memory:")

    try:
        ambiente["criar_esquema_novo"](conn)

        query = """
        SELECT
            type,
            name,
            tbl_name,
            sql
        FROM sqlite_master
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """

        rows = conn.execute(query).fetchall()

    finally:
        conn.close()

    objetos = []

    for tipo, nome, tabela, sql in rows:
        sql_normalizado = (
            re.sub(r"\s+", " ", sql).strip()
            if sql is not None
            else None
        )

        objetos.append(
            {
                "tipo": tipo,
                "nome": nome,
                "tabela": tabela,
                "sql": sql_normalizado,
            }
        )

    return objetos


def salvar_json(nome, conteudo):
    DESTINO.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = DESTINO / nome

    caminho.write_text(
        json.dumps(
            conteudo,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return caminho


def main():
    hash_legado = sha256(SOURCE)

    print("Gerando referência de equivalência...")

    casos = gerar_casos_equivalencia()
    invalidos = gerar_breguet_invalidos()

    equivalencia = {
        "proveniencia": {
            "arquivo": SOURCE.name,
            "sha256": hash_legado,
            "quantidade_casos": len(casos),
        },
        "casos": casos,
        "breguet_invalidos": invalidos,
    }

    caminho_equivalencia = salvar_json(
        "equivalencia_apolo_26.json",
        equivalencia,
    )

    print(
        f"Equivalência gerada: "
        f"{len(casos)} casos"
    )

    print("Gerando snapshot do schema...")

    schema = {
        "proveniencia": {
            "arquivo": SOURCE.name,
            "sha256": hash_legado,
        },
        "objetos": gerar_schema_original(),
    }

    caminho_schema = salvar_json(
        "schema_apolo_26.json",
        schema,
    )

    print()
    print("Concluído.")
    print(f"Equivalência: {caminho_equivalencia}")
    print(f"Schema:       {caminho_schema}")


if __name__ == "__main__":
    main()