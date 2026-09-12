import streamlit as st

from modulos.config import (
    inicializar_session_state, iniciar_sesion, cerrar_sesion,
    ADMIN_OPERATIVO, ADMIN_SOCIO, TECNICO, CLIENTE, USUARIOS_DEMO,
)
from modulos.estilos import aplicar_estilos
from modulos.datos_demo import inicializar_datos
from modulos import admin_operativo, admin_socio, portal_tecnico, portal_cliente

st.set_page_config(page_title="Homyfix", page_icon="🧰", layout="wide")

inicializar_session_state()
inicializar_datos()
aplicar_estilos()


def pantalla_login():
    st.markdown(
        "<h1 style='text-align:center; color:#0B1F3A;'>🧰 Homyfix</h1>"
        "<p style='text-align:center; color:#5B6B82;'>Tu hogar en manos seguras</p>",
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            enviado = st.form_submit_button("Entrar", use_container_width=True)
            if enviado:
                if iniciar_sesion(usuario, password):
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        with st.expander("Usuarios de demostración (fase beta)"):
            for u, datos_u in USUARIOS_DEMO.items():
                st.caption(f"**{datos_u['rol']}** · usuario: `{u}` · contraseña: `{datos_u['password']}`")


def app_autenticada():
    with st.sidebar:
        st.markdown(f"**{st.session_state.nombre}**")
        st.caption(st.session_state.rol.replace('_', ' ').title())
        if st.button("Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()
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
    pantalla_login()
else:
    app_autenticada()
