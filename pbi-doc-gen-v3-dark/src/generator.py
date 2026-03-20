"""
Markdown document generator.

Generates the /docs folder structure from a Project instance.
All user-facing text is in German; code identifiers stay English.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from .models import (
    Project, KPI, DataSource, PowerQuery, Measure,
    ReportPage, ChangeLogEntry, ModelTable, ModelRelationship,
)

DOCS_ROOT = Path("docs")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _esc(text: str) -> str:
    """Escape pipe chars for Markdown tables."""
    return text.replace("|", "\\|").replace("\n", " ")


def _build_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Build a Markdown table, omitting columns that are empty in every row."""
    if not rows:
        return []
    keep = [
        ci for ci in range(len(headers))
        if any((row[ci] if ci < len(row) else "").strip() for row in rows)
    ]
    if not keep:
        return []
    hdr = "| " + " | ".join(headers[ci] for ci in keep) + " |"
    sep = "|" + "|".join("---" for _ in keep) + "|"
    result = [hdr, sep]
    for row in rows:
        result.append("| " + " | ".join((row[ci] if ci < len(row) else "") for ci in keep) + " |")
    return result


def _safe_mermaid_id(name: str) -> str:
    """Make a table/column name safe for Mermaid identifiers (ASCII only)."""
    # Replace common non-ASCII chars
    s = name
    for old, new in [("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"),
                     ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue")]:
        s = s.replace(old, new)
    # Replace spaces and special chars with underscores
    s = s.replace(" ", "_").replace("-", "_").replace(".", "_")
    # Keep only ASCII alphanumeric and underscore
    s = "".join(c for c in s if c.isascii() and (c.isalnum() or c == "_"))
    # Strip leading underscores – Mermaid requires identifiers to start with a letter
    s = s.lstrip("_")
    # If empty or starts with a digit, prefix with 'T'
    if not s or s[0].isdigit():
        s = "T" + s
    # Avoid Mermaid reserved constraint keywords used as bare names
    if s.upper() in ("PK", "FK", "UK"):
        s = s + "_col"
    return s


def _mermaid_cardinality(card: str) -> str:
    """Convert cardinality to Mermaid ER notation."""
    card_upper = card.upper().replace(" ", "")
    mapping = {
        "1:1": "||--||",
        "1:N": "||--o{",
        "N:1": "}o--||",
        "N:M": "}o--o{",
        "ONE-TO-ONE": "||--||",
        "ONE-TO-MANY": "||--o{",
        "MANYTOONE": "}o--||",
        "MANYTOMANY": "}o--o{",
    }
    return mapping.get(card_upper, "||--o{")


def _gen_mermaid_er(dm) -> list:
    """Generate a Mermaid ER diagram for the data model."""
    lines = [
        "## Datenmodell-Diagramm",
        "",
        "```mermaid",
        "erDiagram",
    ]

    # Collect table info: columns from keys/description
    table_info = {}
    for t in dm.tables:
        safe_id = _safe_mermaid_id(t.name)
        cols = []
        # Extract key columns
        if t.keys:
            key_text = t.keys.replace("PK:", "").replace("FK:", "").strip()
            for k in key_text.split(","):
                k = k.strip()
                if k:
                    cols.append(("PK", _safe_mermaid_id(k)))
        # Extract first few columns from description
        if t.description and "Spalten:" in t.description:
            col_part = t.description.split("Spalten:")[-1].strip()
            # Remove "(+N weitere)" suffix
            col_part = col_part.split("(+")[0].strip()
            for c in col_part.split(","):
                c = c.strip()
                if c:
                    safe_col = _safe_mermaid_id(c)
                    if not any(existing[1] == safe_col for existing in cols):
                        cols.append(("", safe_col))

        table_info[t.name] = (safe_id, cols)

    # Entity definitions
    for tname, (safe_id, cols) in table_info.items():
        table_type = ""
        for t in dm.tables:
            if t.name == tname:
                table_type = t.table_type
                break
        if cols:
            lines.append(f"    {safe_id} {{")
            for kind, col_name in cols[:8]:  # Limit to 8 columns for readability
                if kind == "PK":
                    lines.append(f"        string {col_name} PK")
                else:
                    lines.append(f"        string {col_name}")
            lines.append("    }")
        else:
            lines.append(f"    {safe_id} {{")
            lines.append(f"        string id PK")
            lines.append("    }")

    # Relationships – only between tables that are defined as entities
    known_ids = {safe_id for (safe_id, _cols) in table_info.values()}
    for r in dm.relationships:
        from_id = _safe_mermaid_id(r.from_table)
        to_id = _safe_mermaid_id(r.to_table)
        if from_id not in known_ids or to_id not in known_ids:
            continue
        rel = _mermaid_cardinality(r.cardinality)
        label = f"{r.from_column} - {r.to_column}"
        lines.append(f"    {from_id} {rel} {to_id} : \"{label}\"")

    # If we have tables but no relationships, show them as isolated entities
    if dm.tables and not dm.relationships:
        lines.append("    %% Keine Beziehungen dokumentiert")

    lines += ["```", ""]
    return lines


# ===================================================================
# Individual generators
# ===================================================================

def gen_index(p: Project) -> str:
    m = p.meta
    lines = [
        f"# {m.report_name or 'Power BI Report'} – Dokumentation",
        "",
        f"> {m.short_description}" if m.short_description else "",
        "",
        "| Feld | Wert |",
        "|---|---|",
        f"| **Eigentümer** | {m.owner} |",
        f"| **Autor** | {m.author} |",
        f"| **Version** | {m.version} |",
        f"| **Datum** | {m.date} |",
        f"| **Zielgruppe** | {m.audience} |",
        "",
        "## Inhaltsverzeichnis",
        "",
        "1. [Übersicht](01_overview/overview.md)",
        "2. [KPIs & Kennzahlen](01_overview/kpis.md)",
        "3. [Datenquellen](02_data_sources/data_sources.md)",
        "4. [Power Query (M)](03_power_query/queries.md)",
        "5. [Datenmodell](04_data_model/data_model.md)",
        "6. [Measures (DAX)](05_measures/measures.md)",
        "7. [Berichtsseiten & Visuals](06_report_design/pages_visuals.md)",
        "8. [Governance – Aktualisierung, Gateway, RLS](07_governance/refresh_gateway_rls.md)",
        "9. [Annahmen & Einschränkungen](07_governance/assumptions_limitations.md)",
        "10. [Änderungsprotokoll](08_change_log/change_log.md)",
        "11. [Berechtigungen](09_permissions/permissions.md)",
        "12. [Ablagestruktur](10_storage/storage.md)",
        "13. [Namenskonzept](11_naming/naming_conventions.md)",
        "14. [Änderungshinweise & Best Practices](12_change_guidance/change_guidance.md)",
        "",
        "---",
        f"*Generiert mit Power BI Documentation Generator*",
    ]
    return "\n".join(lines) + "\n"


def gen_overview(p: Project) -> str:
    m = p.meta
    envs_table = ""
    if m.environments:
        envs_table = (
            "\n## Umgebungen\n\n"
            "| Umgebung | Arbeitsbereich | URL |\n"
            "|---|---|---|\n"
        )
        for e in m.environments:
            envs_table += f"| {e.name} | {e.workspace} | {e.url} |\n"

    links = ""
    if m.powerbi_service_url or m.sharepoint_folder_url:
        links = "\n## Links\n\n"
        if m.powerbi_service_url:
            links += f"- **Power BI Service:** {m.powerbi_service_url}\n"
        if m.sharepoint_folder_url:
            links += f"- **SharePoint-Ordner:** {m.sharepoint_folder_url}\n"

    return (
        f"# Übersicht – {m.report_name}\n\n"
        f"{m.short_description}\n\n"
        f"| Feld | Wert |\n"
        f"|---|---|\n"
        f"| Eigentümer | {m.owner} |\n"
        f"| Autor | {m.author} |\n"
        f"| Version | {m.version} |\n"
        f"| Datum | {m.date} |\n"
        f"| Zielgruppe | {m.audience} |\n"
        f"{envs_table}"
        f"{links}"
    )


def gen_kpis(p: Project) -> str:
    lines = [
        "# KPIs & Kennzahlen",
        "",
    ]
    if not p.kpis:
        lines.append("*Noch keine KPIs dokumentiert.*\n")
        return "\n".join(lines)

    rows = []
    for i, k in enumerate(p.kpis, 1):
        rows.append([str(i), _esc(k.name), _esc(k.granularity), _esc(k.business_description)])
    lines += _build_table(["#", "Name", "Granularität", "Beschreibung"], rows)

    lines.append("")
    for k in p.kpis:
        lines += [
            f"## {k.name}",
            "",
            f"**Fachliche Beschreibung:** {k.business_description}",
            "",
            f"**Technische Definition:** {k.technical_definition}",
            "",
            f"**Granularität:** {k.granularity}",
            "",
            f"**Filter / Kontext:** {k.filters_context}" if k.filters_context else "",
            "",
            f"**Einschränkungen / Hinweise:** {k.caveats}" if k.caveats else "",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def gen_data_sources(p: Project) -> str:
    lines = [
        "# Datenquellen",
        "",
    ]
    if not p.data_sources:
        lines.append("*Noch keine Datenquellen dokumentiert.*\n")
        return "\n".join(lines)

    rows = []
    for s in p.data_sources:
        gw = s.gateway_name if s.gateway_required else ""
        rows.append([_esc(s.name), _esc(s.source_type), _esc(s.connection_info),
                      _esc(s.refresh_cadence), gw])
    lines += _build_table(["Name", "Typ", "Verbindung", "Aktualisierung", "Gateway"], rows)

    lines.append("")
    for s in p.data_sources:
        lines += [
            f"## {s.name}",
            "",
            f"- **Typ:** {s.source_type}",
            f"- **Verbindung:** {s.connection_info}",
            f"- **Aktualisierung:** {s.refresh_cadence}",
            f"- **Gateway:** {'Ja – ' + s.gateway_name if s.gateway_required else 'Nein'}",
            f"- **Verantwortlich:** {s.owner_contact}",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def gen_queries(p: Project) -> str:
    lines = ["# Power Query (M) – Abfragen", ""]
    if not p.power_queries:
        lines.append("*Noch keine Abfragen dokumentiert.*\n")
        return "\n".join(lines)

    for q in p.power_queries:
        lines += [
            f"## {q.query_name}",
            "",
            f"**Zweck:** {q.purpose}",
            "",
            f"**Eingaben:** {q.inputs}" if q.inputs else "",
            "",
            f"**Wichtige Transformationen:** {q.major_transformations}" if q.major_transformations else "",
            "",
            f"**Ausgabetabelle:** `{q.output_table}`" if q.output_table else "",
            "",
        ]
        if q.m_code:
            lines += [
                "**M-Code:**",
                "",
                "```powerquery",
                q.m_code,
                "```",
                "",
            ]
        if q.notes:
            lines += [f"**Hinweise:** {q.notes}", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def gen_data_model(p: Project) -> str:
    dm = p.data_model
    lines = ["# Datenmodell", ""]

    # ── Mermaid ER-Diagramm ────────────────────────
    if dm.tables or dm.relationships:
        lines += _gen_mermaid_er(dm)

    if dm.tables:
        lines += ["## Tabellen", ""]
        rows = []
        for t in dm.tables:
            rows.append([_esc(t.name), _esc(t.table_type), _esc(t.keys), _esc(t.description)])
        lines += _build_table(["Tabelle", "Typ", "Schlüssel", "Beschreibung"], rows)
        lines.append("")

    if dm.relationships:
        lines += ["## Beziehungen", ""]
        rows = []
        for r in dm.relationships:
            rows.append([f"{r.from_table}.{r.from_column}", f"{r.to_table}.{r.to_column}",
                          r.cardinality, r.filter_direction])
        lines += _build_table(["Von (Tabelle.Spalte)", "Nach (Tabelle.Spalte)", "Kardinalität", "Filterrichtung"], rows)
        lines.append("")

    if dm.date_logic_notes:
        lines += ["## Datumslogik", "", dm.date_logic_notes, ""]

    if dm.screenshot_paths:
        lines += ["## Screenshots", ""]
        for sp in dm.screenshot_paths:
            lines.append(f"![Datenmodell]({sp})")
        lines.append("")

    if dm.notes:
        lines += ["## Anmerkungen", "", dm.notes, ""]

    if not dm.tables and not dm.relationships:
        lines.append("*Noch kein Datenmodell dokumentiert.*\n")

    return "\n".join(lines)


def gen_measures(p: Project) -> str:
    lines = ["# Measures (DAX)", ""]
    if not p.measures:
        lines.append("*Noch keine Measures dokumentiert.*\n")
        return "\n".join(lines)

    rows = []
    for i, ms in enumerate(p.measures, 1):
        rows.append([str(i), f"[{_esc(ms.name)}](#{ms.name.lower().replace(' ', '-')})",
                      _esc(ms.display_folder), _esc(ms.description)])
    lines += _build_table(["#", "Name", "Ordner", "Beschreibung"], rows)
    lines.append("")

    for ms in p.measures:
        lines += [
            f"## {ms.name}",
            "",
            f"**Ordner:** {ms.display_folder}" if ms.display_folder else "",
            "",
            f"**Beschreibung:** {ms.description}",
            "",
            "**DAX-Code:**",
            "",
            "```dax",
            ms.dax_code,
            "```",
            "",
        ]
        if ms.dependencies:
            lines += [f"**Abhängigkeiten:** {ms.dependencies}", ""]
        if ms.filter_context_notes:
            lines += [f"**Filter-/Kontextverhalten:** {ms.filter_context_notes}", ""]
        if ms.validation_notes:
            lines += [f"**Validierung:** {ms.validation_notes}", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def gen_pages_visuals(p: Project) -> str:
    lines = ["# Berichtsseiten & Visuals", ""]
    if not p.report_pages:
        lines.append("*Noch keine Seiten dokumentiert.*\n")
        return "\n".join(lines)

    for pg in p.report_pages:
        lines += [
            f"## {pg.page_name}",
            "",
            f"**Zweck:** {pg.purpose}",
            "",
        ]
        if pg.visuals:
            lines += ["### Visuals", ""]
            rows = []
            for v in pg.visuals:
                rows.append([_esc(v.name), _esc(v.description)])
            lines += _build_table(["Visual", "Beschreibung"], rows)
            lines.append("")
        if pg.slicers_filters:
            lines += [f"**Slicer / Filter:** {pg.slicers_filters}", ""]
        if pg.notes:
            lines += [f"**Hinweise:** {pg.notes}", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def gen_refresh_gateway_rls(p: Project) -> str:
    g = p.governance
    lines = ["# Governance – Aktualisierung, Gateway & RLS", ""]
    lines += [
        "## Aktualisierungsplan",
        "",
        g.refresh_schedule or "*Nicht dokumentiert.*",
        "",
        "## Monitoring",
        "",
        g.monitoring_notes or "*Nicht dokumentiert.*",
        "",
        "## Row-Level Security (RLS)",
        "",
        g.rls_notes or "*Nicht konfiguriert / dokumentiert.*",
        "",
        "## Performance-Hinweise",
        "",
        g.performance_notes or "*Keine bekannten Engpässe dokumentiert.*",
        "",
    ]
    return "\n".join(lines)


def gen_assumptions_limitations(p: Project) -> str:
    g = p.governance
    lines = [
        "# Annahmen & Einschränkungen",
        "",
        "## Annahmen",
        "",
        g.assumptions or "*Keine dokumentiert.*",
        "",
        "## Einschränkungen",
        "",
        g.limitations or "*Keine dokumentiert.*",
        "",
    ]
    return "\n".join(lines)


def gen_change_log(p: Project) -> str:
    lines = ["# Änderungsprotokoll", ""]
    if not p.change_log:
        lines.append("*Noch keine Einträge.*\n")
        return "\n".join(lines)

    rows = []
    for c in p.change_log:
        rows.append([_esc(c.version), c.date, _esc(c.description),
                      _esc(c.author), _esc(c.impact), _esc(c.ticket_link)])
    lines += _build_table(["Version", "Datum", "Beschreibung", "Autor", "Auswirkung", "Ticket"], rows)
    lines.append("")
    return "\n".join(lines)


def gen_permissions(p: Project) -> str:
    perm = p.permissions
    lines = [
        "# Berechtigungen",
        "",
        "## Best Practices",
        "",
        "- Verwende Workspace-Rollen statt individueller Freigaben",
        "- Setze Row-Level Security (RLS) fuer sensible Daten ein",
        "- Pruefe regelmaessig die Zugriffsrechte (mindestens quartalsweise)",
        "- Dokumentiere alle Berechtigungsaenderungen im Aenderungsprotokoll",
        "- Nutze Sicherheitsgruppen statt Einzelpersonen fuer Berechtigungen",
        "",
        "## Workspace-Rollen",
        "",
        perm.workspace_roles or "*Nicht dokumentiert.*",
        "",
        "## Row-Level Security (RLS)",
        "",
        perm.rls_details or "*Nicht konfiguriert / dokumentiert.*",
        "",
        "## Freigabe & Sharing",
        "",
        perm.sharing_permissions or "*Nicht dokumentiert.*",
        "",
        "## Zielgruppen-Zugriff",
        "",
        perm.audience_access or "*Nicht dokumentiert.*",
        "",
        "## App-Berechtigungen",
        "",
        perm.app_permissions or "*Nicht dokumentiert.*",
        "",
        "## Datensatz-Berechtigungen",
        "",
        perm.dataset_permissions or "*Nicht dokumentiert.*",
        "",
        "## Datensensitivität / Klassifizierung",
        "",
        perm.data_sensitivity or "*Nicht dokumentiert.*",
        "",
        "## Erforderliche Rollen für Änderungen",
        "",
        perm.required_roles_for_changes or "*Nicht dokumentiert.*",
        "",
        "## Service Principal / App-Registrierung",
        "",
        perm.service_principal or "*Nicht konfiguriert.*",
        "",
    ]
    if perm.entries:
        lines += [
            "## Berechtigungseinträge (Wer → Was → Wo)",
            "",
        ]
        rows = []
        for e in perm.entries:
            rows.append([_esc(e.who), _esc(e.what), _esc(e.where), _esc(e.notes)])
        lines += _build_table(["Wer", "Was", "Wo", "Anmerkung"], rows)
        lines.append("")
    if perm.notes:
        lines += ["## Anmerkungen", "", perm.notes, ""]
    return "\n".join(lines)


def gen_storage(p: Project) -> str:
    st = p.storage_structure
    lines = [
        "# Ablagestruktur",
        "",
        "## Best Practices",
        "",
        "- Speichere PBIX-Dateien nie auf lokalen Laufwerken ohne Backup",
        "- Nutze SharePoint/OneDrive oder ein Git-Repository fuer Versionierung",
        "- Trenne Entwicklungs-, Test- und Produktionsumgebungen",
        "- Verwende Deployment Pipelines fuer kontrollierte Releases",
        "- Erstelle regelmaessige Backups der PBIX-Datei vor groesseren Aenderungen",
        "",
        "## PBIX-Speicherort",
        "",
        st.pbix_location or "*Nicht dokumentiert.*",
        "",
        "## Power BI Workspace",
        "",
        st.workspace_name or "*Nicht dokumentiert.*",
        "",
        "## SharePoint- / OneDrive-Pfad",
        "",
        st.sharepoint_path or "*Nicht dokumentiert.*",
        "",
        "## Data Gateway",
        "",
        st.data_gateway or "*Nicht konfiguriert.*",
        "",
        "## Backup-Strategie / Versionierung",
        "",
        st.backup_strategy or "*Nicht dokumentiert.*",
        "",
        "## Deployment Pipeline",
        "",
        st.deployment_pipeline or "*Nicht konfiguriert.*",
        "",
        "## Git-Repository",
        "",
        st.repo_url or "*Nicht konfiguriert.*",
        "",
    ]
    if st.notes:
        lines += ["## Anmerkungen", "", st.notes, ""]
    return "\n".join(lines)


def gen_naming_conventions(p: Project) -> str:
    nc = p.naming_conventions
    lines = [
        "# Namenskonzept",
        "",
        "## Best Practices",
        "",
        "- Verwende konsistente, sprechende Benennungen in einer einheitlichen Sprache",
        "- Nutze Praefix-Konventionen (z.B. `_` fuer Hilfsmeasures, `dim_` fuer Dimensionen)",
        "- Vermeide Leerzeichen und Sonderzeichen in technischen Namen",
        "- Gruppiere Measures in Display Folders nach Themengebiet",
        "- Dokumentiere alle Abweichungen von den Namensregeln",
        "",
        "## Allgemeine Regeln",
        "",
        nc.general_rules or "*Nicht dokumentiert.*",
        "",
        "## Measures",
        "",
        nc.measures or "*Nicht dokumentiert.*",
        "",
        "## Tabellen",
        "",
        nc.tables or "*Nicht dokumentiert.*",
        "",
        "## Spalten",
        "",
        nc.columns or "*Nicht dokumentiert.*",
        "",
        "## Berichtsseiten",
        "",
        nc.pages or "*Nicht dokumentiert.*",
        "",
        "## Berichte / Dateien",
        "",
        nc.reports or "*Nicht dokumentiert.*",
        "",
        "## Power Queries",
        "",
        nc.queries or "*Nicht dokumentiert.*",
        "",
    ]
    if nc.notes:
        lines += ["## Anmerkungen", "", nc.notes, ""]
    return "\n".join(lines)


def gen_change_guidance(p: Project) -> str:
    cg = p.change_guidance
    lines = [
        "# Änderungshinweise & Best Practices",
        "",
        "## Best Practices für Änderungen am Bericht",
        "",
        "- Erstelle immer ein Backup der PBIX-Datei vor Änderungen",
        "- Teste Änderungen in einer Entwicklungsumgebung vor dem Deployment",
        "- Dokumentiere jede Änderung im Änderungsprotokoll",
        "- Stimme grössere Änderungen vorher mit dem Eigentümer ab",
        "- Prüfe nach Änderungen alle betroffenen Measures und Visuals",
        "- Validiere die Datenaktualisierung nach Modell-Änderungen",
        "",
        "## Vor Änderungen zu beachten",
        "",
        cg.before_changes or "*Nicht dokumentiert.*",
        "",
        "## Test-Checkliste",
        "",
        cg.testing_checklist or "*Nicht dokumentiert.*",
        "",
        "## Deployment-Schritte",
        "",
        cg.deployment_steps or "*Nicht dokumentiert.*",
        "",
        "## Rollback-Plan",
        "",
        cg.rollback_plan or "*Nicht dokumentiert.*",
        "",
        "## Ansprechpartner",
        "",
        cg.contact_persons or "*Nicht dokumentiert.*",
        "",
    ]
    if cg.notes:
        lines += ["## Anmerkungen", "", cg.notes, ""]
    return "\n".join(lines)


# ===================================================================
# Main generator entry point
# ===================================================================

def generate_docs(project: Project, output_dir: Path | None = None) -> Path:
    """Generate the full /docs folder. Returns the output directory path."""
    root = output_dir or DOCS_ROOT
    files = {
        root / "index.md": gen_index(project),
        root / "01_overview" / "overview.md": gen_overview(project),
        root / "01_overview" / "kpis.md": gen_kpis(project),
        root / "02_data_sources" / "data_sources.md": gen_data_sources(project),
        root / "03_power_query" / "queries.md": gen_queries(project),
        root / "04_data_model" / "data_model.md": gen_data_model(project),
        root / "05_measures" / "measures.md": gen_measures(project),
        root / "06_report_design" / "pages_visuals.md": gen_pages_visuals(project),
        root / "07_governance" / "refresh_gateway_rls.md": gen_refresh_gateway_rls(project),
        root / "07_governance" / "assumptions_limitations.md": gen_assumptions_limitations(project),
        root / "08_change_log" / "change_log.md": gen_change_log(project),
        root / "09_permissions" / "permissions.md": gen_permissions(project),
        root / "10_storage" / "storage.md": gen_storage(project),
        root / "11_naming" / "naming_conventions.md": gen_naming_conventions(project),
        root / "12_change_guidance" / "change_guidance.md": gen_change_guidance(project),
    }
    for fpath, content in files.items():
        _write(fpath, content)

    return root
