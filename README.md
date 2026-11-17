# Calculadora de intereses con tasas de Banxico

Esta versión permite capturar la información de un préstamo y calcular el
interés del período y su vencimiento. La tasa base se captura manualmente o
se consulta en el SIE de Banxico. Los datos de identificación son opcionales.
El cálculo requiere saldo insoluto, tasa base anual, spread y fechas de inicio
y fin. La amortización comienza en cero y es editable.
La página utiliza el ancho de la pantalla y organiza los campos en tres columnas.

## 1. Captura los datos y las condiciones

En el catálogo inicial `Tasas_Interés_1.xlsx`, las filas 35 a 40 están marcadas como
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

La base de 360 días y el redondeo diario a centavos siguen el numeral 1.5.4
de la imagen en **Tipos Tasas y Fórmula** y T5:T6 de **Cálculo de Interés** del
archivo `EDO CTA  SIN INFONAVIT Y FIDE_Ago2026_copia.xlsx` proporcionado.
Se utiliza redondeo de mitades alejándose de cero, equivalente a REDONDEAR
de Excel. El tercer decimal determina el centavo; no se redondea primero
a tres decimales, porque eso introduciría un doble redondeo. El interés se aplica al saldo
insoluto capturado, antes del abono a capital del vencimiento.
Los montos admiten hasta dos decimales y las tasas hasta seis decimales.
La fecha final debe ser igual o
posterior a la inicial y la amortización debe estar entre cero y el saldo insoluto.

El spread se introduce manualmente. **Método de cálculo** distingue interés
simple, tasa compuesta y tasa equivalente. **Capitalizar sobre** determina
si se capitaliza sólo la base o también el spread.
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

Los cuatro criterios corresponden a **Recálculo**, L4:N9. La propia hoja
indica que se determinan contractualmente; se conserva la elección del usuario.

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

## Métodos de cálculo y capitalización

La hoja **Recálculo** contiene una imagen de las opciones Tasa Compuesta,
Tasa Equivalente sobre tasa total y Tasa Equivalente sobre tasa base.
La página reproduce esa distinción mediante **Método de cálculo** y
**Capitalizar sobre**, y añade el interés simple del primer bloque de
**Cálculo de Interés**. La opción inicial sigue siendo Tasa equivalente / Sólo tasa base.

Las siguientes fórmulas reciben tasas en porcentaje anual (por ejemplo,
`6.75`, no `0.0675`); por eso el denominador es `36000 = 100 × 360`.
`K` es el saldo insoluto original, `n_i` los días del tramo y `N` los días totales.
La base de esta versión es días naturales / 360, utilizada en los ejemplos.
El numeral 1.5.4 permite otras bases según el contrato; no se implementan
convenciones 30/360 ni otras bases anuales en esta versión.

### Interés simple

```text
Interés_i = REDONDEAR(K × (base_i + spread) / 36000, 2) × n_i
Interés del período = suma de Interés_i
```

No incorpora intereses previos al capital. Corresponde a la fórmula diaria
del numeral 1.5.4 y a T5:T6. **Capitalizar sobre** se deshabilita.

### Tasa compuesta

Se calculan importes por tramo, conforme a U23:U25 y U55:U57.
Con **Tasa base + spread**:

```text
K_i = K + suma de los intereses de tramos anteriores
Interés_i = REDONDEAR(K_i × (base_i + spread) / 36000, 2) × n_i
```

Con **Sólo tasa base**, siguiendo también la hoja diaria del usuario:

```text
K_i = K + suma de intereses BASE de tramos anteriores
Interés base_i = REDONDEAR(K_i × base_i / 36000, 2) × n_i
Interés spread_i = REDONDEAR(K × spread / 36000, 2) × n_i
Interés_i = Interés base_i + Interés spread_i
```

Sólo se incorpora el interés capitalizable al pasar al siguiente tramo.
El spread conserva el saldo original cuando queda fuera de la capitalización.
Los componentes se redondean por separado en esa opción. El interés final
es la suma de los importes de los tramos. No se sustituye este proceso por
una tasa equivalente: sus redondeos pueden producir importes distintos.

### Tasa equivalente sobre tasa base

Corresponde a T33:Z33 y S41:Z42, con margen fuera de los factores:

```text
Factor_i = 1 + base_i × n_i / 36000
Rendimiento = producto de Factor_i − 1
Tasa base equivalente anual (%) = Rendimiento × 36000 / N
Tasa total anual (%) = Tasa base equivalente anual + spread
Interés = REDONDEAR(K × Tasa total anual / 36000, 2) × N
```

**La conversión conserva toda su precisión**, conforme a la aclaración del
usuario y a la nota U42 «sin redondeo por la conversión». Esta decisión
sustituye la regla anterior de cuatro decimales. El libro contiene una
diferencia interna: L41 utiliza Z42, una tasa total capturada a cuatro
decimales porcentuales, en lugar de la conversión completa X41+Y41.
Con los datos de ese bloque, la precisión completa produce **4,110,224.30**;
con la tasa capturada `10.1317 %`, L41 produce **4,110,238.86**. La calculadora
aplica la precisión completa solicitada, sin forzar el importe de Z42.

### Tasa equivalente sobre tasa total

Corresponde a U51:W52 y L51; el spread queda dentro del factor:

```text
Factor_i = 1 + (base_i + spread) × n_i / 36000
Rendimiento = producto de Factor_i − 1
Interés = REDONDEAR(K × Rendimiento, 2)
```

Se utiliza directamente el rendimiento efectivo del período. La tasa anual
equivalente mostrada sirve como referencia; no se redondea ni se usa un
promedio diario para obtener el interés. No se suma de nuevo el spread.
El resultado de L51 se presenta en centavos.

### Precisión, pantalla y comprobaciones

Los factores se muestran con cinco decimales y el equivalente anual con diez,
pero esos valores de presentación no se reutilizan para calcular importes.
Los factores y sus productos se conservan internamente como fracciones exactas.
El redondeo monetario compara el centavo exacto con su mitad; así una división
periódica no convierte un empate de `0.005` en `0.004999…`.
Los montos capturados y los resultados monetarios usan Decimal.

La pantalla muestra las tasas por tramo, las fórmulas del método seleccionado
y el resumen final. No se añade una tabla diaria de intereses. El saldo insoluto
registrado se conserva; el capital de cálculo sólo crece dentro del método
compuesto. Cambiar el método, el alcance o el spread reutiliza las tasas originales
consultadas. Los importes se actualizan al pulsar **Calcular interés y vencimiento**.
En captura manual y **Sin revisión** se conserva el interés simple.

Regresiones incluidas en `tests/test_normativa.py`:

| Referencia en Cálculo de Interés | Método | Interés |
| --- | --- | ---: |
| T5 | Simple | 26,332.95 |
| T6 | Simple | 369,859.14 |
| U23:U25 | Compuesta, base + spread | 7,733,389.12 |
| U27 | Equivalente sobre total | 7,733,389.20 |
| L32 / Z33 | Equivalente sobre base, conversión completa | 98,364.33 |
| L51 | Equivalente sobre total | 2,281,351.86 |
| U55:U57 | Compuesta, base + spread | 2,281,351.86 |

Los valores TERM SOFR del ejemplo se utilizan como datos fijos para verificar
la fórmula; no se incorpora una conexión a CME.

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
  tramo. Un sábado, domingo o festivo utiliza la referencia hábil anterior,
  con el lookback seleccionado.
- **Revisión sólo en días hábiles.** Un tramo cubre
  desde la revisión hábil hasta la siguiente, incluyendo los días inhábiles
  intermedios. Si el período comienza en un inhábil, se toma la revisión hábil
  anterior y se cuentan sólo los días desde el inicio del período.

Por ejemplo, del viernes al martes siguiente, con sábado y domingo inhábiles y
sin otros festivos: la primera convención produce cuatro tramos de un día;
la segunda produce un tramo viernes–lunes de tres días y otro lunes–martes de
un día. En ambas se devengan cuatro días y se aplica el lookback a cada
referencia. Si la tasa del viernes es `r` en decimal y el lunes es `s`, los
factores, al elegir tasa equivalente, son `(1 + r/360)^3 × (1 + s/360)` y
`(1 + 3r/360) × (1 + s/360)`, respectivamente. Sus resultados pueden diferir.
Esta elección corresponde a la frecuencia de revisión, no al recálculo por
ajuste de la fecha de pago. Ambas opciones se controlan por separado.

Para la revisión diaria la aplicación agrupa las fechas necesarias en una
consulta de rango al SIE. Verifica cada observación solicitada, no la sustituye
por otra y muestra un error si falta; los fines de semana se mapean al hábil
anterior según el calendario seleccionado antes de consultar.

Ejemplo verificado con las tasas de las imágenes proporcionadas:

| Inicio | Final | Días | Consulta, lookback 0 | Tasa anual | Factor mostrado |
| --- | --- | ---: | --- | ---: | ---: |
| 15/06/2026 | 15/07/2026 | 30 | 15/06/2026 | 6.7559 % | 1.00563 |
| 15/07/2026 | 15/08/2026 | 31 | 15/07/2026 | 6.7559 % | 1.00582 |
| 15/08/2026 | 15/09/2026 | 31 | 14/08/2026 | 6.7358 % | 1.00580 |
| 15/09/2026 | 15/10/2026 | 30 | 15/09/2026 | 6.7458 % | 1.00562 |
| 15/10/2026 | 31/10/2026 | 16 | 15/10/2026 | 6.7659 % | 1.00301 |

Con 138 días, el equivalente anual es aproximadamente 6.8197970459 %.
Con saldo 76,704,742.39, spread 2.85 % y amortización cero, la conversión
completa produce **2,843,256.78**. El resultado anterior **2,843,258.16** usaba
6.8198 % antes de sumar el spread. La diferencia responde a la precisión
ahora solicitada. Las pruebas usan tasas de las imágenes, sin consulta real.

Ejemplo de la hoja diaria: saldo `4,278,722,682.86`, spread `1 %`, del
29/10/2026 al 05/11/2026, revisión diaria en días hábiles, lookback 5 y
02/11/2026 inhábil. Con las tasas de la imagen 6.53 %, 6.52 % (cuatro días),
6.51 % y 6.52 %:

- **Tasa compuesta / Sólo tasa base:** **6,258,548.93**, como en la hoja diaria.
  El interés base capitalizable suma 5,426,575.06 y el spread 831,973.87.
- **Tasa equivalente / Sólo tasa base, precisión completa:** **6,258,548.94**.
  El equivalente es aproximadamente 6.5225307778 % y el interés diario 894,078.42.

La diferencia de un centavo se debe a los distintos puntos de redondeo.
El importe anterior 6,258,523.32 usaba el equivalente reducido a 6.5225 %.
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
