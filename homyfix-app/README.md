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

## Siguiente paso: pasar de datos en memoria a Google Sheets

Cuando quieras que los datos persistan de verdad (no se reinicien cada vez),
el patrón a seguir es el mismo que ya usas y ya sabes que funciona en tu
organización (Apps Script como mini-API, porque la creación de llaves de
cuenta de servicio está bloqueada por política del Workspace):

1. Crear un Google Sheet "HOMYFIX_BD" con pestañas: `Usuarios`, `Tecnicos`,
   `Solicitudes`.
2. Crear un Apps Script desplegado como Web App (igual que
   `ALEMA_API_Candados`) con acciones tipo `crear_solicitud`,
   `asignar_tecnico`, `actualizar_estatus`, `agregar_tecnico`, etc.
3. Reemplazar, una por una, las funciones de `modulos/datos_demo.py`
   (`obtener_tecnicos`, `crear_solicitud`, `asignar_tecnico`, ...) por llamadas
   `requests.post(...)` a esa Web App. El resto de la app (los 4 paneles) no
   debería necesitar cambios porque ya solo habla con esas funciones, nunca
   directamente con la estructura de datos.
4. Las contraseñas de los 4 roles pasan de `modulos/config.py` a una pestaña
   `Usuarios` en el Sheet (con hash bcrypt, igual que ya hiciste en el portal
   educativo).

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
