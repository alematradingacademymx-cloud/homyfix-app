import pandas as pd
import streamlit as st
from modulos import datos, geo
from modulos.estilos import encabezado, badge_estatus


def pagina():
    cliente_id = st.session_state.cliente_id
    nombre = st.session_state.nombre
    encabezado(f"Hola, {nombre}", "Solicita un servicio o revisa el estatus de tus solicitudes")

    tab_nueva, tab_mis = st.tabs(["🛠️ Nueva solicitud", "📋 Mis solicitudes"])

    with tab_nueva:
        st.caption("Opcional pero recomendado: comparte tu ubicación exacta así el técnico ve el tiempo estimado de llegada real hacia tu domicilio.")
        ubicacion = geo.obtener_ubicacion_navegador()
        if ubicacion:
            st.session_state["nueva_solicitud_lat"] = ubicacion[0]
            st.session_state["nueva_solicitud_lng"] = ubicacion[1]
        if st.session_state.get("nueva_solicitud_lat"):
            st.success("📍 Ubicación compartida — se guardará junto con tu solicitud.")

        with st.form("nueva_solicitud_cliente", clear_on_submit=True):
            categoria = st.selectbox("¿Qué necesitas?", ["Plomería", "Electricidad", "Pintura", "Albañilería", "Carpintería", "Otro"])
            zona = st.text_input("Tu colonia / zona")
            urgencia = st.selectbox("Urgencia", ["Inmediata", "Para hoy", "Para mañana", "Sin prisa"])
            descripcion = st.text_area("Cuéntanos qué pasó")
            if st.form_submit_button("Enviar solicitud"):
                if zona and descripcion:
                    nuevo_id = datos.crear_solicitud(
                        cliente_id, nombre, categoria, zona, descripcion, urgencia,
                        cliente_lat=st.session_state.get("nueva_solicitud_lat"),
                        cliente_lng=st.session_state.get("nueva_solicitud_lng"),
                    )
                    st.session_state.pop("nueva_solicitud_lat", None)
                    st.session_state.pop("nueva_solicitud_lng", None)
                    st.success(f"¡Listo! Tu solicitud {nuevo_id} fue enviada. Te avisaremos en cuanto tengamos un técnico cerca.")
                    st.rerun()
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

                if fila.estatus in ("Asignado", "En Visita", "Cotizado", "Aceptado", "En curso"):
                    st.info(
                        f"🔐 Código de seguridad: **{fila.codigo_seguridad}** — dáselo al técnico cuando "
                        f"llegue a tu casa para confirmar que sí es de Homyfix."
                    )

                if fila.estatus == "En Puja":
                    st.warning("No aceptaste la cotización anterior. Estamos buscando otro técnico con mejor precio para ti — te avisaremos en cuanto tengamos una nueva propuesta.")

                if fila.estatus == "Cotizado":
                    if fila.tipo_cotizacion == "Visita" and fila.costo_visita:
                        st.caption(f"Costo de la visita/diagnóstico: ${fila.costo_visita}")
                    st.markdown(f"### Costo de la reparación: ${fila.costo_reparacion}")
                    if fila.diagnostico:
                        st.caption(f"Diagnóstico del técnico: {fila.diagnostico}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Aceptar", key=f"aceptar_{fila.solicitud_id}", use_container_width=True):
                        datos.aceptar_solicitud(fila.solicitud_id)
                        st.rerun()
                    if c2.button("❌ Rechazar (buscar otro precio)", key=f"rechazar_{fila.solicitud_id}", use_container_width=True):
                        datos.rechazar_solicitud(fila.solicitud_id)
                        st.rerun()

                if fila.tecnico_id and fila.estatus in ("Aceptado", "En curso", "Completado", "Calificado"):
                    tecnico = datos.obtener_tecnicos()
                    tecnico = tecnico[tecnico.tecnico_id == fila.tecnico_id]
                    if not tecnico.empty:
                        t = tecnico.iloc[0]
                        foto = t.get("foto_perfil_url") if hasattr(t, "get") else None
                        if foto:
                            c1, c2 = st.columns([1, 4])
                            c1.image(foto, width=80)
                            c2.caption(f"Técnico asignado: {t.nombre} · Costo acordado: ${fila.costo_reparacion}")
                        else:
                            st.caption(f"Técnico asignado: {t.nombre} · Costo acordado: ${fila.costo_reparacion}")

                if fila.estatus in ("Aceptado", "En curso"):
                    cli_lat, cli_lng = fila.get("cliente_lat"), fila.get("cliente_lng")
                    tec_lat, tec_lng = fila.get("tecnico_lat"), fila.get("tecnico_lng")
                    tiene_cliente = cli_lat not in (None, "") and not pd.isna(cli_lat)
                    tiene_tecnico = tec_lat not in (None, "") and not pd.isna(tec_lat)
                    if not tiene_cliente:
                        st.caption("💡 Comparte tu ubicación al crear una solicitud para poder ver aquí el mapa y el tiempo estimado de llegada del técnico.")
                    elif not tiene_tecnico:
                        st.caption("📍 El técnico todavía no ha compartido su ubicación en camino.")
                    else:
                        eta = geo.calcular_eta(tec_lat, tec_lng, cli_lat, cli_lng)
                        if eta:
                            st.info(f"🚗 El técnico está a {eta['distancia_km']:.1f} km · tiempo estimado de llegada: **{eta['duracion_min']:.0f} min**")
                        else:
                            st.caption("🚗 El técnico ya está en camino (tiempo estimado no disponible por ahora).")
                        geo.mostrar_mapa(tec_lat, tec_lng, cli_lat, cli_lng, ruta=eta.get("ruta") if eta else None, key=f"mapa_{fila.solicitud_id}")

                if fila.estatus == "Completado":
                    etiqueta = "¿Cómo calificarías la visita y la compostura?" if fila.tipo_cotizacion == "Visita" else "¿Cómo calificarías la compostura?"
                    calificacion = st.slider(etiqueta, 1, 5, 5, key=f"cal_{fila.solicitud_id}")
                    if st.button("Enviar calificación", key=f"btn_cal_{fila.solicitud_id}"):
                        datos.calificar_solicitud(fila.solicitud_id, calificacion)
                        st.rerun()
                elif fila.estatus == "Calificado":
                    st.caption(f"Tu calificación: {'⭐' * int(fila.calificacion)}")
