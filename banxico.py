"""Consulta puntual de tasas porcentuales oficiales del SIE de Banxico.

Catálogo verificado en los metadatos HTML del cuadro CF111 y en el orden de
series/columnas de CA766 (los primeros dos códigos de CA766 son índices,
SF355630 y SF355631, no tasas y por eso no se incluyen).

https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CF111&locale=es
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadroAnalitico&idCuadro=CA766&locale=es
https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieRango
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TASAS_BANXICO = {
    "SF43783": "TIIE a 28 días (publicación diaria)",
    "SF43878": "TIIE a 91 días",
    "SF111916": "TIIE a 182 días",
    "SF331451": "TIIE de Fondeo a un día",
    "SF355632": "TIIE de Fondeo compuesta por adelantado a 28 días",
    "SF355633": "TIIE de Fondeo compuesta por adelantado a 91 días",
    "SF355634": "TIIE de Fondeo compuesta por adelantado a 182 días",
}

CONVENCIONES_FECHA = {
    **dict.fromkeys(
        ("SF43783", "SF43878", "SF111916"),
        "La fecha SIE de esta TIIE corresponde a su aplicación (publicación en el DOF).",
    ),
    "SF331451": "La fecha SIE de TIIE de Fondeo corresponde a su determinación.",
    **dict.fromkeys(
        ("SF355632", "SF355633", "SF355634"),
        "La fecha de la tasa compuesta por adelantado corresponde a su aplicación.",
    ),
}

URL_BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"


class ErrorBanxico(Exception):
    """Error legible sin exponer credenciales ni el cuerpo de la respuesta."""


@dataclass(frozen=True)
class ObservacionTasa:
    serie_id: str
    fecha: date
    tasa: Decimal
    consultada_en: datetime


def consultar_tasa(serie_id: str, fecha: date, token: str) -> ObservacionTasa:
    """Obtiene sólo la observación exacta solicitada; no sustituye faltantes."""
    if serie_id not in TASAS_BANXICO:
        raise ValueError("Selecciona una tasa del catálogo de Banxico.")
    if type(fecha) is not date:
        raise ValueError("Selecciona una fecha válida para consultar la tasa.")
    if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9]{64}", token.strip()):
        raise ErrorBanxico("Revisa BANXICO_TOKEN: debe contener los 64 caracteres del token del SIE.")
    fecha_iso = fecha.isoformat()
    solicitud = Request(
        f"{URL_BASE}/{serie_id}/datos/{fecha_iso}/{fecha_iso}",
        headers={"Bmx-Token": token.strip(), "Accept": "application/json"},
    )
    try:
        with urlopen(solicitud, timeout=15) as respuesta:
            contenido = json.load(respuesta)
    except HTTPError as error:
        if error.code in (401, 403):
            mensaje = "Banxico no autorizó la consulta. Revisa el token y su estado en el SIE."
        elif error.code == 429:
            mensaje = "Se alcanzó el límite de consultas de Banxico. Intenta de nuevo más tarde."
        else:
            mensaje = f"Banxico respondió con un error de servicio (HTTP {error.code}). Intenta de nuevo más tarde."
        raise ErrorBanxico(mensaje) from None
    except (URLError, TimeoutError, OSError):
        raise ErrorBanxico("No fue posible conectar con Banxico. Revisa la conexión e intenta de nuevo.") from None
    except (json.JSONDecodeError, UnicodeError):
        raise ErrorBanxico("Banxico devolvió una respuesta que no se pudo interpretar.") from None

    try:
        series = contenido["bmx"]["series"]
        if not isinstance(series, list) or len(series) != 1 or series[0]["idSerie"] != serie_id:
            raise ValueError
        datos = series[0].get("datos", [])
        if not isinstance(datos, list):
            raise ValueError
        if not datos:
            raise ErrorBanxico(
                f"Banxico no tiene dato de {TASAS_BANXICO[serie_id]} para {fecha:%d/%m/%Y}. "
                "Revisa el calendario y la fecha de fijación; la tasa puede no estar publicada todavía."
            )
        if len(datos) != 1:
            raise ValueError
        fecha_dato = datetime.strptime(datos[0]["fecha"], "%d/%m/%Y").date()
        if fecha_dato != fecha:
            raise ValueError
        valor = datos[0]["dato"]
        if not isinstance(valor, str):
            raise ValueError
        if valor.strip().upper() in ("N/E", "N/D", "N.D.", "N/A", "", "ND"):
            raise ErrorBanxico(f"Banxico no publicó una tasa numérica para {fecha:%d/%m/%Y}.")
        tasa = Decimal(valor.replace(",", "").strip())
        if not tasa.is_finite():
            raise ValueError
    except (KeyError, TypeError, ValueError, InvalidOperation):
        raise ErrorBanxico("La respuesta de Banxico no coincide con la serie, fecha o valor esperado.") from None

    return ObservacionTasa(serie_id, fecha_dato, tasa, datetime.now(timezone.utc))
