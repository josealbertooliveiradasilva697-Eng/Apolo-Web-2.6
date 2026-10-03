# Extraído mecanicamente do Apolo 2.6.0; IDs e unidades preservados.
import re
import unicodedata
VERSAO_PROGRAMA = "2.6.0"
SCHEMA_VERSION = 2

def remover_acentos(texto):
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere
        for caractere in normalizado
        if not unicodedata.combining(caractere)
    )


def gerar_acronimo(nome):
    """
    Gera a sigla usando a primeira letra de cada palavra.
    Ex.: 'Densidade do ar' -> 'DDA'
    """
    palavras = re.findall(r"[A-Za-zÀ-ÿ0-9]+", nome)
    if not palavras:
        return "VAR"

    acronimo = "".join(remover_acentos(palavra)[0] for palavra in palavras)
    return acronimo.upper()


def gerar_id_variavel(nome, unidade_codigo):
    """
    ID estável da variável:
    ACRÔNIMO_DA_NOME + código da unidade SI.
    """
    return f"{gerar_acronimo(nome)}_{unidade_codigo}"


# Os IDs são gerados desta tabela e não dependem do valor da variável.
# Isso permite que o valor mude sem alterar a identidade da variável.
CATALOGO_VARIAVEIS = {}


def definir_variavel(
    nome,
    unidade_si,
    unidade_codigo,
    tipo="REAL",
    categoria="Geral",
    eh_saida=False,
    padrao=0.0,
    descricao="",
):
    id_variavel = gerar_id_variavel(nome, unidade_codigo)

    if nome in CATALOGO_VARIAVEIS:
        raise ValueError(f"Variável duplicada no catálogo: {nome}")

    CATALOGO_VARIAVEIS[nome] = {
        "id_variavel": id_variavel,
        "nome": nome,
        "unidade_si": unidade_si,
        "unidade_codigo": unidade_codigo,
        "tipo": tipo,
        "categoria": categoria,
        "eh_saida": int(eh_saida),
        "padrao": padrao,
        "descricao": descricao,
    }


# -------------------------
# Grandezas físicas / SI
# -------------------------

definir_variavel(
    "status_projeto",
    "sem unidade",
    "text",
    tipo="TEXT",
    categoria="Sistema",
    padrao="Conectado com sucesso",
    descricao="Estado operacional do banco e da aplicação.",
)

definir_variavel(
    "Densidade do ar",
    "kg/m³",
    "kg_m3",
    categoria="Aerodinâmica",
    descricao="Massa de ar por unidade de volume.",
)

definir_variavel(
    "Pressão do ar",
    "Pa",
    "Pa",
    categoria="Aerodinâmica",
    descricao="Pressão estática utilizada na equação de Bernoulli.",
)

definir_variavel(
    "Velocidade da aeronave ou do escoamento do ar",
    "m/s",
    "m_s",
    categoria="Aerodinâmica",
    descricao="Velocidade característica do escoamento/aeronave.",
)

definir_variavel(
    "Velocidade dos gases de escape do motor",
    "m/s",
    "m_s",
    categoria="Propulsão",
    descricao="Velocidade dos gases na saída do motor a jato.",
)

definir_variavel(
    "Velocidade da aeronave antes da passagem pelo motor",
    "m/s",
    "m_s",
    categoria="Propulsão",
    descricao="Velocidade de entrada usada no cálculo de empuxo.",
)

definir_variavel(
    "Área de referência da asa",
    "m²",
    "m2",
    categoria="Geometria",
    descricao="Área de referência usada nas equações aerodinâmicas.",
)

definir_variavel(
    "Altura em relação a um nível de referência",
    "m",
    "m",
    categoria="Mecânica",
    descricao="Altura geométrica em relação ao nível de referência.",
)

definir_variavel(
    "Coeficiente de sustentação",
    "1",
    "1",
    categoria="Aerodinâmica",
    descricao="Coeficiente adimensional de sustentação (CL).",
)

definir_variavel(
    "Coeficiente de arrasto",
    "1",
    "1",
    categoria="Aerodinâmica",
    descricao="Coeficiente adimensional de arrasto (CD).",
)

definir_variavel(
    "Massa da aeronave",
    "kg",
    "kg",
    categoria="Mecânica",
    descricao="Massa da aeronave.",
)

definir_variavel(
    "Vazão mássica dos gases ou do ar através do motor",
    "kg/s",
    "kg_s",
    categoria="Propulsão",
    descricao="Vazão mássica utilizada no cálculo de empuxo.",
)

definir_variavel(
    "Aceleração",
    "m/s²",
    "m_s2",
    categoria="Mecânica",
    descricao="Aceleração linear.",
)

# Para a forma de Breguet implementada neste programa:
# R = (V/c)(L/D)ln(Wi/Wf)
# V em m/s e R em m => c possui dimensão s^-1.
definir_variavel(
    "Consumo específico de combustível",
    "s⁻¹",
    "s-1",
    categoria="Propulsão",
    descricao="Consumo específico compatível com a forma de Breguet usada nesta versão.",
)

definir_variavel(
    "Peso inicial da aeronave",
    "N",
    "N",
    categoria="Mecânica",
    descricao="Peso inicial utilizado na equação de alcance.",
)

definir_variavel(
    "Peso final da aeronave após consumo de combustível",
    "N",
    "N",
    categoria="Mecânica",
    descricao="Peso final utilizado na equação de alcance.",
)

definir_variavel(
    "gravidade",
    "m/s²",
    "m_s2",
    categoria="Mecânica",
    padrao=9.81,
    descricao="Aceleração gravitacional utilizada na equação de Bernoulli.",
)

# -------------------------
# Variáveis de saída
# -------------------------

definir_variavel(
    "Sustentação",
    "N",
    "N",
    categoria="Resultados",
    eh_saida=True,
    descricao="Força de sustentação calculada.",
)

definir_variavel(
    "Arrasto",
    "N",
    "N",
    categoria="Resultados",
    eh_saida=True,
    descricao="Força de arrasto calculada.",
)

definir_variavel(
    "Empuxo",
    "N",
    "N",
    categoria="Resultados",
    eh_saida=True,
    descricao="Empuxo calculado para o motor a jato.",
)

definir_variavel(
    "Força resultante",
    "N",
    "N",
    categoria="Resultados",
    eh_saida=True,
    descricao="Força resultante pela segunda lei de Newton.",
)

definir_variavel(
    "Alcance da aeronave",
    "m",
    "m",
    categoria="Resultados",
    eh_saida=True,
    descricao="Alcance calculado pela equação de Breguet.",
)

definir_variavel(
    "Resultado Bernoulli",
    "Pa",
    "Pa",
    categoria="Resultados",
    eh_saida=True,
    descricao="Constante/termo energético de Bernoulli na forma de pressão.",
)


# Verificação de IDs duplicados
_ids = [meta["id_variavel"] for meta in CATALOGO_VARIAVEIS.values()]
if len(_ids) != len(set(_ids)):
    duplicados = sorted({x for x in _ids if _ids.count(x) > 1})
    raise ValueError(f"IDs de variáveis duplicados: {duplicados}")


# Aliases de nomes antigos. O backup legado continua preservado.
# Isso permite corrigir nomenclaturas sem perder o valor já armazenado.
ALIASES_VARIAVEIS_LEGADAS = {
    "Resultado Bernolli": "Resultado Bernoulli",
}


# ============================================================
# 3. METADADOS DOS CÁLCULOS
# ============================================================

CATALOGO_CALCULOS = {
    "CAL_SUST": {
        "nome": "Equação Sustentação",
        "versao": VERSAO_PROGRAMA,
        "formula": "L = 0.5 * rho * V² * S * Cl",
        "unidade_saida": "N",
        "descricao": "Cálculo da força de sustentação.",
        "entradas": [
            "Densidade do ar",
            "Velocidade da aeronave ou do escoamento do ar",
            "Área de referência da asa",
            "Coeficiente de sustentação",
        ],
        "saidas": ["Sustentação"],
    },
    "CAL_ARR": {
        "nome": "Equação do Arrasto",
        "versao": VERSAO_PROGRAMA,
        "formula": "D = 0.5 * rho * V² * S * Cd",
        "unidade_saida": "N",
        "descricao": "Cálculo da força de arrasto.",
        "entradas": [
            "Densidade do ar",
            "Velocidade da aeronave ou do escoamento do ar",
            "Área de referência da asa",
            "Coeficiente de arrasto",
        ],
        "saidas": ["Arrasto"],
    },
    "CAL_EMP": {
        "nome": "Empuxo de Motor a Jato",
        "versao": VERSAO_PROGRAMA,
        "formula": "T = mdot * (Ve - V0)",
        "unidade_saida": "N",
        "descricao": "Cálculo simplificado do empuxo.",
        "entradas": [
            "Vazão mássica dos gases ou do ar através do motor",
            "Velocidade dos gases de escape do motor",
            "Velocidade da aeronave antes da passagem pelo motor",
        ],
        "saidas": ["Empuxo"],
    },
    "CAL_NEWTON": {
        "nome": "Segunda Lei de Newton",
        "versao": VERSAO_PROGRAMA,
        "formula": "F = m * a",
        "unidade_saida": "N",
        "descricao": "Cálculo da força resultante.",
        "entradas": ["Massa da aeronave", "Aceleração"],
        "saidas": ["Força resultante"],
    },
    "CAL_BER": {
        "nome": "Equação de Bernoulli",
        "versao": VERSAO_PROGRAMA,
        "formula": "B = P + 0.5*rho*V² + rho*g*h",
        "unidade_saida": "Pa",
        "descricao": "Cálculo do termo energético equivalente em pressão.",
        "entradas": [
            "Pressão do ar",
            "Densidade do ar",
            "Velocidade da aeronave ou do escoamento do ar",
            "gravidade",
            "Altura em relação a um nível de referência",
        ],
        "saidas": ["Resultado Bernoulli"],
    },
    "CAL_BREG": {
        "nome": "Equação de Alcance de Breguet",
        "versao": VERSAO_PROGRAMA,
        "formula": "R = (V/c) * (L/D) * ln(Wi/Wf)",
        "unidade_saida": "m",
        "descricao": "Cálculo de alcance usando a forma de Breguet implementada.",
        "entradas": [
            "Velocidade da aeronave ou do escoamento do ar",
            "Consumo específico de combustível",
            "Sustentação",
            "Arrasto",
            "Peso inicial da aeronave",
            "Peso final da aeronave após consumo de combustível",
        ],
        "saidas": ["Alcance da aeronave"],
    },
}
