import streamlit as st
from modulos import datos
from modulos.estilos import encabezado, badge_estatus

MEMBRESIA_MXN = 150


def pagina():
    encabezado("Panel Admin Operativo", "Despacho de trabajos, pujas, validación de técnicos y cuotas")

    registros_pendientes = datos.obtener_solicitudes_registro("Pendiente")
    etiqueta_registros = "📥 Registros"
    if not registros_pendientes.empty:
        etiqueta_registros = f"📥 Registros ({len(registros_pendientes)})"

    tecnicos_df = datos.obtener_tecnicos()
    n_tecnicos_pendientes = 0
    if not tecnicos_df.empty:
        n_tecnicos_pendientes = int(
            tecnicos_df.estatus.astype(str).str.strip().str.lower().str.startswith("pendiente").sum()
        )
    etiqueta_tecnicos = "🧰 Técnicos" if not n_tecnicos_pendientes else f"🧰 Técnicos (⚠️ {n_tecnicos_pendientes})"

    tab_solicitudes, tab_puja, tab_tecnicos, tab_registros = st.tabs(
        ["📋 Solicitudes", "💰 Pujas activas", etiqueta_tecnicos, etiqueta_registros]
    )

    with tab_solicitudes:
        _tab_solicitudes()

    with tab_puja:
        _tab_puja()

    with tab_tecnicos:
        _tab_tecnicos(tecnicos_df)

    with tab_registros:
        _tab_registros(registros_pendientes)


def _tab_solicitudes():
    df = datos.obtener_solicitudes()
    if df.empty:
        st.info("Todavía no hay solicitudes registradas.")
        return

    activas = df[df.estatus.isin(["Pendiente", "Asignado", "En Visita", "Cotizado", "En Puja", "Aceptado", "En Camino", "Cerca", "En curso"])]
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
                if fila.estatus in ("Asignado", "En Visita", "Cotizado", "Aceptado", "En Camino", "Cerca", "En curso"):
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
                    st.caption("Esperando que el técnico inicie su viaje")
                elif fila.estatus == "En Camino":
                    st.caption("El técnico va en camino")
                elif fila.estatus == "Cerca":
                    st.caption("El técnico está cerca del domicilio")
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


def _tab_tecnicos(df):
    pendientes = df[df.estatus.astype(str).str.strip().str.lower().str.startswith("pendiente")] if not df.empty else df
    if not pendientes.empty:
        st.markdown(
            f"### ⚠️ Pendientes de validar ({len(pendientes)})"
        )
        for _, fila in pendientes.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{fila.nombre}** · {fila.especialidad} · {fila.zona}")
                if c2.button("✅ Aprobar", key=f"aprobar_{fila.tecnico_id}", use_container_width=True):
                    datos.actualizar_estatus_tecnico(fila.tecnico_id, "Activo")
                    st.rerun()
                if c3.button("❌ Rechazar", key=f"rechazar_{fila.tecnico_id}", use_container_width=True):
                    datos.actualizar_estatus_tecnico(fila.tecnico_id, "Suspendido")
                    st.rerun()
        st.divider()

    st.subheader("Todos los técnicos")
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


_ETIQUETAS_DOC = {
    "ine_frente": "INE (frente)", "ine_reverso": "INE (reverso)",
    "comprobante_domicilio": "Comprobante de domicilio",
    "carta_recomendacion_1": "Carta de recomendación 1", "carta_recomendacion_2": "Carta de recomendación 2",
    "foto_trabajo_1": "Foto de trabajo 1", "foto_trabajo_2": "Foto de trabajo 2", "foto_trabajo_3": "Foto de trabajo 3",
    "carta_antecedentes": "Carta de antecedentes no penales", "foto_perfil": "Foto de perfil",
}


def _tab_registros(pendientes):
    st.caption(
        "Solicitudes de alta de nuevos técnicos y clientes, con sus documentos. "
        "Revísalas a mano (referencias, antecedentes, trabajos previos) antes de aprobar — "
        "al aprobar se genera un código de acceso de un solo uso y se le envía por correo "
        "a la persona para que cree su usuario y contraseña."
    )

    if pendientes.empty:
        st.info("No hay solicitudes de registro pendientes.")
        return

    for _, fila in pendientes.sort_values("creado", ascending=False).iterrows():
        etiqueta_tipo = "🧰 Técnico" if fila.tipo == "TECNICO" else "🏠 Cliente"
        with st.container(border=True):
            st.markdown(f"**{etiqueta_tipo} · {fila.nombre}** &nbsp;&nbsp;`{fila.registro_id}`", unsafe_allow_html=True)
            st.caption(f"Correo: {fila.correo} · Teléfono: {fila.telefono}" + (f" · Dirección: {fila.direccion}" if fila.direccion else ""))
            if fila.tipo == "TECNICO":
                st.caption(
                    f"Especialidad: {fila.especialidad} · Experiencia: {fila.experiencia} · "
                    f"Herramienta: {fila.herramienta} · Edad: {fila.edad}"
                )

            documentos = fila.documentos if isinstance(fila.documentos, dict) else {}
            if documentos:
                st.markdown("**Documentos:**")
                for campo, url in documentos.items():
                    etiqueta = _ETIQUETAS_DOC.get(campo, campo)
                    st.markdown(f"- [{etiqueta}]({url})")

            c1, c2 = st.columns(2)
            if c1.button("✅ Aprobar", key=f"aprobar_reg_{fila.registro_id}", use_container_width=True):
                resultado = datos.aprobar_solicitud_registro(fila.registro_id)
                if resultado.get("ok"):
                    st.success(
                        f"Aprobado. Código de acceso: **{resultado.get('codigo')}** "
                        f"(enviado a {resultado.get('correo', fila.correo)})."
                    )
                    st.rerun()
                else:
                    st.error(resultado.get("error", "No se pudo aprobar"))
            if c2.button("❌ Rechazar", key=f"rechazar_reg_{fila.registro_id}", use_container_width=True):
                datos.rechazar_solicitud_registro(fila.registro_id)
                st.rerun()
