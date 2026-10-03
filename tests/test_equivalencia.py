"""Executa os callbacks originais com widgets em memória e compara o novo core."""
import ast
import json
import math
from pathlib import Path
import random
from types import SimpleNamespace
import pytest
from core.calculos import calcular, EntradaInvalida
from core.catalogo import CATALOGO_CALCULOS

SOURCE = Path(__file__).resolve().parents[1]/"originals"/"Apolo_2_6_exportado.py"
TREE = ast.parse(SOURCE.read_text(encoding="utf-8"))
MAPPING = {"CAL_SUST":"calcular_sustentacao","CAL_ARR":"calcular_arrasto","CAL_EMP":"calcular_Empuxo_de_Motor_a_Jato","CAL_NEWTON":"calcular_Newton","CAL_BER":"calcular_Bernoulli","CAL_BREG":"calcular_Breguet"}


def original(id_calc, entradas):
    """Somente uma definição de cálculo auditada, sem imports ou inicialização."""
    callbacks, results = [],[]
    class Button:
        def __init__(self,**kw): pass
        def on_click(self,callback): callbacks.append(callback)
    widgets=SimpleNamespace(Button=Button,HTML=lambda **kw:SimpleNamespace(value=""),Label=lambda **kw:None,VBox=lambda v:v)
    env={"math":math,"widgets":widgets,"display":lambda *a:None,
        "criar_float_widget":lambda nome,*a:SimpleNamespace(value=entradas[nome]),
        "ler_variavel_float":lambda nome,*a:entradas[nome],
        "atualizar_resultado":lambda *a:None,"salvar_variavel":lambda *a:None,
        "registrar_execucao":lambda *a,**kw:results.append(kw["saidas"])}
    node=next(n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name==MAPPING[id_calc])
    module=ast.Module(body=[node],type_ignores=[])
    exec(compile(module,str(SOURCE),"exec"),env)
    env[node.name]()
    callbacks[0](None)
    return results[0] if results else None


@pytest.mark.parametrize("id_calc",list(MAPPING))
@pytest.mark.parametrize("seed",range(100))
def test_resultado_igual_ao_callback_original(id_calc,seed):
    rng=random.Random(seed)
    names=CATALOGO_CALCULOS[id_calc]["entradas"]
    # Inclui valores negativos/zero onde o original os aceita.
    entradas={n:rng.uniform(-100,1000) for n in names}
    if id_calc=="CAL_BREG":
        entradas[names[1]]=rng.uniform(0.00001,0.1)
        entradas[names[3]]=rng.uniform(0.1,10000)
        entradas[names[4]]=rng.uniform(1000,100000)
        entradas[names[5]]=entradas[names[4]]*rng.uniform(0.05,0.99)
    assert calcular(id_calc,entradas)==original(id_calc,entradas)


@pytest.mark.parametrize("id_calc,values,expected",[
    ("CAL_SUST",[1.225,50,10,0.8],12250.0),
    ("CAL_ARR",[1.225,50,10,0.04],612.5),
    ("CAL_EMP",[10,500,100],4000.0),
    ("CAL_NEWTON",[1000,2],2000.0),
    ("CAL_BER",[101325,1.225,50,9.81,100],104057.975),
    ("CAL_BREG",[100,0.0002,20000,1000,100000,80000],2231435.5131420977),
])
def test_casos_numericos_independentes(id_calc,values,expected):
    entradas=dict(zip(CATALOGO_CALCULOS[id_calc]["entradas"],values))
    assert next(iter(calcular(id_calc,entradas).values()))==pytest.approx(expected,rel=1e-12)


@pytest.mark.parametrize("index,value",[(5,0),(5,100000),(1,0),(1,-1),(3,0)])
def test_mesmas_restricoes_de_breguet(index,value):
    names=CATALOGO_CALCULOS["CAL_BREG"]["entradas"]
    values=[100,0.0002,20000,1000,100000,80000]
    values[index]=value
    entradas=dict(zip(names,values))
    assert original("CAL_BREG",entradas) is None
    with pytest.raises(EntradaInvalida): calcular("CAL_BREG",entradas)


@pytest.mark.parametrize("value",[float("nan"),float("inf"),float("-inf"),1e308])
def test_nao_finitos_e_overflow(value):
    with pytest.raises(EntradaInvalida):
        calcular("CAL_SUST",dict(zip(CATALOGO_CALCULOS["CAL_SUST"]["entradas"],[1.225,value,10,0.8])))


def test_codigo_colab_equivalente_a_library():
    lib=SOURCE.parent/"Programa_Calculos_Aerodinamicos_V2.6.0_Colab.ipynb"
    notebook=json.loads(lib.read_text(encoding="utf-8"))
    code="\n\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"]=="code")
    assert ast.dump(ast.parse(code),include_attributes=False)==ast.dump(TREE,include_attributes=False)
