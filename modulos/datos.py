"""
Punto único de acceso a datos para toda la app.

Si en `.streamlit/secrets.toml` (o en los Secrets de Streamlit Cloud) existe
la sección [homyfix] con api_url y token, se usa Google Sheets de verdad
(modulos/datos_sheets.py). Si no, se usa la versión en memoria con datos de
ejemplo (modulos/datos_demo.py) para poder seguir probando sin configurar
nada.

El resto de la app (paneles, login) siempre importa de aquí:
    from modulos import datos
    datos.obtener_tecnicos()
"""

import streamlit as st


def _backend():
    try:
        if "homyfix" in st.secrets and st.secrets["homyfix"].get("api_url"):
            from modulos import datos_sheets
            return datos_sheets
    except Exception:
        pass
    from modulos import datos_demo
    return datos_demo


def usando_sheets() -> bool:
    return _backend().__name__.endswith("datos_sheets")


def inicializar_datos():
    _backend().inicializar_datos()


def autenticar(usuario, password):
    return _backend().autenticar(usuario, password)


def obtener_tecnicos():
    return _backend().obtener_tecnicos()


def agregar_tecnico(nombre, especialidad, zona, telefono):
    return _backend().agregar_tecnico(nombre, especialidad, zona, telefono)


def actualizar_estatus_tecnico(tecnico_id, nuevo_estatus):
    return _backend().actualizar_estatus_tecnico(tecnico_id, nuevo_estatus)


def actualizar_membresia_tecnico(tecnico_id, al_corriente):
    return _backend().actualizar_membresia_tecnico(tecnico_id, al_corriente)


def obtener_solicitudes():
    return _backend().obtener_solicitudes()


def crear_solicitud(cliente_id, cliente_nombre, categoria, zona, descripcion, urgencia):
    return _backend().crear_solicitud(cliente_id, cliente_nombre, categoria, zona, descripcion, urgencia)


def asignar_tecnico(solicitud_id, tecnico_id, costo=None):
    return _backend().asignar_tecnico(solicitud_id, tecnico_id, costo)


def actualizar_estatus_solicitud(solicitud_id, nuevo_estatus):
    return _backend().actualizar_estatus_solicitud(solicitud_id, nuevo_estatus)


def cotizar_directo(solicitud_id, costo_reparacion):
    return _backend().cotizar_directo(solicitud_id, costo_reparacion)


def solicitar_visita(solicitud_id, costo_visita):
    return _backend().solicitar_visita(solicitud_id, costo_visita)


def subir_foto_diagnostico(solicitud_id, nombre_archivo, bytes_imagen, mime_type):
    return _backend().subir_foto_diagnostico(solicitud_id, nombre_archivo, bytes_imagen, mime_type)


def subir_bitacora(solicitud_id, diagnostico, foto_url, costo_reparacion):
    return _backend().subir_bitacora(solicitud_id, diagnostico, foto_url, costo_reparacion)


def aceptar_solicitud(solicitud_id):
    return _backend().aceptar_solicitud(solicitud_id)


def rechazar_solicitud(solicitud_id):
    return _backend().rechazar_solicitud(solicitud_id)


def obtener_pujas(solicitud_id=None):
    return _backend().obtener_pujas(solicitud_id)


def ofertar_puja(solicitud_id, tecnico_id, costo):
    return _backend().ofertar_puja(solicitud_id, tecnico_id, costo)


def cerrar_puja(solicitud_id):
    return _backend().cerrar_puja(solicitud_id)


def calificar_solicitud(solicitud_id, calificacion):
    return _backend().calificar_solicitud(solicitud_id, calificacion)
