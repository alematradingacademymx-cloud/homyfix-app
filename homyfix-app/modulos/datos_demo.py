"""
Capa de datos de la fase beta.

Todo vive en memoria (st.session_state) con datos de ejemplo para poder
probar el flujo completo (alta de técnico -> solicitud -> cotización ->
puja -> cierre -> calificación) sin depender de nada externo todavía.

IMPORTANTE PARA LA MIGRACIÓN FUTURA:
Cada función de aquí (obtener_tecnicos, crear_solicitud, etc.) es la que se
debe reemplazar por una llamada real a Google Sheets (vía el mismo patrón de
Apps Script que ya usas en el portal educativo) cuando decidan pasar a datos
persistentes de verdad. El resto de la app (paneles, portales) no debería
necesitar cambios porque ya consume estas funciones, no las estructuras
internas.
"""

import random
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

ESTATUS_SOLICITUD = [
    "Pendiente", "Asignado", "En Visita", "Cotizado", "En Puja",
    "Aceptado", "En curso", "Completado", "Calificado", "Cancelado",
]
ESTATUS_TECNICO = ["Pendiente de validación", "Activo", "Suspendido"]

# Usuarios de demostración (solo se usan si NO hay Google Sheets configurado,
# ver modulos/datos.py). usuario -> {password, rol, nombre, tecnico_id/cliente_id}
USUARIOS_DEMO = {
    "admin.operativo": {"password": "admin123", "rol": "ADMIN_OPERATIVO", "nombre": "Admin Operativo"},
    "admin.socio": {"password": "socio123", "rol": "ADMIN_SOCIO", "nombre": "Socio Homyfix"},
    "carlos.plomero": {"password": "tec123", "rol": "TECNICO", "nombre": "Carlos (Plomero)", "tecnico_id": "T-001"},
    "martha.cliente": {"password": "cli123", "rol": "CLIENTE", "nombre": "Sra. Martha", "cliente_id": "C-001"},
}


def _semilla_usuarios():
    filas = []
    for usuario, d in USUARIOS_DEMO.items():
        filas.append({
            "usuario": usuario, "password": d["password"], "rol": d["rol"], "nombre": d["nombre"],
            "tecnico_id": d.get("tecnico_id"), "cliente_id": d.get("cliente_id"),
        })
    return pd.DataFrame(filas)


def autenticar(usuario, password):
    df = st.session_state.usuarios_df
    usuario_norm = (usuario or "").strip().lower()
    fila = df[df.usuario.astype(str).str.strip().str.lower() == usuario_norm]
    if fila.empty or str(fila.iloc[0].password) != str(password):
        return None
    f = fila.iloc[0]
    return {
        "rol": f.rol,
        "nombre": f.nombre,
        "tecnico_id": f.tecnico_id or None,
        "cliente_id": f.cliente_id or None,
    }


def _semilla_tecnicos():
    return pd.DataFrame([
        {"tecnico_id": "T-001", "nombre": "Carlos Pérez", "especialidad": "Plomería",
         "zona": "Narvarte", "telefono": "5511111111", "estatus": "Activo",
         "membresia_al_corriente": True, "calificacion_prom": 4.8, "num_calificaciones": 10, "rechazos": 0,
         "foto_perfil_url": None},
        {"tecnico_id": "T-002", "nombre": "Roberto (Don Beto)", "especialidad": "Plomería",
         "zona": "Centro", "telefono": "5522222222", "estatus": "Activo",
         "membresia_al_corriente": True, "calificacion_prom": 4.9, "num_calificaciones": 22, "rechazos": 1,
         "foto_perfil_url": None},
        {"tecnico_id": "T-003", "nombre": "Ana López", "especialidad": "Electricidad",
         "zona": "Del Valle", "telefono": "5533333333", "estatus": "Pendiente de validación",
         "membresia_al_corriente": False, "calificacion_prom": None, "num_calificaciones": 0, "rechazos": 0,
         "foto_perfil_url": None},
    ])


def _semilla_solicitudes():
    ahora = datetime.now()
    return pd.DataFrame([
        {"solicitud_id": "S-1001", "cliente_id": "C-001", "cliente_nombre": "Sra. Martha",
         "categoria": "Plomería", "zona": "Narvarte",
         "descripcion": "Fuga en manguera debajo del fregadero", "urgencia": "Inmediata",
         "estatus": "Completado", "tecnico_id": "T-002", "costo": 450,
         "codigo_seguridad": "482913", "tipo_cotizacion": "Directo", "costo_visita": None,
         "costo_reparacion": 450, "diagnostico": None, "foto_url": None, "tecnicos_rechazados": "",
         "calificacion": None, "creado": ahora - timedelta(days=2)},
        {"solicitud_id": "S-1002", "cliente_id": "C-002", "cliente_nombre": "Juan Ramírez",
         "categoria": "Electricidad", "zona": "Centro",
         "descripcion": "Corto circuito en la cocina", "urgencia": "Para hoy",
         "estatus": "Pendiente", "tecnico_id": None, "costo": None,
         "codigo_seguridad": "731064", "tipo_cotizacion": None, "costo_visita": None,
         "costo_reparacion": None, "diagnostico": None, "foto_url": None, "tecnicos_rechazados": "",
         "calificacion": None, "creado": ahora - timedelta(hours=3)},
    ])


def _semilla_pujas():
    return pd.DataFrame(columns=["solicitud_id", "tecnico_id", "costo", "fecha"])


COLUMNAS_REGISTROS = [
    "registro_id", "tipo", "nombre", "correo", "telefono", "direccion", "edad",
    "especialidad", "experiencia", "herramienta", "documentos", "estatus",
    "vinculo_id", "codigo_acceso", "codigo_usado", "creado",
]


def _semilla_registros():
    return pd.DataFrame(columns=COLUMNAS_REGISTROS)


def inicializar_datos():
    if "usuarios_df" not in st.session_state:
        st.session_state.usuarios_df = _semilla_usuarios()
    if "tecnicos_df" not in st.session_state:
        st.session_state.tecnicos_df = _semilla_tecnicos()
    if "solicitudes_df" not in st.session_state:
        st.session_state.solicitudes_df = _semilla_solicitudes()
    if "pujas_df" not in st.session_state:
        st.session_state.pujas_df = _semilla_pujas()
    if "registros_df" not in st.session_state:
        st.session_state.registros_df = _semilla_registros()


def _generar_codigo():
    return f"{random.randint(0, 999999):06d}"


def _generar_codigo_acceso():
    alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O/1/I para evitar confusiones
    return "".join(random.choice(alfabeto) for _ in range(8))


# ---------- Técnicos ----------

def obtener_tecnicos() -> pd.DataFrame:
    return st.session_state.tecnicos_df


def agregar_tecnico(nombre, especialidad, zona, telefono):
    df = st.session_state.tecnicos_df
    nuevo_id = f"T-{len(df) + 1:03d}"
    fila = {"tecnico_id": nuevo_id, "nombre": nombre, "especialidad": especialidad,
            "zona": zona, "telefono": telefono, "estatus": "Pendiente de validación",
            "membresia_al_corriente": False, "calificacion_prom": None,
            "num_calificaciones": 0, "rechazos": 0, "foto_perfil_url": None}
    st.session_state.tecnicos_df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
    return nuevo_id


def actualizar_estatus_tecnico(tecnico_id, nuevo_estatus):
    df = st.session_state.tecnicos_df
    df.loc[df.tecnico_id == tecnico_id, "estatus"] = nuevo_estatus


def actualizar_membresia_tecnico(tecnico_id, al_corriente: bool):
    df = st.session_state.tecnicos_df
    df.loc[df.tecnico_id == tecnico_id, "membresia_al_corriente"] = al_corriente


def _registrar_calificacion_tecnico(tecnico_id, valor, es_rechazo=False):
    """Actualiza el promedio y contador de calificaciones de un técnico.
    Un rechazo del cliente también entra aquí con un valor bajo (penaliza el
    promedio), además de sumar al contador de rechazos."""
    df = st.session_state.tecnicos_df
    idx = df.index[df.tecnico_id == tecnico_id]
    if len(idx) == 0:
        return
    i = idx[0]
    n_actual = int(df.at[i, "num_calificaciones"] or 0)
    prom_actual = df.at[i, "calificacion_prom"]
    prom_actual = float(prom_actual) if prom_actual not in (None, "") and not pd.isna(prom_actual) else 0.0
    nuevo_n = n_actual + 1
    nuevo_prom = ((prom_actual * n_actual) + valor) / nuevo_n
    df.at[i, "num_calificaciones"] = nuevo_n
    df.at[i, "calificacion_prom"] = round(nuevo_prom, 2)
    if es_rechazo:
        df.at[i, "rechazos"] = int(df.at[i, "rechazos"] or 0) + 1


# ---------- Solicitudes ----------

def obtener_solicitudes() -> pd.DataFrame:
    return st.session_state.solicitudes_df


def crear_solicitud(cliente_id, cliente_nombre, categoria, zona, descripcion, urgencia):
    df = st.session_state.solicitudes_df
    nuevo_id = f"S-{1000 + len(df) + 1}"
    fila = {"solicitud_id": nuevo_id, "cliente_id": cliente_id, "cliente_nombre": cliente_nombre,
            "categoria": categoria, "zona": zona, "descripcion": descripcion, "urgencia": urgencia,
            "estatus": "Pendiente", "tecnico_id": None, "costo": None,
            "codigo_seguridad": _generar_codigo(), "tipo_cotizacion": None, "costo_visita": None,
            "costo_reparacion": None, "diagnostico": None, "foto_url": None, "tecnicos_rechazados": "",
            "calificacion": None, "creado": datetime.now()}
    st.session_state.solicitudes_df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
    return nuevo_id


def asignar_tecnico(solicitud_id, tecnico_id, costo=None):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "tecnico_id"] = tecnico_id
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Asignado"
    if costo is not None:
        df.loc[df.solicitud_id == solicitud_id, "costo"] = costo
        df.loc[df.solicitud_id == solicitud_id, "costo_reparacion"] = costo


def actualizar_estatus_solicitud(solicitud_id, nuevo_estatus):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = nuevo_estatus


def cotizar_directo(solicitud_id, costo_reparacion):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "tipo_cotizacion"] = "Directo"
    df.loc[df.solicitud_id == solicitud_id, "costo_reparacion"] = costo_reparacion
    df.loc[df.solicitud_id == solicitud_id, "costo"] = costo_reparacion
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Cotizado"


def solicitar_visita(solicitud_id, costo_visita):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "tipo_cotizacion"] = "Visita"
    df.loc[df.solicitud_id == solicitud_id, "costo_visita"] = costo_visita
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "En Visita"


def subir_foto_diagnostico(solicitud_id, nombre_archivo, bytes_imagen, mime_type):
    # En modo demo no hay Drive real: solo simulamos que se guardó.
    return f"demo://foto/{solicitud_id}/{nombre_archivo}"


def subir_bitacora(solicitud_id, diagnostico, foto_url, costo_reparacion):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "diagnostico"] = diagnostico
    df.loc[df.solicitud_id == solicitud_id, "foto_url"] = foto_url
    df.loc[df.solicitud_id == solicitud_id, "costo_reparacion"] = costo_reparacion
    df.loc[df.solicitud_id == solicitud_id, "costo"] = costo_reparacion
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Cotizado"


def aceptar_solicitud(solicitud_id):
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Aceptado"


def rechazar_solicitud(solicitud_id):
    df = st.session_state.solicitudes_df
    fila = df[df.solicitud_id == solicitud_id].iloc[0]
    tecnico_id = fila.tecnico_id
    if tecnico_id:
        _registrar_calificacion_tecnico(tecnico_id, 1, es_rechazo=True)
        actuales = (fila.tecnicos_rechazados or "").split(",") if fila.tecnicos_rechazados else []
        actuales = [t for t in actuales if t]
        actuales.append(tecnico_id)
        df.loc[df.solicitud_id == solicitud_id, "tecnicos_rechazados"] = ",".join(actuales)
    df.loc[df.solicitud_id == solicitud_id, "tecnico_id"] = None
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "En Puja"


def obtener_pujas(solicitud_id=None) -> pd.DataFrame:
    df = st.session_state.pujas_df
    if solicitud_id:
        return df[df.solicitud_id == solicitud_id]
    return df


def ofertar_puja(solicitud_id, tecnico_id, costo):
    df = st.session_state.pujas_df
    df = df[~((df.solicitud_id == solicitud_id) & (df.tecnico_id == tecnico_id))]
    nueva = pd.DataFrame([{"solicitud_id": solicitud_id, "tecnico_id": tecnico_id,
                            "costo": costo, "fecha": datetime.now()}])
    st.session_state.pujas_df = pd.concat([df, nueva], ignore_index=True)


def cerrar_puja(solicitud_id):
    """Elige ganador: mayor calificación promedio primero, empate = menor costo."""
    pujas = obtener_pujas(solicitud_id)
    if pujas.empty:
        return {"ok": False, "error": "no hay ofertas todavía"}
    tecnicos = obtener_tecnicos()[["tecnico_id", "calificacion_prom"]]
    combinado = pujas.merge(tecnicos, on="tecnico_id", how="left")
    combinado["calificacion_prom"] = combinado["calificacion_prom"].fillna(0)
    combinado = combinado.sort_values(["calificacion_prom", "costo"], ascending=[False, True])
    ganador = combinado.iloc[0]
    df = st.session_state.solicitudes_df
    df.loc[df.solicitud_id == solicitud_id, "tecnico_id"] = ganador.tecnico_id
    df.loc[df.solicitud_id == solicitud_id, "costo_reparacion"] = ganador.costo
    df.loc[df.solicitud_id == solicitud_id, "costo"] = ganador.costo
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Cotizado"
    st.session_state.pujas_df = st.session_state.pujas_df[st.session_state.pujas_df.solicitud_id != solicitud_id]
    return {"ok": True, "tecnico_id": ganador.tecnico_id, "costo": ganador.costo}


def calificar_solicitud(solicitud_id, calificacion):
    df = st.session_state.solicitudes_df
    fila = df[df.solicitud_id == solicitud_id].iloc[0]
    if fila.tecnico_id:
        _registrar_calificacion_tecnico(fila.tecnico_id, calificacion)
    df.loc[df.solicitud_id == solicitud_id, "calificacion"] = calificacion
    df.loc[df.solicitud_id == solicitud_id, "estatus"] = "Calificado"


# ---------- Registro / alta con documentos (técnico y cliente) ----------

def _subir_documento_demo(nombre_archivo, bytes_datos, mime_type):
    # En modo demo no hay Drive real: solo simulamos la URL del documento.
    return f"demo://documento/{nombre_archivo}"


def enviar_solicitud_registro(tipo, nombre, correo, telefono, direccion=None, edad=None,
                               especialidad=None, experiencia=None, herramienta=None,
                               documentos=None):
    """documentos: dict {nombre_campo: archivo_streamlit (o None)}"""
    df = st.session_state.registros_df
    nuevo_id = f"R-{len(df) + 1:04d}"
    urls_documentos = {}
    for campo, archivo in (documentos or {}).items():
        if archivo is not None:
            urls_documentos[campo] = _subir_documento_demo(archivo.name, archivo.getvalue(), archivo.type)
    fila = {
        "registro_id": nuevo_id, "tipo": tipo, "nombre": nombre, "correo": correo,
        "telefono": telefono, "direccion": direccion, "edad": edad,
        "especialidad": especialidad, "experiencia": experiencia, "herramienta": herramienta,
        "documentos": urls_documentos, "estatus": "Pendiente",
        "vinculo_id": None, "codigo_acceso": None, "codigo_usado": False,
        "creado": datetime.now(),
    }
    st.session_state.registros_df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
    return nuevo_id


def obtener_solicitudes_registro(estatus="Pendiente") -> pd.DataFrame:
    df = st.session_state.registros_df
    if estatus:
        return df[df.estatus == estatus]
    return df


def aprobar_solicitud_registro(registro_id):
    df = st.session_state.registros_df
    idx = df.index[df.registro_id == registro_id]
    if len(idx) == 0:
        return {"ok": False, "error": "solicitud no encontrada"}
    i = idx[0]
    fila = df.loc[i]
    codigo = _generar_codigo_acceso()

    if fila.tipo == "TECNICO":
        tecnicos = st.session_state.tecnicos_df
        nuevo_tecnico_id = f"T-{len(tecnicos) + 1:03d}"
        foto_perfil_url = (fila.documentos or {}).get("foto_perfil")
        nueva_fila = {
            "tecnico_id": nuevo_tecnico_id, "nombre": fila.nombre, "especialidad": fila.especialidad,
            "zona": fila.direccion, "telefono": fila.telefono, "estatus": "Activo",
            "membresia_al_corriente": False, "calificacion_prom": None,
            "num_calificaciones": 0, "rechazos": 0, "foto_perfil_url": foto_perfil_url,
        }
        st.session_state.tecnicos_df = pd.concat([tecnicos, pd.DataFrame([nueva_fila])], ignore_index=True)
        vinculo_id = nuevo_tecnico_id
    else:
        vinculo_id = f"C-{len(df) + 1:04d}"

    df.at[i, "estatus"] = "Aprobado"
    df.at[i, "vinculo_id"] = vinculo_id
    df.at[i, "codigo_acceso"] = codigo
    df.at[i, "codigo_usado"] = False
    # En modo demo no hay correo real: regresamos el código para mostrarlo en pantalla.
    return {"ok": True, "codigo": codigo, "correo": fila.correo, "vinculo_id": vinculo_id}


def rechazar_solicitud_registro(registro_id):
    df = st.session_state.registros_df
    idx = df.index[df.registro_id == registro_id]
    if len(idx) == 0:
        return {"ok": False, "error": "solicitud no encontrada"}
    df.at[idx[0], "estatus"] = "Rechazado"
    return {"ok": True}


def canjear_codigo(codigo, usuario, password):
    df = st.session_state.registros_df
    codigo = (codigo or "").strip().upper()
    fila = df[(df.codigo_acceso == codigo) & (df.estatus == "Aprobado") & (df.codigo_usado == False)]
    if fila.empty:
        return {"ok": False, "error": "Código inválido, ya usado, o la solicitud todavía no ha sido aprobada."}
    f = fila.iloc[0]
    usuarios = st.session_state.usuarios_df
    usuario_norm = (usuario or "").strip()
    if (usuarios.usuario.astype(str).str.strip().str.lower() == usuario_norm.lower()).any():
        return {"ok": False, "error": "Ese nombre de usuario ya existe, elige otro."}
    nueva_fila = {
        "usuario": usuario_norm, "password": password, "rol": f.tipo, "nombre": f.nombre,
        "tecnico_id": f.vinculo_id if f.tipo == "TECNICO" else None,
        "cliente_id": f.vinculo_id if f.tipo == "CLIENTE" else None,
    }
    st.session_state.usuarios_df = pd.concat([usuarios, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.loc[df.registro_id == f.registro_id, "codigo_usado"] = True
    return {"ok": True, "rol": f.tipo}
