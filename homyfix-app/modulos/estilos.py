"""Estilos compartidos de la app (siguiendo el mismo patrón del portal educativo)."""

import streamlit as st

CSS = """
<style>
header[data-testid="stHeader"] {background: transparent;}
#MainMenu, footer, .stAppDeployButton {visibility: hidden;}

.main-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0B1F3A;
    margin-bottom: 0;
}
.sub-title {
    color: #5B6B82;
    margin-top: 0;
}
.app-card {
    background: #F5F6FA;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    border: 1px solid #E7EAF0;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-pendiente {background:#FFF1E0; color:#B5610A;}
.badge-asignado {background:#E4EEFF; color:#1D4ED8;}
.badge-visita {background:#EDE4FF; color:#5B21B6;}
.badge-cotizado {background:#FFF9C4; color:#8A6D00;}
.badge-puja {background:#FFE4F0; color:#BE185D;}
.badge-aceptado {background:#DCFCE7; color:#15803D;}
.badge-encurso {background:#FDE8FF; color:#A21CAF;}
.badge-completado {background:#E4FFEE; color:#0F8A3E;}
.badge-calificado {background:#EAF7EA; color:#1C7C33;}
.badge-cancelado {background:#FFE4E4; color:#B91C1C;}
</style>
"""


def aplicar_estilos():
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, subtitulo: str = ""):
    st.markdown(f"<p class='main-title'>{titulo}</p>", unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f"<p class='sub-title'>{subtitulo}</p>", unsafe_allow_html=True)


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
