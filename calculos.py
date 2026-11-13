from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from tramos import CAPITALIZAR_SOBRE, componer_condiciones


def calcular_vencimiento(
    saldo_insoluto,
    tasa_base,
    spread,
    fecha_inicio: date,
    fecha_fin: date,
    amortizacion=0,
):
    """Calcula interés sobre el saldo insoluto con tasas anuales y base 360.

    Sigue el Excel de referencia: redondea el interés diario a centavos antes
    de multiplicar por los días. La amortización corresponde al vencimiento
    del período y se suma al interés monetario.
    """
    saldo = Decimal(str(saldo_insoluto))
    base = Decimal(str(tasa_base))
    margen = Decimal(str(spread))
    abono = Decimal(str(amortizacion))

    if not all(valor.is_finite() for valor in (saldo, base, margen, abono)):
        raise ValueError("Los montos y las tasas deben ser números finitos.")
    if saldo < 0 or abono < 0:
        raise ValueError("El saldo insoluto y la amortización deben ser cero o positivos.")
    if abono > saldo:
        raise ValueError("La amortización no puede superar el saldo insoluto.")
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha final debe ser igual o posterior a la fecha de inicio.")
    if saldo != saldo.quantize(Decimal("0.01")) or abono != abono.quantize(Decimal("0.01")):
        raise ValueError("Captura el saldo insoluto y la amortización con hasta dos decimales.")
    if base != base.quantize(Decimal("0.000001")) or margen != margen.quantize(Decimal("0.000001")):
        raise ValueError("Captura la tasa base y el spread con hasta seis decimales.")

    dias = (fecha_fin - fecha_inicio).days
    tasa_total = base + margen
    interes_diario = (saldo * tasa_total / Decimal("100") / Decimal("360")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    interes = interes_diario * dias
    vencimiento = interes + abono

    return {
        "dias": dias,
        "tasa_total": tasa_total,
        "interes_diario": interes_diario,
        "interes": interes,
        "amortizacion": abono,
        "vencimiento": vencimiento,
    }


def calcular_vencimiento_por_tramos(saldo_insoluto, spread, amortizacion, detalle,
                                    capitalizar_sobre=CAPITALIZAR_SOBRE[0]):
    """Aplica la base de capitalización elegida, con equivalente a 4 decimales.

    La composición ocurre en los factores por revisión de tasa. El resultado
    Sólo base: el spread se suma después de componer. Base + spread: se incluye
    en los factores y no se vuelve a sumar al equivalente. El interés total se
    aplica al saldo original con redondeo diario a centavos.
    """
    detalle = list(detalle)
    if not detalle:
        raise ValueError("Se necesita al menos un tramo con su tasa.")
    compuesto = componer_condiciones(
        [f["tramo"] for f in detalle], [f.get("tasa_base", f["tasa"]) for f in detalle],
        spread, capitalizar_sobre,
    )
    inicio = detalle[0]["tramo"].inicio
    fin = detalle[-1]["tramo"].fin
    resultado = calcular_vencimiento(saldo_insoluto, compuesto["tasa_total"], 0,
                                     inicio, fin, amortizacion)
    resultado["tasa_equivalente"] = compuesto["tasa_equivalente"]
    resultado["capitalizar_sobre"] = capitalizar_sobre
    return resultado
