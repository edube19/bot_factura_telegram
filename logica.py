import difflib
import unicodedata

from config import DISTANCIAS, IDA, IDA_Y_VUELTA, JEFES


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.upper().split())


_CLAVES = {normalizar(k): k for k in DISTANCIAS}


def buscar_distancia(*candidatos):
    """Devuelve (nombre_en_tabla, km) usando el primer candidato que coincida, o (None, None)."""
    for candidato in candidatos:
        texto = normalizar(candidato)
        if not texto:
            continue
        if texto in _CLAVES:
            clave = _CLAVES[texto]
            return clave, DISTANCIAS[clave]
        for norm, clave in _CLAVES.items():
            if norm in texto:
                return clave, DISTANCIAS[clave]
        cercanos = difflib.get_close_matches(texto, _CLAVES, n=1, cutoff=0.75)
        if cercanos:
            clave = _CLAVES[cercanos[0]]
            return clave, DISTANCIAS[clave]
    return None, None


def calcular_trayecto(km, ida_y_vuelta):
    if km is None:
        return ""
    total = round(km * (IDA_Y_VUELTA if ida_y_vuelta else IDA), 2)
    return int(total) if total == int(total) else total


def armar_fila(datos, area, ida_y_vuelta):
    """Orden de columnas del Excel: boleta, fecha, origen, jefe, inicio, final, destino, trayecto, peaje, total."""
    _, km = buscar_distancia(datos.get("destino"), datos.get("empresa"))
    return [
        datos.get("boleta") or "",
        datos.get("fecha") or "",
        datos.get("origen") or "",
        JEFES.get(area, ""),
        datos.get("inicio") or "",
        datos.get("final") or "",
        datos.get("destino") or "",
        calcular_trayecto(km, ida_y_vuelta),
        datos.get("peaje") if datos.get("peaje") is not None else "",
        datos.get("total") if datos.get("total") is not None else "",
    ]


def resumen(datos, area=None, ida_y_vuelta=None):
    clave, km = buscar_distancia(datos.get("destino"), datos.get("empresa"))
    lineas = [
        f"Boleta: {datos.get('boleta') or '?'}",
        f"Fecha: {datos.get('fecha') or '?'}",
        f"Origen: {datos.get('origen') or '?'}",
        f"Destino: {datos.get('destino') or '?'}",
        f"Inicio: {datos.get('inicio') or '?'}   Final: {datos.get('final') or '?'}",
        f"Peaje: {datos.get('peaje') if datos.get('peaje') is not None else '-'}",
        f"Total: {datos.get('total') if datos.get('total') is not None else '?'}",
    ]
    if area:
        lineas.append(f"Área: {area}  (jefe: {JEFES.get(area, '?')})")
    if ida_y_vuelta is not None:
        tipo = "IDA y VUELTA" if ida_y_vuelta else "solo IDA"
        dist = calcular_trayecto(km, ida_y_vuelta)
        detalle = f"{dist} km ({clave})" if km is not None else "sin distancia registrada para este destino"
        lineas.append(f"Trayecto: {tipo} - {detalle}")
    return "\n".join(lineas)
