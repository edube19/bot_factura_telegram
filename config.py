"""Datos editables del bot. Cambia aquí jefes, áreas y distancias."""

# Área -> jefe del área. Si cambia el personal, se edita solo este diccionario.
# La clave es el texto del botón en Telegram; el valor es lo que se escribe en la columna JEFE.
JEFES = {
    "Comercial": "JUAN",
    "Logística": "ANDRES",
    "Lavandería": "POR_DEFINIR",
}

# Destino -> distancia (km, solo ida). Viene de la fórmula IFS del Excel.
DISTANCIAS = {
    "ATE": 1.2,
    "ESTRADA": 0.6,
    "SAN JACINTO": 0.8,
    "CERTINTEX": 12,
    "PRIME": 16,
    "THIMBLE": 28,
    "TEXTIMAX": 12,
    "AYALA": 22,
    "MARTHA": 22,
    "DESATEX": 14,
    "ARTEXTIL": 24,
    "TINTOTEX": 12,
    "GAMARRITA": 6,
    "TAYLOY": 4,
    "JAIME CHAVEZ": 22,
    "CYF PRINT": 24,
    "DICAZA": 28,
    "GAMARRA": 12,
    "DIGITAL INK": 12,
    "LANDEO": 10,
    "MENDEZ": 30,
    "LUTEX": 11,
}

# Multiplicador de la distancia según el tipo de viaje.
IDA = 1
IDA_Y_VUELTA = 2

# Modelo de Gemini para leer la foto.
MODELO_GEMINI = "gemini-2.5-flash"
