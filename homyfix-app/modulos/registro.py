"""
Alta de nuevos técnicos y clientes con verificación de documentos.

Reemplaza el registro manual en Google Sheets: la persona llena su
solicitud con sus documentos aquí mismo en la app, el equipo la revisa a
mano (referencias, antecedentes, trabajos previos) desde el panel admin, y
al aprobarla se genera un código de acceso de un solo uso que se le envía
por correo para que cree su propio usuario y contraseña.
"""

import streamlit as st
from modulos import datos

TIPOS_ARCHIVO_DOC = ["jpg", "jpeg", "png", "pdf"]
TIPOS_ARCHIVO_FOTO = ["jpg", "jpeg", "png"]

ESPECIALIDADES = ["Plomería", "Electricidad", "Pintura", "Albañilería", "Herrería", "Carpintería", "Otro"]
EXPERIENCIA_OPCIONES = ["0 - 1 años", "2 - 5 años", "+5 años", "+10 años"]
HERRAMIENTA_OPCIONES = ["Sí / Completa", "Sí / Básica", "No / Necesito que me presten"]

TERMINOS_TECNICO = """
**ACUERDO DE COLABORACIÓN, INTERMEDIACIÓN MERCANTIL Y USO DE PLATAFORMA**

Homyfix ("LA PLATAFORMA") actúa como intermediario digital para conectar a
técnicos independientes ("EL PROFESIONAL") con clientes que requieren
servicios de mantenimiento, reparación o construcción.

No existe relación laboral entre las partes: EL PROFESIONAL trabaja de forma
independiente, con recursos propios, libertad de horario y autonomía técnica.
Este acuerdo es de naturaleza puramente mercantil.

EL PROFESIONAL cubrirá una cuota mensual de recuperación (actualmente
$150.00 MXN, sujeta a cambios sin previo aviso) para mantener acceso a la
red de contactos. EL PROFESIONAL cobra directamente a los clientes por sus
servicios; Homyfix no recibe ese dinero salvo pacto en contrario.

EL PROFESIONAL es el único responsable de la calidad, ejecución y garantía
de los trabajos realizados, así como de cualquier daño o incidente ocurrido
durante el servicio, liberando a Homyfix de cualquier responsabilidad al
respecto.

EL PROFESIONAL se compromete a presentarse puntual y debidamente
identificado, tratar con respeto a los clientes, no realizar cobros
distintos a los pactados y no compartir los datos de los clientes con
terceros.

Homyfix se reserva el derecho de dar de baja a EL PROFESIONAL de forma
inmediata ante quejas recurrentes, incumplimiento de la cuota, o violación
de las normas de conducta o seguridad.

El nombre, logotipo y metodología operativa de Homyfix son propiedad
intelectual exclusiva de la marca.
"""

TERMINOS_CLIENTE = """
Homyfix te pide una identificación oficial únicamente para verificar tu
identidad y evitar perfiles falsos o duplicados que puedan afectar a otros
usuarios y a los técnicos de la red. Tus documentos se revisan solo para
ese fin y no se comparten con los técnicos ni con terceros.
"""


def _volver():
    st.session_state.vista_publica = "login"
    st.rerun()


def formulario_tecnico():
    st.markdown("### 🧰 Quiero ser técnico Homyfix")
    st.caption(
        "Únete a la red de expertos de confianza. Revisamos cada solicitud a mano "
        "(documentos, referencias y trabajos previos) antes de aprobarla."
    )

    with st.form("registro_tecnico"):
        nombre = st.text_input("Nombre completo (como aparece en tu INE)")
        correo = st.text_input("Correo electrónico — aquí recibirás tu código de acceso")
        whatsapp = st.text_input("Número de WhatsApp (donde recibirás alertas de trabajo)")
        direccion = st.text_input("Dirección (calle, colonia y municipio)")
        edad = st.number_input("Edad", min_value=18, max_value=90, step=1, value=18)

        st.markdown("**Habilidades y experiencia**")
        especialidad = st.selectbox("¿Cuál es tu especialidad principal?", ESPECIALIDADES)
        experiencia = st.selectbox("Años de experiencia en tu oficio", EXPERIENCIA_OPCIONES)
        herramienta = st.selectbox("¿Cuentas con herramienta propia?", HERRAMIENTA_OPCIONES)

        st.markdown("**Documentación y seguridad** (todo obligatorio)")
        ine_frente = st.file_uploader("INE — frente", type=TIPOS_ARCHIVO_DOC, key="reg_tec_ine_f")
        ine_reverso = st.file_uploader("INE — reverso", type=TIPOS_ARCHIVO_DOC, key="reg_tec_ine_r")
        comprobante = st.file_uploader(
            "Comprobante de domicilio (luz, agua o teléfono — no mayor a 2 meses)",
            type=TIPOS_ARCHIVO_DOC, key="reg_tec_comp",
        )
        carta1 = st.file_uploader("Carta de recomendación 1", type=TIPOS_ARCHIVO_DOC, key="reg_tec_c1")
        carta2 = st.file_uploader("Carta de recomendación 2", type=TIPOS_ARCHIVO_DOC, key="reg_tec_c2")
        trabajo1 = st.file_uploader("Foto de trabajo anterior 1", type=TIPOS_ARCHIVO_FOTO, key="reg_tec_t1")
        trabajo2 = st.file_uploader("Foto de trabajo anterior 2", type=TIPOS_ARCHIVO_FOTO, key="reg_tec_t2")
        trabajo3 = st.file_uploader("Foto de trabajo anterior 3", type=TIPOS_ARCHIVO_FOTO, key="reg_tec_t3")
        antecedentes = st.file_uploader(
            "Carta de antecedentes no penales", type=TIPOS_ARCHIVO_DOC, key="reg_tec_ant",
        )
        foto_perfil = st.file_uploader(
            "Foto de perfil (selfie o foto formal, sin gorra) — el cliente la verá para reconocerte",
            type=TIPOS_ARCHIVO_FOTO, key="reg_tec_perfil",
        )

        with st.expander("Ver términos legales y acuerdo de colaboración"):
            st.markdown(TERMINOS_TECNICO)
        acepto = st.checkbox("Acepto los términos legales y el acuerdo de colaboración")

        enviado = st.form_submit_button("Enviar solicitud", use_container_width=True)

        if enviado:
            documentos = {
                "ine_frente": ine_frente, "ine_reverso": ine_reverso, "comprobante_domicilio": comprobante,
                "carta_recomendacion_1": carta1, "carta_recomendacion_2": carta2,
                "foto_trabajo_1": trabajo1, "foto_trabajo_2": trabajo2, "foto_trabajo_3": trabajo3,
                "carta_antecedentes": antecedentes, "foto_perfil": foto_perfil,
            }
            faltan_datos = not (nombre and correo and whatsapp and direccion)
            faltan_docs = any(v is None for v in documentos.values())
            if faltan_datos or faltan_docs or not acepto:
                st.warning("Completa todos los campos, sube todos los documentos y acepta los términos.")
            else:
                with st.spinner("Enviando tu solicitud..."):
                    datos.enviar_solicitud_registro(
                        tipo="TECNICO", nombre=nombre, correo=correo, telefono=whatsapp,
                        direccion=direccion, edad=int(edad), especialidad=especialidad,
                        experiencia=experiencia, herramienta=herramienta, documentos=documentos,
                    )
                st.success(
                    "¡Listo! Tu solicitud fue enviada. En cuanto la revisemos y aprobemos "
                    "(documentos, referencias y trabajos previos) te llegará un correo con tu "
                    "código de acceso para crear tu usuario y contraseña."
                )
                st.balloons()

    if st.button("⬅️ Volver", key="volver_tecnico"):
        _volver()


def formulario_cliente():
    st.markdown("### 🏠 Quiero ser cliente Homyfix")
    st.caption("Verificamos tu identidad con tu INE para evitar perfiles falsos o duplicados.")

    with st.form("registro_cliente"):
        nombre = st.text_input("Nombre completo (como aparece en tu INE)")
        correo = st.text_input("Correo electrónico — aquí recibirás tu código de acceso")
        whatsapp = st.text_input("Número de WhatsApp / teléfono")
        direccion = st.text_input("Dirección (calle, colonia y municipio)")

        st.markdown("**Verificación de identidad**")
        ine_frente = st.file_uploader("INE — frente", type=TIPOS_ARCHIVO_DOC, key="reg_cli_ine_f")
        ine_reverso = st.file_uploader("INE — reverso", type=TIPOS_ARCHIVO_DOC, key="reg_cli_ine_r")

        with st.expander("¿Para qué piden esto?"):
            st.markdown(TERMINOS_CLIENTE)
        acepto = st.checkbox("Acepto que Homyfix use mi identificación solo para verificar mi identidad")

        enviado = st.form_submit_button("Enviar solicitud", use_container_width=True)

        if enviado:
            documentos = {"ine_frente": ine_frente, "ine_reverso": ine_reverso}
            faltan_datos = not (nombre and correo and whatsapp)
            faltan_docs = any(v is None for v in documentos.values())
            if faltan_datos or faltan_docs or not acepto:
                st.warning("Completa tus datos, sube tu INE (frente y reverso) y acepta la verificación.")
            else:
                with st.spinner("Enviando tu solicitud..."):
                    datos.enviar_solicitud_registro(
                        tipo="CLIENTE", nombre=nombre, correo=correo, telefono=whatsapp,
                        direccion=direccion, documentos=documentos,
                    )
                st.success(
                    "¡Listo! En cuanto verifiquemos tu identidad (normalmente en minutos) te "
                    "llegará un correo con tu código de acceso para crear tu usuario y contraseña."
                )
                st.balloons()

    if st.button("⬅️ Volver", key="volver_cliente"):
        _volver()


def formulario_canjear():
    st.markdown("### 🔑 Ya tengo mi código de acceso")
    st.caption("Crea tu usuario y contraseña con el código de 8 caracteres que te enviamos por correo.")

    with st.form("canjear_codigo"):
        codigo = st.text_input("Código de acceso")
        usuario = st.text_input("Usuario que quieres usar para entrar")
        password = st.text_input("Contraseña", type="password")
        password2 = st.text_input("Confirma tu contraseña", type="password")
        enviado = st.form_submit_button("Crear mi cuenta", use_container_width=True)

        if enviado:
            if not (codigo and usuario and password):
                st.warning("Completa todos los campos.")
            elif password != password2:
                st.warning("Las contraseñas no coinciden.")
            else:
                resultado = datos.canjear_codigo(codigo, usuario, password)
                if resultado.get("ok"):
                    st.success("¡Cuenta creada! Ya puedes iniciar sesión con tu usuario y contraseña.")
                else:
                    st.error(resultado.get("error", "No se pudo crear la cuenta."))

    if st.button("⬅️ Volver", key="volver_canjear"):
        _volver()
