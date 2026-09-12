import streamlit as st
from modulos import datos
from modulos.estilos import encabezado, badge_estatus

MEMBRESIA_MXN = 150


def pagina():
    tecnico_id = st.session_state.tecnico_id
    tecnicos = datos.obtener_tecnicos()
    mi_fila = tecnicos[tecnicos.tecnico_id == tecnico_id]

    if mi_fila.empty:
        st.error("No se encontró tu perfil de técnico en el sistema (demo).")
        return

    mi_fila = mi_fila.iloc[0]
    encabezado(f"Hola, {mi_fila.nombre}", f"{mi_fila.especialidad} · Zona {mi_fila.zona}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Estatus", mi_fila.estatus)
    c2.metric("Membresía", "Al corriente" if mi_fila.membresia_al_corriente else "Pendiente de pago")
    c3.metric("Calificación", mi_fila.calificacion_prom or "Sin calificar")

    if not mi_fila.membresia_al_corriente:
        st.warning(f"Tu cuota mensual de ${MEMBRESIA_MXN} MXN está pendiente. Recuerda pagarla antes del corte para seguir recibiendo alertas de trabajo.")

    st.divider()
    st.subheader("🔔 Trabajos disponibles / asignados a ti")

    solicitudes = datos.obtener_solicitudes()
    disponibles = solicitudes[solicitudes.estatus == "Pendiente"]
    mias = solicitudes[solicitudes.tecnico_id == tecnico_id]

    if not disponibles.empty:
        st.caption("Oportunidades sin asignar en tu categoría")
        for _, fila in disponibles[disponibles.categoria == mi_fila.especialidad].iterrows():
            with st.container(border=True):
                st.markdown(f"**{fila.categoria}** · {fila.zona} &nbsp;&nbsp;{badge_estatus(fila.estatus)}", unsafe_allow_html=True)
                st.write(fila.descripcion)
                st.caption(f"Urgencia: {fila.urgencia}")
                st.info("El administrador confirmará la asignación final.")

    st.subheader("Mis trabajos")
    if mias.empty:
        st.info("Aún no tienes trabajos asignados.")
    for _, fila in mias.sort_values("creado", ascending=False).iterrows():
        with st.container(border=True):
            st.markdown(f"**{fila.solicitud_id}** · {fila.categoria} · {fila.zona} &nbsp;&nbsp;{badge_estatus(fila.estatus)}", unsafe_allow_html=True)
            st.write(fila.descripcion)
            st.caption(f"Cliente: {fila.cliente_nombre} · Costo acordado: {fila.costo if fila.costo else 'por definir'}")
            if fila.estatus == "Asignado":
                if st.button("Marcar en curso", key=f"tec_curso_{fila.solicitud_id}"):
                    datos.actualizar_estatus_solicitud(fila.solicitud_id, "En curso")
                    st.rerun()
            elif fila.estatus == "En curso":
                if st.button("Marcar completado", key=f"tec_completo_{fila.solicitud_id}"):
                    datos.actualizar_estatus_solicitud(fila.solicitud_id, "Completado")
                    st.rerun()
