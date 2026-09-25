import os
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel

from config import DISTANCIAS, MODELO_GEMINI


class ValeLeido(BaseModel):
    boleta: Optional[str] = None
    fecha: Optional[str] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    empresa: Optional[str] = None
    inicio: Optional[str] = None
    final: Optional[str] = None
    peaje: Optional[float] = None
    total: Optional[float] = None


PROMPT = f"""Esta es la foto de un "Vale de servicio" de taxi de Perú, con campos impresos y datos escritos a mano.
Extrae solo estos datos:
- boleta: el número del vale (impreso en rojo, junto a "Nº"), con sus ceros, por ejemplo "000686".
- fecha: la fecha del campo FECHA en formato DD/MM/AAAA (el año puede venir con 2 dígitos: 26 = 2026).
- empresa: el texto del campo EMPRESA.
- origen: el primer "DE:" de la tabla RUTAS.
- destino: el lugar de llegada de la ruta (campo "A:" o el segundo lugar escrito en RUTAS).
- inicio: HORA INICIO en formato 24 horas HH:MM.
- final: FINAL en formato 24 horas HH:MM.
- peaje: importe de "PEAJE Y/O ESTAC." como número, o null si está vacío.
- total: "TOTAL TARIFA S/" como número.

Destinos/empresas conocidos: {", ".join(DISTANCIAS)}.
Si el destino o la empresa se parece a uno de esos, escribe exactamente ese nombre.
Si un dato no se puede leer con seguridad, devuelve null; no inventes valores."""


def _cliente():
    proxy = None if os.getenv("SIN_PROXY") else "http://proxy.server:3128"
    opciones = types.HttpOptions(client_args={"proxy": proxy}) if proxy else None
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=opciones)


def extraer_vale(imagen_bytes):
    respuesta = _cliente().models.generate_content(
        model=MODELO_GEMINI,
        contents=[types.Part.from_bytes(data=imagen_bytes, mime_type="image/jpeg"), PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ValeLeido,
            temperature=0,
        ),
    )
    return respuesta.parsed.model_dump()
