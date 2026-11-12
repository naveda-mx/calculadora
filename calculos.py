from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP


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


def calcular_vencimiento_por_tramos(saldo_insoluto, spread, amortizacion, detalle):
    """Calcula intereses diarios separados y capitaliza la tasa al final de cada tramo.

    El spread siempre se aplica al saldo insoluto original y no se capitaliza.
    Cada importe diario se redondea a centavos antes de acumularlo. La base de
    la tasa permanece constante dentro de un tramo, incluidos los días inhábiles
    agrupados, y aumenta con el interés de tasa al iniciar el tramo siguiente.
    El detalle debe proceder de ``componer_tasas`` y contener tramos consecutivos.
    """
    detalle = list(detalle)
    if not detalle:
        raise ValueError("Se necesita al menos un tramo con su tasa.")
    inicio = detalle[0]["tramo"].inicio
    fin = detalle[-1]["tramo"].fin
    # Conserva las validaciones de importes, spread, amortización y fechas del
    # cálculo manual, sin limitar la precisión de la tasa equivalente calculada.
    validar = calcular_vencimiento(saldo_insoluto, 0, spread, inicio, fin, amortizacion)
    saldo = Decimal(str(saldo_insoluto))
    margen = Decimal(str(spread))
    centavo = Decimal("0.01")
    interes_spread_diario = (saldo * margen / Decimal("36000")).quantize(
        centavo, rounding=ROUND_HALF_UP
    )
    base_calculo = saldo
    acumulado_tasa = Decimal("0.00")
    acumulado_spread = Decimal("0.00")
    filas = []
    anterior = inicio
    for fila in detalle:
        tramo = fila["tramo"]
        tasa = Decimal(str(fila["tasa"]))
        if tramo.inicio != anterior or tramo.dias <= 0 or not tasa.is_finite():
            raise ValueError("Los tramos deben ser consecutivos y contener tasas válidas.")
        interes_tasa_diario = (base_calculo * tasa / Decimal("36000")).quantize(
            centavo, rounding=ROUND_HALF_UP
        )
        for desplazamiento in range(tramo.dias):
            dia = tramo.inicio + timedelta(days=desplazamiento)
            acumulado_tasa += interes_tasa_diario
            acumulado_spread += interes_spread_diario
            filas.append({
                "inicio": dia, "fin": dia + timedelta(days=1),
                "consulta": tramo.consulta, "tasa": tasa,
                "base_calculo": base_calculo,
                "interes_tasa": interes_tasa_diario,
                "interes_spread": interes_spread_diario,
                "interes_total": interes_tasa_diario + interes_spread_diario,
                "interes_tasa_acumulado": acumulado_tasa,
            })
        base_calculo += interes_tasa_diario * tramo.dias
        anterior = tramo.fin
    if len(filas) != validar["dias"]:
        raise ValueError("Los tramos no cubren todos los días del período.")
    interes = acumulado_tasa + acumulado_spread
    return {
        "dias": validar["dias"],
        "interes_tasa": acumulado_tasa,
        "interes_spread": acumulado_spread,
        "interes_spread_diario": interes_spread_diario,
        "interes": interes,
        "amortizacion": validar["amortizacion"],
        "vencimiento": interes + validar["amortizacion"],
        "detalle_diario": filas,
    }
