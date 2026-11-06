# calculadora
Primera versión calculadora de Vencimientos
# Primera pantalla: información de referencia

Esta versión permite capturar manualmente la información de un préstamo y
revisarla en una tabla. Todos los campos comienzan vacíos y son editables.
El botón **Revisar información** solicita únicamente el ID de cliente y el ID de
préstamo. El resto puede permanecer vacío en esta etapa.

## 1. Identifica los campos de esta primera etapa

En la hoja de referencia, las filas 35 a 40 y 55 están marcadas como
**Referencia** en la columna D. De ahí se toman los siguientes campos:

| Campo | Captura |
| --- | --- |
| ID de cliente | Texto para conservar ceros iniciales |
| ID de préstamo | Texto para conservar ceros iniciales |
| Nombre del cliente | Texto |
| Agencia | Texto para conservar el código tal como se escribe |
| Subaplicación | Texto para conservar el código tal como se escribe |
| Fecha de operación | Selector de fecha, inicialmente vacío |
| Monto operado | Número no negativo, mostrado con dos decimales |

Se incluyen también **Disposición (Disp.)** y **Moneda**, presentes en las filas
34 y 47 del catálogo. Moneda permite identificar la unidad del monto operado.
Por ahora ambos son campos de texto libres.

Los periodos, tasas, spreads, saldo insoluto, amortización e intereses se
incorporarán en etapas posteriores. Esta versión no calcula intereses,
consulta SIRAC, importa el Excel ni autocompleta datos.

## 2. Prepara tu repositorio de GitHub

Abre el repositorio donde estás desarrollando tu calculadora. Si todavía no
tienes uno, créalo desde **+ → New repository**. Puedes llamarlo
`calculadora-creditos`.

Para esta pantalla sólo necesitas estos dos archivos en la raíz del repositorio:

```text
calculadora-creditos/
├── app.py
└── requirements.txt
```

- `app.py` contiene el formulario y la vista de revisión.
- `requirements.txt` contiene la dependencia `streamlit`.

Si tu repositorio ya contiene un `app.py`, conserva una copia antes de sustituirlo
o integra el ejemplo en tu aplicación existente. Si ya tienes
`requirements.txt`, agrega `streamlit` sin borrar tus otras dependencias.

## 3. Sube los archivos

1. En la raíz del repositorio, selecciona **Add file → Upload files**.
2. Arrastra `app.py` y `requirements.txt` desde esta carpeta.
3. Escribe un mensaje, por ejemplo: `Agregar formulario de información de referencia`.
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

1. Comprueba que los nueve campos aparecen vacíos.
2. Pulsa **Revisar información** sin llenar los identificadores. Debe aparecer
   un aviso solicitando ambos.
3. Usa datos ficticios, por ejemplo ID de cliente `000123` e ID de préstamo
   `000456`, y verifica que los ceros se conservan en la tabla.
4. Captura una fecha, un monto y su moneda. Confirma que se muestran en el resumen.
5. Prueba el monto `0`: debe mostrarse como `0.00`, no como un campo vacío.
6. Cambia un dato y pulsa de nuevo **Revisar información** para actualizar la tabla.

El botón sólo muestra la captura enviada. No guarda registros en GitHub ni en
una base de datos. La captura no tiene almacenamiento permanente y puede
perderse al recargar o cerrar la pestaña.

## 6. Modifica el formulario después
