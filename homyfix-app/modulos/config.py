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


def inicializar_session_state():
    defaults = {
        "autenticado": False,
        "usuario": None,
        "rol": None,
        "nombre": None,
        "tecnico_id": None,
        "cliente_id": None,
        "sesion_token": None,
    }
    for llave, valor in defaults.items():
        if llave not in st.session_state:
            st.session_state[llave] = valor


def restaurar_sesion():
    """Si ya estás autenticado en esta corrida no hace nada. Si no, revisa si
    la URL trae un token de sesión (?s=...) — lo pusimos ahí al iniciar
    sesión — y si es válido, restaura la sesión sin pedir usuario/contraseña
    de nuevo.

    Esto es lo que evita que un refresh de la página (o que Streamlit Cloud
    reinicie el servidor, algo normal después de cada redeploy) te regrese
    al login: `st.session_state` vive solo en memoria y se pierde en esos
    casos, pero la URL y el token guardado en Google Sheets sí sobreviven."""
    if st.session_state.autenticado:
        return
    token = st.query_params.get("s")
    if not token:
        return
    from modulos import datos as capa_datos
    resultado = capa_datos.sesion_por_token(token)
    if not resultado:
        st.query_params.pop("s", None)
        return
    st.session_state.autenticado = True
    st.session_state.usuario = resultado.get("usuario")
    st.session_state.rol = resultado["rol"]
    st.session_state.nombre = resultado["nombre"]
    st.session_state.tecnico_id = resultado.get("tecnico_id")
    st.session_state.cliente_id = resultado.get("cliente_id")
    st.session_state.sesion_token = token


def iniciar_sesion(usuario: str, password: str) -> bool:
    from modulos import datos as capa_datos
    resultado = capa_datos.autenticar(usuario, password)
    if not resultado:
        return False
    st.session_state.autenticado = True
    st.session_state.usuario = usuario
    st.session_state.rol = resultado["rol"]
    st.session_state.nombre = resultado["nombre"]
    st.session_state.tecnico_id = resultado.get("tecnico_id")
    st.session_state.cliente_id = resultado.get("cliente_id")
    token = resultado.get("token")
    st.session_state.sesion_token = token
    if token:
        # Guardamos el token en la URL para que un refresh (o que el
        # servidor se reinicie) no te saque de la sesión — ver
        # restaurar_sesion().
        st.query_params["s"] = token
    return True


def cerrar_sesion():
    from modulos import datos as capa_datos
    token = st.session_state.get("sesion_token")
    if token:
        try:
            capa_datos.cerrar_sesion(token)
        except Exception:
            pass
    st.query_params.pop("s", None)
    for llave in ("autenticado", "usuario", "rol", "nombre", "tecnico_id", "cliente_id", "sesion_token"):
        st.session_state[llave] = None
    st.session_state.autenticado = False
