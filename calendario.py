"""Calendario configurable para fijar la fecha de consulta de una tasa.

El lookback desplaza la fecha de consulta; no descuenta días del período de
intereses ni cambia la fecha de vencimiento del préstamo.
"""

from datetime import date, timedelta
from typing import Iterable


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
