from datetime import date
from decimal import Decimal
from fractions import Fraction

from tramos import CAPITALIZAR_SOBRE, componer_condiciones


METODOS_CALCULO = ("Tasa equivalente", "Tasa compuesta", "Interés simple")
CENTAVO = Decimal("0.01")
BASE_PORCENTUAL = 36000  # Tasa en porcentaje anual: 100 × 360.


def _redondear_centavos(importe):
    """Mitades alejándose de cero, sin aproximar cocientes periódicos.

    Se compara la fracción exacta del centavo con 1/2. Así, una conversión
    periódica no puede transformar un empate de 0.005 en 0.004999…
    """
    importe = Fraction(importe)
    centavos, resto = divmod(abs(importe.numerator) * 100, importe.denominator)
    if resto * 2 >= importe.denominator:
        centavos += 1
    return Decimal(-centavos if importe < 0 else centavos).scaleb(-2)


def redondear_interes_diario(capital, tasa_anual):
    """Numeral 1.5.4: (K × i / 360) REDONDEO, antes de multiplicar por días.

    i se recibe como porcentaje. Se decide el centavo con el tercer decimal;
    no se redondea antes a tres decimales, pues eso crearía doble redondeo.
    Se redondean mitades alejándose de cero, como REDONDEAR de Excel.
    """
    return _redondear_centavos(Fraction(capital) * Fraction(tasa_anual) / BASE_PORCENTUAL)


def _validar_importes_y_tasas(saldo_insoluto, tasa_base, spread, amortizacion):
    saldo, base, margen, abono = (
        Decimal(str(valor)) for valor in (saldo_insoluto, tasa_base, spread, amortizacion)
    )
    if not all(valor.is_finite() for valor in (saldo, base, margen, abono)):
        raise ValueError("Los montos y las tasas deben ser números finitos.")
    if saldo < 0 or abono < 0:
        raise ValueError("El saldo insoluto y la amortización deben ser cero o positivos.")
    if abono > saldo:
        raise ValueError("La amortización no puede superar el saldo insoluto.")
    if saldo != saldo.quantize(CENTAVO) or abono != abono.quantize(CENTAVO):
        raise ValueError("Captura el saldo insoluto y la amortización con hasta dos decimales.")
    if base != base.quantize(Decimal("0.000001")) or margen != margen.quantize(Decimal("0.000001")):
        raise ValueError("Captura la tasa base y el spread con hasta seis decimales.")
    return saldo, base, margen, abono


def calcular_vencimiento(
    saldo_insoluto,
    tasa_base,
    spread,
    fecha_inicio: date,
    fecha_fin: date,
    amortizacion=0,
):
    """Calcula interés sobre el saldo insoluto con tasas anuales y base 360.

    Numeral 1.5.4 y hoja «Cálculo de Interés», T5:T6: primero se redondea
    el interés diario; después se multiplica por los días. La amortización
    corresponde al vencimiento final y se suma al interés monetario.
    """
    saldo, base, margen, abono = _validar_importes_y_tasas(
        saldo_insoluto, tasa_base, spread, amortizacion
    )
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha final debe ser igual o posterior a la fecha de inicio.")
    dias = (fecha_fin - fecha_inicio).days
    tasa_total = base + margen
    interes_diario = redondear_interes_diario(saldo, tasa_total)
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


def calcular_vencimiento_por_tramos(
    saldo_insoluto, spread, amortizacion, detalle,
    capitalizar_sobre=CAPITALIZAR_SOBRE[0], metodo=METODOS_CALCULO[0],
):
    """Métodos explícitos de la hoja «Cálculo de Interés» del Excel de referencia.

    Simple: Σ REDONDEAR(K × (base_i + spread) / 36000, 2) × n_i.
    Compuesta: U23:U25 / U55:U57. El K de cada tramo incorpora los importes
    capitalizables previos, ya redondeados. Sólo base conserva el spread sobre
    K original y redondea ambos componentes por separado (hoja diaria del usuario).
    Equivalente sobre base: X41:Z42 y L41. Se anualiza el producto de factores,
    sin redondear factores ni producto. Sólo el equivalente anual se redondea
    a cuatro decimales porcentuales, antes de agregar el spread. Después se
    aplica el redondeo monetario diario del numeral 1.5.4.
    Equivalente sobre total: W51:W52 y L51. K × (producto de factores − 1),
    redondeado a centavos al final; el spread ya está dentro de los factores.

    No se intercambian estos métodos: sus puntos de redondeo pueden producir
    importes distintos. El detalle interno conserva tramos, no se exige mostrar
    una tabla diaria. Las fechas y el recálculo se resuelven antes de esta función.
    """
    detalle = list(detalle)
    if not detalle:
        raise ValueError("Se necesita al menos un tramo con su tasa.")
    if metodo not in METODOS_CALCULO:
        raise ValueError("Selecciona un método de cálculo válido.")
    saldo, _, margen, abono = _validar_importes_y_tasas(saldo_insoluto, 0, spread, amortizacion)
    tasas_base = []
    for fila in detalle:
        tasa_original = fila["tasa_base"] if "tasa_base" in fila else fila["tasa"]
        _, tasa, _, _ = _validar_importes_y_tasas(saldo, tasa_original, margen, abono)
        tasas_base.append(tasa)
    compuesto = componer_condiciones(
        [f["tramo"] for f in detalle], tasas_base, margen, capitalizar_sobre,
    )
    dias = compuesto["dias"]
    interes_diario = None
    tasa_total = None
    detalle_calculo = []
    if metodo == "Tasa equivalente":
        if compuesto["incluye_spread"]:
            # L51: K × rendimiento efectivo, sin convertir de vuelta a una
            # tasa anual redondeada ni sustituirlo por un promedio diario.
            interes = _redondear_centavos(Fraction(saldo) * compuesto["_acumulado_exacto"])
            tasa_total = compuesto["tasa_equivalente"]
        else:
            tasa_total = compuesto["tasa_equivalente"] + margen
            interes_diario = redondear_interes_diario(saldo, tasa_total)
            interes = interes_diario * dias
    else:
        capital = saldo
        interes = Decimal(0)
        for fila in compuesto["detalle"]:
            tramo, tasa = fila["tramo"], fila["tasa_base"]
            if metodo == "Interés simple":
                # No se capitaliza: K siempre es el saldo insoluto original.
                diario = redondear_interes_diario(saldo, tasa + margen)
                interes_tramo = diario * tramo.dias
                capitalizable = Decimal(0)
            elif compuesto["incluye_spread"]:
                diario = redondear_interes_diario(capital, tasa + margen)
                interes_tramo = diario * tramo.dias
                capitalizable = interes_tramo
            else:
                diario_base = redondear_interes_diario(capital, tasa)
                diario_spread = redondear_interes_diario(saldo, margen)
                interes_tramo = (diario_base + diario_spread) * tramo.dias
                capitalizable = diario_base * tramo.dias
            detalle_calculo.append({
                "tramo": tramo, "capital_calculo": capital,
                "interes": interes_tramo, "interes_capitalizable": capitalizable,
            })
            interes += interes_tramo
            capital += capitalizable
    return {
        "dias": dias, "tasa_total": tasa_total, "interes_diario": interes_diario,
        "interes": interes, "amortizacion": abono, "vencimiento": interes + abono,
        "tasa_equivalente": compuesto["tasa_equivalente"],
        "capitalizar_sobre": capitalizar_sobre if metodo != "Interés simple" else None,
        "metodo": metodo,
        "detalle_calculo": detalle_calculo,
    }
