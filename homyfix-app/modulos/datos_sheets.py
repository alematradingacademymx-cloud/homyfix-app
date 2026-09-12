"""
Cliente HTTP hacia el Apps Script de Google Sheets (ver apps_script/Code.gs).

Expone exactamente las mismas funciones que modulos/datos_demo.py, para que
modulos/datos.py pueda intercambiarlas sin que el resto de la app se entere.
"""

import requests
import streamlit as st
import pandas as pd
from datetime import datetime

TIMEOUT = 15


def _config():
    cfg = st.secrets["homyfix"]
    return cfg["api_url"], cfg["token"]


def _post(action, **params):
    api_url, token = _config()
    payload = {"action": action, "token": token, **params}
    r = requests.post(api_url, data=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def inicializar_datos():
    # No hace falta sembrar nada: el Apps Script crea las pestañas solo con
    # sus encabezados la primera vez que se usan.
    pass


def autenticar(usuario, password):
    resp = _post("login", usuario=usuario, password=password)
    if not resp.get("ok"):
        return None
    return {
        "rol": resp["rol"],
        "nombre": resp["nombre"],
        "tecnico_id": resp.get("tecnico_id") or None,
        "cliente_id": resp.get("cliente_id") or None,
    }


# ---------- Técnicos ----------

def obtener_tecnicos() -> pd.DataFrame:
    resp = _post("obtener_tecnicos")
    datos = resp.get("datos", [])
    if not datos:
        return pd.DataFrame(columns=[
            "tecnico_id", "nombre", "especialidad", "zona", "telefono",
            "estatus", "membresia_al_corriente", "calificacion_prom",
        ])
    df = pd.DataFrame(datos)
    return df.rename(columns={
        "TecnicoID": "tecnico_id", "Nombre": "nombre", "Especialidad": "especialidad",
        "Zona": "zona", "Telefono": "telefono", "Estatus": "estatus",
        "MembresiaAlCorriente": "membresia_al_corriente", "CalificacionProm": "calificacion_prom",
    })


def agregar_tecnico(nombre, especialidad, zona, telefono):
    resp = _post("agregar_tecnico", nombre=nombre, especialidad=especialidad, zona=zona, telefono=telefono)
    return resp.get("tecnico_id")


def actualizar_estatus_tecnico(tecnico_id, nuevo_estatus):
    _post("actualizar_estatus_tecnico", tecnico_id=tecnico_id, nuevo_estatus=nuevo_estatus)


# ---------- Solicitudes ----------

def obtener_solicitudes() -> pd.DataFrame:
    resp = _post("obtener_solicitudes")
    datos = resp.get("datos", [])
    columnas = ["solicitud_id", "cliente_id", "cliente_nombre", "categoria", "zona",
                "descripcion", "urgencia", "estatus", "tecnico_id", "costo", "calificacion", "creado"]
    if not datos:
        return pd.DataFrame(columns=columnas)
    df = pd.DataFrame(datos).rename(columns={
        "SolicitudID": "solicitud_id", "ClienteID": "cliente_id", "ClienteNombre": "cliente_nombre",
        "Categoria": "categoria", "Zona": "zona", "Descripcion": "descripcion", "Urgencia": "urgencia",
        "Estatus": "estatus", "TecnicoID": "tecnico_id", "Costo": "costo",
        "Calificacion": "calificacion", "Creado": "creado",
    })
    if "creado" in df.columns:
        df["creado"] = pd.to_datetime(df["creado"], errors="coerce")
    return df


def crear_solicitud(cliente_id, cliente_nombre, categoria, zona, descripcion, urgencia):
    resp = _post(
        "crear_solicitud", cliente_id=cliente_id, cliente_nombre=cliente_nombre,
        categoria=categoria, zona=zona, descripcion=descripcion, urgencia=urgencia,
    )
    return resp.get("solicitud_id")


def asignar_tecnico(solicitud_id, tecnico_id, costo=None):
    _post("asignar_tecnico", solicitud_id=solicitud_id, tecnico_id=tecnico_id, costo=costo or "")


def actualizar_estatus_solicitud(solicitud_id, nuevo_estatus):
    _post("actualizar_estatus_solicitud", solicitud_id=solicitud_id, nuevo_estatus=nuevo_estatus)


def calificar_solicitud(solicitud_id, calificacion):
    _post("calificar_solicitud", solicitud_id=solicitud_id, calificacion=calificacion)
