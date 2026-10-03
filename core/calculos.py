"""Expressões preservadas dos seis callbacks do Apolo 2.6.0."""
import math
from .catalogo import CATALOGO_CALCULOS


class EntradaInvalida(ValueError):
    pass


def calcular(id_calculo: str, entradas: dict[str, float]) -> dict[str, float]:
    if id_calculo not in CATALOGO_CALCULOS:
        raise EntradaInvalida("Cálculo desconhecido.")
    meta = CATALOGO_CALCULOS[id_calculo]
    try:
        valores = [float(entradas[nome]) for nome in meta["entradas"]]
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise EntradaInvalida("Preencha todas as entradas com números válidos.") from exc
    if not all(math.isfinite(v) for v in valores):
        raise EntradaInvalida("As entradas devem ser números finitos.")
    try:
        if id_calculo == "CAL_SUST":
            Da, V, S, Cl = valores
            resultado = 0.5 * Da * (V ** 2) * S * Cl
        elif id_calculo == "CAL_ARR":
            Da, V, S, Cd = valores
            resultado = 0.5 * Da * (V ** 2) * S * Cd
        elif id_calculo == "CAL_EMP":
            Vm, Ve, V0 = valores
            resultado = Vm * (Ve - V0)
        elif id_calculo == "CAL_NEWTON":
            m, a = valores
            resultado = m * a
        elif id_calculo == "CAL_BER":
            P, Da, V, g_val, h = valores
            resultado = P + 0.5 * Da * (V ** 2) + Da * g_val * h
        else:
            V, c, L, D, Wi, Wf = valores
            if Wf <= 0 or Wf >= Wi or c <= 0 or D == 0:
                raise EntradaInvalida("Breguet requer 0 < peso final < peso inicial, consumo > 0 e arrasto diferente de zero.")
            resultado = (V / c) * (L / D) * math.log(Wi / Wf)
    except (OverflowError, ZeroDivisionError) as exc:
        raise EntradaInvalida("As entradas excedem os limites numéricos do cálculo.") from exc
    if not math.isfinite(resultado):
        raise EntradaInvalida("O resultado excede os limites numéricos do cálculo.")
    return {meta["saidas"][0]: resultado}
