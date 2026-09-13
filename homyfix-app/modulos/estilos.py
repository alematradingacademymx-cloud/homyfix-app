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
.badge-pendiente {{background:#FFF1E0; color:#B5610A;}}
.badge-asignado {{background:#E4EEFF; color:{AZUL_PRIMARIO};}}
.badge-visita {{background:#EDE4FF; color:{MORADO_CLARO};}}
.badge-cotizado {{background:#FFF3D6; color:#8A5A00;}}
.badge-puja {{background:#FFE4F0; color:#BE185D;}}
.badge-aceptado {{background:{VERDE}; color:#1F3D00;}}
.badge-encurso {{background:#F1E4FF; color:{MORADO_OSCURO};}}
.badge-completado {{background:{VERDE}; color:#1F3D00;}}
.badge-calificado {{background:#EAF7EA; color:#1C7C33;}}
.badge-cancelado {{background:#FFE4E4; color:#B91C1C;}}

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

/* Botones primarios con el naranja de marca y texto oscuro para buen contraste */
.stButton > button[kind="primary"], .stFormSubmitButton > button {{
    background-color: {NARANJA};
    color: #0B1F3A;
    border: none;
    font-weight: 700;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {{
    background-color: #E68A00;
    color: #0B1F3A;
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
