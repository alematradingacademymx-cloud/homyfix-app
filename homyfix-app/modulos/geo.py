"""
Geolocalización, cálculo de tiempo estimado de llegada (ETA) y mapa para el
seguimiento del técnico camino al domicilio del cliente.

Fase 1 (no en vivo-vivo): el técnico comparte su ubicación con un botón cada
vez que quiera actualizarla (no es tracking continuo automático); el cliente
ve un mapa con su domicilio, la última ubicación conocida del técnico y un
tiempo estimado de llegada calculado con OpenRouteService (gratis hasta 2,000
rutas/día — de sobra para la fase beta).

NOTA IMPORTANTE (por qué usamos `streamlit-geolocation` y no un botón HTML
casero): la primera versión de esto usaba un botón HTML propio (via
`st.components.v1.html`) que llamaba a `navigator.geolocation` y luego hacía
`window.parent.location.href = ...` para "avisarle" a la app con query
params. Eso se quedaba congelado en "Obteniendo tu ubicación..." para
siempre: Streamlit mete ese HTML en un iframe con sandbox, y ese sandbox no
deja que el contenido de adentro navegue/redirija la página de arriba — el
navegador sí pedía permiso y sí obtenía la ubicación, pero la forma de
regresarla a Python quedaba bloqueada en silencio. `streamlit-geolocation`
es un componente de verdad de Streamlit (usa el mecanismo oficial para que
JS le regrese un valor a Python) y no depende de navegar la página, así que
no tiene ese problema.
"""

import requests
import streamlit as st


def obtener_ubicacion_navegador():
    """Muestra el botón de geolocalización del navegador (componente
    streamlit-geolocation, ver requirements.txt) y regresa (lat, lng) en
    cuanto el usuario la comparte, o None si todavía no lo ha hecho o si el
    paquete no está instalado.

    IMPORTANTE: este componente solo se puede mostrar UNA vez por corrida de
    la página (su key interno viene fijo dentro del paquete) — si necesitas
    pedir ubicación en más de un lugar de la misma pantalla (p. ej. el
    técnico con varios trabajos activos), pide primero con un botón normal
    cuál ubicación se va a compartir y solo entonces llama a esta función
    una sola vez, fuera de cualquier `for`."""
    try:
        from streamlit_geolocation import streamlit_geolocation
    except ImportError:
        st.error(
            "Falta instalar `streamlit-geolocation` (revisa requirements.txt) "
            "para poder compartir tu ubicación."
        )
        return None
    ubicacion = streamlit_geolocation()
    if ubicacion and ubicacion.get("latitude") is not None and ubicacion.get("longitude") is not None:
        return (ubicacion["latitude"], ubicacion["longitude"])
    return None


def _ors_api_key():
    try:
        return st.secrets["openrouteservice"]["api_key"]
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def calcular_eta(origen_lat, origen_lng, destino_lat, destino_lng):
    """Calcula tiempo/distancia real por calles con OpenRouteService (gratis).
    Regresa None si no hay API key configurada o si falla la petición — en
    ese caso el resto de la app debe caer en la distancia en línea recta."""
    api_key = _ors_api_key()
    if not api_key:
        return None
    try:
        url = "https://api.heigit.org/openrouteservice/v2/directions/driving-car"
        headers = {"Authorization": api_key}
        params = {
            "start": f"{origen_lng},{origen_lat}",
            "end": f"{destino_lng},{destino_lat}",
        }
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        feature = data["features"][0]
        resumen = feature["properties"]["summary"]
        coords = feature["geometry"]["coordinates"]  # [lng, lat]
        ruta = [[c[1], c[0]] for c in coords]
        return {
            "duracion_min": resumen["duration"] / 60,
            "distancia_km": resumen["distance"] / 1000,
            "ruta": ruta,
        }
    except Exception:
        return None


def mostrar_mapa(tecnico_lat, tecnico_lng, cliente_lat, cliente_lng, ruta=None, altura=340, key=None):
    """Mapa con el domicilio del cliente y la última ubicación del técnico,
    usando OpenStreetMap (gratis, sin API key)."""
    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        st.info("Falta instalar `folium` y `streamlit-folium` para ver el mapa (revisa requirements.txt).")
        return

    centro = [(tecnico_lat + cliente_lat) / 2, (tecnico_lng + cliente_lng) / 2]
    m = folium.Map(location=centro, zoom_start=13, tiles="OpenStreetMap")

    folium.Marker(
        [tecnico_lat, tecnico_lng], tooltip="Técnico",
        icon=folium.Icon(color="orange", icon="wrench", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        [cliente_lat, cliente_lng], tooltip="Tu domicilio",
        icon=folium.Icon(color="blue", icon="home", prefix="fa"),
    ).add_to(m)

    if ruta:
        folium.PolyLine(ruta, color="#FF9900", weight=5, opacity=0.85).add_to(m)
    else:
        folium.PolyLine(
            [[tecnico_lat, tecnico_lng], [cliente_lat, cliente_lng]],
            color="#13499C", weight=3, opacity=0.7, dash_array="6,10",
        ).add_to(m)

    bounds = [[tecnico_lat, tecnico_lng], [cliente_lat, cliente_lng]]
    m.fit_bounds(bounds, padding=(30, 30))

    st_folium(m, width=None, height=altura, returned_objects=[], key=key or "mapa_homyfix")
