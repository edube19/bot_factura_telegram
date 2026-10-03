=====================================================================
 BOT DE FACTURAS (VALES DE SERVICIO) POR TELEGRAM
=====================================================================

QUE HACE
--------
Recibe por Telegram la FOTO de un "Vale de servicio" de taxi (papel con
datos escritos a mano), lee los datos con la IA de Google (Gemini), te los
muestra para que los confirmes con botones y, al confirmar, agrega una fila
en una hoja de Google Sheets.

Flujo de uso (lo que ve quien manda la foto):
  1. Enviar la foto del vale al bot.
  2. El bot responde "Leyendo el vale..." y luego muestra lo que leyo.
  3. Elegir con un boton el AREA del servicio (define el jefe).
  4. Elegir con un boton: "Solo IDA" o "IDA y VUELTA".
  5. Revisar el resumen y pulsar "Confirmar y guardar" (o "Cancelar").
  6. Se guarda la fila en Google Sheets. Nada se guarda sin confirmar.

Tambien acepta texto manual como respaldo (ver "FORMATO DE TEXTO").


REQUISITOS
----------
  - Python 3.10 o superior
  - Una cuenta de Telegram
  - Una cuenta de Google (para Google Sheets y la API de Gemini)


1) DESCARGAR E INSTALAR
-----------------------
  git clone https://github.com/edube19/bot_factura_telegram.git
  cd bot_factura_telegram
  pip install -r requirements.txt

(O descarga el ZIP desde GitHub: boton "Code" > "Download ZIP".)

Si tienes instalado un paquete llamado "telebot" (distinto de
"pyTelegramBotAPI") puede dar errores raros. En ese caso:
  pip uninstall -y telebot
  pip install -r requirements.txt


2) CREAR EL BOT DE TELEGRAM
---------------------------
  1. En Telegram abre @BotFather y escribe /newbot.
  2. Sigue los pasos y copia el TOKEN que te entrega.
  3. Si lo quieres usar en un grupo, agrega el bot al grupo.


3) PREPARAR GOOGLE SHEETS
-------------------------
  1. Crea una hoja de calculo de Google llamada exactamente: bot-factura
     El bot escribe en la PRIMERA hoja (pestana) del archivo.
  2. Pon estos encabezados en la fila 1 (10 columnas, en este orden):

     BOLETA | FECHA | ORIGEN | JEFE | INICIO | FINAL | DESTINO | TRAYECTO | PEAJE | TOTAL

  3. En https://console.cloud.google.com crea un proyecto y habilita
     "Google Sheets API" y "Google Drive API".
  4. En "IAM y administracion > Cuentas de servicio" crea una cuenta de
     servicio, entra a ella > pestana "Claves" > "Agregar clave" > JSON.
     Se descarga un archivo .json.
  5. Guarda ese archivo en la carpeta del proyecto como: bot-factura.json
  6. Abre la hoja "bot-factura" > "Compartir" > pega el correo de la cuenta
     de servicio (termina en ...iam.gserviceaccount.com) con permiso de
     EDITOR.


4) API KEY DE GEMINI (GRATIS)
-----------------------------
  1. Entra a https://aistudio.google.com/apikey con tu cuenta de Google.
  2. "Create API key" y copia la clave.
  El nivel gratuito tiene limite diario de peticiones; para pocas fotos al
  dia alcanza. Segun el plan gratuito, Google puede usar las imagenes para
  mejorar sus modelos: no subas vales con datos que no quieras compartir.


5) CONFIGURAR EL ARCHIVO .env
-----------------------------
  1. Copia ".env.example" y renombralo a ".env" (cuidado: en Windows el
     Bloc de notas puede guardarlo como ".env.txt"; debe llamarse solo ".env").
  2. Completa:
       TELEGRAM_BOT_TOKEN=...      (paso 2)
       GOOGLE_CREDENTIALS_FILE=bot-factura.json
       GEMINI_API_KEY=...          (paso 4)
       SIN_PROXY=1                 (solo para correr en tu PC)


6) EJECUTAR EN TU PC (PRUEBAS)
------------------------------
  python main.py

Debe mostrar: "Bot activo (modo polling) y escuchando...". Manda una foto
al bot en Telegram. Si cierras la ventana o apagas la PC, el bot deja de
responder (para dejarlo 24/7 ver la seccion 9).


7) FORMATO EN QUE SE LEE EL VALE (FOTO)
---------------------------------------
Foto recomendada: vale completo, bien iluminado, de frente, sin sombras ni
reflejos y con la letra legible. Si algun dato no se puede leer con
seguridad, el bot lo deja vacio (aparece como "?") en vez de inventarlo.

Datos que se extraen de la foto:

  CAMPO     DE DONDE SALE EN EL VALE          FORMATO QUE SE GUARDA
  --------  --------------------------------  --------------------------
  BOLETA    Numero impreso en rojo (N°)       Texto con ceros: 000686
  FECHA     Casilla "FECHA"                   DD/MM/AAAA (21/9/26 pasa a
                                              21/09/2026)
  ORIGEN    Primer "DE:" de la tabla RUTAS    Texto
  DESTINO   Lugar de llegada ("A:" o segundo  Texto; si se parece a un
            lugar escrito en RUTAS)           nombre de la tabla de
                                              distancias, se usa ese nombre
  INICIO    "HORA INICIO"                     HH:MM en 24 horas (11:00)
  FINAL     "FINAL"                           HH:MM en 24 horas (12:30)
  PEAJE     "PEAJE Y/O ESTAC."                Numero (vacio si no hay)
  TOTAL     "TOTAL TARIFA S/"                 Numero (34)

  (Tambien se lee el campo EMPRESA, solo para ayudar a encontrar la
   distancia cuando el destino no coincide; no se guarda en la hoja.)

Datos que NO salen de la foto (los define el bot):

  JEFE      Se elige el AREA con un boton y el bot escribe el jefe de esa
            area segun el diccionario JEFES de config.py.
  TRAYECTO  Distancia en km segun el destino (tabla DISTANCIAS de
            config.py). "Solo IDA" = km de la tabla. "IDA y VUELTA" = km x 2.
            Si el destino no esta en la tabla, TRAYECTO queda vacio.
            El bot busca primero con el DESTINO y, si no coincide, con la
            EMPRESA. La comparacion ignora mayusculas y tildes y tolera
            pequenos errores de lectura (ej. "Texttimax" = TEXTIMAX).

Columnas que se escriben en la hoja, en este orden:

  BOLETA, FECHA, ORIGEN, JEFE, INICIO, FINAL, DESTINO, TRAYECTO, PEAJE, TOTAL

Ejemplo (vale 000686): se guarda
  000686 | 21/09/2026 | Jesus Maria | JUAN | 11:00 | 12:30 | Textimax |
  12 | (vacio) | 34
(si se elige area Comercial y "Solo IDA").


8) FORMATO DE TEXTO (RESPALDO, SIN FOTO)
----------------------------------------
Se puede enviar un mensaje de texto con una linea por dato. Debe contener
las palabras "Boleta" y "Fecha". Ejemplo:

  Boleta 000686
  Fecha 21/09/2026
  Jesus Maria
  Jefe JUAN
  Inicio 11:00
  Final 12:30
  Textimax
  Ida y vuelta
  Peaje 0
  Total 34

Reglas:
  - Lineas que empiezan con: Boleta, Fecha, Jefe, Inicio, Final, Total, Peaje.
  - Una linea que contenga "ida" o "vuelta" se guarda como TRAYECTO.
    (Ojo: palabras como "Avenida" tambien contienen "ida".)
  - La primera linea que no sea ninguna de las anteriores es el ORIGEN y la
    siguiente es el DESTINO.
  - En este modo el bot guarda lo escrito tal cual, sin calcular nada.


9) DEJARLO FUNCIONANDO 24/7 SIN TU PC (PythonAnywhere GRATIS)
-------------------------------------------------------------
El plan gratuito de PythonAnywhere no permite procesos "siempre
encendidos", asi que se usa WEBHOOK (Telegram avisa al servidor cuando
llega un mensaje). Resumen:

  1. Crea una cuenta en https://www.pythonanywhere.com
  2. Sube los archivos del proyecto a una carpeta (pestana "Files"),
     incluidos .env y bot-factura.json (estos NO estan en GitHub).
     En ese .env NO pongas SIN_PROXY y agrega:
       WEBHOOK_URL_BASE=https://TU_USUARIO.pythonanywhere.com
  3. En una consola Bash:
       cd tu_carpeta
       mkvirtualenv miapp --python=python3.10
       pip install -r requirements.txt
  4. Pestana "Web" > "Add a new web app" > "Manual configuration" > mismo
     Python. En "Virtualenv" pon: /home/TU_USUARIO/.virtualenvs/miapp
  5. Edita el archivo WSGI de esa pagina y deja solo esto:
       import sys
       path = '/home/TU_USUARIO/tu_carpeta'
       if path not in sys.path:
           sys.path.insert(0, path)
       from webhook_app import app as application
  6. Boton "Reload". Al abrir https://TU_USUARIO.pythonanywhere.com debe
     decir "Bot de facturas activo."
  7. En la consola Bash, dentro de la carpeta:  python configurar_webhook.py
  8. Manda una foto al bot. Para volver a probar en tu PC con polling:
       python configurar_webhook.py quitar
     y luego  python main.py

Mas detalle en CONTEXTO.md. Las cuentas gratuitas de PythonAnywhere piden
renovar la web app cada 3 meses entrando a la pestana "Web".


10) PERSONALIZAR (config.py)
----------------------------
  JEFES           Area -> jefe. Cada clave es el texto del boton de area.
                  Cambia, agrega o quita areas aqui.
  DISTANCIAS      Destino -> km (solo ida). Agrega tus destinos aqui.
  IDA_Y_VUELTA    Multiplicador para viajes de ida y vuelta (por defecto 2).
  MODELO_GEMINI   Modelo que lee la foto. Si aparece un error 404 de que el
                  modelo ya no esta disponible, cambia el nombre por uno
                  vigente en https://ai.google.dev/gemini-api/docs/models
                  Los modelos "flash-lite" son mas baratos y con mas cuota
                  gratuita diaria, pero algo menos precisos.


11) PROBLEMAS FRECUENTES
------------------------
  - "Invalid JWT Signature": la clave bot-factura.json fue revocada o es de
    otra cuenta. Genera una clave nueva (paso 3) y comparte la hoja con ese
    correo como editor.
  - "404 NOT_FOUND ... model no longer available": cambia MODELO_GEMINI.
  - "503 UNAVAILABLE ... high demand": Gemini esta saturado; el bot
    reintenta 3 veces solo. Si persiste, reenvia la foto mas tarde o prueba
    un modelo "flash-lite".
  - El bot no responde: revisa que python main.py siga abierto (PC) o, en
    PythonAnywhere, el "Error log" de la pestana "Web".
  - No encuentra el .env: verifica que no se llame ".env.txt".
  - Los botones dicen "Este vale ya no esta disponible": el bot se reinicio
    entre la foto y la confirmacion. Reenvia la foto.


12) SEGURIDAD
-------------
  - NUNCA subas a GitHub: .env, bot-factura.json ni ningun token o clave.
    El .gitignore ya los excluye.
  - Si un token o clave se expuso, revocalo (token: /revoke en @BotFather;
    clave de Google: borrala en la consola y crea otra).
  - Cualquier persona con acceso al bot en Telegram puede mandarle fotos;
    usa un grupo privado o no compartas el nombre del bot.
=====================================================================
