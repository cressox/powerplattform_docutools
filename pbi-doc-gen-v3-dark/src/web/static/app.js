/* ═══════════════════════════════════════════════════════════════
   Power BI Documentation Generator – SPA Frontend
   ═══════════════════════════════════════════════════════════════ */

"use strict";

// ── Global State ────────────────────────────────────────────────
let project = null;

const PAGE_TITLES = {
  dashboard:          "Dashboard",
  meta:               "Metadaten",
  ci_branding:        "CI / Branding",
  kpis:               "KPIs & Kennzahlen",
  data_sources:       "Datenquellen",
  power_queries:      "Power Query (M)",
  data_model:         "Datenmodell",
  measures:           "Measures (DAX)",
  report_pages:       "Berichtsseiten & Visuals",
  governance:         "Governance",
  permissions:        "Berechtigungen",
  storage_structure:  "Ablagestruktur",
  naming_conventions: "Namenskonzept",
  change_guidance:    "Änderungshinweise",
  change_log:         "Änderungsprotokoll",
  preview:            "Vorschau",
  export:             "Export",
};

// ── Init ────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadProject();
  initNavigation();
  initToolbar();
});

// ── API helpers ─────────────────────────────────────────────────
async function api(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ error: resp.statusText }));
    throw new Error(err.error || resp.statusText);
  }
  return resp;
}

async function apiJson(url, options) {
  return (await api(url, options)).json();
}

// ── Toast ───────────────────────────────────────────────────────
function toast(message, type) {
  type = type || "info";
  var el = document.getElementById("toast");
  el.textContent = message;
  el.className = "toast " + type;
  clearTimeout(el._timer);
  el._timer = setTimeout(function () {
    el.className = "toast hidden";
  }, 3500);
}

// ── Navigation ──────────────────────────────────────────────────
function initNavigation() {
  document.querySelectorAll(".nav-item").forEach(function (item) {
    item.addEventListener("click", function () {
      navigateTo(this.dataset.page);
    });
  });
}

function navigateTo(pageId) {
  // Collect form data before switching
  collectFormData();

  // Activate nav
  document.querySelectorAll(".nav-item").forEach(function (n) {
    n.classList.toggle("active", n.dataset.page === pageId);
  });
  // Activate page
  document.querySelectorAll(".page").forEach(function (p) {
    p.classList.toggle("active", p.id === "page-" + pageId);
  });
  // Title
  document.getElementById("page-title").textContent =
    PAGE_TITLES[pageId] || pageId;

  // Rebuild list editors when navigating to them
  if (project) {
    switch (pageId) {
      case "dashboard": updateDashboard(); break;
      case "kpis": renderKpis(); break;
      case "data_sources": renderDataSources(); break;
      case "power_queries": renderPowerQueries(); break;
      case "data_model": renderDataModel(); renderDataModelDiagram(); break;
      case "measures": renderMeasures(); break;
      case "report_pages": renderReportPages(); break;
      case "permissions": renderPermEntries(); break;
      case "change_log": renderChangeLog(); break;
      case "meta": renderEnvironments(); break;
    }
  }
}

// ── Toolbar ─────────────────────────────────────────────────────
function initToolbar() {
  document.getElementById("btn-sidebar-toggle").addEventListener("click", function () {
    document.getElementById("sidebar").classList.toggle("collapsed");
  });

  document.getElementById("btn-save").addEventListener("click", saveProject);

  document.getElementById("btn-load-file").addEventListener("click", function () {
    document.getElementById("file-load").click();
  });
  document.getElementById("file-load").addEventListener("change", function () {
    if (this.files.length) uploadProject(this.files[0]);
    this.value = "";
  });

  document.getElementById("btn-import").addEventListener("click", function () {
    document.getElementById("file-import").click();
  });
  document.getElementById("file-import").addEventListener("change", function () {
    if (this.files.length) {
      showModal("import-dialog");
      document.getElementById("file-import")._pending = this.files[0];
    }
    this.value = "";
  });
}

// ── Modal ───────────────────────────────────────────────────────
function showModal(id) {
  document.getElementById(id).classList.remove("hidden");
}
function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
}

// ── Load / Save / Upload ────────────────────────────────────────
async function loadProject() {
  try {
    project = await apiJson("/api/project");
    populateUI();
    updateDashboard();
    toast("Projekt geladen", "success");
  } catch (e) {
    project = getEmptyProject();
    populateUI();
    toast("Neues Projekt erstellt", "info");
  }
}

async function saveProject() {
  collectFormData();
  try {
    await apiJson("/api/project", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
    toast("Projekt gespeichert ✓", "success");
  } catch (e) {
    toast("Fehler: " + e.message, "error");
  }
}

async function uploadProject(file) {
  var fd = new FormData();
  fd.append("file", file);
  try {
    project = await apiJson("/api/project/upload", { method: "POST", body: fd });
    populateUI();
    updateDashboard();
    toast("Projekt geladen ✓", "success");
  } catch (e) {
    toast("Fehler: " + e.message, "error");
  }
}

async function doImport() {
  var file = document.getElementById("file-import")._pending;
  if (!file) return;
  closeModal("import-dialog");

  var fd = new FormData();
  fd.append("file", file);
  fd.append("merge_mode", document.getElementById("import-merge-mode").value);
  fd.append("skip_hidden", document.getElementById("import-skip-hidden").checked ? "true" : "false");

  try {
    var result = await apiJson("/api/import", { method: "POST", body: fd });
    project = result.project;
    populateUI();
    updateDashboard();
    toast("Import erfolgreich: " + (result.report || ""), "success");
  } catch (e) {
    toast("Import-Fehler: " + e.message, "error");
  }
}

// ── Empty project template ──────────────────────────────────────
function getEmptyProject() {
  return {
    meta: { report_name: "", short_description: "", audience: "", owner: "", author: "", version: "0.1.0", date: new Date().toISOString().slice(0, 10), environments: [], powerbi_service_url: "", sharepoint_folder_url: "" },
    ci_branding: { company_name: "", primary_color: "#1B3A5C", accent_color: "#F2C811", secondary_color: "#2563EB", font_name: "", footer_text: "", header_text: "", cover_subtitle: "", confidentiality_notice: "" },
    kpis: [],
    data_sources: [],
    power_queries: [],
    data_model: { tables: [], relationships: [], date_logic_notes: "", notes: "" },
    measures: [],
    report_pages: [],
    governance: { refresh_schedule: "", monitoring_notes: "", rls_notes: "", performance_notes: "", assumptions: "", limitations: "" },
    change_log: [],
    screenshots: [],
    permissions: { workspace_roles: "", rls_details: "", sharing_permissions: "", data_sensitivity: "", required_roles_for_changes: "", service_principal: "", audience_access: "", app_permissions: "", dataset_permissions: "", entries: [], notes: "" },
    storage_structure: { pbix_location: "", workspace_name: "", sharepoint_path: "", data_gateway: "", backup_strategy: "", deployment_pipeline: "", repo_url: "", notes: "" },
    naming_conventions: { general_rules: "", measures: "", tables: "", columns: "", pages: "", reports: "", queries: "", notes: "" },
    change_guidance: { before_changes: "", testing_checklist: "", deployment_steps: "", rollback_plan: "", contact_persons: "", notes: "" },
  };
}

// ═══════════════════════════════════════════════════════════════
// DATA BINDING
// ═══════════════════════════════════════════════════════════════

function populateUI() {
  if (!project) return;
  // Simple data-bind attributes
  document.querySelectorAll("[data-bind]").forEach(function (el) {
    var path = el.dataset.bind.split(".");
    var val = getNestedValue(project, path);
    if (val === undefined || val === null) val = "";
    if (el.type === "checkbox") {
      el.checked = !!val;
    } else {
      el.value = val;
    }
  });

  // Render list editors for current page
  renderEnvironments();
  renderKpis();
  renderDataSources();
  renderPowerQueries();
  renderDataModel();
  renderMeasures();
  renderReportPages();
  renderPermEntries();
  renderChangeLog();
  updateDashboard();
}

function collectFormData() {
  if (!project) return;
  document.querySelectorAll("[data-bind]").forEach(function (el) {
    var path = el.dataset.bind.split(".");
    var val;
    if (el.type === "checkbox") {
      val = el.checked;
    } else if (el.type === "color") {
      val = el.value;
    } else {
      val = el.value;
    }
    setNestedValue(project, path, val);
  });

  // Collect list editors
  collectKpis();
  collectDataSources();
  collectPowerQueries();
  collectDataModelTables();
  collectDataModelRels();
  collectMeasures();
  collectReportPages();
  collectPermEntries();
  collectChangeLog();
  collectEnvironments();
}

function getNestedValue(obj, path) {
  var o = obj;
  for (var i = 0; i < path.length; i++) {
    if (o === undefined || o === null) return undefined;
    o = o[path[i]];
  }
  return o;
}

function setNestedValue(obj, path, val) {
  var o = obj;
  for (var i = 0; i < path.length - 1; i++) {
    if (o[path[i]] === undefined) o[path[i]] = {};
    o = o[path[i]];
  }
  o[path[path.length - 1]] = val;
}

// ═══════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════

function updateDashboard() {
  if (!project) return;
  var m = project.meta || {};
  setText("dash-report-name", m.report_name || "–");
  setText("dash-version", m.version || "–");
  setText("dash-source-count", (project.data_sources || []).length);
  setText("dash-measure-count", (project.measures || []).length);
  setText("dash-page-count", (project.report_pages || []).length);
  setText("dash-perm-count", ((project.permissions || {}).entries || []).length);

  // Structure table
  var st = project.storage_structure || {};
  var table = document.getElementById("dash-structure-table");
  var rows = [
    ["PBIX-Datei", st.pbix_location || "–"],
    ["Workspace", st.workspace_name || "–"],
    ["SharePoint", st.sharepoint_path || "–"],
    ["Gateway", st.data_gateway || "–"],
    ["Git-Repository", st.repo_url || "–"],
    ["Deployment", st.deployment_pipeline || "–"],
  ];
  table.innerHTML = "<tr><th>Element</th><th>Ort</th></tr>";
  rows.forEach(function (r) {
    var tr = document.createElement("tr");
    tr.innerHTML = "<td>" + escapeHtml(r[0]) + "</td><td>" + escapeHtml(r[1]) + "</td>";
    table.appendChild(tr);
  });
}

function setText(id, txt) {
  var el = document.getElementById(id);
  if (el) el.textContent = txt;
}

function escapeHtml(str) {
  if (!str) return "";
  var div = document.createElement("div");
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════
// LIST EDITOR: Generic helpers
// ═══════════════════════════════════════════════════════════════

function uid() {
  return Math.random().toString(36).substring(2, 10);
}

function makeItemHtml(title, fields, index) {
  var html = '<div class="list-item" data-index="' + index + '">';
  html += '<div class="item-header">';
  html += '<span class="item-title">' + escapeHtml(title) + '</span>';
  html += '<button class="btn-remove" onclick="this.closest(\'.list-item\').remove()">✕</button>';
  html += '</div>';
  html += '<div class="item-grid">';
  fields.forEach(function (f) {
    html += '<label>' + escapeHtml(f.label) + '</label>';
    if (f.type === "textarea") {
      html += '<textarea data-field="' + f.key + '" rows="' + (f.rows || 2) + '">' + escapeHtml(f.value) + '</textarea>';
    } else if (f.type === "select") {
      html += '<select data-field="' + f.key + '">';
      (f.options || []).forEach(function (opt) {
        html += '<option value="' + escapeHtml(opt) + '"' + (opt === f.value ? ' selected' : '') + '>' + escapeHtml(opt) + '</option>';
      });
      html += '</select>';
    } else if (f.type === "checkbox") {
      html += '<input type="checkbox" data-field="' + f.key + '"' + (f.value ? ' checked' : '') + '>';
    } else {
      html += '<input type="text" data-field="' + f.key + '" value="' + escapeHtml(f.value) + '">';
    }
  });
  html += '</div></div>';
  return html;
}

function collectListItems(containerId) {
  var items = [];
  var container = document.getElementById(containerId);
  if (!container) return items;
  container.querySelectorAll(".list-item").forEach(function (el) {
    var obj = {};
    el.querySelectorAll("[data-field]").forEach(function (input) {
      if (input.type === "checkbox") {
        obj[input.dataset.field] = input.checked;
      } else {
        obj[input.dataset.field] = input.value;
      }
    });
    items.push(obj);
  });
  return items;
}

// ═══════════════════════════════════════════════════════════════
// ENVIRONMENTS
// ═══════════════════════════════════════════════════════════════

function renderEnvironments() {
  var container = document.getElementById("env-list");
  if (!container) return;
  container.innerHTML = "";
  var envs = (project.meta || {}).environments || [];
  envs.forEach(function (env, i) {
    container.innerHTML += makeItemHtml("Umgebung " + (i + 1), [
      { key: "name", label: "Name", value: env.name || "" },
      { key: "workspace", label: "Workspace", value: env.workspace || "" },
      { key: "url", label: "URL", value: env.url || "" },
    ], i);
  });
}

function collectEnvironments() {
  project.meta.environments = collectListItems("env-list");
}

function addEnvironment() {
  project.meta.environments = project.meta.environments || [];
  project.meta.environments.push({ name: "", workspace: "", url: "" });
  renderEnvironments();
}

// ═══════════════════════════════════════════════════════════════
// KPIs
// ═══════════════════════════════════════════════════════════════

function renderKpis() {
  var container = document.getElementById("kpi-list");
  if (!container) return;
  container.innerHTML = "";
  (project.kpis || []).forEach(function (k, i) {
    container.innerHTML += makeItemHtml(k.name || "KPI " + (i + 1), [
      { key: "name", label: "Name", value: k.name || "" },
      { key: "business_description", label: "Beschreibung", type: "textarea", value: k.business_description || "" },
      { key: "technical_definition", label: "Techn. Definition", type: "textarea", value: k.technical_definition || "" },
      { key: "granularity", label: "Granularität", value: k.granularity || "" },
      { key: "filters_context", label: "Filter / Kontext", value: k.filters_context || "" },
      { key: "caveats", label: "Hinweise", value: k.caveats || "" },
    ], i);
  });
}

function collectKpis() {
  var items = collectListItems("kpi-list");
  project.kpis = items.map(function (k) {
    k.id = k.id || uid();
    return k;
  });
}

// ═══════════════════════════════════════════════════════════════
// DATA SOURCES
// ═══════════════════════════════════════════════════════════════

function renderDataSources() {
  var container = document.getElementById("data_sources-list");
  if (!container) return;
  container.innerHTML = "";
  (project.data_sources || []).forEach(function (s, i) {
    container.innerHTML += makeItemHtml(s.name || "Datenquelle " + (i + 1), [
      { key: "name", label: "Name", value: s.name || "" },
      { key: "source_type", label: "Typ", value: s.source_type || "" },
      { key: "connection_info", label: "Verbindung", type: "textarea", value: s.connection_info || "" },
      { key: "refresh_cadence", label: "Aktualisierung", value: s.refresh_cadence || "" },
      { key: "gateway_required", label: "Gateway nötig", type: "checkbox", value: s.gateway_required || false },
      { key: "gateway_name", label: "Gateway Name", value: s.gateway_name || "" },
      { key: "owner_contact", label: "Verantwortlich", value: s.owner_contact || "" },
    ], i);
  });
}

function collectDataSources() {
  var items = collectListItems("data_sources-list");
  project.data_sources = items.map(function (s) {
    s.id = s.id || uid();
    s.gateway_required = !!s.gateway_required;
    return s;
  });
}

// ═══════════════════════════════════════════════════════════════
// POWER QUERIES
// ═══════════════════════════════════════════════════════════════

function renderPowerQueries() {
  var container = document.getElementById("power_queries-list");
  if (!container) return;
  container.innerHTML = "";
  (project.power_queries || []).forEach(function (q, i) {
    container.innerHTML += makeItemHtml(q.query_name || "Abfrage " + (i + 1), [
      { key: "query_name", label: "Name", value: q.query_name || "" },
      { key: "purpose", label: "Zweck", type: "textarea", value: q.purpose || "" },
      { key: "inputs", label: "Eingaben", value: q.inputs || "" },
      { key: "major_transformations", label: "Transformationen", type: "textarea", value: q.major_transformations || "" },
      { key: "m_code", label: "M-Code", type: "textarea", rows: 4, value: q.m_code || "" },
      { key: "output_table", label: "Ausgabetabelle", value: q.output_table || "" },
      { key: "notes", label: "Hinweise", value: q.notes || "" },
    ], i);
  });
}

function collectPowerQueries() {
  var items = collectListItems("power_queries-list");
  project.power_queries = items.map(function (q) {
    q.id = q.id || uid();
    return q;
  });
}

// ═══════════════════════════════════════════════════════════════
// DATA MODEL
// ═══════════════════════════════════════════════════════════════

function renderDataModel() {
  // Tables
  var tc = document.getElementById("dm-tables-list");
  if (!tc) return;
  tc.innerHTML = "";
  ((project.data_model || {}).tables || []).forEach(function (t, i) {
    tc.innerHTML += makeItemHtml(t.name || "Tabelle " + (i + 1), [
      { key: "name", label: "Name", value: t.name || "" },
      { key: "table_type", label: "Typ", value: t.table_type || "", type: "select", options: ["", "Fact", "Dimension", "Bridge", "Calculated", "Other"] },
      { key: "description", label: "Beschreibung", type: "textarea", value: t.description || "" },
      { key: "keys", label: "Schlüssel", value: t.keys || "" },
    ], i);
  });

  // Relationships
  var rc = document.getElementById("dm-rels-list");
  if (!rc) return;
  rc.innerHTML = "";
  ((project.data_model || {}).relationships || []).forEach(function (r, i) {
    var title = (r.from_table || "?") + " → " + (r.to_table || "?");
    rc.innerHTML += makeItemHtml(title, [
      { key: "from_table", label: "Von Tabelle", value: r.from_table || "" },
      { key: "from_column", label: "Von Spalte", value: r.from_column || "" },
      { key: "to_table", label: "Nach Tabelle", value: r.to_table || "" },
      { key: "to_column", label: "Nach Spalte", value: r.to_column || "" },
      { key: "cardinality", label: "Kardinalität", value: r.cardinality || "", type: "select", options: ["", "1:1", "1:N", "N:1", "N:M"] },
      { key: "filter_direction", label: "Filterrichtung", value: r.filter_direction || "", type: "select", options: ["", "Single", "Both"] },
    ], i);
  });
}

function collectDataModelTables() {
  project.data_model = project.data_model || {};
  project.data_model.tables = collectListItems("dm-tables-list");
}

function collectDataModelRels() {
  project.data_model = project.data_model || {};
  project.data_model.relationships = collectListItems("dm-rels-list");
}

function addDmTable() {
  project.data_model = project.data_model || { tables: [], relationships: [] };
  project.data_model.tables = project.data_model.tables || [];
  project.data_model.tables.push({ name: "", table_type: "", description: "", keys: "" });
  renderDataModel();
}

function addDmRel() {
  project.data_model = project.data_model || { tables: [], relationships: [] };
  project.data_model.relationships = project.data_model.relationships || [];
  project.data_model.relationships.push({ from_table: "", from_column: "", to_table: "", to_column: "", cardinality: "", filter_direction: "" });
  renderDataModel();
}

// ═══════════════════════════════════════════════════════════════
// MERMAID DATA MODEL DIAGRAM
// ═══════════════════════════════════════════════════════════════

function _safeMermaidId(name) {
  var s = (name || "");
  // Replace common German chars
  var rep = [["ä","ae"],["ö","oe"],["ü","ue"],["ß","ss"],["Ä","Ae"],["Ö","Oe"],["Ü","Ue"]];
  rep.forEach(function(r){ s = s.split(r[0]).join(r[1]); });
  s = s.replace(/[\s\-.]/g, "_").replace(/[^a-zA-Z0-9_]/g, "").replace(/^_+/, "");
  if (!s || /^\d/.test(s)) s = "T" + s;
  if (/^(PK|FK|UK)$/i.test(s)) s = s + "_col";
  return s;
}

function _mermaidCardinality(card) {
  var c = (card || "").toUpperCase().replace(/\s/g, "");
  var map = {
    "1:1": "||--||", "1:N": "||--o{", "N:1": "}o--||", "N:M": "}o--o{",
    "ONE-TO-ONE": "||--||", "ONE-TO-MANY": "||--o{",
    "MANYTOONE": "}o--||", "MANYTOMANY": "}o--o{",
  };
  return map[c] || "||--o{";
}

function buildMermaidER() {
  collectFormData();
  var dm = project.data_model || {};
  var tables = dm.tables || [];
  var rels = dm.relationships || [];

  if (tables.length === 0 && rels.length === 0) return null;

  var lines = ["erDiagram"];

  // Entity definitions
  tables.forEach(function (t) {
    var id = _safeMermaidId(t.name);
    var cols = [];
    if (t.keys) {
      t.keys.replace(/PK:|FK:/g, "").split(",").forEach(function (k) {
        k = k.trim();
        if (k) cols.push({ kind: "PK", name: _safeMermaidId(k) });
      });
    }
    if (t.description && t.description.indexOf("Spalten:") !== -1) {
      var colPart = t.description.split("Spalten:")[1].split("(+")[0].trim();
      colPart.split(",").forEach(function (c) {
        c = c.trim();
        if (c) {
          var sc = _safeMermaidId(c);
          if (!cols.some(function (x) { return x.name === sc; })) {
            cols.push({ kind: "", name: sc });
          }
        }
      });
    }
    if (cols.length > 0) {
      lines.push("    " + id + " {");
      cols.slice(0, 8).forEach(function (col) {
        lines.push("        string " + col.name + (col.kind === "PK" ? " PK" : ""));
      });
      lines.push("    }");
    } else {
      lines.push("    " + id + " {");
      lines.push("        string id PK");
      lines.push("    }");
    }
  });

  // Relationships
  rels.forEach(function (r) {
    if (!r.from_table || !r.to_table) return;
    var fromId = _safeMermaidId(r.from_table);
    var toId = _safeMermaidId(r.to_table);
    var rel = _mermaidCardinality(r.cardinality);
    var label = (r.from_column || "?") + " - " + (r.to_column || "?");
    lines.push('    ' + fromId + ' ' + rel + ' ' + toId + ' : "' + label + '"');
  });

  return lines.join("\n");
}

async function renderDataModelDiagram() {
  var container = document.getElementById("dm-mermaid-output");
  if (!container) return;

  var code = buildMermaidER();
  if (!code) {
    container.innerHTML = '<p class="hint">Keine Tabellen oder Beziehungen vorhanden.</p>';
    return;
  }

  try {
    container.innerHTML = "";
    var id = "mermaid-dm-" + Date.now();
    var { svg } = await mermaid.render(id, code);
    container.innerHTML = svg;
  } catch (e) {
    container.innerHTML = '<p class="hint" style="color:var(--warning)">Diagramm konnte nicht gerendert werden: ' + escapeHtml(e.message) + '</p><pre style="font-size:11px;color:var(--text-muted)">' + escapeHtml(code) + '</pre>';
  }
}

// ═══════════════════════════════════════════════════════════════
// MEASURES
// ═══════════════════════════════════════════════════════════════

function renderMeasures() {
  var container = document.getElementById("measures-list");
  if (!container) return;
  container.innerHTML = "";
  (project.measures || []).forEach(function (ms, i) {
    container.innerHTML += makeItemHtml(ms.name || "Measure " + (i + 1), [
      { key: "name", label: "Name", value: ms.name || "" },
      { key: "display_folder", label: "Ordner", value: ms.display_folder || "" },
      { key: "description", label: "Beschreibung", type: "textarea", value: ms.description || "" },
      { key: "dax_code", label: "DAX-Code", type: "textarea", rows: 4, value: ms.dax_code || "" },
      { key: "dependencies", label: "Abhängigkeiten", value: ms.dependencies || "" },
      { key: "filter_context_notes", label: "Filterkontext", value: ms.filter_context_notes || "" },
      { key: "validation_notes", label: "Validierung", value: ms.validation_notes || "" },
    ], i);
  });
}

function collectMeasures() {
  var items = collectListItems("measures-list");
  project.measures = items.map(function (m) {
    m.id = m.id || uid();
    return m;
  });
}

// ═══════════════════════════════════════════════════════════════
// REPORT PAGES
// ═══════════════════════════════════════════════════════════════

function renderReportPages() {
  var container = document.getElementById("report_pages-list");
  if (!container) return;
  container.innerHTML = "";
  (project.report_pages || []).forEach(function (pg, i) {
    container.innerHTML += makeItemHtml(pg.page_name || "Seite " + (i + 1), [
      { key: "page_name", label: "Name", value: pg.page_name || "" },
      { key: "purpose", label: "Zweck", type: "textarea", value: pg.purpose || "" },
      { key: "slicers_filters", label: "Slicer / Filter", type: "textarea", value: pg.slicers_filters || "" },
      { key: "notes", label: "Hinweise", value: pg.notes || "" },
    ], i);
  });
}

function collectReportPages() {
  var items = collectListItems("report_pages-list");
  project.report_pages = items.map(function (p) {
    p.id = p.id || uid();
    p.visuals = p.visuals || [];
    return p;
  });
}

// ═══════════════════════════════════════════════════════════════
// PERMISSION ENTRIES
// ═══════════════════════════════════════════════════════════════

function renderPermEntries() {
  var container = document.getElementById("perm-entries-list");
  if (!container) return;
  container.innerHTML = "";
  var entries = ((project.permissions || {}).entries || []);
  entries.forEach(function (e, i) {
    container.innerHTML += makeItemHtml(e.who || "Eintrag " + (i + 1), [
      { key: "who", label: "Wer", value: e.who || "" },
      { key: "what", label: "Was (Rolle)", value: e.what || "" },
      { key: "where", label: "Wo (Bereich)", value: e.where || "" },
      { key: "notes", label: "Anmerkung", value: e.notes || "" },
    ], i);
  });
}

function collectPermEntries() {
  project.permissions = project.permissions || {};
  var items = collectListItems("perm-entries-list");
  project.permissions.entries = items.map(function (e) {
    e.id = e.id || uid();
    return e;
  });
}

function addPermEntry() {
  project.permissions = project.permissions || { entries: [] };
  project.permissions.entries = project.permissions.entries || [];
  project.permissions.entries.push({ id: uid(), who: "", what: "", where: "", notes: "" });
  renderPermEntries();
}

// ═══════════════════════════════════════════════════════════════
// CHANGE LOG
// ═══════════════════════════════════════════════════════════════

function renderChangeLog() {
  var container = document.getElementById("change_log-list");
  if (!container) return;
  container.innerHTML = "";
  (project.change_log || []).forEach(function (c, i) {
    container.innerHTML += makeItemHtml(c.version || "v" + (i + 1), [
      { key: "version", label: "Version", value: c.version || "" },
      { key: "date", label: "Datum", value: c.date || "" },
      { key: "description", label: "Beschreibung", type: "textarea", value: c.description || "" },
      { key: "author", label: "Autor", value: c.author || "" },
      { key: "impact", label: "Auswirkung", value: c.impact || "" },
      { key: "ticket_link", label: "Ticket", value: c.ticket_link || "" },
    ], i);
  });
}

function collectChangeLog() {
  var items = collectListItems("change_log-list");
  project.change_log = items.map(function (c) {
    c.id = c.id || uid();
    return c;
  });
}

// ═══════════════════════════════════════════════════════════════
// GENERIC ADD ITEM
// ═══════════════════════════════════════════════════════════════

function addListItem(section) {
  collectFormData();

  switch (section) {
    case "kpis":
      project.kpis = project.kpis || [];
      project.kpis.push({ id: uid(), name: "", business_description: "", technical_definition: "", granularity: "", filters_context: "", caveats: "" });
      renderKpis();
      break;
    case "data_sources":
      project.data_sources = project.data_sources || [];
      project.data_sources.push({ id: uid(), name: "", source_type: "", connection_info: "", refresh_cadence: "", gateway_required: false, gateway_name: "", owner_contact: "" });
      renderDataSources();
      break;
    case "power_queries":
      project.power_queries = project.power_queries || [];
      project.power_queries.push({ id: uid(), query_name: "", purpose: "", inputs: "", major_transformations: "", m_code: "", output_table: "", notes: "" });
      renderPowerQueries();
      break;
    case "measures":
      project.measures = project.measures || [];
      project.measures.push({ id: uid(), name: "", display_folder: "", description: "", dax_code: "", dependencies: "", filter_context_notes: "", validation_notes: "" });
      renderMeasures();
      break;
    case "report_pages":
      project.report_pages = project.report_pages || [];
      project.report_pages.push({ id: uid(), page_name: "", purpose: "", visuals: [], slicers_filters: "", notes: "" });
      renderReportPages();
      break;
    case "change_log":
      project.change_log = project.change_log || [];
      project.change_log.push({ id: uid(), version: "", date: new Date().toISOString().slice(0, 10), description: "", author: "", impact: "", ticket_link: "" });
      renderChangeLog();
      break;
  }
}

// ═══════════════════════════════════════════════════════════════
// PREVIEW
// ═══════════════════════════════════════════════════════════════

async function loadPreview() {
  collectFormData();
  await saveProject();

  var section = document.getElementById("preview-section").value;
  try {
    var data = await apiJson("/api/preview/" + section);
    var md = data.markdown || "";
    document.getElementById("preview-md").textContent = md;
    document.getElementById("preview-html").innerHTML = renderMarkdown(md);

    // Render any Mermaid diagrams in preview
    var previewEl = document.getElementById("preview-html");
    var mermaidBlocks = previewEl.querySelectorAll("pre code.language-mermaid");
    for (var i = 0; i < mermaidBlocks.length; i++) {
      var block = mermaidBlocks[i];
      var code = block.textContent;
      var pre = block.parentElement;
      try {
        var mermaidId = "preview-mermaid-" + Date.now() + "-" + i;
        var result = await mermaid.render(mermaidId, code);
        var wrapper = document.createElement("div");
        wrapper.className = "mermaid-preview";
        wrapper.innerHTML = result.svg;
        pre.replaceWith(wrapper);
      } catch (err) {
        // Leave the code block as-is if Mermaid can't render it
      }
    }
  } catch (e) {
    toast("Vorschau-Fehler: " + e.message, "error");
  }
}

// Simple Markdown→HTML renderer (no external dependency)
function renderMarkdown(md) {
  var html = escapeHtml(md);
  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Code blocks (with language class)
  html = html.replace(/```(\w+)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>');
  // Code blocks (no language)
  html = html.replace(/```\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
  // HR
  html = html.replace(/^---$/gm, '<hr>');
  // Tables
  html = html.replace(/^\|(.+)\|$/gm, function (match, inner) {
    if (/^[\s\-|]+$/.test(inner)) return '';
    var cells = inner.split('|').map(function (c) { return c.trim(); });
    return '<tr>' + cells.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
  });
  html = html.replace(/(<tr>[\s\S]*?<\/tr>)/g, function (m) {
    if (m.indexOf('<table>') === -1) return '<table>' + m + '</table>';
    return m;
  });
  // Fix consecutive table rows
  html = html.replace(/<\/table>\s*<table>/g, '');
  // Lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>[\s\S]*?<\/li>)/g, function (m) {
    return '<ul>' + m + '</ul>';
  });
  html = html.replace(/<\/ul>\s*<ul>/g, '');
  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  // Paragraphs
  html = html.replace(/\n\n/g, '</p><p>');
  html = '<p>' + html + '</p>';
  html = html.replace(/<p>\s*<\/p>/g, '');
  html = html.replace(/<p>\s*(<h[123])/g, '$1');
  html = html.replace(/(<\/h[123]>)\s*<\/p>/g, '$1');
  html = html.replace(/<p>\s*(<table)/g, '$1');
  html = html.replace(/(<\/table>)\s*<\/p>/g, '$1');
  html = html.replace(/<p>\s*(<ul)/g, '$1');
  html = html.replace(/(<\/ul>)\s*<\/p>/g, '$1');
  html = html.replace(/<p>\s*(<hr)/g, '$1');
  html = html.replace(/(<hr>)\s*<\/p>/g, '$1');
  html = html.replace(/<p>\s*(<pre)/g, '$1');
  html = html.replace(/(<\/pre>)\s*<\/p>/g, '$1');
  html = html.replace(/<p>\s*(<blockquote)/g, '$1');
  html = html.replace(/(<\/blockquote>)\s*<\/p>/g, '$1');
  return html;
}

// ═══════════════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════════════

function toggleAllSections(checked) {
  document.querySelectorAll(".export-section").forEach(function (cb) {
    cb.checked = checked;
  });
}

function getSelectedSections() {
  var sections = [];
  document.querySelectorAll(".export-section:checked").forEach(function (cb) {
    sections.push(cb.value);
  });
  return sections;
}

async function exportMarkdown() {
  collectFormData();
  await saveProject();

  var sections = getSelectedSections();
  if (sections.length === 0) {
    toast("Bitte mindestens einen Bereich auswählen", "error");
    return;
  }

  try {
    var resp = await fetch("/api/export/markdown/zip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sections: sections }),
    });
    if (!resp.ok) throw new Error((await resp.json()).error || "Export fehlgeschlagen");
    var blob = await resp.blob();
    downloadBlob(blob, "pbi-docs.zip");
    toast("Markdown-Export heruntergeladen ✓", "success");
  } catch (e) {
    toast("Export-Fehler: " + e.message, "error");
  }
}

async function exportPDF() {
  collectFormData();
  await saveProject();

  var sections = getSelectedSections();
  if (sections.length === 0) {
    toast("Bitte mindestens einen Bereich auswählen", "error");
    return;
  }

  try {
    var resp = await fetch("/api/export/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sections: sections }),
    });
    if (!resp.ok) throw new Error((await resp.json()).error || "PDF-Export fehlgeschlagen");
    var blob = await resp.blob();
    downloadBlob(blob, "pbi-docs.pdf");
    toast("PDF-Export heruntergeladen ✓", "success");
  } catch (e) {
    toast("PDF-Export-Fehler: " + e.message, "error");
  }
}

function downloadBlob(blob, filename) {
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ── AI Metadata Export / Import ─────────────────────────────────

async function aiExportJson() {
  collectFormData();
  await saveProject();
  try {
    var resp = await fetch("/api/ai/export/download");
    if (!resp.ok) throw new Error((await resp.json()).error || "Export fehlgeschlagen");
    var blob = await resp.blob();
    var name = (project.meta.report_name || "pbi-report").replace(/[^a-zA-Z0-9_\- ]/g, "_");
    downloadBlob(blob, name + "_ai_metadata.json");
    toast("AI-Metadaten heruntergeladen ✓", "success");
  } catch (e) {
    toast("AI-Export-Fehler: " + e.message, "error");
  }
}

async function aiExportPrompt() {
  collectFormData();
  await saveProject();
  try {
    var resp = await fetch("/api/ai/prompt/download");
    if (!resp.ok) throw new Error((await resp.json()).error || "Export fehlgeschlagen");
    var blob = await resp.blob();
    var name = (project.meta.report_name || "pbi-report").replace(/[^a-zA-Z0-9_\- ]/g, "_");
    downloadBlob(blob, name + "_ai_prompt.txt");
    toast("AI-Prompt heruntergeladen ✓ – Inhalt in Claude / ChatGPT einfügen", "success");
  } catch (e) {
    toast("AI-Export-Fehler: " + e.message, "error");
  }
}

function showAiImportDialog() {
  document.getElementById("ai-import-json").value = "";
  document.getElementById("ai-import-overwrite").checked = false;
  showModal("ai-import-dialog");
}

async function doAiImport() {
  var raw = document.getElementById("ai-import-json").value.trim();
  if (!raw) {
    toast("Bitte JSON einfügen", "error");
    return;
  }

  var enriched;
  try {
    enriched = JSON.parse(raw);
  } catch (e) {
    toast("Ungültiges JSON: " + e.message, "error");
    return;
  }

  var overwrite = document.getElementById("ai-import-overwrite").checked;
  closeModal("ai-import-dialog");

  try {
    var result = await apiJson("/api/ai/import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enriched: enriched, overwrite: overwrite }),
    });
    project = result.project;
    populateUI();
    updateDashboard();
    toast("AI-Import erfolgreich ✓", "success");
    alert(result.summary);
  } catch (e) {
    toast("AI-Import-Fehler: " + e.message, "error");
  }
}
