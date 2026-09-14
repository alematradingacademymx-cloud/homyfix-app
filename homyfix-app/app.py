from pathlib import Path

import streamlit as st
from PIL import Image

from modulos.config import (
    inicializar_session_state, restaurar_sesion, iniciar_sesion, cerrar_sesion,
    ADMIN_OPERATIVO, ADMIN_SOCIO, TECNICO, CLIENTE,
)
from modulos.estilos import aplicar_estilos, logo, lema
from modulos import datos
from modulos.datos_demo import USUARIOS_DEMO
from modulos import admin_operativo, admin_socio, portal_tecnico, portal_cliente, registro

_FAVICON_PATH = Path(__file__).resolve().parent / "assets" / "favicon.png"
_favicon = Image.open(_FAVICON_PATH) if _FAVICON_PATH.exists() else "🧰"

st.set_page_config(page_title="Homyfix", page_icon=_favicon, layout="wide")

inicializar_session_state()
datos.inicializar_datos()
restaurar_sesion()
aplicar_estilos()


def pantalla_login():
    logo(ancho=190)
    lema()
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            enviado = st.form_submit_button("Entrar", use_container_width=True, key="btn_entrar")
            if enviado:
                if iniciar_sesion(usuario, password):
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        st.divider()
        st.caption("¿Aún no tienes cuenta?")
        c1, c2 = st.columns(2)
        if c1.button("🧰 Quiero ser técnico", use_container_width=True):
            st.session_state.vista_publica = "registro_tecnico"
            st.rerun()
        if c2.button("🏠 Quiero ser cliente", use_container_width=True):
            st.session_state.vista_publica = "registro_cliente"
            st.rerun()
        if st.button("🔑 Ya tengo un código de acceso", use_container_width=True, key="btn_codigo_acceso"):
            st.session_state.vista_publica = "canjear"
            st.rerun()

        if not datos.usando_sheets():
            with st.expander("Usuarios de demostración (fase beta, sin Google Sheets configurado)"):
                for u, datos_u in USUARIOS_DEMO.items():
                    st.caption(f"**{datos_u['rol']}** · usuario: `{u}` · contraseña: `{datos_u['password']}`")


def app_autenticada():
    with st.sidebar:
        st.markdown(f"**{st.session_state.nombre}**")
        st.caption(st.session_state.rol.replace('_', ' ').title())
        if st.button("Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()
        logo(ancho=110, centrado=False)
        st.divider()

    rol = st.session_state.rol
    if rol == ADMIN_OPERATIVO:
        admin_operativo.pagina()
    elif rol == ADMIN_SOCIO:
        admin_socio.pagina()
    elif rol == TECNICO:
        portal_tecnico.pagina()
    elif rol == CLIENTE:
        portal_cliente.pagina()
    else:
        st.error("Rol no reconocido")


if not st.session_state.autenticado:
    st.session_state.setdefault("vista_publica", "login")
    vista = st.session_state.vista_publica
    if vista == "registro_tecnico":
        registro.formulario_tecnico()
    elif vista == "registro_cliente":
        registro.formulario_cliente()
    elif vista == "canjear":
        registro.formulario_canjear()
    else:
        pantalla_login()
else:
    app_autenticada()
