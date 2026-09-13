/**
 * HOMYFIX_API — Web App que conecta la app de Streamlit con Google Sheets.
 *
 * Mismo patrón que ALEMA_API_Candados: se despliega como Web App (acceso
 * "Cualquier usuario") y todas las peticiones llegan por doPost con un
 * "token" secreto que tú inventas, para que nadie más pueda escribir en tu
 * Sheet aunque conozca la URL.
 */

const TOKEN_SECRETO = "hmyfx-2026-9f3kd8s7q2";
const SHEET_ID = "1ECWIYcCqs3FgID6CKOyXXOaKGi6AaB-s6K3q9XOSrD0"; // HOMYFIX_BD
const CARPETA_FOTOS = "Homyfix_Diagnosticos";
const CARPETA_REGISTROS = "Homyfix_Registros";

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
      case "actualizar_ubicacion_tecnico": return respuesta(actualizarUbicacionTecnico(p));
      case "asignar_tecnico": return respuesta(asignarTecnico(p));
      case "actualizar_estatus_solicitud": return respuesta(actualizarEstatusSolicitud(p));
      case "cotizar_directo": return respuesta(cotizarDirecto(p));
      case "solicitar_visita": return respuesta(solicitarVisita(p));
      case "subir_foto_diagnostico": return respuesta(subirFotoDiagnostico(p));
      case "subir_bitacora": return respuesta(subirBitacora(p));
      case "aceptar_solicitud": return respuesta(aceptarSolicitud(p));
      case "rechazar_solicitud": return respuesta(rechazarSolicitud(p));
      case "obtener_pujas": return respuesta({ok: true, datos: obtenerPujas(p)});
      case "ofertar_puja": return respuesta(ofertarPuja(p));
      case "cerrar_puja": return respuesta(cerrarPuja(p));
      case "calificar_solicitud": return respuesta(calificarSolicitud(p));
      case "enviar_solicitud_registro": return respuesta(enviarSolicitudRegistro(p));
      case "obtener_solicitudes_registro": return respuesta({ok: true, datos: obtenerSolicitudesRegistro(p)});
      case "aprobar_solicitud_registro": return respuesta(aprobarSolicitudRegistro(p));
      case "rechazar_solicitud_registro": return respuesta(rechazarSolicitudRegistro(p));
      case "canjear_codigo": return respuesta(canjearCodigo(p));
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

function asegurarColumnas(hoja, columnasEsperadas) {
  const ultimaCol = hoja.getLastColumn() || 1;
  const encabezados = hoja.getRange(1, 1, 1, ultimaCol).getValues()[0];
  const faltantes = columnasEsperadas.filter(c => encabezados.indexOf(c) === -1);
  if (faltantes.length > 0) {
    hoja.getRange(1, encabezados.length + 1, 1, faltantes.length).setValues([faltantes]);
  }
}

function crearPestanaSiNoExiste(nombre, encabezados) {
  const libro = getSheet();
  let hoja = libro.getSheetByName(nombre);
  if (!hoja) {
    hoja = libro.insertSheet(nombre);
    hoja.appendRow(encabezados);
  } else {
    asegurarColumnas(hoja, encabezados);
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
    if (String(valores[i][idx]) === String(valorId)) return i + 1;
  }
  return -1;
}

function actualizarCelda(hoja, fila, columna, valor) {
  const encabezados = hoja.getDataRange().getValues()[0];
  const idx = encabezados.indexOf(columna);
  if (idx === -1) throw new Error("columna no encontrada: " + columna);
  hoja.getRange(fila, idx + 1).setValue(valor);
}

function leerCelda(hoja, fila, columna) {
  const encabezados = hoja.getDataRange().getValues()[0];
  const idx = encabezados.indexOf(columna);
  if (idx === -1) return null;
  return hoja.getRange(fila, idx + 1).getValue();
}

function generarCodigoSeguridad() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

function generarCodigoAcceso() {
  const alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // sin 0/O/1/I
  let codigo = "";
  for (let i = 0; i < 8; i++) {
    codigo += alfabeto.charAt(Math.floor(Math.random() * alfabeto.length));
  }
  return codigo;
}

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

const COLS_TECNICOS = ["TecnicoID", "Nombre", "Especialidad", "Zona", "Telefono", "Estatus", "MembresiaAlCorriente", "CalificacionProm", "NumCalificaciones", "Rechazos", "FotoPerfilURL"];

function obtenerTecnicos() {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  return filasComoObjetos(hoja);
}

function agregarTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  const nuevoId = "T-" + Utilities.getUuid().slice(0, 8);
  hoja.appendRow([nuevoId, p.nombre, p.especialidad, p.zona, p.telefono, "Pendiente de validación", false, "", 0, 0, ""]);
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

function registrarCalificacionTecnico(tecnicoId, valor, esRechazo) {
  const hoja = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  const fila = encontrarFila(hoja, "TecnicoID", tecnicoId);
  if (fila === -1) return;
  const nActual = Number(leerCelda(hoja, fila, "NumCalificaciones")) || 0;
  const promActual = Number(leerCelda(hoja, fila, "CalificacionProm")) || 0;
  const nuevoN = nActual + 1;
  const nuevoProm = ((promActual * nActual) + Number(valor)) / nuevoN;
  actualizarCelda(hoja, fila, "NumCalificaciones", nuevoN);
  actualizarCelda(hoja, fila, "CalificacionProm", Math.round(nuevoProm * 100) / 100);
  if (esRechazo) {
    const rechazosActuales = Number(leerCelda(hoja, fila, "Rechazos")) || 0;
    actualizarCelda(hoja, fila, "Rechazos", rechazosActuales + 1);
  }
}

const COLS_SOLICITUDES = ["SolicitudID", "ClienteID", "ClienteNombre", "Categoria", "Zona", "Descripcion", "Urgencia", "Estatus", "TecnicoID", "Costo", "Calificacion", "Creado", "CodigoSeguridad", "TipoCotizacion", "CostoVisita", "CostoReparacion", "Diagnostico", "FotoURL", "TecnicosRechazados", "ClienteLat", "ClienteLng", "TecnicoLat", "TecnicoLng", "UbicacionTecnicoHora"];

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
    generarCodigoSeguridad(), "", "", "", "", "", "",
    p.cliente_lat || "", p.cliente_lng || "", "", "", "",
  ]);
  return {ok: true, solicitud_id: nuevoId};
}

function actualizarUbicacionTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "TecnicoLat", p.lat);
  actualizarCelda(hoja, fila, "TecnicoLng", p.lng);
  actualizarCelda(hoja, fila, "UbicacionTecnicoHora", new Date());
  return {ok: true};
}

function asignarTecnico(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "TecnicoID", p.tecnico_id);
  actualizarCelda(hoja, fila, "Estatus", "Asignado");
  if (p.costo) {
    actualizarCelda(hoja, fila, "Costo", p.costo);
    actualizarCelda(hoja, fila, "CostoReparacion", p.costo);
  }
  return {ok: true};
}

function actualizarEstatusSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "Estatus", p.nuevo_estatus);
  return {ok: true};
}

function cotizarDirecto(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "TipoCotizacion", "Directo");
  actualizarCelda(hoja, fila, "CostoReparacion", p.costo_reparacion);
  actualizarCelda(hoja, fila, "Costo", p.costo_reparacion);
  actualizarCelda(hoja, fila, "Estatus", "Cotizado");
  return {ok: true};
}

function solicitarVisita(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "TipoCotizacion", "Visita");
  actualizarCelda(hoja, fila, "CostoVisita", p.costo_visita);
  actualizarCelda(hoja, fila, "Estatus", "En Visita");
  return {ok: true};
}

function guardarArchivoEnCarpeta(nombreCarpeta, base64, mimeType, nombreArchivo) {
  const carpetas = DriveApp.getFoldersByName(nombreCarpeta);
  const carpeta = carpetas.hasNext() ? carpetas.next() : DriveApp.createFolder(nombreCarpeta);
  const bytes = Utilities.base64Decode(base64);
  const blob = Utilities.newBlob(bytes, mimeType || "image/jpeg", nombreArchivo || "archivo");
  const archivo = carpeta.createFile(blob);
  archivo.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return archivo.getUrl();
}

function subirFotoDiagnostico(p) {
  const url = guardarArchivoEnCarpeta(CARPETA_FOTOS, p.contenido_base64, p.mime_type, p.nombre_archivo);
  return {ok: true, foto_url: url};
}

function subirBitacora(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "Diagnostico", p.diagnostico);
  actualizarCelda(hoja, fila, "FotoURL", p.foto_url || "");
  actualizarCelda(hoja, fila, "CostoReparacion", p.costo_reparacion);
  actualizarCelda(hoja, fila, "Costo", p.costo_reparacion);
  actualizarCelda(hoja, fila, "Estatus", "Cotizado");
  return {ok: true};
}

function aceptarSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "Estatus", "Aceptado");
  return {ok: true};
}

function rechazarSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  const tecnicoActual = leerCelda(hoja, fila, "TecnicoID");
  if (tecnicoActual) {
    registrarCalificacionTecnico(tecnicoActual, 1, true);
    const previos = String(leerCelda(hoja, fila, "TecnicosRechazados") || "");
    const lista = previos ? previos.split(",").filter(x => x) : [];
    lista.push(tecnicoActual);
    actualizarCelda(hoja, fila, "TecnicosRechazados", lista.join(","));
  }
  actualizarCelda(hoja, fila, "TecnicoID", "");
  actualizarCelda(hoja, fila, "Estatus", "En Puja");
  return {ok: true};
}

const COLS_PUJAS = ["SolicitudID", "TecnicoID", "Costo", "Fecha"];

function obtenerPujas(p) {
  const hoja = crearPestanaSiNoExiste("Pujas", COLS_PUJAS);
  const filas = filasComoObjetos(hoja);
  if (p.solicitud_id) {
    return filas.filter(f => String(f.SolicitudID) === String(p.solicitud_id));
  }
  return filas;
}

function ofertarPuja(p) {
  const hoja = crearPestanaSiNoExiste("Pujas", COLS_PUJAS);
  const valores = hoja.getDataRange().getValues();
  for (let i = 1; i < valores.length; i++) {
    if (String(valores[i][0]) === String(p.solicitud_id) && String(valores[i][1]) === String(p.tecnico_id)) {
      hoja.getRange(i + 1, 3).setValue(p.costo);
      hoja.getRange(i + 1, 4).setValue(new Date());
      return {ok: true};
    }
  }
  hoja.appendRow([p.solicitud_id, p.tecnico_id, p.costo, new Date()]);
  return {ok: true};
}

function cerrarPuja(p) {
  const hojaPujas = crearPestanaSiNoExiste("Pujas", COLS_PUJAS);
  const ofertas = filasComoObjetos(hojaPujas).filter(f => String(f.SolicitudID) === String(p.solicitud_id));
  if (ofertas.length === 0) return {ok: false, error: "no hay ofertas todavía"};

  const hojaTecnicos = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
  const tecnicos = filasComoObjetos(hojaTecnicos);
  const calificacionPorId = {};
  tecnicos.forEach(t => calificacionPorId[t.TecnicoID] = Number(t.CalificacionProm) || 0);

  ofertas.sort((a, b) => {
    const califA = calificacionPorId[a.TecnicoID] || 0;
    const califB = calificacionPorId[b.TecnicoID] || 0;
    if (califB !== califA) return califB - califA;
    return Number(a.Costo) - Number(b.Costo);
  });
  const ganador = ofertas[0];

  const hojaSolicitudes = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hojaSolicitudes, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hojaSolicitudes, fila, "TecnicoID", ganador.TecnicoID);
  actualizarCelda(hojaSolicitudes, fila, "CostoReparacion", ganador.Costo);
  actualizarCelda(hojaSolicitudes, fila, "Costo", ganador.Costo);
  actualizarCelda(hojaSolicitudes, fila, "Estatus", "Cotizado");

  const valoresPujas = hojaPujas.getDataRange().getValues();
  for (let i = valoresPujas.length - 1; i >= 1; i--) {
    if (String(valoresPujas[i][0]) === String(p.solicitud_id)) {
      hojaPujas.deleteRow(i + 1);
    }
  }
  return {ok: true, tecnico_id: ganador.TecnicoID, costo: ganador.Costo};
}

function calificarSolicitud(p) {
  const hoja = crearPestanaSiNoExiste("Solicitudes", COLS_SOLICITUDES);
  const fila = encontrarFila(hoja, "SolicitudID", p.solicitud_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  const tecnicoId = leerCelda(hoja, fila, "TecnicoID");
  if (tecnicoId) {
    registrarCalificacionTecnico(tecnicoId, Number(p.calificacion), false);
  }
  actualizarCelda(hoja, fila, "Calificacion", p.calificacion);
  actualizarCelda(hoja, fila, "Estatus", "Calificado");
  return {ok: true};
}

// ---------- Registro / alta con documentos (técnico y cliente) ----------

const CAMPOS_DOC_REGISTRO = [
  "ine_frente", "ine_reverso", "comprobante_domicilio",
  "carta_recomendacion_1", "carta_recomendacion_2",
  "foto_trabajo_1", "foto_trabajo_2", "foto_trabajo_3",
  "carta_antecedentes", "foto_perfil",
];

function colsRegistros() {
  const base = ["RegistroID", "Tipo", "Nombre", "Correo", "Telefono", "Direccion", "Edad",
    "Especialidad", "Experiencia", "Herramienta", "Estatus", "VinculoID",
    "CodigoAcceso", "CodigoUsado", "Creado"];
  const docs = CAMPOS_DOC_REGISTRO.map(c => "DocUrl_" + c);
  return base.concat(docs);
}

function enviarSolicitudRegistro(p) {
  const cols = colsRegistros();
  const hoja = crearPestanaSiNoExiste("SolicitudesRegistro", cols);
  const nuevoId = "R-" + Utilities.getUuid().slice(0, 8);

  const urlsDocumentos = {};
  CAMPOS_DOC_REGISTRO.forEach(campo => {
    const b64 = p["doc_" + campo + "_b64"];
    if (b64) {
      const nombreArchivo = p["doc_" + campo + "_nombre"] || campo;
      const mime = p["doc_" + campo + "_mime"] || "image/jpeg";
      urlsDocumentos[campo] = guardarArchivoEnCarpeta(CARPETA_REGISTROS, b64, mime, nombreArchivo);
    }
  });

  const fila = {
    RegistroID: nuevoId, Tipo: p.tipo, Nombre: p.nombre, Correo: p.correo, Telefono: p.telefono,
    Direccion: p.direccion || "", Edad: p.edad || "", Especialidad: p.especialidad || "",
    Experiencia: p.experiencia || "", Herramienta: p.herramienta || "",
    Estatus: "Pendiente", VinculoID: "", CodigoAcceso: "", CodigoUsado: false, Creado: new Date(),
  };
  CAMPOS_DOC_REGISTRO.forEach(campo => {
    fila["DocUrl_" + campo] = urlsDocumentos[campo] || "";
  });

  hoja.appendRow(cols.map(c => fila[c] !== undefined ? fila[c] : ""));
  return {ok: true, registro_id: nuevoId};
}

function obtenerSolicitudesRegistro(p) {
  const hoja = crearPestanaSiNoExiste("SolicitudesRegistro", colsRegistros());
  const filas = filasComoObjetos(hoja);
  if (p.estatus) {
    return filas.filter(f => String(f.Estatus) === String(p.estatus));
  }
  return filas;
}

function aprobarSolicitudRegistro(p) {
  const hoja = crearPestanaSiNoExiste("SolicitudesRegistro", colsRegistros());
  const fila = encontrarFila(hoja, "RegistroID", p.registro_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};

  const tipo = leerCelda(hoja, fila, "Tipo");
  const nombre = leerCelda(hoja, fila, "Nombre");
  const correo = leerCelda(hoja, fila, "Correo");
  const codigo = generarCodigoAcceso();
  let vinculoId;

  if (tipo === "TECNICO") {
    const direccion = leerCelda(hoja, fila, "Direccion");
    const especialidad = leerCelda(hoja, fila, "Especialidad");
    const telefono = leerCelda(hoja, fila, "Telefono");
    const fotoPerfilUrl = leerCelda(hoja, fila, "DocUrl_foto_perfil") || "";
    const hojaTecnicos = crearPestanaSiNoExiste("Tecnicos", COLS_TECNICOS);
    const nuevoTecnicoId = "T-" + Utilities.getUuid().slice(0, 8);
    hojaTecnicos.appendRow([nuevoTecnicoId, nombre, especialidad, direccion, telefono, "Activo", false, "", 0, 0, fotoPerfilUrl]);
    vinculoId = nuevoTecnicoId;
  } else {
    vinculoId = "C-" + Utilities.getUuid().slice(0, 8);
  }

  actualizarCelda(hoja, fila, "Estatus", "Aprobado");
  actualizarCelda(hoja, fila, "VinculoID", vinculoId);
  actualizarCelda(hoja, fila, "CodigoAcceso", codigo);
  actualizarCelda(hoja, fila, "CodigoUsado", false);

  try {
    const asunto = "Homyfix — tu solicitud fue aprobada";
    const cuerpo =
      "Hola " + nombre + ",\n\n" +
      "¡Tu solicitud para unirte a Homyfix fue aprobada!\n\n" +
      "Tu código de acceso es: " + codigo + "\n\n" +
      "Para crear tu cuenta:\n" +
      "1. Entra a la app de Homyfix.\n" +
      "2. En la pantalla de inicio, da clic en \"Ya tengo un código de acceso\".\n" +
      "3. Ingresa este código junto con el usuario y la contraseña que quieras usar.\n\n" +
      "Este código es de un solo uso. Si tú no solicitaste esto, ignora este correo.\n\n" +
      "— Equipo Homyfix";
    MailApp.sendEmail(correo, asunto, cuerpo);
  } catch (err) {
    // Si el envío de correo falla, la aprobación ya quedó registrada; el código
    // se puede compartir manualmente desde el panel admin si hace falta.
  }

  return {ok: true, codigo: codigo, correo: correo, vinculo_id: vinculoId};
}

function rechazarSolicitudRegistro(p) {
  const hoja = crearPestanaSiNoExiste("SolicitudesRegistro", colsRegistros());
  const fila = encontrarFila(hoja, "RegistroID", p.registro_id);
  if (fila === -1) return {ok: false, error: "solicitud no encontrada"};
  actualizarCelda(hoja, fila, "Estatus", "Rechazado");
  return {ok: true};
}

function canjearCodigo(p) {
  const hoja = crearPestanaSiNoExiste("SolicitudesRegistro", colsRegistros());
  const filas = filasComoObjetos(hoja);
  const codigo = String(p.codigo || "").trim().toUpperCase();
  const encontrado = filas.find(f =>
    String(f.CodigoAcceso).trim().toUpperCase() === codigo &&
    String(f.Estatus) === "Aprobado" &&
    !f.CodigoUsado
  );
  if (!encontrado) {
    return {ok: false, error: "Código inválido, ya usado, o la solicitud todavía no ha sido aprobada."};
  }

  const hojaUsuarios = crearPestanaSiNoExiste("Usuarios", ["Usuario", "Password", "Rol", "Nombre", "TecnicoID", "ClienteID"]);
  const usuarios = filasComoObjetos(hojaUsuarios);
  const usuarioNuevo = String(p.usuario || "").trim();
  const yaExiste = usuarios.some(u => String(u.Usuario).trim().toLowerCase() === usuarioNuevo.toLowerCase());
  if (yaExiste) {
    return {ok: false, error: "Ese nombre de usuario ya existe, elige otro."};
  }

  const tecnicoId = encontrado.Tipo === "TECNICO" ? encontrado.VinculoID : "";
  const clienteId = encontrado.Tipo === "CLIENTE" ? encontrado.VinculoID : "";
  hojaUsuarios.appendRow([usuarioNuevo, p.password, encontrado.Tipo, encontrado.Nombre, tecnicoId, clienteId]);

  const filaRegistro = encontrarFila(hoja, "RegistroID", encontrado.RegistroID);
  if (filaRegistro !== -1) {
    actualizarCelda(hoja, filaRegistro, "CodigoUsado", true);
  }

  return {ok: true, rol: encontrado.Tipo};
}
