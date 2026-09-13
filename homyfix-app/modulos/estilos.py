"""Estilos compartidos de la app (siguiendo el mismo patrón del portal educativo)."""

import base64
from pathlib import Path

import streamlit as st

_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.png"


def _logo_base64() -> str:
    if not _LOGO_PATH.exists():
        return ""
    return base64.b64encode(_LOGO_PATH.read_bytes()).decode("utf-8")

# Paleta de marca Homyfix
AZUL_PRIMARIO = "#13499C"   # azul del logo — títulos, marca, sidebar
AZUL_SECUNDARIO = "#2A3C96"  # azul de apoyo — degradados, hover
NARANJA = "#FF9900"          # acento del logo (llave) — botones de acción
VERDE = "#B9E25E"            # estados positivos / aprobado
MORADO_OSCURO = "#751083"    # panel admin / socio — distinción de rol
MORADO_CLARO = "#601C88"     # apoyo del morado — hover, degradados

CSS = f"""
<style>
header[data-testid="stHeader"] {{background: transparent;}}
#MainMenu, footer, .stAppDeployButton {{visibility: hidden;}}

.main-title {{
    font-size: 1.8rem;
    font-weight: 800;
    color: {AZUL_PRIMARIO};
    margin-bottom: 0;
}}
.sub-title {{
    color: #5B6B82;
    margin-top: 0;
}}
.homyfix-lema {{
    text-align: center;
    font-size: 1.3rem;
    font-weight: 800;
    color: {NARANJA};
    margin: 0.4rem 0 1.2rem 0;
}}
.app-card {{
    background: #F5F6FA;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    border: 1px solid #E7EAF0;
}}
.badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}}
.badge-pendiente {{background:#FFF1E0 !important; color:#B5610A !important;}}
.badge-asignado {{background:#E4EEFF !important; color:{AZUL_PRIMARIO} !important;}}
.badge-visita {{background:#EDE4FF !important; color:{MORADO_CLARO} !important;}}
.badge-cotizado {{background:#FFF3D6 !important; color:#8A5A00 !important;}}
.badge-puja {{background:#FFE4F0 !important; color:#BE185D !important;}}
.badge-aceptado {{background:{VERDE} !important; color:#1F3D00 !important;}}
.badge-encamino {{background:#FFE9C7 !important; color:#8A5A00 !important;}}
.badge-cerca {{background:#FFD9A0 !important; color:#7A3E00 !important;}}
.badge-encurso {{background:#F1E4FF !important; color:{MORADO_OSCURO} !important;}}
.badge-completado {{background:{VERDE} !important; color:#1F3D00 !important;}}
.badge-calificado {{background:#EAF7EA !important; color:#1C7C33 !important;}}
.badge-cancelado {{background:#FFE4E4 !important; color:#B91C1C !important;}}

/* Logo Homyfix */
.homyfix-logo-login {{
    display: flex;
    justify-content: center;
    margin-bottom: 0.3rem;
}}
.homyfix-logo-sidebar {{
    display: flex;
    justify-content: center;
    padding: 0.4rem 0 0.8rem 0;
}}

/* Botones de acción: naranja de marca, letras blancas */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
    background-color: {NARANJA} !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
    background-color: #E68A00 !important;
    color: #FFFFFF !important;
}}
.stButton > button:disabled, .stFormSubmitButton > button:disabled {{
    background-color: #FFD699 !important;
    color: #7A5200 !important;
}}

/* Botones "primary" (usados para marcar una opción como seleccionada, p. ej.
   la calificación o las confirmaciones de cobro/limpieza) en azul, para que
   se distingan claramente de los botones normales (naranja). */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {{
    background-color: {AZUL_PRIMARIO} !important;
    color: #FFFFFF !important;
}}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {{
    background-color: {AZUL_SECUNDARIO} !important;
    color: #FFFFFF !important;
}}

/* Botones de login (Entrar / Ya tengo un código) en el azul del logo, no naranja */
.st-key-btn_entrar button, .st-key-btn_codigo_acceso button {{
    background-color: {AZUL_PRIMARIO} !important;
    color: #FFFFFF !important;
}}
.st-key-btn_entrar button:hover, .st-key-btn_codigo_acceso button:hover {{
    background-color: {AZUL_SECUNDARIO} !important;
    color: #FFFFFF !important;
}}

/* Cajas / paneles con borde: relleno azul, letras blancas, para que resalten */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {AZUL_SECUNDARIO} !important;
    border: 1px solid {AZUL_PRIMARIO} !important;
    border-radius: 14px !important;
    padding: 0.3rem 0.2rem !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] span:not(.badge),
[data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stVerticalBlockBorderWrapper"] h1,
[data-testid="stVerticalBlockBorderWrapper"] h2,
[data-testid="stVerticalBlockBorderWrapper"] h3,
[data-testid="stVerticalBlockBorderWrapper"] h4,
[data-testid="stVerticalBlockBorderWrapper"] li,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] {{
    color: #FFFFFF !important;
}}
[data-testid="stExpander"] {{
    background: {AZUL_SECUNDARIO} !important;
    border: 1px solid {AZUL_PRIMARIO} !important;
    border-radius: 14px !important;
}}
[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] li,
[data-testid="stExpander"] summary {{
    color: #FFFFFF !important;
}}

/* Campos de texto: relleno blanco, contorno naranja, letras negras */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stDateInput input, .stTimeInput input,
[data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    color: #0B1F3A !important;
    border: 2px solid {NARANJA} !important;
    border-radius: 8px !important;
}}
[data-baseweb="select"] span, [data-baseweb="select"] div {{
    color: #0B1F3A !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background-color: #FFFFFF !important;
    border: 2px dashed {NARANJA} !important;
    border-radius: 8px !important;
}}

/* Línea de tiempo del servicio (paso a paso, sin mapa) */
.homyfix-timeline {{
    margin: 0.6rem 0 0.4rem 0;
    padding: 0;
}}
.homyfix-timeline .paso {{
    position: relative;
    padding: 0 0 1.3rem 2.1rem;
}}
.homyfix-timeline .paso:last-child {{
    padding-bottom: 0;
}}
.homyfix-timeline .paso::before {{
    /* la línea vertical que conecta los pasos */
    content: "";
    position: absolute;
    left: 0.55rem;
    top: 1.5rem;
    bottom: -0.2rem;
    width: 2px;
    background: #DCE2ED;
}}
.homyfix-timeline .paso:last-child::before {{
    display: none;
}}
.homyfix-timeline .paso.hecho::before {{
    background: {NARANJA};
}}
.homyfix-timeline .circulo {{
    position: absolute;
    left: 0;
    top: 0.15rem;
    width: 1.2rem;
    height: 1.2rem;
    border-radius: 50%;
    background: #DCE2ED;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    color: #FFFFFF;
    font-weight: 700;
}}
.homyfix-timeline .paso.hecho .circulo {{
    background: {NARANJA};
}}
.homyfix-timeline .paso.actual .circulo {{
    background: {AZUL_PRIMARIO};
    box-shadow: 0 0 0 4px #DCE7FA;
}}
.homyfix-timeline .texto {{
    font-size: 0.92rem;
    color: #8B93A3;
    line-height: 1.2rem;
}}
.homyfix-timeline .paso.hecho .texto {{
    color: #3A4256;
}}
.homyfix-timeline .paso.actual .texto {{
    color: {AZUL_PRIMARIO};
    font-weight: 700;
}}
</style>
"""


def aplicar_estilos():
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, subtitulo: str = ""):
    st.markdown(f"<p class='main-title'>{titulo}</p>", unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f"<p class='sub-title'>{subtitulo}</p>", unsafe_allow_html=True)


def logo(ancho: int = 160, centrado: bool = True):
    """Muestra el logo de Homyfix. Usar en el login (grande, centrado) y en el sidebar (chico)."""
    b64 = _logo_base64()
    if not b64:
        return
    if centrado:
        st.markdown(
            f"<div style='text-align:center;'>"
            f"<img src='data:image/png;base64,{b64}' width='{ancho}'/>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='homyfix-logo-sidebar'>"
            f"<img src='data:image/png;base64,{b64}' width='{ancho}'/>"
            f"</div>",
            unsafe_allow_html=True,
        )


def lema(texto: str = "Tu hogar en manos seguras"):
    """Leyenda naranja, grande, con la misma tipografía del título — para debajo del logo."""
    st.markdown(f"<p class='homyfix-lema'>{texto}</p>", unsafe_allow_html=True)


_BADGE_CLASE = {
    "Pendiente": "badge-pendiente",
    "Asignado": "badge-asignado",
    "En Visita": "badge-visita",
    "Cotizado": "badge-cotizado",
    "En Puja": "badge-puja",
    "Aceptado": "badge-aceptado",
    "En Camino": "badge-encamino",
    "Cerca": "badge-cerca",
    "En curso": "badge-encurso",
    "Completado": "badge-completado",
    "Calificado": "badge-calificado",
    "Cancelado": "badge-cancelado",
}


def badge_estatus(estatus: str) -> str:
    clase = _BADGE_CLASE.get(estatus, "badge-pendiente")
    return f"<span class='badge {clase}'>{estatus}</span>"


# Pasos del "viaje" del servicio que se le muestran al cliente como línea de
# tiempo, en vez de un mapa — el técnico avanza estos pasos a mano desde su
# panel (ver portal_tecnico.py). "Calificado" se trata como el mismo punto
# final que "Completado" (la calificación es un paso aparte, no una etapa
# más del viaje).
PASOS_SOLICITUD = [
    ("Pendiente", "Buscando un técnico disponible"),
    ("Asignado", "Técnico asignado, preparando tu cotización"),
    ("Cotizado", "Cotización enviada, esperando tu respuesta"),
    ("Aceptado", "Cotización aceptada, esperando que el técnico inicie su viaje"),
    ("En Camino", "El técnico ha comenzado su trayecto"),
    ("Cerca", "El técnico está cerca (a menos de 100 m)"),
    ("En curso", "El técnico ha llegado y está trabajando"),
    ("Completado", "Servicio concluido"),
]
_INDICE_PASO = {estatus: i for i, (estatus, _) in enumerate(PASOS_SOLICITUD)}


def linea_tiempo(estatus_actual: str):
    """Dibuja la línea de tiempo del servicio para el estatus dado. No dibuja
    nada para estatus fuera del flujo lineal (p. ej. 'En Puja' o
    'Cancelado') — esos casos ya se explican con un mensaje aparte."""
    indice_actual = _INDICE_PASO.get("Completado" if estatus_actual == "Calificado" else estatus_actual)
    if indice_actual is None:
        return
    filas = []
    for i, (_, etiqueta) in enumerate(PASOS_SOLICITUD):
        if i < indice_actual:
            clase, icono = "hecho", "✓"
        elif i == indice_actual:
            clase, icono = "actual", ""
        else:
            clase, icono = "pendiente", ""
        filas.append(
            f"<div class='paso {clase}'>"
            f"<div class='circulo'>{icono}</div>"
            f"<div class='texto'>{etiqueta}</div>"
            f"</div>"
        )
    st.markdown(f"<div class='homyfix-timeline'>{''.join(filas)}</div>", unsafe_allow_html=True)
