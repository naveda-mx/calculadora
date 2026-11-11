# Calculadora de intereses con tasas de Banxico

Esta versión permite capturar la información de un préstamo y calcular el
interés del período y su vencimiento. La tasa base se captura manualmente o
se consulta en el SIE de Banxico. Los datos de identificación son opcionales.
El cálculo requiere saldo insoluto, tasa base anual, spread y fechas de inicio
y fin. La amortización comienza en cero y es editable.
La página utiliza el ancho de la pantalla y organiza los campos en tres columnas.

## 1. Captura los datos y las condiciones

En la hoja de referencia, las filas 35 a 40 están marcadas como
**Referencia** en la columna D. De ahí se toman los siguientes campos:

| Campo | Captura |
| --- | --- |
| ID de cliente | Texto para conservar ceros iniciales |
| ID de préstamo | Texto para conservar ceros iniciales |
| Nombre del cliente | Texto |
| Agencia | Texto para conservar el código tal como se escribe |
| Subaplicación | Texto para conservar el código tal como se escribe |
| Fecha de operación | Selector de fecha, inicialmente vacío |

Se incluyen también **Disposición (Disp.)** y **Moneda**, presentes en las filas
34 y 47 del catálogo. Moneda permite identificar la unidad de los importes.
Por ahora ambos son campos de texto libres.

Las condiciones adicionales se capturan en el formulario:

| Campo | Captura |
| --- | --- |
| Saldo insoluto | Capital pendiente de pago, con hasta dos decimales |
| Tasa | Captura manual o una de las siete series de Banxico |
| Tasa base anual | Porcentaje manual, por ejemplo `6.8198`, o valor de Banxico |
| Spread anual | Puntos porcentuales, por ejemplo `2.85` |
| Fecha de inicio y fecha final | Fechas del período de intereses |
| Amortización de este vencimiento | Abono a capital en la moneda del préstamo |

Para un crédito con amortización a fin de año, captura cero en los períodos
sin abono y el importe programado en el período del pago anual. El importe
se introduce manualmente para cada vencimiento.

El cálculo mantiene el saldo insoluto y las tasas constantes durante el período:

```text
Días = fecha final − fecha de inicio
Tasa total anual (%) = tasa base + spread
Interés diario = redondear(saldo insoluto × tasa total / 100 / 360, 2)
Interés del período = interés diario × días
Vencimiento = interés del período + amortización
```

La base de 360 días y el redondeo diario a centavos siguen las fórmulas R29,
R30 y R68 de la hoja de referencia. Se utiliza redondeo de mitades alejándose
de cero, equivalente a REDONDEAR de Excel. El interés se aplica al saldo
insoluto capturado, antes del abono a capital del vencimiento.
Los montos admiten hasta dos decimales y las tasas hasta seis decimales.
La fecha final debe ser igual o
posterior a la inicial y la amortización debe estar entre cero y el saldo insoluto.

El spread se introduce manualmente. El ajuste del spread corresponde a una
etapa posterior. Seleccionar una tasa de fondeo no activa composición diaria:
se fija una observación anual para todo el período. Las tasas compuestas por
adelantado ya vienen calculadas por Banxico; la aplicación no las recompone.

## Tasas disponibles, lookback y calendario

El selector **Tasa** incluye captura manual y estas series oficiales:

- TIIE a 28 días (publicación diaria), a 91 días y a 182 días.
- TIIE de Fondeo a un día.
- TIIE de Fondeo compuesta por adelantado a 28, 91 y 182 días.

Los nombres usan los plazos oficiales 91 y 182, no 90 y 180. Los índices
acumulados de fondeo no se ofrecen como tasas porcentuales. Las fuentes y los
identificadores del catálogo están documentados en `banxico.py`.

Para consultar una tasa:

1. Captura la fecha de inicio y elige la tasa.
2. Elige **Lookback (días hábiles)**. Cero consulta la fecha de referencia si
   es hábil. Puedes desmarcar **Usar la fecha de inicio como fecha de referencia**
   para indicar otra fecha de fijación prevista en el contrato.
3. Se precarga el calendario bancario mexicano de **2025 y 2026**, con sábados
   y domingos inhábiles. En **Editar fechas inhábiles**, agrega, modifica o
   elimina fechas; también puedes cambiar los días semanales inhábiles.
4. Para otros años selecciona **Personalizado** y captura las fechas pertinentes.
   Se bloquea la consulta automática si el recorrido atraviesa un año sin
   cobertura en el calendario mexicano precargado. No se extrapolan festivos.
5. Si la referencia es inhábil, se ajusta al hábil anterior y luego se descuentan
   los días de lookback. Por ejemplo, referencia 06/04/2026 y lookback 2 resulta
   en 31/03/2026: se excluyen Semana Santa (2 y 3 de abril) y el fin de semana.
6. Pulsa **Consultar / actualizar tasa Banxico** para revisar la tasa. También
   puedes pulsar directamente **Calcular interés y vencimiento**: se obtiene
   la tasa si aún no se ha consultado con esas condiciones.

La pantalla muestra la fecha objetivo antes de consultar y la fecha del dato
SIE, serie, valor y hora de descarga después. **Fecha del dato SIE no significa
necesariamente fecha de publicación**: cada serie tiene su propia convención.
Revisa las reglas de fijación del contrato al elegir la fecha de referencia.
El calendario sólo afecta la consulta: el interés sigue contando días
naturales y la fecha final no se mueve.

Si Banxico no devuelve un dato válido para esa fecha, se muestra un aviso y
no se calcula con otra observación. No hay sustitución silenciosa por la última
tasa ni se inventan tasas futuras. La consulta tiene un tiempo máximo de espera
y mensajes para problemas de conexión, credenciales o límites de servicio.
Los datos se conservan en caché durante una hora; el botón de actualización
fuerza una nueva consulta. Cambiar la serie, la fecha, el lookback o el calendario
invalida la tasa mostrada. No hay actualización diaria programada ni histórico
permanente todavía.

## Configura el token de Banxico

La consulta SIE requiere un token. La captura manual funciona sin él.

1. Abre [Generar token del SIE](https://www.banxico.org.mx/SieAPIRest/service/v1/token).
2. Completa el código de seguridad y genera tu token.
3. En la configuración de tu aplicación de Streamlit Community Cloud, abre
   **Secrets** y agrega esta línea, sustituyendo el texto por tu token:

   ```toml
   BANXICO_TOKEN = "TU_TOKEN_PERSONAL_DE_BANXICO"
   ```

4. Guarda los secretos y vuelve a abrir la aplicación. El token se envía
   a Banxico mediante el encabezado `Bmx-Token`, no dentro de la URL.

En tu computadora puedes copiar `.streamlit/secrets.toml.example` a
`.streamlit/secrets.toml` y completar el token, o usar la variable de entorno
`BANXICO_TOKEN`. La variable de entorno tiene prioridad. El archivo real de
secretos está excluido de Git; sube únicamente el ejemplo, nunca tu token.

## 2. Prepara tu repositorio de GitHub

Abre el repositorio donde estás desarrollando tu calculadora. Si todavía no
tienes uno, créalo desde **+ → New repository**. Puedes llamarlo
`calculadora-creditos`.

Coloca estos archivos en la raíz del repositorio:

```text
calculadora-creditos/
├── app.py
├── calculos.py
├── banxico.py
├── calendario.py
└── requirements.txt
```

- `app.py` contiene el formulario y los resultados.
- `calculos.py` contiene las fórmulas y las validaciones numéricas.
- `banxico.py` contiene las series y la consulta oficial del SIE.
- `calendario.py` calcula la fecha de consulta y contiene los festivos verificados.
- `requirements.txt` contiene las dependencias `streamlit` y `pandas`.

Si tu repositorio ya contiene un `app.py`, conserva una copia antes de sustituirlo
o integra el ejemplo en tu aplicación existente. Si ya tienes
`requirements.txt`, integra las dependencias sin borrar las otras que utilices.

## 3. Sube los archivos

1. En la raíz del repositorio, selecciona **Add file → Upload files**.
2. Arrastra `app.py`, `calculos.py`, `banxico.py`, `calendario.py` y `requirements.txt`.
3. Escribe un mensaje, por ejemplo: `Agregar tasas Banxico y lookback con calendario editable`.
4. Confirma con **Commit changes** y comprueba la rama donde quedaron los archivos.

También puedes usar **Add file → Create new file**, escribir el nombre exacto
de cada archivo y copiar su contenido. Evita nombres como `app.py.txt`.

El Excel sirve como referencia para diseñar los campos. No es necesario subirlo
para que funcione esta primera versión. El ejemplo no incorpora sus registros.

## 4. Despliega en Streamlit Community Cloud

1. Entra a [Streamlit Community Cloud](https://share.streamlit.io/) y conecta tu
   cuenta de GitHub.
2. Pulsa **Create app** y después **Yup, I have an app**.
3. En **Repository**, selecciona tu repositorio.
4. En **Branch**, selecciona la rama donde subiste los archivos, normalmente `main`.
5. En **Main file path**, escribe `app.py` si está en la raíz.
6. Pulsa **Deploy** y espera a que termine el despliegue.

Si ya tienes una aplicación desplegada desde esa misma rama y ruta, basta con
confirmar los cambios en GitHub para que se actualice el despliegue conectado.

Revisa quién puede abrir la aplicación en **App settings → Sharing**.

## 5. Revisa el resultado

1. Pulsa **Calcular interés y vencimiento** con los campos vacíos. El aviso
   debe identificar los datos de cálculo que faltan.
2. Captura saldo insoluto `1000`, tasa base `8`, spread `2`, inicio `01/12/2026`,
   fecha final `31/12/2026` y amortización `100`.
3. El resultado debe ser 30 días, interés diario `0.28`, interés del período
   `8.40` y vencimiento `108.40`.
4. Abre **Ver datos y desglose** para revisar las condiciones utilizadas.
5. Usa identificadores ficticios `000123` y `000456` y verifica que conservan
   los ceros en el desglose. Estos campos pueden permanecer vacíos.
6. Prueba saldo insoluto `0` con amortización `0`. Los importes calculados deben ser `0.00`.
7. Cambia un dato y vuelve a pulsar el botón para actualizar los resultados.

Los campos conservan la captura durante la sesión. Los resultados aparecen
tras cada cálculo válido; al editar una condición debes pulsar Calcular nuevamente.
La captura puede perderse al recargar o cerrar la pestaña.

## 6. Modifica el formulario después

Edita `app.py` en GitHub y confirma con **Commit changes**. Por ejemplo, cambia
el texto de `st.title(...)` para renombrar tu página.

Los campos tienen claves estables como `id_cliente`, `id_prestamo` y
`fecha_operacion`. Esto facilita incorporar después una consulta por cliente y
préstamo que complete el mismo formulario, manteniendo los campos editables.
El autollenado corresponde a una etapa posterior.

## Ejecución local opcional

Si tienes Python instalado, abre una terminal en la carpeta que contiene
`app.py` y ejecuta estos comandos por separado:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre en tu navegador la dirección local que indique la terminal. Para subir el
ejemplo por la página web de GitHub y desplegarlo en Community Cloud no necesitas
instalar Python en tu computadora.

Las pruebas de fórmulas, calendarios, consultas y pantalla se ejecutan con:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas de Banxico utilizan respuestas simuladas: no necesitan token ni
consumen consultas. Para verificar la conexión real, configura tu token y
consulta una fecha hábil histórica; compara el resultado con la serie SIE.

## Documentación oficial

- [API y token de Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/token)
- [Tasas de interés, cuadro CF101](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CF101&locale=es)
- [Índices y tasas compuestas de fondeo, cuadro CA766](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadroAnalitico&idCuadro=CA766&locale=es)
- [Calendario bancario 2025, CNBV](https://sidof.segob.gob.mx/notas/docFuente/5746258)
- [Calendario bancario 2026, CNBV](https://sidof.segob.gob.mx/notas/docFuente/5775684)
- [Secretos de Streamlit](https://docs.streamlit.io/develop/concepts/connections/secrets-management)
- [Crear un repositorio en GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
- [Subir archivos a GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [Dependencias en Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Desplegar una aplicación](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Formularios de Streamlit](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Estado de sesión](https://docs.streamlit.io/develop/concepts/architecture/session-state)
