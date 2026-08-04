import telebot
from telebot import apihelper  # <--- NUEVO
import gspread

apihelper.proxy = {'https': 'http://proxy.server:3128'}  # <--- NUEVO

#Conf de google
try:
    gc = gspread.service_account(filename='bot-factura.json')
    sheet = gc.open("bot-factura").sheet1
except Exception as e:
    print(f"Error de configuración: {e}")

bot = telebot.TeleBot("8649437681:AAENI_pYM6OsYdOQD_KbZD9Thu5P_YojZtA")

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
            continue #ignorar saltos de línea
            
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
        # Aquí definimos el orden exacto de las columnas de tu Excel (10 en total)
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