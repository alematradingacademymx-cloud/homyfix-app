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
    "En curso": "badge-encurso",
    "Completado": "badge-completado",
    "Calificado": "badge-calificado",
    "Cancelado": "badge-cancelado",
}


def badge_estatus(estatus: str) -> str:
    clase = _BADGE_CLASE.get(estatus, "badge-pendiente")
    return f"<span class='badge {clase}'>{estatus}</span>"
