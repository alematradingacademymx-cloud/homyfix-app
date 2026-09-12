"""
Configuración central de Homyfix: roles, sesión y usuarios de demostración.

En esta fase beta los usuarios están "hardcodeados" aquí mismo para poder
probar los 4 roles sin depender todavía de una base de datos externa.
Cuando se conecte Google Sheets (ver README.md), esta función se reemplaza
por una consulta real a la hoja de Usuarios, igual que en el portal educativo.
"""

import streamlit as st

# --- Roles del sistema ---
ADMIN_OPERATIVO = "ADMIN_OPERATIVO"   # despacha trabajos, valida técnicos, cobra cuotas
ADMIN_SOCIO = "ADMIN_SOCIO"           # ve métricas globales y finanzas, sin operar el día a día
TECNICO = "TECNICO"
CLIENTE = "CLIENTE"

ROLES_ADMIN = (ADMIN_OPERATIVO, ADMIN_SOCIO)

# --- Usuarios de demostración (fase beta) ---
# usuario -> {password, rol, nombre, tecnico_id (solo si rol=TECNICO)}
USUARIOS_DEMO = {
    "admin.operativo": {"password": "admin123", "rol": ADMIN_OPERATIVO, "nombre": "Admin Operativo"},
    "admin.socio": {"password": "socio123", "rol": ADMIN_SOCIO, "nombre": "Socio Homyfix"},
    "carlos.plomero": {"password": "tec123", "rol": TECNICO, "nombre": "Carlos (Plomero)", "tecnico_id": "T-001"},
    "martha.cliente": {"password": "cli123", "rol": CLIENTE, "nombre": "Sra. Martha", "cliente_id": "C-001"},
}


def inicializar_session_state():
    defaults = {
        "autenticado": False,
        "usuario": None,
        "rol": None,
        "nombre": None,
        "tecnico_id": None,
        "cliente_id": None,
    }
    for llave, valor in defaults.items():
        if llave not in st.session_state:
            st.session_state[llave] = valor


def iniciar_sesion(usuario: str, password: str) -> bool:
    datos = USUARIOS_DEMO.get(usuario.strip().lower())
    if not datos or datos["password"] != password:
        return False
    st.session_state.autenticado = True
    st.session_state.usuario = usuario
    st.session_state.rol = datos["rol"]
    st.session_state.nombre = datos["nombre"]
    st.session_state.tecnico_id = datos.get("tecnico_id")
    st.session_state.cliente_id = datos.get("cliente_id")
    return True


def cerrar_sesion():
    for llave in ("autenticado", "usuario", "rol", "nombre", "tecnico_id", "cliente_id"):
        st.session_state[llave] = None
    st.session_state.autenticado = False
