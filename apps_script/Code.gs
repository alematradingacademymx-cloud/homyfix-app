/**
 * HOMYFIX_API — Web App que conecta la app de Streamlit con Google Sheets.
 *
 * Mismo patrón que ALEMA_API_Candados: se despliega como Web App (acceso
 * "Cualquier usuario") y todas las peticiones llegan por doPost con un
 * "token" secreto que tú inventas, para que nadie más pueda escribir en tu
 * Sheet aunque conozca la URL.
 *
 * PASOS:
 * 1. Crea un Google Sheet llamado "HOMYFIX_BD" con 3 pestañas: Usuarios,
 *    Tecnicos, Solicitudes (los encabezados se crean solos la primera vez
 *    que se use cada una, ver crearPestanaSiNoExiste).
 * 2. Extensiones > Apps Script, borra el contenido de Code.gs y pega esto.
 * 3. Cambia TOKEN_SECRETO por uno que inventes tú (letras y números).
 * 4. Implementar > Nueva implementación > Tipo: Aplicación web.
 *    Ejecutar como: Yo. Quién tiene acceso: Cualquier usuario.
 * 5. Copia la URL que te da (termina en /exec) — esa es API_URL para
 *    Streamlit.
 */

const TOKEN_SECRETO = "CAMBIA_ESTO_POR_TU_TOKEN";
const SHEET_ID = "1ECWIYcCqs3FgID6CKOyXXOaKGi6AaB-s6K3q9XOSrD0"; // HOMYFIX_BD

function doPost(e) {
  try {
    const p = e.parameter;
    if (p.token !== TOKEN_SECRETO) {
      return respuesta({ok: false, error: "token inválido"});
    }
    switch (p.action) {
      case "login": return respuesta(login(p));
      case "obtener_tecnicos": return respuesta({ok: true, datos: obtenerTecnicos()});
      case "agregar_tecnico": return respuesta(agregarTecnico(p));
      case "actualizar_estatus_tecnico": return respuesta(actualizarEstatusTecnico(p));
      case "actualizar_membresia_tecnico": return respuesta(actualizarMembresiaTecnico(p));
      case "obtener_solicitudes": return respuesta({ok: true, datos: obtenerSolicitudes()});
      case "crear_solicitud": return respuesta(crearSolicitud(p));
      case "asignar_tecnico": return respuesta(asignarTecnico(p));
      case "actualizar_estatus_solicitud": return respuesta(actualizarEstatusSolicitud(p));
      case "calificar_solicitud": return respuesta(calificarSolicitud(p));
      default: return respuesta({ok: false, error: "acción no reconocida"});
    }
  } catch (err) {
    return respuesta({ok: false, error: String(err)});
  }
}

function respuesta(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function getSheet() {
  return SpreadsheetApp.openById(SHEET_ID);
}

function crearPestanaSiNoExiste(nombre, encabezados) {
  const libro = getSheet();
  let hoja = libro.getSheetByName(nombre);
  if (!hoja) {
    hoja = libro.insertSheet(nombre);
    hoja.appendRow(encabezados);
  }
  return hoja;
}

function filasComoObjetos(hoja) {
  const valores = hoja.getDataRange().getValues();
  if (valores.length < 2) return [];
  const encabezados = valores[0];
  return valores.slice(1).map(fila => {
    const obj = {};
    encabezados.forEach((h, i) => obj[h] = fila[i]);
    return obj;
  });
}

function encontrarFila(hoja, columnaId, valorId) {
  const valores = hoja.getDataRange().getValues();
  const encabezados = valores[0];
  const idx = encabezados.indexOf(columnaId);
  for (let i = 1; i < valores.length; i++) {
    if (String(valores[i][idx]) === String(valorId)) return i + 1; // 1-indexed para getRange
  }
  return -1;
}

function actualizarCelda(hoja, fila, columna, valor) {
  const encabezados = hoja.getDataRange().getValues()[0];
  const idx = encabezados.indexOf(columna);
  if (idx === -1) throw new Error("columna no encontrada: " + columna);
  hoja.getRange(fila, idx + 1).setValue(valor);
}

// ---------- Usuarios / Login ----------
// Pestaña Usuarios: Usuario | Password | Rol | Nombre | TecnicoID | ClienteID
function login(p) {
  const hoja = crearPestanaSiNoExiste("Usuarios", ["Usuario", "Password", "Rol", "Nombre", "TecnicoID", "ClienteID"]);
  const filas = filasComoObjetos(hoja);
  const usuario = (p.usuario || "").trim().toLowerCase();
  const encontrado = filas.find(f => String(f.Usuario).trim().toLowerCase() === usuario);
  if (!encontrado || String(encontrado.Password) !== String(p.password)) {
    return {ok: false, error: "usuario o contraseña incorrectos"};
  }
  return {
    ok: true,
    rol: encontrado.Rol,
    nombre: encontrado.Nombre,
    tecnico_id: encontrado.TecnicoID || null,
    cliente_id: encontrado.ClienteID || null,
  };
}

// ---------- Técnicos ----------
// Pestaña Tecnicos: TecnicoID | Nombre | Especialidad | Zona | Telefono | Estatus | MembresiaAlCorriente | CalificacionProm
const COLS_TECNICOS = ["TecnicoID", "Nombre", "Especialidad", "Zona", "Telefono", "Estatus", "MembresiaAlCorriente", "CalificacionProm"];

function obtenerTecnicos() {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  return filasComoObjetos(hoja);
}

function agregarTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  const nuevoId = "T-" + Utilities.getUuid().slice(0, 8);
  hoja.appendRow([nuevoId, p.nombre, p.especialidad, p.zona, p.telefono, "Pendiente de validación", false, ""]);
  return {ok: true, tecnico_id: nuevoId};
}

function actualizarEstatusTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  const fila = encontrarFila(hoja, "TecnicoID", p.tecnico_id);
  if (fila === -1) return {ok: false, error: "técnico no encontrado"};
  actualizarCelda(hoja, fila, "Estatus", p.nuevo_estatus);
  return {ok: true};
}

function actualizarMembresiaTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  const fila = encontrarFila(hoja, "TecnicoID", p.tecnico_id);
  if (fila === -1) return {ok: false, error: "técnico no encontrado"};
  actualizarCelda(hoja, fila, "MembresiaAlCorriente", p.al_corriente ? "SI" : "");
  return {ok: true};
}

// ---------- Solicitudes ----------
// Pestaña Solicitudes: SolicitudID | ClienteID | ClienteNombre | Categoria | Zona | Descripcion | Urgencia | Estatus | TecnicoID | Costo | Calificacion | Creado
const COLS_SOLICITUDES = ["SolicitudID", "ClienteID", "ClienteNombre", "Categoria", "Zona", "Descripcion", "Urgencia", "Estatus", "TecnicoID", "Costo", "Calificacion", "Creado"];

function obtenerSolicitudes() {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  return filasComoObjetos(hoja);
}

function crearSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const nuevoId = "S-" + Utilities.getUuid().slice(0, 8);
  hoja.appendRow([
    nuevoId, p.cliente_id, p.cliente_nombre, p.categoria, p.zona, p.descripcion,
    p.urgencia, "Pendiente", "", "", "", new Date(),
  ]);
  return {ok: true, solicitud_id: nuevoId};
}

function asignarTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "TecnicoID", p.tecnico_id);
  actualizarCelda(hoja, fila, "Estatus", "Asignado");
  if (p.costo) actualizarCelda(hoja, fila, "Costo", p.costo);
  return {ok: true};
}

function actualizarEstatusSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "Estatus", p.nuevo_estatus);
  return {ok: true};
}

function calificarSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "Calificacion", p.calificacion);
  actualizarCelda(hoja, fila, "Estatus", "Calificado");
  return {ok: true};
}
