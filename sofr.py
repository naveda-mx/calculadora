"""Observaciones diarias de la SOFR de la Fed de Nueva York."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SERIE_SOFR = "SOFR"
URL_SOFR = "https://markets.newyorkfed.org/api/rates/secured/sofr/search.json"


class ErrorSOFR(Exception):
    """No se pudo obtener el conjunto completo de tasas requeridas."""


@dataclass(frozen=True)
class ObservacionSOFR:
    fecha: date
    tasa: Decimal
    consultada_en: datetime


def consultar_sofr(fechas):
    """Consulta en lote por fecha de valor y devuelve tasas en porcentaje anual."""
    fechas = tuple(fechas)
    if not fechas or any(type(fecha) is not date for fecha in fechas):
        raise ValueError("Selecciona fechas válidas para consultar la SOFR.")
    fechas = tuple(sorted(set(fechas)))
    parametros = urlencode({
        "startDate": fechas[0].isoformat(), "endDate": fechas[-1].isoformat(), "type": "rate",
    })
    solicitud = Request(f"{URL_SOFR}?{parametros}", headers={"Accept": "application/json"})
    try:
        with urlopen(solicitud, timeout=15) as respuesta:
            contenido = json.load(respuesta, parse_float=Decimal)
    except HTTPError as error:
        if error.code != 404:
            raise ErrorSOFR(f"La Fed de Nueva York respondió con un error (HTTP {error.code}).") from None
        contenido = {"refRates": []}
    except (URLError, TimeoutError, OSError):
        raise ErrorSOFR("No fue posible conectar con la Fed de Nueva York. Intenta de nuevo.") from None
    except (json.JSONDecodeError, UnicodeError):
        raise ErrorSOFR("No se pudo leer la respuesta de SOFR.") from None

    solicitadas = set(fechas)
    observaciones = {}
    consultada_en = datetime.now(timezone.utc)
    try:
        datos = contenido["refRates"]
        if not isinstance(datos, list):
            raise ValueError
        for dato in datos:
            fecha = date.fromisoformat(dato["effectiveDate"])
            if dato["type"] != SERIE_SOFR or not fechas[0] <= fecha <= fechas[-1]:
                raise ValueError
            if fecha not in solicitadas:
                continue
            valor = dato["percentRate"]
            if fecha in observaciones or type(valor) not in (Decimal, int):
                raise ValueError
            tasa = Decimal(valor)
            if not tasa.is_finite():
                raise ValueError
            observaciones[fecha] = ObservacionSOFR(fecha, tasa, consultada_en)
    except (KeyError, TypeError, ValueError):
        raise ErrorSOFR("La respuesta de la Fed de Nueva York no coincide con la tasa o fecha solicitada.") from None

    faltantes = [fecha for fecha in fechas if fecha not in observaciones]
    if faltantes:
        resumen = ", ".join(fecha.strftime("%d/%m/%Y") for fecha in faltantes[:5])
        if len(faltantes) > 5:
            resumen += f" y {len(faltantes) - 5} fecha(s) más"
        raise ErrorSOFR(
            f"No hay SOFR publicada con fecha de valor: {resumen}. "
            "Revisa el período y el lookback. La observación puede estar pendiente de publicación."
        )
    return {fecha: observaciones[fecha] for fecha in fechas}
