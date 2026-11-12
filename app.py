from datetime import date, datetime, timezone
from decimal import InvalidOperation
from copy import deepcopy
import os

import pandas as pd
import streamlit as st

from banxico import TASAS_BANXICO, CONVENCIONES_FECHA, ErrorBanxico, consultar_tasa
from calendario import CALENDARIOS_MX, FUENTES_CALENDARIO, fecha_consulta
from calculos import calcular_vencimiento
from tramos import FRECUENCIAS, generar_tramos, componer_tasas


@st.cache_data(ttl=3600, max_entries=512, show_spinner=False)
def consultar_con_cache(serie_id, fecha, token):
    return consultar_tasa(serie_id, fecha, token)


def token_banxico():
    """Las credenciales se configuran en el servidor, nunca en el formulario."""
    token = os.environ.get("BANXICO_TOKEN", "").strip()
    if not token:
        try:
            token = str(st.secrets.get("BANXICO_TOKEN", "")).strip()
        except (FileNotFoundError, KeyError):
            pass
    if not token:
        raise ValueError(
            'Falta configurar BANXICO_TOKEN en los secretos de Streamlit. '
            'Consulta las instrucciones del README. La captura manual sigue disponible.'
        )
    return token


def recuperar_captura(clave):
    """Restaura controles ocultados al cambiar entre Banxico y captura manual."""
    copia = "borrador_" + clave
    if clave not in st.session_state and copia in st.session_state:
        st.session_state[clave] = deepcopy(st.session_state[copia])


def conservar_captura(clave):
    st.session_state["borrador_" + clave] = deepcopy(st.session_state[clave])


st.set_page_config(page_title="Calculadora de intereses", layout="wide")

st.title("Calculadora de intereses")
st.subheader("Información de referencia")
st.caption("Un préstamo por cálculo. Los datos de identificación son opcionales.")

with st.container():
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
        disposicion = st.text_input("Disposición (Disp.)", key="disposicion")

    st.subheader("Condiciones del cálculo")
    st.caption(
        "Captura las tasas anuales en porcentaje, con hasta seis decimales. "
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
            "Spread anual (puntos porcentuales) *",
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

    st.subheader("Tasa de referencia")
    izquierda, centro, derecha = st.columns(3)
    with izquierda:
        serie_id = st.selectbox(
            "Tasa",
            options=["manual", *TASAS_BANXICO],
            format_func=lambda codigo: "Captura manual" if codigo == "manual" else TASAS_BANXICO[codigo],
            key="serie_id",
        )
    es_banxico = serie_id != "manual"
    with centro:
        if not es_banxico:
            recuperar_captura("tasa_base")
            tasa_base = st.number_input(
                "Tasa base anual (%) *", value=None, step=0.0001,
                format="%.6f", key="tasa_base",
            )
            conservar_captura("tasa_base")
        else:
            tasa_base = None
            indicador_tasa = st.empty()
    with derecha:
        lookback = st.number_input(
            "Lookback (días hábiles)", min_value=0, max_value=365,
            value=0, step=1, key="lookback", disabled=not es_banxico,
            help="Días hábiles que se retrocede desde la fecha de referencia para consultar la tasa.",
        )

    configuracion = None
    fecha_tasa = None
    error_calendario = None
    por_tramos = False
    tramos = []
    fechas_consulta = []
    if es_banxico:
        st.caption(
            "Plazos oficiales: TIIE a 28, 91 y 182 días; TIIE de Fondeo a un día; "
            "TIIE de Fondeo compuesta por adelantado a 28, 91 y 182 días. "
            "Puedes revisar la tasa por tramos o fijar una sola tasa para todo el período."
        )
        izquierda, derecha = st.columns(2)
        recuperar_captura("frecuencia")
        frecuencia = izquierda.selectbox(
            "Frecuencia de revisión", [*FRECUENCIAS, "Sin revisión"], key="frecuencia",
        )
        conservar_captura("frecuencia")
        por_tramos = frecuencia != "Sin revisión"
        recuperar_captura("dia_revision")
        dia_revision = derecha.number_input(
            "Día de revisión", min_value=1, max_value=31, value=15, step=1,
            key="dia_revision", disabled=not por_tramos,
        )
        conservar_captura("dia_revision")
        if por_tramos:
            fecha_referencia = fecha_inicio
            st.caption(
                "Las revisiones se anclan al mes de inicio y se repiten según la frecuencia. "
                "Si el inicio cae entre revisiones, se usa la revisión anterior para el primer tramo. "
                "Si el día elegido no existe en un mes, se usa su último día. "
                "Los cortes son fechas de revisión de tasa; la amortización sigue aplicándose al vencimiento final."
            )
        else:
            usar_inicio = st.checkbox("Usar la fecha de inicio como fecha de referencia", value=True)
            fecha_referencia = fecha_inicio if usar_inicio else st.date_input(
                "Fecha de referencia para fijar la tasa", value=fecha_inicio,
                min_value=date.min, max_value=date.max, format="DD/MM/YYYY", key="fecha_referencia",
            )
        izquierda, derecha = st.columns(2)
        with izquierda:
            recuperar_captura("calendario")
            calendario = st.selectbox(
                "Calendario de días inhábiles", ["Bancario de México", "Personalizado"],
                key="calendario",
            )
            conservar_captura("calendario")
        with derecha:
            nombres_dias = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")
            recuperar_captura("dias_semana")
            dias_semana = st.multiselect(
                "Días de la semana inhábiles", options=list(range(7)), default=[5, 6],
                format_func=lambda dia: nombres_dias[dia], key="dias_semana",
            )
            conservar_captura("dias_semana")
        festivos_base = (
            sorted(fecha for fechas in CALENDARIOS_MX.values() for fecha in fechas)
            if calendario == "Bancario de México" else []
        )
        with st.expander("Editar fechas inhábiles"):
            if calendario == "Bancario de México":
                st.caption(
                    "Calendario bancario oficial precargado para "
                    + ", ".join(str(anio) for anio in sorted(CALENDARIOS_MX))
                    + ". Puedes agregar, modificar o eliminar fechas."
                )
                st.markdown(" · ".join(
                    f"[Fuente {anio}]({url})" for anio, url in FUENTES_CALENDARIO.items()
                ))
            else:
                st.caption("Agrega los festivos de todos los años que atraviese el lookback.")
            clave_editor = "festivos_mx" if calendario == "Bancario de México" else "festivos_personalizados"
            # El editor no admite asignación a su estado. Al volver a mostrarlo,
            # usamos la última tabla como nueva base; mientras esté visible, la
            # base permanece estable para no aplicar dos veces una misma edición.
            clave_base = "base_" + clave_editor
            if clave_editor not in st.session_state:
                st.session_state[clave_base] = st.session_state.get(
                    "borrador_" + clave_editor,
                    pd.DataFrame({"Fecha inhábil": pd.to_datetime(festivos_base)}),
                ).copy(deep=True)
            tabla_festivos = st.data_editor(
                st.session_state[clave_base],
                num_rows="dynamic", hide_index=True, height=260,
                column_config={"Fecha inhábil": st.column_config.DateColumn(
                    "Fecha inhábil", format="DD/MM/YYYY", required=True,
                )},
                key=clave_editor,
            )
            st.session_state["borrador_" + clave_editor] = tabla_festivos.copy(deep=True)
        festivos = tuple(sorted({pd.Timestamp(f).date() for f in tabla_festivos["Fecha inhábil"].dropna()}))
        if fecha_referencia is not None:
            try:
                if por_tramos:
                    tramos = generar_tramos(
                        fecha_inicio, fecha_fin, frecuencia, dia_revision, lookback, dias_semana, festivos,
                    )
                    fechas_consulta = list(dict.fromkeys(t.consulta for t in tramos))
                    ultima_referencia = tramos[-1].referencia
                else:
                    fecha_tasa = fecha_consulta(fecha_referencia, lookback, dias_semana, festivos)
                    fechas_consulta = [fecha_tasa]
                    ultima_referencia = fecha_referencia
                if calendario == "Bancario de México":
                    sin_cobertura = set(range(min(fechas_consulta).year, ultima_referencia.year + 1)) - set(CALENDARIOS_MX)
                    if sin_cobertura:
                        raise ValueError(
                            "No hay calendario bancario precargado para "
                            + ", ".join(str(anio) for anio in sorted(sin_cobertura))
                            + ". Selecciona Personalizado y captura sus fechas inhábiles."
                        )
                configuracion = (
                    serie_id, fecha_referencia, lookback, tuple(sorted(dias_semana)),
                    festivos, calendario, tuple(fechas_consulta), frecuencia,
                    dia_revision if por_tramos else None, fecha_fin if por_tramos else None,
                )
                if por_tramos:
                    st.info(f"{len(tramos)} tramos · {(fecha_fin - fecha_inicio).days} días naturales.")
                    with st.expander("Ver fechas de revisión y consulta"):
                        st.table([{
                            "Inicio": t.inicio.strftime("%d/%m/%Y"),
                            "Final": t.fin.strftime("%d/%m/%Y"), "Días": t.dias,
                            "Revisión": t.referencia.strftime("%d/%m/%Y"),
                            "Consulta con lookback": t.consulta.strftime("%d/%m/%Y"),
                        } for t in tramos])
                else:
                    st.info(f"Fecha de tasa a consultar: {fecha_tasa:%d/%m/%Y}.")
            except ValueError as error:
                error_calendario = str(error)
                st.warning(error_calendario)
        else:
            error_calendario = "Captura la fecha de inicio o una fecha de referencia para consultar Banxico."
            st.info(error_calendario)
        st.caption(
            "Si la referencia es inhábil, primero se lleva al hábil anterior y después se resta el lookback. "
            "Los inhábiles sólo afectan la búsqueda de la tasa: no descuentan días de interés "
            "ni cambian la fecha final. La fecha consultada corresponde a la fecha de la serie SIE."
        )
        st.caption(CONVENCIONES_FECHA[serie_id])

    # Una tasa consultada sólo puede reutilizarse con las mismas condiciones y durante una hora.
    registro = st.session_state.get("consulta_banxico")
    if registro and (
        registro["configuracion"] != configuracion
        or any((datetime.now(timezone.utc) - o.consultada_en).total_seconds() >= 3600
               for o in registro["observaciones"].values())
    ):
        st.session_state.pop("consulta_banxico", None)

    st.caption(
        "Saldo insoluto constante durante el período. En el modo por tramos se componen "
        "los factores y se anualiza el resultado, redondeando la tasa equivalente a cuatro decimales; "
        "después se suma el spread. "
        "Días naturales = fecha final − fecha de inicio. Base de 360 días. "
        "El interés diario se redondea a dos decimales antes de multiplicar por los días."
    )
    st.caption("* Campos obligatorios para calcular.")
    acciones = st.columns(2)
    consultar = acciones[0].button("Consultar / actualizar tasa Banxico", disabled=not es_banxico)
    revisar = acciones[1].button("Calcular interés y vencimiento", type="primary")

obligatorios = {
    "saldo insoluto": saldo_insoluto, "spread": spread,
    "fecha de inicio": fecha_inicio, "fecha final": fecha_fin, "amortización": amortizacion,
}
if not es_banxico:
    obligatorios["tasa base"] = tasa_base
faltantes = [nombre for nombre, valor in obligatorios.items() if valor is None]

if es_banxico and (consultar or (revisar and not faltantes)):
    try:
        if error_calendario:
            raise ValueError(error_calendario)
        if consultar:
            st.session_state.pop("consulta_banxico", None)
        if consultar or "consulta_banxico" not in st.session_state:
            token = token_banxico()
            observaciones = {}
            with st.spinner("Consultando las tasas en Banxico…"):
                for fecha in fechas_consulta:
                    if consultar:
                        consultar_con_cache.clear(serie_id, fecha, token)
                    observaciones[fecha] = consultar_con_cache(serie_id, fecha, token)
                # Publicamos el conjunto sólo si todas las consultas fueron válidas.
                compuesto = componer_tasas(tramos, [observaciones[t.consulta].tasa for t in tramos]) if por_tramos else None
            st.session_state["consulta_banxico"] = {
                "configuracion": configuracion, "observaciones": observaciones,
                "compuesto": compuesto,
            }
    except (ValueError, ErrorBanxico) as error:
        st.session_state.pop("consulta_banxico", None)
        st.warning(str(error))

registro = st.session_state.get("consulta_banxico") if es_banxico else None
if es_banxico:
    if registro:
        if por_tramos:
            compuesto = registro["compuesto"]
            tasa_base = compuesto["tasa_equivalente"]
            indicador_tasa.metric("Tasa equivalente anual", f"{tasa_base:.4f} %")
            st.subheader("Desglose por tramos")
            st.table([{
                "Inicio": fila["tramo"].inicio.strftime("%d/%m/%Y"),
                "Final": fila["tramo"].fin.strftime("%d/%m/%Y"),
                "Días": fila["tramo"].dias,
                "Revisión": fila["tramo"].referencia.strftime("%d/%m/%Y"),
                "Fecha de consulta": fila["tramo"].consulta.strftime("%d/%m/%Y"),
                "Tasa anual (%)": f"{fila['tasa']:.4f}",
                "Tasa equivalente (factor)": f"{fila['factor']:.5f}",
            } for fila in compuesto["detalle"]])
            a, b, c = st.columns(3)
            a.metric("Total de días", compuesto["dias"])
            b.metric("Producto de factores − 1", f"{compuesto['acumulado']:.8f}")
            c.metric("Período (360 / días)", f"{compuesto['periodo']:.6f}")
            st.caption(
                "Factor = 1 + tasa anual (%) × días / 36000. Se multiplican los factores "
                "sin redondearlos y se resta 1. Tasa equivalente anual (%) = resultado × 36000 / días. "
                "El spread se agrega después de redondear esta tasa a cuatro decimales."
            )
            st.caption(f"Fuente: Banxico SIE · Serie: {serie_id} · {TASAS_BANXICO[serie_id]}.")
            with st.expander("Detalle de las consultas a Banxico"):
                st.table([{
                    "Fecha del dato": o.fecha.strftime("%d/%m/%Y"),
                    "Consulta (UTC)": o.consultada_en.strftime("%d/%m/%Y %H:%M"),
                } for o in registro["observaciones"].values()])
        else:
            observacion = registro["observaciones"][fecha_tasa]
            tasa_base = observacion.tasa
            indicador_tasa.metric("Tasa base anual de Banxico", f"{tasa_base:.6f} %")
            st.caption(
                f"Fuente: Banxico SIE · Serie: {serie_id} · Fecha del dato: {observacion.fecha:%d/%m/%Y} · "
                f"Consultada: {observacion.consultada_en:%d/%m/%Y %H:%M} UTC."
            )
    else:
        indicador_tasa.info("Consulta Banxico o pulsa Calcular para obtener la tasa.")

if revisar:
    resultado = None
    if faltantes:
        st.warning("Completa los siguientes campos: " + ", ".join(faltantes) + ".")
    elif tasa_base is not None:
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
            ("Tasa de referencia", TASAS_BANXICO[serie_id] if es_banxico else "Captura manual"),
            ("Tasa base anual", f"{tasa_base:.6f} %"),
            ("Spread anual", f"{spread:.6f} puntos porcentuales"),
            ("Tasa total anual", f"{resultado['tasa_total']:.6f} %"),
            ("Interés diario redondeado", f"{resultado['interes_diario']:,.2f}"),
            ("Amortización del vencimiento", f"{resultado['amortizacion']:,.2f}"),
        ]
        if registro:
            campos.extend([
                ("Fuente / serie", f"Banxico SIE / {serie_id}"),
                ("Fecha de referencia", fecha_referencia.strftime("%d/%m/%Y")),
                ("Lookback hábil", str(lookback)),
                ("Frecuencia de revisión", frecuencia),
                ("Día de revisión", str(dia_revision) if por_tramos else "No aplica"),
                ("Fechas de la tasa SIE", ", ".join(f.strftime("%d/%m/%Y") for f in fechas_consulta)),
                ("Calendario", calendario + " (con las fechas seleccionadas)"),
            ])

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
