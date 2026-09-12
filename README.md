# Homyfix — App web (fase beta)

Scaffold inicial de la app web de Homyfix, siguiendo el mismo patrón que ya usas
en tu portal educativo (Streamlit + módulos separados por sección), para que el
mantenimiento te resulte familiar.

## Qué incluye esta primera versión

4 roles con su propia vista, navegando desde un solo `app.py`:

- **Admin Operativo**: valida técnicos nuevos, ve solicitudes entrantes, asigna
  técnico y costo, avanza el estatus del trabajo. También puede dar de alta
  técnicos y registrar solicitudes manuales (por ejemplo, las que sigan llegando
  por WhatsApp mientras migras clientes al portal).
- **Admin Socio**: tablero de solo lectura con métricas (técnicos activos, cuotas
  al corriente, ingreso estimado por membresías, solicitudes por estatus,
  técnicos por zona).
- **Técnico**: ve su estatus de membresía, sus trabajos asignados y las
  oportunidades disponibles en su categoría; puede marcar "en curso" y
  "completado".
- **Cliente**: puede levantar una solicitud de servicio, ver el estatus de las
  suyas, ver qué técnico le fue asignado y calificar al finalizar.

Los datos de esta fase viven **en memoria** (`modulos/datos_demo.py`), con
usuarios y solicitudes de ejemplo, para poder probar el flujo completo
(alta de técnico → solicitud → asignación → cierre → calificación) sin
depender todavía de nada externo. Cada vez que se reinicia la app, los datos
vuelven a la semilla de ejemplo.

Usuarios de demostración (visibles también dentro de la pantalla de login):

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin.operativo` | `admin123` | Admin Operativo |
| `admin.socio` | `socio123` | Admin Socio |
| `carlos.plomero` | `tec123` | Técnico |
| `martha.cliente` | `cli123` | Cliente |

## Cómo correrlo localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo subirlo (mismo flujo que ya usas)

1. Crea un repo nuevo en GitHub (por ejemplo `homyfix-app`).
2. Sube esta carpeta tal cual.
3. Despliega en Streamlit Community Cloud apuntando a `app.py` — igual que
   hiciste con el portal educativo.

## Conectar Google Sheets (ya implementado, falta tu parte de configuración)

Ya está el código: `modulos/datos.py` decide solo si usar Google Sheets
(`modulos/datos_sheets.py`) o los datos de ejemplo en memoria
(`modulos/datos_demo.py`), según si encuentra la sección `[homyfix]` en
`st.secrets`. El resto de la app no cambia nada. Te toca la parte de Google,
igual que hiciste con `ALEMA_API_Candados`:

1. Crea un Google Sheet nuevo llamado **HOMYFIX_BD** (vacío, las pestañas se
   crean solas la primera vez que se usan).
2. En ese Sheet: **Extensiones → Apps Script**, borra lo que haya en
   `Code.gs` y pega el contenido de `apps_script/Code.gs` de este repo.
3. En la primera línea del script cambia `TOKEN_SECRETO` por uno que
   inventes tú (cualquier texto/número largo, es tu contraseña de API).
4. **Implementar → Nueva implementación** → tipo *Aplicación web* → Ejecutar
   como *Yo* → Quién tiene acceso *Cualquier usuario* → Implementar. Te va a
   pedir autorizar permisos (es tu propio script, dale que sí). Copia la URL
   que termina en `/exec`.
5. En ese mismo Sheet, crea manualmente la pestaña **Usuarios** con columnas
   `Usuario | Password | Rol | Nombre | TecnicoID | ClienteID` y da de alta
   ahí a tu admin operativo, admin socio, y a cada técnico/cliente real (Rol
   debe ser exactamente `ADMIN_OPERATIVO`, `ADMIN_SOCIO`, `TECNICO` o
   `CLIENTE`; TecnicoID/ClienteID solo aplican para esos roles y deben
   coincidir con el TecnicoID que uses en la pestaña Tecnicos).
6. En Streamlit Cloud: tu app → **Settings → Secrets**, pega esto (con tus
   valores reales):

   ```toml
   [homyfix]
   api_url = "https://script.google.com/macros/s/TU_ID/exec"
   token = "el-mismo-token-que-pusiste-en-el-script"
   ```

   Para probarlo en tu computadora antes, copia `.streamlit/secrets.toml.example`
   como `.streamlit/secrets.toml` (ese archivo no se sube a GitHub) y pon ahí
   los mismos valores.

7. Guarda los secrets y reinicia la app (Streamlit Cloud lo hace solo). En
   cuanto detecta `[homyfix]`, deja de usar los usuarios de demostración —
   solo entran los que tú diste de alta en la pestaña Usuarios — y todo lo
   que pase en la app (altas de técnico, solicitudes, calificaciones) queda
   guardado en el Sheet.

Las contraseñas de esta primera versión quedan en texto plano en la pestaña
Usuarios (para arrancar rápido); cuando quieras, aplicamos la misma migración
gradual a bcrypt que ya hiciste en el portal educativo.

## Siguiente paso: landing page pública

Para reclutamiento de técnicos y explicación a clientes, se recomienda un sitio
estático separado (como tu `landing-alemaventas`), con el formulario de
registro de técnico apuntando ya al Apps Script en vez de a Google Forms, y un
botón de "Solicitar servicio" que lleve directo al portal de cliente.

## Cuándo migrar a Fly.io

Tiene sentido moverlo de Streamlit Community Cloud a Fly.io cuando:

- Ya validaste el flujo completo con técnicos y clientes reales en fase beta.
- Quieres usar el dominio propio de Homyfix en vez de `*.streamlit.app`.
- El negocio ya genera ingresos consistentes que justifiquen el gasto fijo
  mensual (recuerda que en tu otro proyecto ya tienes listos `Dockerfile`,
  `entrypoint.sh` y `.dockerignore` de referencia — se pueden reutilizar casi
  tal cual para esta app, porque la estructura Streamlit es la misma).

No hay prisa por migrar antes de eso: Streamlit Community Cloud es gratis y
suficiente para toda la fase beta.
