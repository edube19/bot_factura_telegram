import os
import uuid

import gspread
import telebot
from dotenv import load_dotenv
from telebot import apihelper, types

from config import JEFES
from logica import armar_fila, resumen
from vision import extraer_vale

load_dotenv()

if not os.getenv("SIN_PROXY"):
    apihelper.proxy = {'https': 'http://proxy.server:3128'}

# Conf de google
try:
    gc = gspread.service_account(filename=os.getenv("GOOGLE_CREDENTIALS_FILE", "bot-factura.json"))
    sheet = gc.open("bot-factura").sheet1
except Exception as e:
    print(f"Error de configuración: {e}")

bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])

# Vales leídos que esperan que se elijan área/trayecto y se confirmen. Se pierden si el bot se reinicia.
pendientes = {}


def teclado_areas(clave):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(*[types.InlineKeyboardButton(a, callback_data=f"a|{clave}|{a}") for a in JEFES])
    kb.add(types.InlineKeyboardButton("Cancelar", callback_data=f"no|{clave}"))
    return kb


def teclado_trayecto(clave):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Solo IDA", callback_data=f"t|{clave}|0"),
        types.InlineKeyboardButton("IDA y VUELTA", callback_data=f"t|{clave}|1"),
    )
    kb.add(types.InlineKeyboardButton("Cancelar", callback_data=f"no|{clave}"))
    return kb


def teclado_confirmar(clave):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Confirmar y guardar", callback_data=f"ok|{clave}"),
        types.InlineKeyboardButton("Cancelar", callback_data=f"no|{clave}"),
    )
    return kb


@bot.message_handler(content_types=['photo'])
def procesar_foto(message):
    aviso = bot.reply_to(message, "Leyendo el vale...")
    try:
        info = bot.get_file(message.photo[-1].file_id)
        imagen = bot.download_file(info.file_path)
        datos = extraer_vale(imagen)
    except Exception as e:
        bot.edit_message_text(f"No pude leer la foto: {e}", aviso.chat.id, aviso.message_id)
        return

    clave = uuid.uuid4().hex[:8]
    pendientes[clave] = {"datos": datos, "area": None, "ida_y_vuelta": None}
    bot.edit_message_text(
        f"Esto leí:\n\n{resumen(datos)}\n\n¿De qué área es el servicio?",
        aviso.chat.id, aviso.message_id, reply_markup=teclado_areas(clave),
    )


@bot.callback_query_handler(func=lambda call: True)
def procesar_boton(call):
    accion, clave, *resto = call.data.split("|")
    chat_id, msg_id = call.message.chat.id, call.message.message_id
    pendiente = pendientes.get(clave)

    if pendiente is None:
        bot.answer_callback_query(call.id, "Este vale ya no está disponible. Envía la foto otra vez.")
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=None)
        return

    datos = pendiente["datos"]

    if accion == "no":
        del pendientes[clave]
        bot.edit_message_text("Cancelado. No se guardó nada.", chat_id, msg_id)
    elif accion == "a":
        pendiente["area"] = resto[0]
        bot.edit_message_text(
            f"{resumen(datos, pendiente['area'])}\n\n¿El viaje fue solo de ida o de ida y vuelta?",
            chat_id, msg_id, reply_markup=teclado_trayecto(clave),
        )
    elif accion == "t":
        pendiente["ida_y_vuelta"] = resto[0] == "1"
        bot.edit_message_text(
            f"{resumen(datos, pendiente['area'], pendiente['ida_y_vuelta'])}\n\n¿Guardo esto en el Excel?",
            chat_id, msg_id, reply_markup=teclado_confirmar(clave),
        )
    elif accion == "ok":
        fila = armar_fila(datos, pendiente["area"], pendiente["ida_y_vuelta"])
        try:
            sheet.append_row(fila)
        except Exception as e:
            bot.answer_callback_query(call.id, "Falló la conexión con Google. Intenta de nuevo.")
            bot.send_message(chat_id, f"❌ Hubo un problema de conexión con Google: {e}")
            return
        del pendientes[clave]
        bot.edit_message_text(
            f"✅ Boleta {fila[0]} guardada en el Excel.\n\n{resumen(datos, pendiente['area'], pendiente['ida_y_vuelta'])}",
            chat_id, msg_id,
        )
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: True)
def procesar_mensaje(message):
    texto = message.text.strip()
    texto_lower = texto.lower()

    if "boleta" not in texto_lower or "fecha" not in texto_lower:
        return

    lineas = texto.split('\n')

    boleta = ""
    fecha = ""
    origen = ""
    jefe = ""
    inicio = ""
    final = ""
    destino = ""
    trayecto = ""
    total = ""
    peaje = ""

    for linea in lineas:
        lin = linea.strip()
        if not lin:
            continue  # ignorar saltos de línea

        lin_lower = lin.lower()

        if lin_lower.startswith("boleta"):
            boleta = lin[6:].strip()
        elif lin_lower.startswith("fecha"):
            fecha = lin[5:].strip()
        elif lin_lower.startswith("jefe"):
            jefe = lin[4:].strip()
        elif lin_lower.startswith("inicio"):
            inicio = lin[6:].strip()
        elif lin_lower.startswith("final"):
            final = lin[5:].strip()
        elif lin_lower.startswith("total"):
            total = lin[5:].strip()
        elif lin_lower.startswith("peaje"):
            peaje = lin[5:].strip()
        elif "ida" in lin_lower or "vuelta" in lin_lower:
            trayecto = lin
        else:
            if not origen:
                origen = lin
            else:
                destino = lin

    if boleta and fecha:
        # Orden exacto de las columnas del Excel (10 en total)
        fila_para_excel = [
            boleta, fecha, origen, jefe, inicio, final, destino, trayecto, peaje, total
        ]

        try:
            sheet.append_row(fila_para_excel)
            usuario = message.from_user.first_name
            bot.reply_to(message, f"✅ ¡Listo {usuario}! La Boleta {boleta} se guardó correctamente en el Excel.")
        except Exception as e:
            bot.reply_to(message, f"❌ Hubo un problema de conexión con Google: {e}")
    else:
        bot.reply_to(message, "⚠️ Detecté que es un registro, pero no pude leer bien la 'Boleta' o la 'Fecha'. Revisa cómo está escrito.")


print("Bot activo y escuchando en el grupo 'Control factura'...")
bot.polling()
