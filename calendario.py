"""Calendario configurable para fijar la fecha de consulta de una tasa.

El lookback desplaza la fecha de consulta; no descuenta días del período de
intereses ni cambia la fecha de vencimiento del préstamo.
"""

from datetime import date, timedelta
from typing import Iterable


MODOS_RECALCULO = ("Sin recálculo", "Con recálculo")
AJUSTES_HABILES = ("Día hábil anterior", "Día hábil siguiente")


# Calendarios bancarios CNBV, artículo 1, publicados en el DOF. Se conservan
# las fechas expresamente publicadas, incluso cuando caen en fin de semana.
# No se extrapolan estas disposiciones a años sin una fuente verificada.
FUENTES_CALENDARIO = {
    2025: "https://sidof.segob.gob.mx/notas/docFuente/5746258",
    2026: "https://sidof.segob.gob.mx/notas/docFuente/5775684",
}

CALENDARIOS_MX = {
    2025: (
        date(2025, 1, 1),
        date(2025, 2, 3),
        date(2025, 3, 17),
        date(2025, 4, 17),
        date(2025, 4, 18),
        date(2025, 5, 1),
        date(2025, 9, 16),
        date(2025, 11, 2),
        date(2025, 11, 17),
        date(2025, 12, 12),
        date(2025, 12, 25),
    ),
    2026: (
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 4, 2),
        date(2026, 4, 3),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 2),
        date(2026, 11, 16),
        date(2026, 12, 12),
        date(2026, 12, 25),
    ),
}


CALENDARIO_SOFR = "Mercado SOFR de EE. UU."
FUENTE_CALENDARIO_SOFR = "https://www.sifma.org/resources/guides-playbooks/holiday-schedule"
AVISOS_CALENDARIO_SOFR = "https://www.newyorkfed.org/markets/reference-rates/statements-and-operating-policies"

# Cierres del mercado de valores gubernamentales de EE. UU. y excepciones
# de publicación de la Fed de Nueva York. Los cierres parciales son hábiles.
# Para 2024–2026 se cotejaron las fechas históricas con effectiveDate del API.
# El 03/04/2026 no hubo SOFR pese al cierre parcial de SIFMA (aviso 260312a).
CALENDARIOS_SOFR = {
    2024: (
        date(2024, 1, 1), date(2024, 1, 15), date(2024, 2, 19), date(2024, 3, 29),
        date(2024, 5, 27), date(2024, 6, 19), date(2024, 7, 4), date(2024, 9, 2),
        date(2024, 10, 14), date(2024, 11, 11), date(2024, 11, 28), date(2024, 12, 25),
    ),
    2025: (
        date(2025, 1, 1), date(2025, 1, 20), date(2025, 2, 17), date(2025, 4, 18),
        date(2025, 5, 26), date(2025, 6, 19), date(2025, 7, 4), date(2025, 9, 1),
        date(2025, 10, 13), date(2025, 11, 11), date(2025, 11, 27), date(2025, 12, 25),
    ),
    2026: (
        date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3),
        date(2026, 5, 25), date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7),
        date(2026, 10, 12), date(2026, 11, 11), date(2026, 11, 26), date(2026, 12, 25),
    ),
    2027: (
        date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15), date(2027, 3, 26),
        date(2027, 5, 31), date(2027, 6, 18), date(2027, 7, 5), date(2027, 9, 6),
        date(2027, 10, 11), date(2027, 11, 11), date(2027, 11, 25), date(2027, 12, 24),
    ),
}


def fecha_consulta(
    fecha_referencia: date,
    lookback: int,
    dias_semana_inhabiles: Iterable[int] = (5, 6),
    festivos: Iterable[date] = (),
) -> date:
    """Devuelve una fecha hábil, desplazada hacia atrás por el lookback.

    Los días de semana siguen ``date.weekday()``: lunes=0 y domingo=6.
    Primero se ajusta una referencia inhábil al hábil inmediato anterior;
    después se descuentan ``lookback`` días hábiles. Por tanto, cero mantiene
    una referencia hábil o devuelve el hábil anterior si era inhábil.

    La función aplica exclusivamente el calendario recibido. Quien la llama
    debe asegurar su cobertura para todos los años recorridos.
    """
    if type(fecha_referencia) is not date:
        raise ValueError("Selecciona una fecha de referencia válida.")
    if type(lookback) is not int or not 0 <= lookback <= 365:
        raise ValueError("El lookback debe ser un entero entre 0 y 365 días hábiles.")

    try:
        dias = tuple(dias_semana_inhabiles)
        fechas = tuple(festivos)
    except TypeError:
        raise ValueError("Selecciona los días inhábiles con un formato válido.") from None
    if any(type(dia) is not int or dia not in range(7) for dia in dias):
        raise ValueError("Los días de la semana deben estar entre 0 (lunes) y 6 (domingo).")
    if any(type(fecha) is not date for fecha in fechas):
        raise ValueError("Las fechas inhábiles deben ser fechas válidas.")

    dias_inhabiles = frozenset(dias)
    fechas_inhabiles = frozenset(fechas)
    if len(dias_inhabiles) == 7:
        raise ValueError("Debe quedar al menos un día hábil por semana.")

    def es_habil(fecha: date) -> bool:
        return fecha.weekday() not in dias_inhabiles and fecha not in fechas_inhabiles

    def anterior(fecha: date) -> date:
        if fecha == date.min:
            raise ValueError("El lookback y los días inhábiles exceden el rango de fechas permitido.")
        return fecha - timedelta(days=1)

    resultado = fecha_referencia
    while not es_habil(resultado):
        resultado = anterior(resultado)
    for _ in range(lookback):
        resultado = anterior(resultado)
        while not es_habil(resultado):
            resultado = anterior(resultado)
    return resultado


def ajustar_fecha_habil(fecha, ajuste, dias_semana_inhabiles=(5, 6), festivos=()):
    """Ajusta una fecha de pago; no se utiliza para el lookback de las tasas."""
    dias_semana_inhabiles, festivos = tuple(dias_semana_inhabiles), tuple(festivos)
    anterior = fecha_consulta(fecha, 0, dias_semana_inhabiles, festivos)
    if ajuste not in AJUSTES_HABILES:
        raise ValueError("Selecciona el ajuste al día hábil anterior o siguiente.")
    if ajuste == AJUSTES_HABILES[0] or anterior == fecha:
        return anterior
    resultado = fecha
    while resultado.weekday() in dias_semana_inhabiles or resultado in festivos:
        if resultado == date.max:
            raise ValueError("El ajuste al siguiente día hábil excede el rango de fechas permitido.")
        resultado += timedelta(days=1)
    return resultado


def resolver_fechas(inicio, final, modo, ajuste, dias_semana_inhabiles=(5, 6), festivos=()):
    """Sin recálculo se mueve sólo el pago; con recálculo también el fin de devengo."""
    if type(inicio) is not date or type(final) is not date or final < inicio:
        raise ValueError("La fecha final debe ser igual o posterior a la fecha de inicio.")
    if modo not in MODOS_RECALCULO:
        raise ValueError("Selecciona una opción de recálculo válida.")
    pago = ajustar_fecha_habil(final, ajuste, dias_semana_inhabiles, festivos)
    fin_calculo = pago if modo == MODOS_RECALCULO[1] else final
    if fin_calculo < inicio or pago < inicio:
        raise ValueError("El ajuste de vencimiento lleva la fecha antes del inicio del préstamo.")
    return {"fecha_final_original": final, "fecha_fin_calculo": fin_calculo,
            "fecha_pago": pago, "dias": (fin_calculo - inicio).days}
