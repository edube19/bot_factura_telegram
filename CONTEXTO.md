# Bot de facturas por Telegram

## Objetivo
Mi padre es taxista/conductor (Movil Servis "Santa Isabel" S.A.) y llena "vales de servicio" a mano.
Hoy envía los datos por Telegram como texto y el bot los guarda en un Google Sheet ("bot-factura").
Se quiere que **tome una foto del vale y el bot extraiga los datos solo**, para que el Excel se llene
sin que él tenga que escribir nada.

## Estado actual
- `main.py`: bot con `pyTelegramBotAPI` (telebot) + `gspread`, polling.
- Solo procesa mensajes de texto con las líneas `Boleta`, `Fecha`, `Jefe`, `Inicio`, `Final`, `Total`, `Peaje`, origen/destino y trayecto (ida/vuelta).
- Guarda una fila con 10 columnas: boleta, fecha, origen, jefe, inicio, final, destino, trayecto, peaje, total.
- Usa `bot-factura.json` (cuenta de servicio de Google) y un proxy (`proxy.server:3128`, típico de PythonAnywhere).

## Documento de ejemplo (vale de servicio)
Papel amarillo con campos impresos y datos escritos a mano:
- N° de vale (impreso, rojo): `000686`
- Fecha (manuscrita): `21 / 9 / 26`
- Empresa (manuscrita), Pasajero (manuscrito)
- Hora inicio / Final (manuscritas)
- Rutas: varias líneas "DE / A" (manuscritas) con Importe
- Tiempo de espera, Peaje y/o estacionamiento, Total tarifa S/ (manuscritos)

Ojo: la letra es difícil (cursiva, abreviaturas, números tipo "34="), así que la extracción **no será 100 % fiable**.

## Mapeo vale -> columnas del Excel
Campos que SÍ se leen de la foto (los demás del vale se ignoran):

| Columna Excel | Campo del vale |
|---|---|
| boleta | N° del vale |
| fecha | Fecha |
| origen | Rutas, primer "DE" |
| inicio / final | Hora inicio / Final |
| destino | Rutas, "A" |
| trayecto | Ida/vuelta (no aparece en el vale; por definir) |
| peaje | Peaje y/o estac. |
| total | Total tarifa S/ |

Campo que NO viene de la foto:
- `jefe`: es el jefe del área (comercial, logística, lavandería, etc.) y es fijo por área.
  Se resuelve con un diccionario editable en el código/config, p. ej. `JEFES = {"comercial": "JUAN", "logistica": "ANDRES", ...}`,
  para cambiarlo fácil si cambia el personal.
- Falta definir cómo se determina el área (ver pendientes).

Empresa y Pasajero del vale no se guardan.

## Plan de adaptación
1. Agregar un handler `content_types=['photo']` que descargue la foto de Telegram.
2. Enviar la imagen a un modelo de visión con un prompt que devuelva JSON estricto con los campos.
3. Responder en el chat con lo leído y pedir **confirmación** (botones Confirmar / Corregir) antes de escribir en el Sheet.
4. Al confirmar, `sheet.append_row(...)` con el mismo orden de columnas actual.
5. Mantener el flujo de texto actual como respaldo.
6. Mover el token y credenciales a variables de entorno (`.env`).

## Decisiones tomadas
- Modelo de visión: Gemini (`gemini-2.5-flash`, plan gratuito) vía `google-genai`, ver `vision.py`.
- Flujo por foto: foto -> lectura -> botón de área (define `jefe`) -> botón Solo IDA / IDA y VUELTA -> Confirmar -> se guarda.
- `trayecto` = distancia en km según el destino (tabla `DISTANCIAS` en `config.py`, viene de la fórmula IFS del Excel).
  IDA = km de la tabla, IDA y VUELTA = km x 2 (supuesto, confirmar).
- `jefe` sale del diccionario `JEFES` en `config.py`.
- Archivos: `config.py` (datos editables), `logica.py` (fila, distancias), `vision.py` (Gemini), `main.py` (bot).
- Variables en `.env`: `TELEGRAM_BOT_TOKEN`, `GOOGLE_CREDENTIALS_FILE`, `GEMINI_API_KEY`. `SIN_PROXY=1` para correr en local.

## Pendientes / decisiones abiertas
- Confirmar qué modelo/herramienta de visión usar (ver conversación: Gemini API gratis vs modelo local).
- Confirmar si IDA y VUELTA duplica la distancia y si la clave de la tabla de distancias es el destino o el campo Empresa
  (el código prueba primero el destino y luego la empresa).
- Completar el jefe de Lavandería y las demás áreas en `config.py`.
- El bot corre en PythonAnywhere: verificar que desde ahí se puede llegar a la API de Gemini
  (la cuenta gratuita restringe las salidas a una lista de sitios y requiere proxy) y que el bot puede mantenerse activo.
- Revocar y regenerar el token del bot (estaba escrito directamente en `main.py`).
