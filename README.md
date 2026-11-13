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
| Tasa | Captura manual o una de las ocho series de Banxico |
| Tasa base anual | Porcentaje manual, por ejemplo `6.8198`, o valor de Banxico |
| Spread anual | Puntos porcentuales, por ejemplo `2.85` |
| Fecha de inicio y fecha final | Fechas del período de intereses |
| Amortización de este vencimiento | Abono a capital en la moneda del préstamo |

Para un crédito con amortización a fin de año, captura cero en los períodos
sin abono y el importe programado en el período del pago anual. El importe
se introduce manualmente para cada vencimiento.

En captura manual o **Sin revisión**, el cálculo conserva la fórmula original,
con una tasa fija y saldo insoluto constante:

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

El spread se introduce manualmente y se suma después de obtener la tasa anual
equivalente redondeada a cuatro decimales.
Seleccionar fondeo no activa composición diaria overnight: la frecuencia elegida
determina las revisiones. Las tasas compuestas por adelantado se obtienen ya
calculadas de Banxico; se usan como tasas anuales de los tramos seleccionados.

## Cálculo por tramos

Al elegir Banxico aparecen **Frecuencia de revisión** y **Día de revisión**.
La opción inicial es Mensual, día 15. También hay Diaria, Bimestral, Trimestral,
Semestral y Anual. **Sin revisión** conserva el cálculo anterior con una sola
tasa; la captura manual también conserva su fórmula anterior. El día de revisión
del mes no aplica a la frecuencia diaria.

El calendario de revisiones se ancla al mes de inicio. Para frecuencias de
varios meses, ese mes define la secuencia (por ejemplo, inicio en junio y
frecuencia trimestral: junio, septiembre, diciembre, marzo). Si el día elegido
queda después del inicio, el primer tramo usa la revisión anterior en esa
misma secuencia. Verifica que el ancla coincida con las condiciones del préstamo.
Si el día no existe en un mes, se usa su último día; marzo vuelve al día
original, aunque febrero haya utilizado el 28 o 29. La capitalización intermedia
depende de que haya más de un tramo de revisión. No se insertan capitalizaciones
automáticas cada 28 días por seleccionar TIIE a 28 días. Del 15 de junio al 15 de
julio con revisión mensual día 15 hay un solo tramo de 30 días; no se capitaliza
al día 28. En el ejemplo de 138 días, los cinco factores sí se componen.

## Ajuste del vencimiento con o sin recálculo

Disponible tanto en captura manual como en consulta Banxico. Primero aparece
**Sin recálculo**, seguido de **Con recálculo**. El segundo selector permite
elegir **Día hábil anterior** o **Día hábil siguiente**. La fecha de inicio no se
mueve; el calendario editable determina qué fechas son hábiles.

| Opción | Fin para calcular intereses | Fecha de pago |
| --- | --- | --- |
| Sin recálculo + anterior | Fecha final original | Hábil anterior |
| Sin recálculo + siguiente | Fecha final original | Hábil siguiente |
| Con recálculo + anterior | Hábil anterior | Hábil anterior |
| Con recálculo + siguiente | Hábil siguiente | Hábil siguiente |

Si el final original ya es hábil, no se modifica. Por ejemplo, inicio
10/08/2026 y final sábado 15/08/2026: sin recálculo se devengan cinco días,
pagando el viernes 14 o lunes 17 según la opción. Con recálculo se devengan
cuatro o siete días, respectivamente. Los tramos se generan hasta el fin
efectivo del cálculo, que se muestra separado del final original y del pago.
La regla de lookback se aplica a cada revisión como antes. La dirección elegida
para el pago no invierte la búsqueda histórica de las tasas. Un ajuste que
lleve el pago o el fin de cálculo antes del inicio se rechaza.

Los tramos incluyen el inicio y excluyen el final. No se agrega una fila de
cero días al terminar en una revisión. Cada fecha de revisión se ajusta al hábil
anterior y luego se resta su lookback. Los días inhábiles no se excluyen del
devengo. En revisión diaria, la convención elegida determina si se cortan los
tramos en esos días. Las consultas repetidas se reutilizan. Un dato faltante
impide mostrar un cálculo parcial. El límite de las frecuencias mensuales y
mayores es de 120 tramos; para revisión diaria es de 3660 días naturales.

### Revisión diaria y días inhábiles

Selecciona **Diaria** y elige explícitamente el calendario de revisión;
no es necesario capturar un día del mes:

- **Revisión cada día natural.** Cada día devengado tiene su propio
  factor. Un sábado, domingo o festivo utiliza la referencia hábil anterior,
  con el lookback seleccionado. Los factores se multiplican también en esos días.
- **Revisión sólo en días hábiles.** Un factor cubre
  desde la revisión hábil hasta la siguiente, incluyendo los días inhábiles
  intermedios. Si el período comienza en un inhábil, se toma la revisión hábil
  anterior y se cuentan sólo los días desde el inicio del período.

Por ejemplo, del viernes al martes siguiente, con sábado y domingo inhábiles y
sin otros festivos: la primera convención produce cuatro factores de un día;
la segunda produce un factor viernes–lunes de tres días y otro lunes–martes de
un día. En ambas se devengan cuatro días y se aplica el lookback a cada
referencia. Si la tasa del viernes es `r` en decimal y el lunes es `s`, los
factores son `(1 + r/360)^3 × (1 + s/360)` y
`(1 + 3r/360) × (1 + s/360)`, respectivamente. Sus resultados pueden diferir.
Esta elección corresponde a la frecuencia de revisión, no al recálculo por
ajuste de la fecha de pago. Ambas opciones se controlan por separado.

Para la revisión diaria la aplicación agrupa las fechas necesarias en una
consulta de rango al SIE. Verifica cada observación solicitada, no la sustituye
por otra y muestra un error si falta; los fines de semana se mapean al hábil
anterior según el calendario seleccionado antes de consultar.

```text
Factor del tramo = 1 + tasa anual (%) × días del tramo / 36000
Rendimiento acumulado = producto de los factores − 1
Tasa equivalente anual (%) = rendimiento acumulado × 36000 / días totales
Tasa base = redondear(tasa equivalente anual, 4 decimales)
Tasa total = tasa base + spread
Interés diario = redondear(saldo insoluto original × tasa total / 36000, 2)
Interés = interés diario × días totales del cálculo
Vencimiento = interés + amortización final
```

Los factores se muestran con cinco decimales, pero se componen con precisión
Decimal sin redondeo intermedio. La tasa anual equivalente sí se redondea a
cuatro decimales antes de sumar el spread y calcular importes, siguiendo el
primer ejemplo confirmado. La composición se realiza en los factores de tasa;
el saldo insoluto registrado no aumenta en cada revisión. El spread queda fuera
de los factores y no se capitaliza. La pantalla muestra el resumen y los tramos,
sin tabla diaria de intereses. Las revisiones no son amortizaciones intermedias.
El redondeo es de mitades alejándose de cero, como REDONDEAR de Excel.

Ejemplo verificado con las tasas de las imágenes proporcionadas:

| Inicio | Final | Días | Consulta, lookback 0 | Tasa anual | Factor mostrado |
| --- | --- | ---: | --- | ---: | ---: |
| 15/06/2026 | 15/07/2026 | 30 | 15/06/2026 | 6.7559 % | 1.00563 |
| 15/07/2026 | 15/08/2026 | 31 | 15/07/2026 | 6.7559 % | 1.00582 |
| 15/08/2026 | 15/09/2026 | 31 | 14/08/2026 | 6.7358 % | 1.00580 |
| 15/09/2026 | 15/10/2026 | 30 | 15/09/2026 | 6.7458 % | 1.00562 |
| 15/10/2026 | 31/10/2026 | 16 | 15/10/2026 | 6.7659 % | 1.00301 |

Con 138 días, la tasa anual equivalente sin redondear es aproximadamente
6.8197970459 %, que se utiliza como 6.8198 %. Con saldo 76,704,742.39, spread
2.85 % y amortización cero, el interés y vencimiento son 2,843,258.16. Se
recupera así el primer ejemplo. Las pruebas usan tasas simuladas, no una consulta real.

Ejemplo de la hoja diaria: saldo `4,278,722,682.86`, spread `1 %`, del
29/10/2026 al 05/11/2026, revisión diaria en días hábiles, lookback 5 y
02/11/2026 inhábil. Con las tasas de la imagen 6.53 %, 6.52 % (cuatro días),
6.51 % y 6.52 %, la tasa anual equivalente se usa como 6.5225 % (4 decimales).
La tasa total es 7.5225 %, el interés diario 894,074.76 y el vencimiento sin
amortización 6,258,523.32. La regla confirmada de cuatro decimales sustituye la
versión que redondeaba componentes diarios por separado y daba 6,258,548.93.
Estas tasas son simuladas y no confirman una consulta real a Banxico.

## Tasas disponibles, lookback y calendario

El selector **Tasa** incluye captura manual y estas series oficiales:

- Tasa objetivo de Banxico, serie **SF61745**, solicitada como «TIIE diaria».
  Banxico la denomina tasa objetivo; es distinta de la TIIE de Fondeo y de la
  TIIE a 28 días. La aplicación muestra el nombre oficial para evitar confusión.
- TIIE a 28 días, a 91 días y a 182 días.
- TIIE de Fondeo a un día.
- TIIE de Fondeo compuesta por adelantado a 28, 91 y 182 días.

Los nombres usan los plazos oficiales 91 y 182, no 90 y 180. Los índices
acumulados de fondeo no se ofrecen como tasas porcentuales. Las fuentes y los
identificadores del catálogo están documentados en `banxico.py`.

Para consultar una tasa:

1. Captura las fechas de inicio y final; elige la tasa y la frecuencia. Para
   revisión diaria selecciona si ocurre en días naturales o hábiles; para las demás
   frecuencias selecciona el día de revisión del mes.
2. Elige **Lookback (días hábiles)**. Cero consulta la fecha de referencia si
   es hábil. Se aplica a cada revisión. En **Sin revisión** puedes desmarcar
   **Usar la fecha de inicio como fecha de referencia** para indicar otra fecha.
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
   puedes pulsar directamente **Calcular interés y vencimiento**: se obtienen
   las tasas si aún no se han consultado con esas condiciones.

La pantalla muestra la fecha objetivo antes de consultar y la fecha del dato
SIE, serie, valor y hora de descarga después. **Fecha del dato SIE no significa
necesariamente fecha de publicación**: cada serie tiene su propia convención.
Revisa las reglas de fijación del contrato al elegir la fecha de referencia.
El calendario define las consultas históricas, las revisiones diarias hábiles y
el ajuste del vencimiento. Sólo **Con recálculo** cambia el final del devengo;
los inhábiles intermedios siguen contando dentro de los días naturales.

Si Banxico no devuelve un dato válido para esa fecha, se muestra un aviso y
no se calcula con otra observación. No hay sustitución silenciosa por la última
tasa ni se inventan tasas futuras. La consulta tiene un tiempo máximo de espera
y mensajes para problemas de conexión, credenciales o límites de servicio.
Los datos se conservan en caché durante una hora; el botón de actualización
fuerza nuevas consultas. Cambiar la serie, las fechas, la frecuencia, el día de
revisión, la convención diaria, el lookback o el calendario invalida la tasa
mostrada. No hay actualización diaria programada ni histórico permanente todavía.

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
├── tramos.py
└── requirements.txt
```

- `app.py` contiene el formulario y los resultados.
- `calculos.py` contiene las fórmulas y las validaciones numéricas.
- `banxico.py` contiene las series y la consulta oficial del SIE.
- `calendario.py` calcula la fecha de consulta y contiene los festivos verificados.
- `tramos.py` genera revisiones y obtiene la tasa anual equivalente por composición.
- `requirements.txt` contiene las dependencias `streamlit` y `pandas`.

Si tu repositorio ya contiene un `app.py`, conserva una copia antes de sustituirlo
o integra el ejemplo en tu aplicación existente. Si ya tienes
`requirements.txt`, integra las dependencias sin borrar las otras que utilices.

## 3. Sube los archivos

1. En la raíz del repositorio, selecciona **Add file → Upload files**.
2. Arrastra `app.py`, `calculos.py`, `banxico.py`, `calendario.py`, `tramos.py` y `requirements.txt`.
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
| Tasa | Captura manual o una de las ocho series de Banxico |
| Tasa base anual | Porcentaje manual, por ejemplo `6.8198`, o valor de Banxico |
| Spread anual | Puntos porcentuales, por ejemplo `2.85` |
| Fecha de inicio y fecha final | Fechas del período de intereses |
| Amortización de este vencimiento | Abono a capital en la moneda del préstamo |

Para un crédito con amortización a fin de año, captura cero en los períodos
sin abono y el importe programado en el período del pago anual. El importe
se introduce manualmente para cada vencimiento.

En captura manual o **Sin revisión**, el cálculo conserva la fórmula original,
con una tasa fija y saldo insoluto constante:

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

El spread se introduce manualmente. En la modalidad por tramos sus intereses
se calculan y redondean por separado sobre el saldo insoluto inicial.
Seleccionar fondeo no activa composición diaria overnight: la frecuencia elegida
determina las revisiones. Las tasas compuestas por adelantado se obtienen ya
calculadas de Banxico; se usan como tasas anuales de los tramos seleccionados.

## Cálculo por tramos

Al elegir Banxico aparecen **Frecuencia de revisión** y **Día de revisión**.
La opción inicial es Mensual, día 15. También hay Diaria, Bimestral, Trimestral,
Semestral y Anual. **Sin revisión** conserva el cálculo anterior con una sola
tasa; la captura manual también conserva su fórmula anterior. El día de revisión
del mes no aplica a la frecuencia diaria.

El calendario de revisiones se ancla al mes de inicio. Para frecuencias de
varios meses, ese mes define la secuencia (por ejemplo, inicio en junio y
frecuencia trimestral: junio, septiembre, diciembre, marzo). Si el día elegido
queda después del inicio, el primer tramo usa la revisión anterior en esa
misma secuencia. Verifica que el ancla coincida con las condiciones del préstamo.
Si el día no existe en un mes, se usa su último día; marzo vuelve al día
original, aunque febrero haya utilizado el 28 o 29.

Los tramos incluyen el inicio y excluyen el final. No se agrega una fila de
cero días al terminar en una revisión. Cada fecha de revisión se ajusta al hábil
anterior y luego se resta su lookback. Los días inhábiles no se excluyen del
devengo. En revisión diaria, la convención elegida determina si se cortan los
tramos en esos días. Las consultas repetidas se reutilizan. Un dato faltante
impide mostrar un cálculo parcial. El límite de las frecuencias mensuales y
mayores es de 120 tramos; para revisión diaria es de 3660 días naturales.

### Revisión diaria y días inhábiles

Selecciona **Diaria** y elige explícitamente una convención de composición;
no es necesario capturar un día del mes:

- **Días naturales: capitalizar cada día.** Cada día devengado tiene su propio
  factor. Un sábado, domingo o festivo utiliza la referencia hábil anterior,
  con el lookback seleccionado. Los factores se multiplican también en esos días.
- **Días hábiles: capitalizar hasta el siguiente día hábil.** Un factor cubre
  desde la revisión hábil hasta la siguiente, incluyendo los días inhábiles
  intermedios. Si el período comienza en un inhábil, se toma la revisión hábil
  anterior y se cuentan sólo los días desde el inicio del período.

Por ejemplo, del viernes al martes siguiente, con sábado y domingo inhábiles y
sin otros festivos: la primera convención produce cuatro factores de un día;
la segunda produce un factor viernes–lunes de tres días y otro lunes–martes de
un día. En ambas se devengan cuatro días y se aplica el lookback a cada
referencia. Si la tasa del viernes es `r` en decimal y el lunes es `s`, los
factores son `(1 + r/360)^3 × (1 + s/360)` y
`(1 + 3r/360) × (1 + s/360)`, respectivamente. Sus resultados pueden diferir.

Para la revisión diaria la aplicación agrupa las fechas necesarias en una
consulta de rango al SIE. Verifica cada observación solicitada, no la sustituye
por otra y muestra un error si falta; los fines de semana se mapean al hábil
anterior según el calendario seleccionado antes de consultar.

```text
Factor del tramo = 1 + tasa anual (%) × días del tramo / 36000
Rendimiento acumulado = producto de los factores − 1
Tasa equivalente anual (%) = rendimiento acumulado × 36000 / días totales
Tasa total de referencia = tasa equivalente anual + spread
Interés diario de tasa = redondear(base del tramo × tasa del tramo / 36000, 2)
Interés diario del spread = redondear(saldo insoluto original × spread / 36000, 2)
Base del siguiente tramo = base actual + interés diario de tasa × días del tramo
Interés = suma de intereses diarios de tasa y de spread
Vencimiento = interés + amortización final
```

Los factores se muestran con cinco decimales, pero se componen con precisión
Decimal sin redondeo intermedio; la tasa equivalente se muestra con diez
decimales, pero se conserva con toda la precisión Decimal. La tasa equivalente
es teórica: el importe monetario se obtiene calculando cada tramo y redondeando
por separado los intereses de tasa y spread cada día. Por ello, el interés
puede diferir en centavos de aplicar directamente la tasa equivalente teórica.

La base de cálculo de la tasa es el saldo original más los intereses de tasa
capitalizados al final de tramos anteriores; se mantiene fija dentro de cada
tramo. El spread usa siempre el saldo original y no se capitaliza. La tabla
**Desglose diario de intereses** muestra la base, intereses separados, total
diario y acumulado de la tasa. Las revisiones son de tasa, no abonos intermedios
a capital. Se usa redondeo de mitades alejándose de cero, como REDONDEAR de Excel.

Ejemplo verificado con las tasas de las imágenes proporcionadas:

| Inicio | Final | Días | Consulta, lookback 0 | Tasa anual | Factor mostrado |
| --- | --- | ---: | --- | ---: | ---: |
| 15/06/2026 | 15/07/2026 | 30 | 15/06/2026 | 6.7559 % | 1.00563 |
| 15/07/2026 | 15/08/2026 | 31 | 15/07/2026 | 6.7559 % | 1.00582 |
| 15/08/2026 | 15/09/2026 | 31 | 14/08/2026 | 6.7358 % | 1.00580 |
| 15/09/2026 | 15/10/2026 | 30 | 15/09/2026 | 6.7458 % | 1.00562 |
| 15/10/2026 | 31/10/2026 | 16 | 15/10/2026 | 6.7659 % | 1.00301 |

Con 138 días, la tasa equivalente teórica es aproximadamente 6.8197970459 %.
Con saldo 76,704,742.39, spread 2.85 % y amortización cero, aplicando el nuevo
redondeo diario separado por tramo, el interés y vencimiento son 2,843,257.42.
La versión anterior daba 2,843,258.16 porque primero redondeaba la tasa a cuatro
decimales y redondeaba conjuntamente tasa más spread; ya no usa esa regla en
el modo por tramos. Las pruebas usan tasas simuladas, no una consulta real.

Ejemplo de la hoja diaria: saldo `4,278,722,682.86`, spread `1 %`, del
29/10/2026 al 05/11/2026, revisión diaria en días hábiles, lookback 5 y
02/11/2026 inhábil. Con las tasas de la imagen 6.53 %, 6.52 % (cuatro días),
6.51 % y 6.52 %, la tasa equivalente teórica es 6.5225307778 %. El interés de
tasa es `5,426,575.06` y el spread diario es `118,853.41`, que por siete días
suma `831,973.87`. El interés total y vencimiento sin amortización son
`6,258,548.93`. Estas tasas son un ejemplo simulado y no confirman una consulta
real a Banxico.

## Tasas disponibles, lookback y calendario

El selector **Tasa** incluye captura manual y estas series oficiales:

- Tasa objetivo de Banxico, serie **SF61745**, solicitada como «TIIE diaria».
  Banxico la denomina tasa objetivo; es distinta de la TIIE de Fondeo y de la
  TIIE a 28 días. La aplicación muestra el nombre oficial para evitar confusión.
- TIIE a 28 días, a 91 días y a 182 días.
- TIIE de Fondeo a un día.
- TIIE de Fondeo compuesta por adelantado a 28, 91 y 182 días.

Los nombres usan los plazos oficiales 91 y 182, no 90 y 180. Los índices
acumulados de fondeo no se ofrecen como tasas porcentuales. Las fuentes y los
identificadores del catálogo están documentados en `banxico.py`.

Para consultar una tasa:

1. Captura las fechas de inicio y final; elige la tasa y la frecuencia. Para
   revisión diaria selecciona la convención de inhábiles; para las demás
   frecuencias selecciona el día de revisión del mes.
2. Elige **Lookback (días hábiles)**. Cero consulta la fecha de referencia si
   es hábil. Se aplica a cada revisión. En **Sin revisión** puedes desmarcar
   **Usar la fecha de inicio como fecha de referencia** para indicar otra fecha.
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
   las tasas si aún no se han consultado con esas condiciones.

La pantalla muestra la fecha objetivo antes de consultar y la fecha del dato
SIE, serie, valor y hora de descarga después. **Fecha del dato SIE no significa
necesariamente fecha de publicación**: cada serie tiene su propia convención.
Revisa las reglas de fijación del contrato al elegir la fecha de referencia.
El calendario no descuenta días de interés ni cambia la fecha final. En la
revisión diaria con composición en días hábiles, además define dónde se
cierran los tramos para capitalizar el interés de tasa.

Si Banxico no devuelve un dato válido para esa fecha, se muestra un aviso y
no se calcula con otra observación. No hay sustitución silenciosa por la última
tasa ni se inventan tasas futuras. La consulta tiene un tiempo máximo de espera
y mensajes para problemas de conexión, credenciales o límites de servicio.
Los datos se conservan en caché durante una hora; el botón de actualización
fuerza nuevas consultas. Cambiar la serie, las fechas, la frecuencia, el día de
revisión, la convención diaria, el lookback o el calendario invalida la tasa
mostrada. No hay actualización diaria programada ni histórico permanente todavía.

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
├── tramos.py
└── requirements.txt
```

- `app.py` contiene el formulario y los resultados.
- `calculos.py` contiene las fórmulas y las validaciones numéricas.
- `banxico.py` contiene las series y la consulta oficial del SIE.
- `calendario.py` calcula la fecha de consulta y contiene los festivos verificados.
- `tramos.py` genera revisiones y obtiene la tasa anual equivalente por composición.
- `requirements.txt` contiene las dependencias `streamlit` y `pandas`.

Si tu repositorio ya contiene un `app.py`, conserva una copia antes de sustituirlo
o integra el ejemplo en tu aplicación existente. Si ya tienes
`requirements.txt`, integra las dependencias sin borrar las otras que utilices.

## 3. Sube los archivos

1. En la raíz del repositorio, selecciona **Add file → Upload files**.
2. Arrastra `app.py`, `calculos.py`, `banxico.py`, `calendario.py`, `tramos.py` y `requirements.txt`.
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
