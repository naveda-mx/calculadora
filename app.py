from datetime import date

import streamlit as st

#Configuración inicial de la página 
st.set_page_config(page_title="Información de referencia", layout="centered")

st.title("Calculadora de intereses")
st.subheader("Información de referencia")
st.caption("Captura manual de un préstamo. Todos los campos son editables.")


#Configuración de formulario 

with st.form("formulario_referencia", clear_on_submit=False):
    izquierda, derecha = st.columns(2)
    with izquierda:
        id_cliente = st.text_input("ID de cliente *", key="id_cliente")
    with derecha:
        id_prestamo = st.text_input("ID de préstamo *", key="id_prestamo")

    nombre_cliente = st.text_input("Nombre del cliente", key="nombre_cliente")

    
    izquierda, derecha = st.columns(2)
    with izquierda:
        disposicion = st.text_input("Disposición", key="disposicion")
        agencia = st.text_input("Agencia", key="agencia")
        monto_operado = st.number_input(
            "Monto operado",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.2f",
            key="monto_operado",
        )
    with derecha:
        subaplicacion = st.text_input("Subaplicación", key="subaplicacion")
        fecha_operacion = st.date_input(
            "Fecha de operación",
            value=None,
            min_value=date.min,
            max_value=date.max,
            format="DD/MM/YYYY",
            key="fecha_operacion",
        )
        moneda = st.text_input(
            "Moneda",
            placeholder="Por ejemplo: MXN",
            key="moneda",
            help="Indica la moneda del monto operado.",
        )

# Los datos obligatorios son ID préstamo y cliente 
    
    st.caption("* Campos obligatorios para revisar la captura.")
    revisar = st.form_submit_button("Revisar información")

if revisar:
    if not id_cliente.strip() or not id_prestamo.strip():
        st.warning("Captura el ID de cliente y el ID de préstamo.")
    else:
        # Un solo registro de referencia, preparado para ampliarse después.
        referencia = {
            "id_cliente": id_cliente.strip(),
            "id_prestamo": id_prestamo.strip(),
            "nombre_cliente": nombre_cliente.strip(),
            "disposicion": disposicion.strip(),
            "agencia": agencia.strip(),
            "subaplicacion": subaplicacion.strip(),
            "fecha_operacion": fecha_operacion,
            "monto_operado": monto_operado,
            "moneda": moneda.strip(),
        }

        campos = [
            ("ID de cliente", referencia["id_cliente"]),
            ("ID de préstamo", referencia["id_prestamo"]),
            ("Nombre del cliente", referencia["nombre_cliente"]),
            ("Disposición (Disp.)", referencia["disposicion"]),
            ("Agencia", referencia["agencia"]),
            ("Subaplicación", referencia["subaplicacion"]),
            (
                "Fecha de operación",
                fecha_operacion.strftime("%d/%m/%Y")
                if fecha_operacion is not None else "",
            ),
            (
                "Monto operado",
                f"{monto_operado:,.2f}" if monto_operado is not None else "",
            ),
            ("Moneda", referencia["moneda"]),
        ]

        st.subheader("Última información enviada")
        st.table([
            {"Campo": campo, "Valor": valor or "Sin capturar"}
            for campo, valor in campos
        ])
        st.caption("Para reflejar cambios, vuelve a pulsar «Revisar información».")

st.caption("La información no se guarda de forma permanente.")
