from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def calcular_vencimiento(
    monto_operado,
    tasa_base,
    spread,
    fecha_inicio: date,
    fecha_fin: date,
    amortizacion=0,
):
    """Calcula interés simple con tasas anuales en porcentaje y base 360.

    Sigue el Excel de referencia: redondea el interés diario a centavos antes
    de multiplicar por los días. La amortización corresponde al vencimiento
    del período y se suma al interés monetario.
    """
    monto = Decimal(str(monto_operado))
    base = Decimal(str(tasa_base))
    margen = Decimal(str(spread))
    abono = Decimal(str(amortizacion))

    if not all(valor.is_finite() for valor in (monto, base, margen, abono)):
        raise ValueError("Los montos y las tasas deben ser números finitos.")
    if monto < 0 or abono < 0:
        raise ValueError("El monto operado y la amortización deben ser cero o positivos.")
    if abono > monto:
        raise ValueError("La amortización no puede superar el monto operado.")
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha final debe ser igual o posterior a la fecha de inicio.")
    if monto != monto.quantize(Decimal("0.01")) or abono != abono.quantize(Decimal("0.01")):
        raise ValueError("Captura el monto operado y la amortización con hasta dos decimales.")
    if base != base.quantize(Decimal("0.000001")) or margen != margen.quantize(Decimal("0.000001")):
        raise ValueError("Captura la tasa base y el spread con hasta seis decimales.")

    dias = (fecha_fin - fecha_inicio).days
    tasa_total = base + margen
    interes_diario = (monto * tasa_total / Decimal("100") / Decimal("360")).quantize(
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
