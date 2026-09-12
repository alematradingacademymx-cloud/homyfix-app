import streamlit as st
from modulos import datos_demo as datos
from modulos.estilos import encabezado, badge_estatus


def pagina():
    cliente_id = st.session_state.cliente_id
    nombre = st.session_state.nombre
    encabezado(f"Hola, {nombre}", "Solicita un servicio o revisa el estatus de tus solicitudes")

    tab_nueva, tab_mis = st.tabs(["🛠️ Nueva solicitud", "📋 Mis solicitudes"])

    with tab_nueva:
        with st.form("nueva_solicitud_cliente", clear_on_submit=True):
            categoria = st.selectbox("¿Qué necesitas?", ["Plomería", "Electricidad", "Pintura", "Albañilería", "Carpintería", "Otro"])
            zona = st.text_input("Tu colonia / zona")
            urgencia = st.selectbox("Urgencia", ["Inmediata", "Para hoy", "Para mañana", "Sin prisa"])
            descripcion = st.text_area("Cuéntanos qué pasó")
            if st.form_submit_button("Enviar solicitud"):
                if zona and descripcion:
                    nuevo_id = datos.crear_solicitud(cliente_id, nombre, categoria, zona, descripcion, urgencia)
                    st.success(f"¡Listo! Tu solicitud {nuevo_id} fue enviada. Te avisaremos en cuanto tengamos un técnico cerca.")
                else:
                    st.warning("Completa tu zona y una breve descripción")

    with tab_mis:
        solicitudes = datos.obtener_solicitudes()
        mias = solicitudes[solicitudes.cliente_id == cliente_id]
        if mias.empty:
            st.info("Todavía no tienes solicitudes.")
        for _, fila in mias.sort_values("creado", ascending=False).iterrows():
            with st.container(border=True):
                st.markdown(f"**{fila.solicitud_id}** · {fila.categoria} · {fila.zona} &nbsp;&nbsp;{badge_estatus(fila.estatus)}", unsafe_allow_html=True)
                st.write(fila.descripcion)
                if fila.tecnico_id:
                    tecnico = datos.obtener_tecnicos()
                    tecnico = tecnico[tecnico.tecnico_id == fila.tecnico_id]
                    if not tecnico.empty:
                        t = tecnico.iloc[0]
                        st.caption(f"Técnico asignado: {t.nombre} · Costo: ${fila.costo}")
                if fila.estatus == "Completado":
                    calificacion = st.slider("¿Cómo calificarías el servicio?", 1, 5, 5, key=f"cal_{fila.solicitud_id}")
                    if st.button("Enviar calificación", key=f"btn_cal_{fila.solicitud_id}"):
                        datos.calificar_solicitud(fila.solicitud_id, calificacion)
                        st.rerun()
                elif fila.estatus == "Calificado":
                    st.caption(f"Tu calificación: {'⭐' * int(fila.calificacion)}")
