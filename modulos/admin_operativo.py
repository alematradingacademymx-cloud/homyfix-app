import streamlit as st
from modulos import datos
from modulos.estilos import encabezado, badge_estatus

MEMBRESIA_MXN = 150


def pagina():
    encabezado("Panel Admin Operativo", "Despacho de trabajos, validación de técnicos y cuotas")

    tab_solicitudes, tab_tecnicos = st.tabs(["📋 Solicitudes", "🧰 Técnicos"])

    with tab_solicitudes:
        _tab_solicitudes()

    with tab_tecnicos:
        _tab_tecnicos()


def _tab_solicitudes():
    df = datos.obtener_solicitudes()
    if df.empty:
        st.info("Todavía no hay solicitudes registradas.")
        return

    pendientes = df[df.estatus.isin(["Pendiente", "Asignado", "En curso"])]
    st.caption(f"{len(pendientes)} solicitud(es) activa(s)")

    for _, fila in df.sort_values("creado", ascending=False).iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f"**{fila.solicitud_id}** · {fila.categoria} · {fila.zona} "
                    f"&nbsp;&nbsp;{badge_estatus(fila.estatus)}",
                    unsafe_allow_html=True,
                )
                st.write(fila.descripcion)
                st.caption(f"Cliente: {fila.cliente_nombre} · Urgencia: {fila.urgencia}")
            with col2:
                if fila.estatus == "Pendiente":
                    tecnicos_activos = datos.obtener_tecnicos()
                    tecnicos_activos = tecnicos_activos[tecnicos_activos.estatus == "Activo"]
                    opciones = tecnicos_activos.nombre + " (" + tecnicos_activos.tecnico_id + ")"
                    seleccion = st.selectbox(
                        "Asignar técnico", opciones, key=f"sel_{fila.solicitud_id}",
                        label_visibility="collapsed", placeholder="Elegir técnico",
                        index=None,
                    )
                    costo = st.number_input(
                        "Costo (MXN)", min_value=0, step=50, key=f"costo_{fila.solicitud_id}"
                    )
                    if st.button("Asignar", key=f"btn_{fila.solicitud_id}", use_container_width=True):
                        if seleccion:
                            tecnico_id = seleccion.split("(")[-1].rstrip(")")
                            datos.asignar_tecnico(fila.solicitud_id, tecnico_id, costo or None)
                            st.rerun()
                        else:
                            st.warning("Elige un técnico primero")
                elif fila.estatus in ("Asignado", "En curso"):
                    siguiente = "En curso" if fila.estatus == "Asignado" else "Completado"
                    if st.button(f"Marcar {siguiente}", key=f"avanzar_{fila.solicitud_id}", use_container_width=True):
                        datos.actualizar_estatus_solicitud(fila.solicitud_id, siguiente)
                        st.rerun()

    st.divider()
    st.subheader("Nueva solicitud manual (ej. recibida por WhatsApp)")
    with st.form("nueva_solicitud_admin", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cliente_nombre = c1.text_input("Nombre del cliente")
        categoria = c2.selectbox("Categoría", ["Plomería", "Electricidad", "Pintura", "Albañilería", "Carpintería", "Otro"])
        c3, c4 = st.columns(2)
        zona = c3.text_input("Zona / colonia")
        urgencia = c4.selectbox("Urgencia", ["Inmediata", "Para hoy", "Para mañana", "Sin prisa"])
        descripcion = st.text_area("Descripción del problema")
        if st.form_submit_button("Registrar solicitud"):
            if cliente_nombre and zona and descripcion:
                nuevo_id = datos.crear_solicitud("C-manual", cliente_nombre, categoria, zona, descripcion, urgencia)
                st.success(f"Solicitud {nuevo_id} registrada")
                st.rerun()
            else:
                st.warning("Completa nombre, zona y descripción")


def _tab_tecnicos():
    df = datos.obtener_tecnicos()
    st.dataframe(
        df[["tecnico_id", "nombre", "especialidad", "zona", "telefono", "estatus", "membresia_al_corriente", "calificacion_prom"]],
        use_container_width=True, hide_index=True,
    )

    pendientes = df[df.estatus == "Pendiente de validación"]
    if not pendientes.empty:
        st.subheader("Pendientes de validar")
        for _, fila in pendientes.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{fila.nombre}** · {fila.especialidad} · {fila.zona}")
            if c2.button("Aprobar", key=f"aprobar_{fila.tecnico_id}"):
                datos.actualizar_estatus_tecnico(fila.tecnico_id, "Activo")
                st.rerun()
            if c3.button("Rechazar", key=f"rechazar_{fila.tecnico_id}"):
                datos.actualizar_estatus_tecnico(fila.tecnico_id, "Suspendido")
                st.rerun()

    st.divider()
    st.subheader("Dar de alta técnico manualmente")
    with st.form("alta_tecnico", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre completo")
        especialidad = c2.selectbox("Especialidad", ["Plomería", "Electricidad", "Pintura", "Albañilería", "Carpintería", "Otro"])
        c3, c4 = st.columns(2)
        zona = c3.text_input("Zona donde trabaja")
        telefono = c4.text_input("WhatsApp / teléfono")
        if st.form_submit_button("Registrar técnico"):
            if nombre and zona and telefono:
                nuevo_id = datos.agregar_tecnico(nombre, especialidad, zona, telefono)
                st.success(f"Técnico {nuevo_id} registrado (queda pendiente de validación)")
                st.rerun()
            else:
                st.warning("Completa nombre, zona y teléfono")
