"""
Geolocalización, cálculo de tiempo estimado de llegada (ETA) y mapa para el
seguimiento del técnico camino al domicilio del cliente.

Fase 1 (no en vivo-vivo): el técnico comparte su ubicación con un botón cada
vez que quiera actualizarla (no es tracking continuo automático); el cliente
ve un mapa con su domicilio, la última ubicación conocida del técnico y un
tiempo estimado de llegada calculado con OpenRouteService (gratis hasta 2,000
rutas/día — de sobra para la fase beta).

Streamlit no tiene una API nativa para pedir la ubicación del navegador, así
que usamos un truco simple y confiable: un botón HTML que llama a
`navigator.geolocation`, mete lat/lng como query params en la URL de la app
y recarga la página — del lado de Python simplemente leemos esos query
params con `leer_ubicacion_de_url`.
"""

import requests
import streamlit as st
import streamlit.components.v1 as components


def boton_ubicacion(etiqueta: str, key: str, ayuda: str = ""):
    """Botón que pide la ubicación del navegador y la manda a la app vía
    query params (?geo_key=<key>&geo_lat=..&geo_lng=..). Úsalo junto con
    leer_ubicacion_de_url(key) para recogerla."""
    if ayuda:
        st.caption(ayuda)
    html = f"""
    <div>
      <button id="btn_{key}" onclick="homyfixObtenerUbicacion_{key}()" style="
          background-color:#FF9900;color:#FFFFFF;border:none;border-radius:8px;
          padding:0.55rem 1rem;font-weight:700;font-size:0.95rem;width:100%;
          cursor:pointer;font-family:inherit;">
        {etiqueta}
      </button>
      <p id="estado_{key}" style="color:#8a94a6;font-size:0.8rem;margin-top:4px;"></p>
    </div>
    <script>
    function homyfixObtenerUbicacion_{key}() {{
        var estado = document.getElementById("estado_{key}");
        estado.innerText = "Obteniendo tu ubicación...";
        if (!navigator.geolocation) {{
            estado.innerText = "Tu navegador no soporta geolocalización.";
            return;
        }}
        navigator.geolocation.getCurrentPosition(function(pos) {{
            var lat = pos.coords.latitude;
            var lng = pos.coords.longitude;
            var url = new URL(window.parent.location.href);
            url.searchParams.set("geo_key", "{key}");
            url.searchParams.set("geo_lat", lat);
            url.searchParams.set("geo_lng", lng);
            window.parent.location.href = url.toString();
        }}, function(err) {{
            estado.innerText = "No se pudo obtener tu ubicación: " + err.message;
        }}, {{enableHighAccuracy: true, timeout: 10000}});
    }}
    </script>
    """
    components.html(html, height=80)


def leer_ubicacion_de_url(key: str):
    """Si la URL trae ?geo_key=<key>&geo_lat=..&geo_lng=.. regresa (lat, lng)
    como floats y limpia los query params. Si no, regresa None."""
    qp = st.query_params
    if qp.get("geo_key") == key and "geo_lat" in qp and "geo_lng" in qp:
        try:
            lat = float(qp["geo_lat"])
            lng = float(qp["geo_lng"])
        except (TypeError, ValueError):
            st.query_params.clear()
            return None
        st.query_params.clear()
        return (lat, lng)
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
