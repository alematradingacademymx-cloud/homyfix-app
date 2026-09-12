import streamlit as st
from modulos import datos
from modulos.estilos import encabezado, badge_estatus

MEMBRESIA_MXN = 150


def _tecnicos_rechazados(fila):
    valor = fila.get("tecnicos_rechazados") if hasattr(fila, "get") else fila.tecnicos_rechazados
    if not valor:
        return []
    return [t for t in str(valor).split(",") if t]


def pagina():
    tecnico_id = st.session_state.tecnico_id
    tecnicos = datos.obtener_tecnicos()
    mi_fila = tecnicos[tecnicos.tecnico_id == tecnico_id]

    if mi_fila.empty:
        st.error("No se encontró tu perfil de técnico en el sistema (demo).")
        return

    mi_fila = mi_fila.iloc[0]
    encabezado(f"Hola, {mi_fila.nombre}", f"{mi_fila.especialidad} · Zona {mi_fila.zona}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estatus", mi_fila.estatus)
    c2.metric("Membresía", "Al corriente" if mi_fila.membresia_al_corriente else "Pendiente de pago")
    c3.metric("Calificación", mi_fila.calificacion_prom or "Sin calificar")
    c4.metric("Rechazos", int(mi_fila.get("rechazos", 0) or 0) if hasattr(mi_fila, "get") else 0)

    if not mi_fila.membresia_al_corriente:
        st.warning(f"Tu cuota mensual de ${MEMBRESIA_MXN} MXN está pendiente. Recuerda pagarla antes del corte para seguir recibiendo alertas de trabajo.")

    st.divider()
    tab_trabajos, tab_puja = st.tabs(["🔧 Mis trabajos", "💰 Oportunidades en puja"])

    solicitudes = datos.obtener_solicitudes()

    with tab_trabajos:
        mias = solicitudes[solicitudes.tecnico_id == tecnico_id]
        if mias.empty:
            st.info("Aún no tienes trabajos asignados.")

        for _, fila in mias.sort_values("creado", ascending=False).iterrows():
            with st.container(border=True):
                st.markdown(f"**{fila.solicitud_id}** · {fila.categoria} · {fila.zona} &nbsp;&nbsp;{badge_estatus(fila.estatus)}", unsafe_allow_html=True)
                st.write(fila.descripcion)
                st.caption(f"Cliente: {fila.cliente_nombre} · Urgencia: {fila.urgencia}")

                if fila.estatus in ("Asignado", "En Visita", "Cotizado", "Aceptado", "En curso"):
                    st.info(f"🔐 Código de seguridad del cliente: **{fila.codigo_seguridad}** — pídeselo al llegar para confirmar que estás en la casa correcta.")

                if fila.estatus == "Asignado":
                    modo = st.radio(
                        "¿Cómo quieres cotizar este trabajo?",
                        ["Cotizar directo (ya sé el precio)", "Necesito visitar primero para diagnosticar"],
                        key=f"modo_{fila.solicitud_id}",
                    )
                    if modo.startswith("Cotizar directo"):
                        costo = st.number_input("Costo de la reparación (MXN)", min_value=0, step=50, key=f"costo_directo_{fila.solicitud_id}")
                        if st.button("Enviar cotización", key=f"btn_directo_{fila.solicitud_id}"):
                            if costo > 0:
                                datos.cotizar_directo(fila.solicitud_id, costo)
                                st.rerun()
                            else:
                                st.warning("Coloca un costo mayor a 0")
                    else:
                        costo_visita = st.number_input("Costo de la visita/diagnóstico (MXN)", min_value=0, step=50, key=f"costo_visita_{fila.solicitud_id}")
                        if st.button("Confirmar visita", key=f"btn_visita_{fila.solicitud_id}"):
                            if costo_visita >= 0:
                                datos.solicitar_visita(fila.solicitud_id, costo_visita)
                                st.rerun()

                elif fila.estatus == "En Visita":
                    st.caption(f"Costo de visita acordado: ${fila.costo_visita}")
                    st.markdown("**Registra tu bitácora de la visita** (obligatoria, con foto, para poder cotizar la reparación)")
                    diagnostico = st.text_area("¿Cuál es la falla real que encontraste?", key=f"diag_{fila.solicitud_id}")
                    foto = st.file_uploader("Foto de la falla (obligatoria)", type=["jpg", "jpeg", "png"], key=f"foto_{fila.solicitud_id}")
                    costo_reparacion = st.number_input("Costo de la reparación (MXN)", min_value=0, step=50, key=f"costo_rep_{fila.solicitud_id}")
                    if st.button("Enviar bitácora y cotización", key=f"btn_bitacora_{fila.solicitud_id}"):
                        if not diagnostico or not foto or costo_reparacion <= 0:
                            st.warning("Completa el diagnóstico, sube la foto y coloca un costo mayor a 0")
                        else:
                            foto_url = datos.subir_foto_diagnostico(
                                fila.solicitud_id, foto.name, foto.getvalue(), foto.type,
                            )
                            datos.subir_bitacora(fila.solicitud_id, diagnostico, foto_url, costo_reparacion)
                            st.success("Bitácora enviada, esperando respuesta del cliente")
                            st.rerun()

                elif fila.estatus == "Cotizado":
                    st.info(f"Esperando que el cliente acepte o rechace el costo de ${fila.costo_reparacion}")

                elif fila.estatus == "Aceptado":
                    if st.button("Marcar en curso", key=f"tec_curso_{fila.solicitud_id}"):
                        datos.actualizar_estatus_solicitud(fila.solicitud_id, "En curso")
                        st.rerun()

                elif fila.estatus == "En curso":
                    if st.button("Marcar completado", key=f"tec_completo_{fila.solicitud_id}"):
                        datos.actualizar_estatus_solicitud(fila.solicitud_id, "Completado")
                        st.rerun()

                elif fila.estatus in ("Completado", "Calificado"):
                    st.caption(f"Costo acordado: ${fila.costo_reparacion}" + (f" · Calificación del cliente: {'⭐' * int(fila.calificacion)}" if fila.estatus == "Calificado" else ""))

    with tab_puja:
        en_puja = solicitudes[solicitudes.estatus == "En Puja"]
        en_puja = en_puja[en_puja.categoria == mi_fila.especialidad]
        en_puja = en_puja[en_puja.apply(lambda f: tecnico_id not in _tecnicos_rechazados(f), axis=1)]

        if en_puja.empty:
            st.info("No hay oportunidades en puja para tu especialidad en este momento.")

        for _, fila in en_puja.sort_values("creado", ascending=False).iterrows():
            with st.container(border=True):
                st.markdown(f"**{fila.solicitud_id}** · {fila.categoria} · {fila.zona}", unsafe_allow_html=True)
                st.write(fila.descripcion)
                if fila.diagnostico:
                    st.markdown(f"**Cliente actualizó la falla:** {fila.diagnostico}")
                if fila.foto_url:
                    st.caption(f"[Ver foto de la falla]({fila.foto_url})")
                mis_pujas = datos.obtener_pujas(fila.solicitud_id)
                mi_oferta_actual = mis_pujas[mis_pujas.tecnico_id == tecnico_id] if not mis_pujas.empty else mis_pujas
                valor_previo = int(mi_oferta_actual.iloc[0].costo) if not mi_oferta_actual.empty else 0
                oferta = st.number_input("Tu oferta (MXN)", min_value=0, step=50, value=valor_previo, key=f"oferta_{fila.solicitud_id}")
                if st.button("Enviar oferta" if valor_previo == 0 else "Actualizar oferta", key=f"btn_oferta_{fila.solicitud_id}"):
                    if oferta > 0:
                        datos.ofertar_puja(fila.solicitud_id, tecnico_id, oferta)
                        st.success("Oferta enviada")
                        st.rerun()
                    else:
                        st.warning("Coloca una oferta mayor a 0")
