from datetime import date
from decimal import InvalidOperation

import streamlit as st

from calculos import calcular_vencimiento


st.set_page_config(page_title="Calculadora de intereses", layout="wide")

st.title("Calculadora de intereses")
st.subheader("Información de referencia")
st.caption("Captura manual de un préstamo. Los datos de identificación son opcionales.")

with st.form("formulario_referencia", clear_on_submit=False):
    izquierda, centro, derecha = st.columns([1, 1, 2])
    with izquierda:
        id_cliente = st.text_input("ID de cliente", key="id_cliente")
        agencia = st.text_input("Agencia", key="agencia")
        fecha_operacion = st.date_input(
            "Fecha de operación",
            value=None,
            min_value=date.min,
            max_value=date.max,
            format="DD/MM/YYYY",
            key="fecha_operacion",
        )
    with centro:
        id_prestamo = st.text_input("ID de préstamo", key="id_prestamo")
        subaplicacion = st.text_input("Subaplicación", key="subaplicacion")
        moneda = st.text_input(
            "Moneda",
            placeholder="Por ejemplo: MXN",
            key="moneda",
            help="Indica la moneda del préstamo y de los importes calculados.",
        )
    with derecha:
        nombre_cliente = st.text_input("Nombre del cliente", key="nombre_cliente")
        disposicion = st.text_input("Disposición", key="disposicion")

    st.subheader("Condiciones del cálculo")
    st.caption(
        "Captura las tasas anuales en porcentaje, con hasta cuatro decimales. "
        "Por ejemplo, escribe 6.8 para 6.8 %."
    )
    izquierda, centro, derecha = st.columns(3)
    with izquierda:
        saldo_insoluto = st.number_input(
            "Saldo insoluto *",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.2f",
            key="saldo_insoluto",
            help="Capital pendiente de pago sobre el que se calcula el interés del período.",
        )
        fecha_inicio = st.date_input(
            "Fecha de inicio *",
            value=None,
            min_value=date.min,
            max_value=date.max,
            format="DD/MM/YYYY",
            key="fecha_inicio",
        )
    with centro:
        tasa_base = st.number_input(
            "Tasa base anual (%) *",
            value=None,
            step=0.0001,
            format="%.6f",
            key="tasa_base",
        )
        fecha_fin = st.date_input(
            "Fecha final *",
            value=None,
            min_value=date.min,
            max_value=date.max,
            format="DD/MM/YYYY",
            key="fecha_fin",
        )
    with derecha:
        spread = st.number_input(
            "Spread anual (%) *",
            value=None,
            step=0.0001,
            format="%.6f",
            key="spread",
            help="Se suma a la tasa base. Por ejemplo, 6.8 + 2.85 = 9.65 % anual.",
        )
        amortizacion = st.number_input(
            "Amortización de este vencimiento",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key="amortizacion",
            help="Abono a capital en la moneda del préstamo. Para el pago de fin de año, "
                 "captura el importe programado. Usa cero en los períodos sin amortización.",
        )
    st.caption(
        "Interés simple con saldo insoluto y tasa constantes durante el período. "
        "Días naturales = fecha final − fecha de inicio. Base de 360 días. "
        "El interés diario se redondea a dos decimales antes de multiplicar por los días."
    )
    st.caption("* Campos obligatorios para calcular.")
    revisar = st.form_submit_button("Calcular interés y vencimiento")

if revisar:
    obligatorios = {
        "saldo insoluto": saldo_insoluto,
        "tasa base": tasa_base,
        "spread": spread,
        "fecha de inicio": fecha_inicio,
        "fecha final": fecha_fin,
        "amortización": amortizacion,
    }
    faltantes = [nombre for nombre, valor in obligatorios.items() if valor is None]
    resultado = None
    if faltantes:
        st.warning("Completa los siguientes campos: " + ", ".join(faltantes) + ".")
    else:
        try:
            resultado = calcular_vencimiento(
                saldo_insoluto, tasa_base, spread, fecha_inicio, fecha_fin, amortizacion
            )
        except ValueError as error:
            st.warning(str(error))
        except InvalidOperation:
            st.warning("Revisa el tamaño y la precisión de los montos y las tasas capturados.")

    if resultado is not None:
        # Un solo registro de referencia, preparado para ampliarse después.
        referencia = {
            "id_cliente": id_cliente.strip(),
            "id_prestamo": id_prestamo.strip(),
            "nombre_cliente": nombre_cliente.strip(),
            "disposicion": disposicion.strip(),
            "agencia": agencia.strip(),
            "subaplicacion": subaplicacion.strip(),
            "fecha_operacion": fecha_operacion,
            "saldo_insoluto": saldo_insoluto,
            "moneda": moneda.strip(),
        }

        campos = [
            ("ID de cliente", referencia["id_cliente"]),
            ("ID de préstamo", referencia["id_prestamo"]),
            ("Nombre del cliente", referencia["nombre_cliente"]),
            ("Disposición", referencia["disposicion"]),
            ("Agencia", referencia["agencia"]),
            ("Subaplicación", referencia["subaplicacion"]),
            (
                "Fecha de operación",
                fecha_operacion.strftime("%d/%m/%Y")
                if fecha_operacion is not None else "",
            ),
            (
                "Saldo insoluto",
                f"{saldo_insoluto:,.2f}",
            ),
            ("Moneda", referencia["moneda"]),
            ("Fecha de inicio", fecha_inicio.strftime("%d/%m/%Y")),
            ("Fecha final", fecha_fin.strftime("%d/%m/%Y")),
            ("Días del período", str(resultado["dias"])),
            ("Tasa base anual", f"{tasa_base:.6f} %"),
            ("Spread anual", f"{spread:.6f} %"),
            ("Tasa total anual", f"{resultado['tasa_total']:.6f} %"),
            ("Interés diario redondeado", f"{resultado['interes_diario']:,.2f}"),
            ("Amortización del vencimiento", f"{resultado['amortizacion']:,.2f}"),
        ]

        st.subheader("Resultado del último cálculo")
        unidad = f" {moneda.strip()}" if moneda.strip() else ""
        izquierda, derecha = st.columns(2)
        izquierda.metric("Interés del período", f"{resultado['interes']:,.2f}{unidad}")
        derecha.metric("Vencimiento", f"{resultado['vencimiento']:,.2f}{unidad}")
        st.caption("Vencimiento = interés del período + amortización de este vencimiento.")
        with st.expander("Ver datos y desglose"):
            st.table([
                {"Campo": campo, "Valor": valor or "Sin capturar"}
                for campo, valor in campos
            ])
            st.write("Interés diario = redondear(saldo insoluto × (tasa base + spread) / 100 / 360, 2).")
            st.write("Interés del período = interés diario × días naturales.")
        st.caption("Para reflejar cambios, vuelve a pulsar «Calcular interés y vencimiento».")

st.caption("La información no se guarda de forma permanente.")
