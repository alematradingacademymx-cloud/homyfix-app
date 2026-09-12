"""
Capa de datos de la fase beta.

Todo vive en memoria (st.session_state) con datos de ejemplo para poder
probar el flujo completo (alta de técnico -> solicitud -> asignación ->
cierre -> calificación) sin depender de nada externo todavía.

IMPORTANTE PARA LA MIGRACIÓN FUTURA:
Cada función de aquí (obtener_tecnicos, crear_solicitud, etc.) es la que se
debe reemplazar por una llamada real a Google Sheets (vía el mismo patrón de
Apps Script que ya usas en el portal educativo) cuando decidan pasar a datos
persistentes de verdad. El resto de la app (paneles, portales) no debería
necesitar cambios porque ya consume estas funciones, no las estructuras
internas.
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

ESTATUS_SOLICITUD = ["Pendiente", "Asignado", "En curso", "Completado", "Calificado", "Cancelado"]
ESTATUS_TECNICO = ["Pendiente de validación", "Activo", "Suspendido"]


def _semilla_tecnicos():
    return pd.DataFrame([
        {"tecnico_id": "T-001", "nombre": "Carlos Pérez", "especialidad": "Plomería",
         "zona": "Narvarte", "telefono": "5511111111", "estatus": "Activo",
         "membresia_al_corriente": True, "calificacion_prom": 4.8},
        {"tecnico_id": "T-002", "nombre": "Roberto (Don Beto)", "especialidad": "Plomería",
         "zona": "Centro", "telefono": "5522222222", "estatus": "Activo",
         "membresia_al_corriente": True, "calificacion_prom": 4.9},
        {"tecnico_id": "T-003", "nombre": "Ana López", "especialidad": "Electricidad",
         "zona": "Del Valle", "telefono": "5533333333", "estatus": "Pendiente de validación",
         "membresia_al_corriente": False, "calificacion_prom": None},
    ])


def _semilla_solicitudes():
    ahora = datetime.now()
    return pd.DataFrame([
        {"solicitud_id": "S-1001", "cliente_id": "C-001", "cliente_nombre": "Sra. Martha",
         "categoria": "Plomería", "zona": "Narvarte",
         "descripcion": "Fuga en manguera debajo del fregadero", "urgencia": "Inmediata",
         "estatus": "Completado", "tecnico_id": "T-002", "costo": 450,
         "calificacion": 5, "creado": ahora - timedelta(days=2)},
        {"solicitud_id": "S-1002", "cliente_id": "C-002", "cliente_nombre": "Juan Ramírez",
         "categoria": "Electricidad", "zona": "Centro",
         "descripcion": "Corto circuito en la cocina", "urgencia": "Para hoy",
         "estatus": "Pendiente", "tecnico_id": None, "costo": None,
         "calificacion": None, "creado": ahora - timedelta(hours=3)},
    ])


def inicializar_datos():
    if "tecnicos_df" not in st.session_state:
        st.session_state.tecnicos_df = _semilla_tecnicos()
    if "solicitudes_df" not in st.session_state:
        st.session_state.solicitudes_df = _semilla_solicitudes()


# ---------- Técnicos ----------

def obtener_tecnicos() -> pd.DataFrame:
    return st.session_state.tecnicos_df


def agregar_tecnico(nombre, especialidad, zona, telefono):
    df = st.session_state.tecnicos_df
    nuevo_id = f"T-{len(df) + 1:03d}"
    fila = {"tecnico_id": nuevo_id, "nombre": nombre, "especialidad": especialidad,
            "zona": zona, "telefono": telefono, "estatus": "Pendiente de validación",
            "membresia_al_corriente": False, "calificacion_prom": None}
    st.session_state.tecnicos_df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
    return nuevo_id


def actualizar_estatus_tecnico(tecnico_id, nuevo_estatus):
    df = st.session_state.tecnicos_df
    df.loc[df.tecnico_id == tecnico_id, "estatus"] = nuevo_estatus


# ---------- Solicitudes ----------

def obtener_solicitudes() -> pd.DataFrame:
    return st.session_state.solicitudes_df


def crear_solicitud(cliente_id, cliente_nombre, categoria, zona, descripcion, urgencia):
    df = st.session_state.solicitudes_df
    nuevo_id = f"S-{1000 + len(df) + 1}"
    fila = {"solicitud_id": nuevo_id, "cliente_id": cliente_id, "cliente_nombre": cliente_nombre,
            "categoria": categoria, "zona": zona, "descripcion": descripcion, "urgencia": urgencia,
            "estatus": "Pendiente", "tecnico_id": None, "costo": None,
            "calificacion": None, "creado": datetime.now()}
    st.session_state.solicitudes_df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
    return nuevo_id


def asignar_tecnico(solicitud_id, tecnico_id, costo=None):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "tecnico_id"] = tecnico_id
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Asignado"
    if costo is not None:
        df.loc[df.solicitud_id == solicitud_id, "costo"] = costo


def actualizar_estatus_solicitud(solicitud_id, nuevo_estatus):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = nuevo_estatus


def calificar_solicitud(solicitud_id, calificacion):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "calificacion"] = calificacion
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Calificado"
