import streamlit as st
from modulos import datos
from modulos.estilos import encabezado

MEMBRESIA_MXN = 150


def pagina():
    encabezado("Panel Admin Socio", "Métricas globales del negocio (solo lectura)")

    tecnicos = datos.obtener_tecnicos()
    solicitudes = datos.obtener_solicitudes()

    activos = (tecnicos.estatus == "Activo").sum()
    al_corriente = tecnicos[tecnicos.estatus == "Activo"].membresia_al_corriente.sum()
    ingreso_membresias = al_corriente * MEMBRESIA_MXN

    completadas = (solicitudes.estatus.isin(["Completado", "Calificado"])).sum()
    pendientes = (solicitudes.estatus == "Pendiente").sum()
    en_proceso = (solicitudes.estatus.isin(["Asignado", "En Visita", "Cotizado", "En Puja", "Aceptado", "En curso"])).sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='app-card'><b>Técnicos activos</b><h2>{activos}</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='app-card'><b>Cuotas al corriente</b><h2>{al_corriente}</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='app-card'><b>Ingreso mensual estimado</b><h2>${ingreso_membresias:,.0f}</h2></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='app-card'><b>Trabajos completados</b><h2>{completadas}</h2></div>", unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Solicitudes pendientes de asignar", pendientes)
    c2.metric("Solicitudes en proceso", en_proceso)

    st.divider()
    st.subheader("Técnicos por zona")
    st.bar_chart(tecnicos.groupby("zona").size())

    st.subheader("Solicitudes por categoría")
    st.bar_chart(solicitudes.groupby("categoria").size())

    st.caption(
        "Nota: estos números son de la fase beta con datos de ejemplo/en memoria. "
        "Cuando se conecte la fuente real (Google Sheets), este panel se vuelve el "
        "tablero financiero real del negocio."
    )
