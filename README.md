# calculadora
Primera versión calculadora de Vencimientos e Intereses
# Primera pantalla: información de referencia

Esta versión permite capturar manualmente la información de un préstamo y
revisarla en una tabla. Todos los campos comienzan vacíos y son editables.
El botón **Revisar información** solicita únicamente el ID de cliente y el ID de
préstamo. El resto puede permanecer vacío en esta etapa.

## 1. Campos de esta primera etapa

En app.py, las filas entre la línea 13 y 47 se capturan los siguientes campos:

| Campo | Captura |
| --- | --- |
| ID de cliente | Texto para conservar ceros iniciales |
| ID de préstamo | Texto para conservar ceros iniciales |
| Nombre del cliente | Texto |
| Agencia | Texto para conservar el código tal como se escribe |
| Subaplicación | Texto para conservar el código tal como se escribe |
| Fecha de operación | Selector de fecha, inicialmente vacío |
| Monto operado | Número no negativo, mostrado con dos decimales |

Moneda permite identificar la unidad del monto operado.
Por ahora ambos son campos de texto libres.

Los periodos, tasas, spreads, saldo insoluto, amortización, intereses, etc. Se
incorporarán en etapas posteriores. Esta versión no calcula intereses,
consulta SIRAC, importa el Excel ni autocompleta datos.




