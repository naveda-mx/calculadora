"""Revisiones de tasa y composición por tramos, con base ACT/360."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from calendario import fecha_consulta


FRECUENCIAS = {"Mensual": 1, "Bimestral": 2, "Trimestral": 3, "Semestral": 6, "Anual": 12,
               "Diaria": None}
MODOS_DIARIOS = ("Revisión cada día natural", "Revisión sólo en días hábiles")
CAPITALIZAR_SOBRE = ("Sólo tasa base", "Tasa base + spread")


@dataclass(frozen=True)
class Tramo:
    inicio: date
    fin: date
    referencia: date
    consulta: date

    @property
    def dias(self):
        return (self.fin - self.inicio).days


def generar_tramos(inicio, fin, frecuencia, dia_revision, lookback=0,
                   dias_semana=(5, 6), festivos=(), modo_diario=None):
    """Intervalos [inicio, fin). Ancla mensual: mes de inicio del cálculo.

    La revisión vigente puede preceder al inicio. En meses cortos, el día
    solicitado se limita al último día, sin perder el día original al avanzar.
    Los inhábiles y el lookback sólo desplazan la consulta, nunca los cortes.
    """
    if type(inicio) is not date or type(fin) is not date or fin <= inicio:
        raise ValueError("Para calcular por tramos, la fecha final debe ser posterior a la inicial.")
    if frecuencia not in FRECUENCIAS:
        raise ValueError("Selecciona una frecuencia de revisión válida.")
    dias_semana, festivos = tuple(dias_semana), tuple(festivos)
    if frecuencia == "Diaria":
        if modo_diario not in MODOS_DIARIOS:
            raise ValueError("Selecciona si la revisión diaria ocurre en días naturales o hábiles.")
        if (fin - inicio).days > 3660:
            raise ValueError("El período diario supera 3660 días. Divide el cálculo en períodos menores.")
        resultado = []
        cursor = inicio
        while cursor < fin:
            referencia = cursor
            if modo_diario == MODOS_DIARIOS[1]:
                # Un inicio inhábil utiliza la revisión hábil anterior; el
                # tramo siguiente comienza en el siguiente día hábil.
                referencia = fecha_consulta(cursor, 0, dias_semana, festivos)
            consulta = fecha_consulta(referencia, lookback, dias_semana, festivos)
            corte = cursor + timedelta(days=1)
            if modo_diario == MODOS_DIARIOS[1]:
                while corte < fin and fecha_consulta(corte, 0, dias_semana, festivos) != corte:
                    corte += timedelta(days=1)
            resultado.append(Tramo(cursor, corte, referencia, consulta))
            cursor = corte
        return resultado

    if type(dia_revision) is not int or not 1 <= dia_revision <= 31:
        raise ValueError("El día de revisión debe ser un entero entre 1 y 31.")
    meses = FRECUENCIAS[frecuencia]
    ancla = (inicio.year - 1) * 12 + inicio.month - 1

    def fecha_mes(indice):
        anio, mes = divmod(indice, 12)
        if not 0 <= anio < 9999:
            raise ValueError("El calendario de revisiones excede el rango de fechas permitido.")
        return date(anio + 1, mes + 1, min(dia_revision, monthrange(anio + 1, mes + 1)[1]))

    referencia = fecha_mes(ancla)
    if referencia > inicio:
        ancla -= meses
        referencia = fecha_mes(ancla)
    resultado = []
    cursor = inicio
    while cursor < fin:
        if len(resultado) >= 120:
            raise ValueError("El período supera 120 revisiones. Divide el cálculo en períodos menores.")
        siguiente_indice = ancla + meses
        siguiente = fecha_mes(siguiente_indice) if siguiente_indice < 9999 * 12 else date.max
        corte = min(fin, siguiente)
        resultado.append(Tramo(cursor, corte, referencia,
                               fecha_consulta(referencia, lookback, dias_semana, festivos)))
        cursor, referencia, ancla = corte, siguiente, siguiente_indice
    return resultado


def componer_tasas(tramos, tasas):
    """Compone factores; redondea la tasa anual equivalente a cuatro decimales.

    Las tasas recibidas están en porcentaje anual. El spread se agrega después
    fuera de los factores por tramo. La composición ocurre entre las revisiones
    configuradas, no al completar un número fijo de días del tenor de la tasa.
    Con un solo tramo no hay capitalización intermedia.
    """
    tramos, tasas = list(tramos), list(tasas)
    if not tramos or len(tramos) != len(tasas):
        raise ValueError("Se necesita una tasa para cada tramo.")
    producto = Decimal(1)
    detalle = []
    for i, (tramo, valor) in enumerate(zip(tramos, tasas)):
        if tramo.dias <= 0 or (i and tramo.inicio != tramos[i - 1].fin):
            raise ValueError("Los tramos deben ser consecutivos y tener días positivos.")
        tasa = Decimal(str(valor))
        if not tasa.is_finite():
            raise ValueError("Todas las tasas deben ser números finitos.")
        factor = Decimal(1) + tasa * tramo.dias / Decimal(36000)
        if factor <= 0:
            raise ValueError("Las tasas deben producir factores de acumulación positivos.")
        producto *= factor
        detalle.append({"tramo": tramo, "tasa": tasa, "factor": factor})
    dias = sum(t.dias for t in tramos)
    acumulado = producto - 1
    anual = acumulado * Decimal(36000) / dias
    return {
        "detalle": detalle, "dias": dias, "acumulado": acumulado,
        "periodo": Decimal(360) / dias, "tasa_sin_redondear": anual,
        "tasa_equivalente": anual.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        "capitalizacion_intermedia": len(tramos) > 1,
    }


def componer_condiciones(tramos, tasas_base, spread, capitalizar_sobre=CAPITALIZAR_SOBRE[0]):
    """Compone la base o la tasa total, sin aplicar dos veces el spread.

    Base: equivalente de las tasas base a 4 decimales, más spread simple.
    Total: equivalente de (tasa base + spread) a 4 decimales; ya incluye spread.
    El detalle conserva tanto la tasa original como la utilizada en el factor.
    """
    if capitalizar_sobre not in CAPITALIZAR_SOBRE:
        raise ValueError("Selecciona si capitalizar sólo la tasa base o tasa base más spread.")
    margen = Decimal(str(spread))
    if not margen.is_finite() or margen != margen.quantize(Decimal("0.000001")):
        raise ValueError("Captura el spread como número finito con hasta seis decimales.")
    tasas = [Decimal(str(tasa)) for tasa in tasas_base]
    incluye_spread = capitalizar_sobre == CAPITALIZAR_SOBRE[1]
    tasas_factor = [tasa + margen for tasa in tasas] if incluye_spread else tasas
    compuesto = componer_tasas(tramos, tasas_factor)
    for fila, base in zip(compuesto["detalle"], tasas):
        fila["tasa_base"] = base
        fila["spread"] = margen
    compuesto["capitalizar_sobre"] = capitalizar_sobre
    compuesto["incluye_spread"] = incluye_spread
    compuesto["tasa_total"] = compuesto["tasa_equivalente"] + (Decimal(0) if incluye_spread else margen)
    return compuesto
