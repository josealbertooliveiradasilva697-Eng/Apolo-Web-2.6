"""Testes de equivalência do core com a referência auditada do Apolo 2.6."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

import pytest

from core.calculos import calcular, EntradaInvalida
from core.catalogo import CATALOGO_CALCULOS


RAIZ = Path(__file__).resolve().parents[1]

FIXTURE_EQUIVALENCIA = (
    RAIZ
    / "tests"
    / "fixtures"
    / "equivalencia_apolo_26.json"
)

SOURCE_LEGADO = (
    RAIZ
    / "originals"
    / "Apolo_2_6_exportado.py"
)

NOTEBOOK_LEGADO = (
    RAIZ
    / "originals"
    / "Programa_Calculos_Aerodinamicos_V2.6.0_Colab.ipynb"
)


with FIXTURE_EQUIVALENCIA.open(
    "r",
    encoding="utf-8",
) as arquivo:
    REFERENCIA = json.load(arquivo)


CASOS_EQUIVALENCIA = REFERENCIA["casos"]
BREGUET_INVALIDOS = REFERENCIA["breguet_invalidos"]


@pytest.mark.parametrize(
    "caso",
    CASOS_EQUIVALENCIA,
    ids=lambda caso: (
        f"{caso['id_calc']}-seed-{caso['seed']}"
    ),
)
def test_resultado_igual_ao_legado_auditado(caso):
    """
    O novo core deve reproduzir os resultados previamente
    gerados pelo Apolo 2.6 original.
    """

    resultado = calcular(
        caso["id_calc"],
        caso["entradas"],
    )

    assert resultado == caso["saidas"]


@pytest.mark.parametrize(
    "id_calc,values,expected",
    [
        (
            "CAL_SUST",
            [1.225, 50, 10, 0.8],
            12250.0,
        ),
        (
            "CAL_ARR",
            [1.225, 50, 10, 0.04],
            612.5,
        ),
        (
            "CAL_EMP",
            [10, 500, 100],
            4000.0,
        ),
        (
            "CAL_NEWTON",
            [1000, 2],
            2000.0,
        ),
        (
            "CAL_BER",
            [101325, 1.225, 50, 9.81, 100],
            104057.975,
        ),
        (
            "CAL_BREG",
            [
                100,
                0.0002,
                20000,
                1000,
                100000,
                80000,
            ],
            2231435.5131420977,
        ),
    ],
)
def test_casos_numericos_independentes(
    id_calc,
    values,
    expected,
):
    entradas = dict(
        zip(
            CATALOGO_CALCULOS[id_calc]["entradas"],
            values,
        )
    )

    resultado = calcular(
        id_calc,
        entradas,
    )

    valor = next(iter(resultado.values()))

    assert valor == pytest.approx(
        expected,
        rel=1e-12,
    )


@pytest.mark.parametrize(
    "caso",
    BREGUET_INVALIDOS,
)
def test_mesmas_restricoes_de_breguet(caso):
    """
    Casos classificados como inválidos pelo Apolo 2.6
    também devem ser rejeitados pelo novo core.
    """

    assert caso["esperado_invalido"] is True

    with pytest.raises(EntradaInvalida):
        calcular(
            "CAL_BREG",
            caso["entradas"],
        )


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        1e308,
    ],
)
def test_sustentacao_rejeita_valores_nao_validos(value):
    entradas = dict(
        zip(
            CATALOGO_CALCULOS["CAL_SUST"]["entradas"],
            [
                1.225,
                value,
                10,
                0.8,
            ],
        )
    )

    with pytest.raises(EntradaInvalida):
        calcular(
            "CAL_SUST",
            entradas,
        )


def test_fixture_tem_600_casos_auditados():
    """
    Evita que a referência seja truncada acidentalmente.
    """

    assert len(CASOS_EQUIVALENCIA) == 600

    assert (
        REFERENCIA["proveniencia"]["quantidade_casos"]
        == 600
    )
    assert Counter(caso["id_calc"] for caso in CASOS_EQUIVALENCIA) == {
        id_calc: 100 for id_calc in CATALOGO_CALCULOS
    }
    assert {(caso["id_calc"], caso["seed"]) for caso in CASOS_EQUIVALENCIA} == {
        (id_calc, seed)
        for id_calc in CATALOGO_CALCULOS
        for seed in range(100)
    }
    assert len(BREGUET_INVALIDOS) == 5
    assert REFERENCIA["proveniencia"]["sha256"] == (
        "b06d2d4e064fdafd8c2edae0130435175022da7c62dc2221ee881edb1ae949e7"
    )


@pytest.mark.skipif(
    not (
        SOURCE_LEGADO.exists()
        and NOTEBOOK_LEGADO.exists()
    ),
    reason=(
        "Ativos históricos do Apolo 2.6 "
        "não estão disponíveis neste ambiente."
    ),
)
def test_codigo_colab_equivalente_ao_exportado():
    """
    Auditoria local de proveniência.

    Só é executada quando os arquivos históricos existem.
    Não é necessária para o CI.
    """

    codigo_exportado = SOURCE_LEGADO.read_text(
        encoding="utf-8"
    )
    assert hashlib.sha256(SOURCE_LEGADO.read_bytes()).hexdigest() == (
        REFERENCIA["proveniencia"]["sha256"]
    )

    tree_exportado = ast.parse(
        codigo_exportado
    )

    notebook = json.loads(
        NOTEBOOK_LEGADO.read_text(
            encoding="utf-8"
        )
    )

    codigo_notebook = "\n\n".join(
        "".join(celula["source"])
        for celula in notebook["cells"]
        if celula["cell_type"] == "code"
    )

    tree_notebook = ast.parse(
        codigo_notebook
    )

    assert ast.dump(
        tree_notebook,
        include_attributes=False,
    ) == ast.dump(
        tree_exportado,
        include_attributes=False,
    )
