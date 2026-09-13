import pandas as pd
import streamlit as st
from modulos import datos
from modulos.estilos import encabezado, badge_estatus, linea_tiempo


def _es_si(valor):
    """True si el valor (bool real o texto 'True'/'TRUE' que llega de Sheets) es afirmativo."""
    return valor in (True, "True", "TRUE", "true")


def _tiene_valor(valor):
    """Distingue 'no se guardó nada todavía' (None/NaN/'') de un valor real (incluido False)."""
    if valor is None:
        return False
    try:
        if pd.isna(valor):
            return False
    except (TypeError, ValueError):
        pass
    return valor != ""


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

                if fila.estatus in ("Asignado", "En Visita", "Cotizado", "Aceptado", "En Camino", "Cerca", "En curso"):
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

                if fila.tecnico_id and fila.estatus in ("Aceptado", "En Camino", "Cerca", "En curso", "Completado", "Calificado"):
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

                if fila.estatus not in ("En Puja", "Cancelado"):
                    linea_tiempo(fila.estatus)

                if fila.estatus == "Completado":
                    etiqueta = "¿Cómo calificarías la visita y la compostura?" if fila.tipo_cotizacion == "Visita" else "¿Cómo calificarías la compostura?"
                    st.markdown(f"**{etiqueta}**")

                    key_cal = f"cal_{fila.solicitud_id}"
                    st.session_state.setdefault(key_cal, 5)
                    cols_num = st.columns(5)
                    for i, col in enumerate(cols_num, start=1):
                        if col.button(
                            str(i), key=f"{key_cal}_btn_{i}", use_container_width=True,
                            type="primary" if st.session_state[key_cal] == i else "secondary",
                        ):
                            st.session_state[key_cal] = i
                            st.rerun()

                    key_cobro = f"cobro_{fila.solicitud_id}"
                    st.session_state.setdefault(key_cobro, "correcto")
                    st.caption("¿El cobro fue el indicado por la app?")
                    c1, c2 = st.columns(2)
                    if c1.button(
                        "💰 Cobró lo indicado", key=f"{key_cobro}_ok", use_container_width=True,
                        type="primary" if st.session_state[key_cobro] == "correcto" else "secondary",
                    ):
                        st.session_state[key_cobro] = "correcto"
                        st.rerun()
                    if c2.button(
                        "⚠️ Cobró más de lo indicado", key=f"{key_cobro}_mas", use_container_width=True,
                        type="primary" if st.session_state[key_cobro] == "mas" else "secondary",
                    ):
                        st.session_state[key_cobro] = "mas"
                        st.rerun()

                    key_prof = f"prof_{fila.solicitud_id}"
                    st.session_state.setdefault(key_prof, "si")
                    st.caption("¿El servicio fue limpio y profesional?")
                    c3, c4 = st.columns(2)
                    if c3.button(
                        "✅ Sí, limpio y profesional", key=f"{key_prof}_si", use_container_width=True,
                        type="primary" if st.session_state[key_prof] == "si" else "secondary",
                    ):
                        st.session_state[key_prof] = "si"
                        st.rerun()
                    if c4.button(
                        "❌ No", key=f"{key_prof}_no", use_container_width=True,
                        type="primary" if st.session_state[key_prof] == "no" else "secondary",
                    ):
                        st.session_state[key_prof] = "no"
                        st.rerun()

                    if st.button("Enviar calificación", key=f"btn_{key_cal}", use_container_width=True):
                        datos.calificar_solicitud(
                            fila.solicitud_id,
                            st.session_state[key_cal],
                            cobro_correcto=(st.session_state[key_cobro] == "correcto"),
                            servicio_profesional=(st.session_state[key_prof] == "si"),
                        )
                        st.rerun()
                elif fila.estatus == "Calificado":
                    st.caption(f"Tu calificación: {'⭐' * int(fila.calificacion)}")
                    valor_cobro = fila.get("cobro_correcto") if hasattr(fila, "get") else None
                    if _tiene_valor(valor_cobro):
                        st.caption("💰 Cobro correcto" if _es_si(valor_cobro) else "⚠️ Cobró más de lo indicado")
                    valor_prof = fila.get("servicio_profesional") if hasattr(fila, "get") else None
                    if _tiene_valor(valor_prof):
                        st.caption("✅ Servicio limpio y profesional" if _es_si(valor_prof) else "❌ Servicio no fue limpio/profesional")
