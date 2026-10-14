// app.js: funciones compartidas por todas las páginas

async function enviar(url, datos) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || "Error en el servidor");
  return j;
}

// Lee un input numérico; devuelve null si está vacío
function num(id) {
  const v = document.getElementById(id).value;
  return v === "" ? null : parseFloat(v);
}

function esc(t) {
  return String(t).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function fmt(x, d = 2) {
  return Number(x).toLocaleString("es-BO", { minimumFractionDigits: d, maximumFractionDigits: d });
}

// items: [[etiqueta, valor, unidad], ...]
function tarjetas(items) {
  return '<div class="row g-3 mb-4">' + items.map(([e, v, u]) =>
    `<div class="col-6 col-md-4"><div class="stat">
       <span class="stat-label">${e}</span>
       <span class="stat-value">${v}</span>
       <span class="stat-unit">${u || ""}</span></div></div>`).join("") + "</div>";
}

function pasosHTML(pasos) {
  return `<div class="card-panel"><h5><i class="bi bi-list-check"></i> Procedimiento</h5>
    <ol class="pasos">${pasos.map(p => `<li>${esc(p)}</li>`).join("")}</ol></div>`;
}

function errorHTML(msg) {
  return `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> ${esc(msg)}</div>`;
}

// Gráficas: guarda la instancia para destruirla al recalcular
const _graficas = {};
function dibujar(idCanvas, config) {
  if (_graficas[idCanvas]) _graficas[idCanvas].destroy();
  _graficas[idCanvas] = new Chart(document.getElementById(idCanvas), config);
}

// Tabla simple. filas: [[celda, celda, ...], ...]; resaltar: índice de fila a destacar
function tablaHTML(encabezados, filas, resaltar = -1) {
  return `<div class="table-responsive"><table class="table tabla-res align-middle mb-0">
    <thead><tr>${encabezados.map(h => `<th>${esc(h)}</th>`).join("")}</tr></thead>
    <tbody>${filas.map((f, i) => `<tr class="${i === resaltar ? "ganadora" : ""}">
      ${f.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}