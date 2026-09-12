import streamlit as st
from modulos import datos
from modulos.estilos import encabezado, badge_estatus

MEMBRESIA_MXN = 150


def pagina():
    encabezado("Panel Admin Operativo", "Despacho de trabajos, pujas, validación de técnicos y cuotas")

    tab_solicitudes, tab_puja, tab_tecnicos = st.tabs(["📋 Solicitudes", "💰 Pujas activas", "🧰 Técnicos"])

    with tab_solicitudes:
        _tab_solicitudes()

    with tab_puja:
        _tab_puja()

    with tab_tecnicos:
        _tab_tecnicos()


def _tab_solicitudes():
    df = datos.obtener_solicitudes()
    if df.empty:
        st.info("Todavía no hay solicitudes registradas.")
        return

    activas = df[df.estatus.isin(["Pendiente", "Asignado", "En Visita", "Cotizado", "En Puja", "Aceptado", "En curso"])]
    st.caption(f"{len(activas)} solicitud(es) activa(s)")

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
                if fila.estatus in ("Asignado", "En Visita", "Cotizado", "Aceptado", "En curso"):
                    st.caption(f"🔐 Código de seguridad: **{fila.codigo_seguridad}**")
                if fila.estatus == "Cotizado" and fila.costo_reparacion:
                    st.caption(f"Cotización enviada: ${fila.costo_reparacion} ({fila.tipo_cotizacion})")
                if fila.estatus == "En Puja":
                    st.warning("En puja abierta a todos los técnicos — revisa la pestaña 'Pujas activas' para ver las ofertas y cerrarla.")
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
                    st.caption("El técnico cotizará el trabajo desde su panel (directo o con visita).")
                    if st.button("Asignar", key=f"btn_{fila.solicitud_id}", use_container_width=True):
                        if seleccion:
                            tecnico_id = seleccion.split("(")[-1].rstrip(")")
                            datos.asignar_tecnico(fila.solicitud_id, tecnico_id)
                            st.rerun()
                        else:
                            st.warning("Elige un técnico primero")
                elif fila.estatus == "Aceptado":
                    st.caption("Esperando que el técnico marque 'En curso'")
                elif fila.estatus == "En curso":
                    if st.button("Marcar completado", key=f"avanzar_{fila.solicitud_id}", use_container_width=True):
                        datos.actualizar_estatus_solicitud(fila.solicitud_id, "Completado")
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


def _tab_puja():
    st.caption(
        "Aquí ves todas las ofertas de cada puja — esta información es solo para el equipo de despacho, "
        "nunca se muestra a clientes ni técnicos."
    )
    solicitudes = datos.obtener_solicitudes()
    en_puja = solicitudes[solicitudes.estatus == "En Puja"]

    if en_puja.empty:
        st.info("No hay solicitudes en puja en este momento.")
        return

    tecnicos = datos.obtener_tecnicos()

    for _, fila in en_puja.sort_values("creado", ascending=False).iterrows():
        with st.container(border=True):
            st.markdown(f"**{fila.solicitud_id}** · {fila.categoria} · {fila.zona}", unsafe_allow_html=True)
            st.write(fila.descripcion)
            if fila.diagnostico:
                st.caption(f"Diagnóstico (falla actualizada): {fila.diagnostico}")
            if fila.foto_url:
                st.caption(f"[Ver foto de la falla]({fila.foto_url})")

            pujas = datos.obtener_pujas(fila.solicitud_id)
            if pujas.empty:
                st.info("Todavía no hay ofertas de ningún técnico.")
                continue

            comparativo = pujas.merge(
                tecnicos[["tecnico_id", "nombre", "calificacion_prom"]], on="tecnico_id", how="left"
            )
            comparativo = comparativo.sort_values(
                ["calificacion_prom", "costo"], ascending=[False, True]
            )
            st.dataframe(
                comparativo[["tecnico_id", "nombre", "calificacion_prom", "costo"]].rename(
                    columns={
                        "tecnico_id": "ID",
                        "nombre": "Técnico",
                        "calificacion_prom": "Calificación",
                        "costo": "Oferta (MXN)",
                    }
                ),
                use_container_width=True, hide_index=True,
            )
            ganador = comparativo.iloc[0]
            st.caption(f"Ganaría automáticamente: **{ganador.nombre}** (mejor calificación; precio solo desempata en caso de empate).")
            if st.button("Cerrar puja y asignar automáticamente", key=f"cerrar_puja_{fila.solicitud_id}", use_container_width=True):
                datos.cerrar_puja(fila.solicitud_id)
                st.success("Puja cerrada, técnico asignado")
                st.rerun()


def _tab_tecnicos():
    df = datos.obtener_tecnicos()
    st.dataframe(
        df[["tecnico_id", "nombre", "especialidad", "zona", "telefono", "estatus", "membresia_al_corriente", "calificacion_prom"]],
        use_container_width=True, hide_index=True,
    )

    if not df.empty:
        st.subheader("Membresía")
        for _, fila in df.iterrows():
            c1, c2 = st.columns([3, 1])
            al_corriente = bool(fila.membresia_al_corriente)
            c1.write(f"**{fila.nombre}** ({fila.tecnico_id}) · {'✅ Al corriente' if al_corriente else '⛔ Vencida / pendiente'}")
            etiqueta = "Marcar vencida" if al_corriente else "Marcar al corriente"
            if c2.button(etiqueta, key=f"membresia_{fila.tecnico_id}", use_container_width=True):
                datos.actualizar_membresia_tecnico(fila.tecnico_id, not al_corriente)
                st.rerun()

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
