"""
Cliente HTTP hacia el Apps Script de Google Sheets (ver apps_script/Code.gs).

Expone exactamente las mismas funciones que modulos/datos_demo.py, para que
modulos/datos.py pueda intercambiarlas sin que el resto de la app se entere.
"""

import base64
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

TIMEOUT = 30


def _config():
    cfg = st.secrets["homyfix"]
    return cfg["api_url"], cfg["token"]


def _post(action, **params):
    api_url, token = _config()
    payload = {"action": action, "token": token, **params}
    r = requests.post(api_url, data=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _invalidar_cache():
    """Se llama después de cualquier escritura para que la próxima lectura
    (tabla, tab, refresco de página) traiga el dato actualizado en vez del
    cacheado."""
    st.cache_data.clear()


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

def _es_verdadero(valor) -> bool:
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ("si", "sí", "true", "1", "yes", "verdadero")


@st.cache_data(ttl=15, show_spinner=False)
def obtener_tecnicos() -> pd.DataFrame:
    resp = _post("obtener_tecnicos")
    datos = resp.get("datos", [])
    columnas = ["tecnico_id", "nombre", "especialidad", "zona", "telefono",
                "estatus", "membresia_al_corriente", "calificacion_prom",
                "num_calificaciones", "rechazos", "foto_perfil_url"]
    if not datos:
        return pd.DataFrame(columns=columnas)
    df = pd.DataFrame(datos)
    df = df.rename(columns={
        "TecnicoID": "tecnico_id", "Nombre": "nombre", "Especialidad": "especialidad",
        "Zona": "zona", "Telefono": "telefono", "Estatus": "estatus",
        "MembresiaAlCorriente": "membresia_al_corriente", "CalificacionProm": "calificacion_prom",
        "NumCalificaciones": "num_calificaciones", "Rechazos": "rechazos",
        "FotoPerfilURL": "foto_perfil_url",
    })
    if "membresia_al_corriente" in df.columns:
        df["membresia_al_corriente"] = df["membresia_al_corriente"].apply(_es_verdadero)
    for col in ("calificacion_prom", "num_calificaciones", "rechazos"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def agregar_tecnico(nombre, especialidad, zona, telefono):
    resp = _post("agregar_tecnico", nombre=nombre, especialidad=especialidad, zona=zona, telefono=telefono)
    _invalidar_cache()
    return resp.get("tecnico_id")


def actualizar_estatus_tecnico(tecnico_id, nuevo_estatus):
    _post("actualizar_estatus_tecnico", tecnico_id=tecnico_id, nuevo_estatus=nuevo_estatus)
    _invalidar_cache()


def actualizar_membresia_tecnico(tecnico_id, al_corriente: bool):
    _post("actualizar_membresia_tecnico", tecnico_id=tecnico_id, al_corriente="SI" if al_corriente else "")
    _invalidar_cache()


# ---------- Solicitudes ----------

_COLS_SOLICITUDES_MAP = {
    "SolicitudID": "solicitud_id", "ClienteID": "cliente_id", "ClienteNombre": "cliente_nombre",
    "Categoria": "categoria", "Zona": "zona", "Descripcion": "descripcion", "Urgencia": "urgencia",
    "Estatus": "estatus", "TecnicoID": "tecnico_id", "Costo": "costo",
    "Calificacion": "calificacion", "Creado": "creado",
    "CodigoSeguridad": "codigo_seguridad", "TipoCotizacion": "tipo_cotizacion",
    "CostoVisita": "costo_visita", "CostoReparacion": "costo_reparacion",
    "Diagnostico": "diagnostico", "FotoURL": "foto_url", "TecnicosRechazados": "tecnicos_rechazados",
    "ClienteLat": "cliente_lat", "ClienteLng": "cliente_lng",
    "TecnicoLat": "tecnico_lat", "TecnicoLng": "tecnico_lng",
    "UbicacionTecnicoHora": "ubicacion_tecnico_hora",
}

_COLUMNAS_SOLICITUDES = list(_COLS_SOLICITUDES_MAP.values())


@st.cache_data(ttl=15, show_spinner=False)
def obtener_solicitudes() -> pd.DataFrame:
    resp = _post("obtener_solicitudes")
    datos = resp.get("datos", [])
    if not datos:
        return pd.DataFrame(columns=_COLUMNAS_SOLICITUDES)
    df = pd.DataFrame(datos).rename(columns=_COLS_SOLICITUDES_MAP)
    if "creado" in df.columns:
        df["creado"] = pd.to_datetime(df["creado"], errors="coerce")
    for col in ("costo", "costo_visita", "costo_reparacion", "calificacion",
                "cliente_lat", "cliente_lng", "tecnico_lat", "tecnico_lng"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def crear_solicitud(cliente_id, cliente_nombre, categoria, zona, descripcion, urgencia,
                     cliente_lat=None, cliente_lng=None):
    resp = _post(
        "crear_solicitud", cliente_id=cliente_id, cliente_nombre=cliente_nombre,
        categoria=categoria, zona=zona, descripcion=descripcion, urgencia=urgencia,
        cliente_lat=cliente_lat if cliente_lat is not None else "",
        cliente_lng=cliente_lng if cliente_lng is not None else "",
    )
    _invalidar_cache()
    return resp.get("solicitud_id")


def actualizar_ubicacion_tecnico(solicitud_id, lat, lng):
    _post("actualizar_ubicacion_tecnico", solicitud_id=solicitud_id, lat=lat, lng=lng)
    _invalidar_cache()


def asignar_tecnico(solicitud_id, tecnico_id, costo=None):
    _post("asignar_tecnico", solicitud_id=solicitud_id, tecnico_id=tecnico_id, costo=costo or "")
    _invalidar_cache()


def actualizar_estatus_solicitud(solicitud_id, nuevo_estatus):
    _post("actualizar_estatus_solicitud", solicitud_id=solicitud_id, nuevo_estatus=nuevo_estatus)
    _invalidar_cache()


def cotizar_directo(solicitud_id, costo_reparacion):
    _post("cotizar_directo", solicitud_id=solicitud_id, costo_reparacion=costo_reparacion)
    _invalidar_cache()


def solicitar_visita(solicitud_id, costo_visita):
    _post("solicitar_visita", solicitud_id=solicitud_id, costo_visita=costo_visita)
    _invalidar_cache()


def subir_foto_diagnostico(solicitud_id, nombre_archivo, bytes_imagen, mime_type):
    contenido_b64 = base64.b64encode(bytes_imagen).decode("ascii")
    resp = _post(
        "subir_foto_diagnostico", solicitud_id=solicitud_id, nombre_archivo=nombre_archivo,
        mime_type=mime_type, contenido_base64=contenido_b64,
    )
    return resp.get("foto_url")


def subir_bitacora(solicitud_id, diagnostico, foto_url, costo_reparacion):
    _post(
        "subir_bitacora", solicitud_id=solicitud_id, diagnostico=diagnostico,
        foto_url=foto_url or "", costo_reparacion=costo_reparacion,
    )
    _invalidar_cache()


def aceptar_solicitud(solicitud_id):
    _post("aceptar_solicitud", solicitud_id=solicitud_id)
    _invalidar_cache()


def rechazar_solicitud(solicitud_id):
    _post("rechazar_solicitud", solicitud_id=solicitud_id)
    _invalidar_cache()


@st.cache_data(ttl=15, show_spinner=False)
def obtener_pujas(solicitud_id=None) -> pd.DataFrame:
    resp = _post("obtener_pujas", solicitud_id=solicitud_id or "")
    datos = resp.get("datos", [])
    columnas = ["solicitud_id", "tecnico_id", "costo", "fecha"]
    if not datos:
        return pd.DataFrame(columns=columnas)
    df = pd.DataFrame(datos).rename(columns={
        "SolicitudID": "solicitud_id", "TecnicoID": "tecnico_id", "Costo": "costo", "Fecha": "fecha",
    })
    df["costo"] = pd.to_numeric(df["costo"], errors="coerce")
    return df


def ofertar_puja(solicitud_id, tecnico_id, costo):
    _post("ofertar_puja", solicitud_id=solicitud_id, tecnico_id=tecnico_id, costo=costo)
    _invalidar_cache()


def cerrar_puja(solicitud_id):
    resp = _post("cerrar_puja", solicitud_id=solicitud_id)
    _invalidar_cache()
    return resp


def calificar_solicitud(solicitud_id, calificacion):
    _post("calificar_solicitud", solicitud_id=solicitud_id, calificacion=calificacion)
    _invalidar_cache()


# ---------- Registro / alta con documentos (técnico y cliente) ----------

def enviar_solicitud_registro(tipo, nombre, correo, telefono, direccion=None, edad=None,
                               especialidad=None, experiencia=None, herramienta=None,
                               documentos=None):
    """documentos: dict {nombre_campo: archivo_streamlit (o None)}"""
    params = {
        "tipo": tipo, "nombre": nombre, "correo": correo, "telefono": telefono,
        "direccion": direccion or "", "edad": edad or "", "especialidad": especialidad or "",
        "experiencia": experiencia or "", "herramienta": herramienta or "",
    }
    for campo, archivo in (documentos or {}).items():
        if archivo is not None:
            params[f"doc_{campo}_nombre"] = archivo.name
            params[f"doc_{campo}_mime"] = archivo.type
            params[f"doc_{campo}_b64"] = base64.b64encode(archivo.getvalue()).decode("ascii")
    resp = _post("enviar_solicitud_registro", **params)
    _invalidar_cache()
    return resp.get("registro_id")


@st.cache_data(ttl=15, show_spinner=False)
def obtener_solicitudes_registro(estatus="Pendiente") -> pd.DataFrame:
    resp = _post("obtener_solicitudes_registro", estatus=estatus or "")
    datos = resp.get("datos", [])
    columnas = ["registro_id", "tipo", "nombre", "correo", "telefono", "direccion", "edad",
                "especialidad", "experiencia", "herramienta", "estatus", "vinculo_id",
                "codigo_acceso", "codigo_usado", "creado"]
    if not datos:
        return pd.DataFrame(columns=columnas)
    df = pd.DataFrame(datos).rename(columns={
        "RegistroID": "registro_id", "Tipo": "tipo", "Nombre": "nombre", "Correo": "correo",
        "Telefono": "telefono", "Direccion": "direccion", "Edad": "edad",
        "Especialidad": "especialidad", "Experiencia": "experiencia", "Herramienta": "herramienta",
        "Estatus": "estatus", "VinculoID": "vinculo_id", "CodigoAcceso": "codigo_acceso",
        "CodigoUsado": "codigo_usado", "Creado": "creado",
    })
    # Las columnas de documentos vienen como DocUrl_<campo>; las juntamos en un dict por fila.
    cols_doc = [c for c in df.columns if c.startswith("DocUrl_")]
    if cols_doc and not df.empty:
        df["documentos"] = [
            {c.replace("DocUrl_", ""): fila[c] for c in cols_doc if fila[c]}
            for _, fila in df.iterrows()
        ]
    else:
        df["documentos"] = [{} for _ in range(len(df))]
    return df


def aprobar_solicitud_registro(registro_id):
    resp = _post("aprobar_solicitud_registro", registro_id=registro_id)
    _invalidar_cache()
    return resp


def rechazar_solicitud_registro(registro_id):
    resp = _post("rechazar_solicitud_registro", registro_id=registro_id)
    _invalidar_cache()
    return resp


def canjear_codigo(codigo, usuario, password):
    resp = _post("canjear_codigo", codigo=codigo, usuario=usuario, password=password)
    _invalidar_cache()
    return resp
