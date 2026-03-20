"""
AI Metadata Export / Import – Export report metadata as JSON for AI enrichment.

Workflow:
1. Export: Extracts all report-relevant data (measures, data sources, queries,
   tables, KPIs, pages, etc.) into a structured JSON file together with an
   AI prompt that instructs an LLM (e.g. Claude Sonnet) to enrich descriptions.
2. The user pastes the JSON into an AI chat and receives an enriched version.
3. Import: The enriched JSON is imported back and merged into the project,
   adding AI-generated descriptions to each component.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .models import (
    Project, KPI, DataSource, PowerQuery, ModelTable, ModelRelationship,
    Measure, ReportPage, Visual, Governance, _new_id,
)

# ── AI Prompt Template ──────────────────────────────────────────

AI_PROMPT = """\
Du bist ein Power BI Dokumentations-Experte. Du erhältst die Metadaten eines \
Power BI Berichts als JSON. Deine Aufgabe ist es, die fehlenden oder leeren \
Beschreibungsfelder (description, business_description, purpose, notes, etc.) \
mit fachlich sinnvollen, präzisen Beschreibungen auf Deutsch zu befüllen.

## Regeln

1. **Sprache**: Deutsch, professionell, sachlich.
2. **Kontext**: Leite die Beschreibung aus den vorhandenen technischen Informationen \
ab (Name, DAX-Code, M-Code, Tabellenstruktur, Beziehungen, etc.).
3. **Nur ergänzen**: Überschreibe KEINE bestehenden, nicht-leeren Beschreibungen. \
Fülle nur leere Felder ("") aus.
4. **Measures**: Erkläre die DAX-Formel, ihren Zweck, Filterkontext und mögliche \
Abhängigkeiten. Wenn `filter_context_notes` leer ist, analysiere den DAX-Code \
auf CALCULATE, FILTER, ALL, ALLEXCEPT, Time-Intelligence und beschreibe den \
Filterkontext.
5. **Datenquellen**: Beschreibe den Zweck der Quelle basierend auf Typ und \
Verbindungsinformationen.
6. **Power Queries**: Erkläre den Zweck der Abfrage basierend auf dem M-Code und \
den Transformationen.
7. **Tabellen**: Erkläre den Zweck der Tabelle basierend auf Typ (Fact/Dimension) \
und Schlüsseln.
8. **KPIs**: Falls `business_description` leer ist, leite sie aus der \
`technical_definition` (DAX) ab.
9. **Berichtsseiten**: Beschreibe den Zweck der Seite basierend auf ihrem Namen \
und den enthaltenen Visuals.
10. **Struktur beibehalten**: Gib das JSON exakt im selben Format zurück. Ändere \
KEINE Schlüssel, IDs oder Strukturen. Füge keine neuen Felder hinzu.

## Ausgabe

Gib ausschliesslich das angereicherte JSON zurück – kein Markdown, keine Erklärungen, \
kein umschließender Code-Block. Nur valides JSON.

---

Hier sind die Metadaten:

"""


def _strip_empty(d: dict) -> dict:
    """Remove keys with empty-string or None values (keep booleans and 0)."""
    return {k: v for k, v in d.items()
            if v is not None and v != "" and v != []}


# ── Export ──────────────────────────────────────────────────────

def export_metadata(project: Project, include_prompt: bool = True) -> dict:
    """
    Build a JSON-serializable dict containing all report-relevant metadata
    that an AI can enrich with descriptions.
    """
    payload: dict = {
        "_info": {
            "tool": "pbi-doc-gen-v3-dark – AI Metadata Export",
            "report_name": project.meta.report_name,
            "version": project.meta.version,
            "hinweis": (
                "Dieses JSON enthält die Metadaten eines Power BI Berichts. "
                "Bitte ergänze alle leeren Beschreibungsfelder mit fachlich "
                "sinnvollen Beschreibungen auf Deutsch."
            ),
        },
    }

    # Measures
    if project.measures:
        payload["measures"] = [
            {
                "id": m.id,
                "name": m.name,
                "display_folder": m.display_folder,
                "description": m.description,
                "dax_code": m.dax_code,
                "dependencies": m.dependencies,
                "filter_context_notes": m.filter_context_notes,
                "validation_notes": m.validation_notes,
            }
            for m in project.measures
        ]

    # Data sources
    if project.data_sources:
        payload["data_sources"] = [
            {
                "id": ds.id,
                "name": ds.name,
                "source_type": ds.source_type,
                "connection_info": ds.connection_info,
                "refresh_cadence": ds.refresh_cadence,
                "gateway_required": ds.gateway_required,
                "gateway_name": ds.gateway_name,
                "owner_contact": ds.owner_contact,
            }
            for ds in project.data_sources
        ]

    # Power Queries
    if project.power_queries:
        payload["power_queries"] = [
            {
                "id": q.id,
                "query_name": q.query_name,
                "purpose": q.purpose,
                "inputs": q.inputs,
                "major_transformations": q.major_transformations,
                "m_code": q.m_code,
                "output_table": q.output_table,
                "notes": q.notes,
            }
            for q in project.power_queries
        ]

    # Data model tables
    if project.data_model.tables:
        payload["tables"] = [
            {
                "name": t.name,
                "table_type": t.table_type,
                "description": t.description,
                "keys": t.keys,
            }
            for t in project.data_model.tables
        ]

    # Data model relationships
    if project.data_model.relationships:
        payload["relationships"] = [
            {
                "from_table": r.from_table,
                "from_column": r.from_column,
                "to_table": r.to_table,
                "to_column": r.to_column,
                "cardinality": r.cardinality,
                "filter_direction": r.filter_direction,
            }
            for r in project.data_model.relationships
        ]

    # KPIs
    if project.kpis:
        payload["kpis"] = [
            {
                "id": k.id,
                "name": k.name,
                "business_description": k.business_description,
                "technical_definition": k.technical_definition,
                "granularity": k.granularity,
                "filters_context": k.filters_context,
                "caveats": k.caveats,
            }
            for k in project.kpis
        ]

    # Report pages
    if project.report_pages:
        payload["report_pages"] = [
            {
                "id": p.id,
                "page_name": p.page_name,
                "purpose": p.purpose,
                "visuals": [
                    {"name": v.name, "description": v.description}
                    for v in p.visuals
                ],
                "slicers_filters": p.slicers_filters,
                "notes": p.notes,
            }
            for p in project.report_pages
        ]

    # Governance
    gov = project.governance
    gov_dict = {
        "refresh_schedule": gov.refresh_schedule,
        "monitoring_notes": gov.monitoring_notes,
        "rls_notes": gov.rls_notes,
        "performance_notes": gov.performance_notes,
        "assumptions": gov.assumptions,
        "limitations": gov.limitations,
    }
    if any(v for v in gov_dict.values()):
        payload["governance"] = gov_dict

    result = {"metadata": payload}
    if include_prompt:
        result["_ai_prompt"] = AI_PROMPT
    return result


def export_metadata_to_file(
    project: Project,
    filepath: Path,
    include_prompt: bool = True,
) -> Path:
    """Export metadata JSON to a file. Returns the written path."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = export_metadata(project, include_prompt=include_prompt)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def export_prompt_to_file(project: Project, filepath: Path) -> Path:
    """
    Export a ready-to-paste prompt (text) that includes the AI instructions
    followed by the metadata JSON – ideal for pasting into Claude / ChatGPT.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = export_metadata(project, include_prompt=False)
    prompt_text = AI_PROMPT + json.dumps(data["metadata"], indent=2, ensure_ascii=False)
    filepath.write_text(prompt_text, encoding="utf-8")
    return filepath


# ── Import (merge enriched metadata back) ───────────────────────

def import_enriched_metadata(
    json_path: Path,
    project: Project,
    overwrite_existing: bool = False,
) -> dict:
    """
    Import AI-enriched metadata JSON back into the project.

    Returns a summary dict with counts of updated fields per section.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Accept both wrapped {"metadata": {...}} and flat format
    data = raw.get("metadata", raw)

    summary = {
        "measures_updated": 0,
        "data_sources_updated": 0,
        "power_queries_updated": 0,
        "tables_updated": 0,
        "kpis_updated": 0,
        "report_pages_updated": 0,
        "governance_updated": 0,
        "fields_enriched": 0,
    }

    # ── Measures ────────────────────────────────────────────
    if "measures" in data:
        by_id = {m.id: m for m in project.measures}
        by_name = {m.name: m for m in project.measures}
        for item in data["measures"]:
            target = by_id.get(item.get("id")) or by_name.get(item.get("name"))
            if not target:
                continue
            changed = _merge_fields(target, item, [
                "description", "filter_context_notes", "validation_notes",
                "dependencies",
            ], overwrite_existing)
            if changed:
                summary["measures_updated"] += 1
                summary["fields_enriched"] += changed

    # ── Data Sources ────────────────────────────────────────
    if "data_sources" in data:
        by_id = {ds.id: ds for ds in project.data_sources}
        by_name = {ds.name: ds for ds in project.data_sources}
        for item in data["data_sources"]:
            target = by_id.get(item.get("id")) or by_name.get(item.get("name"))
            if not target:
                continue
            changed = _merge_fields(target, item, [
                "owner_contact",
            ], overwrite_existing)
            if changed:
                summary["data_sources_updated"] += 1
                summary["fields_enriched"] += changed

    # ── Power Queries ───────────────────────────────────────
    if "power_queries" in data:
        by_id = {q.id: q for q in project.power_queries}
        by_name = {q.query_name: q for q in project.power_queries}
        for item in data["power_queries"]:
            target = by_id.get(item.get("id")) or by_name.get(item.get("query_name"))
            if not target:
                continue
            changed = _merge_fields(target, item, [
                "purpose", "inputs", "major_transformations", "notes",
            ], overwrite_existing)
            if changed:
                summary["power_queries_updated"] += 1
                summary["fields_enriched"] += changed

    # ── Tables ──────────────────────────────────────────────
    if "tables" in data:
        by_name = {t.name: t for t in project.data_model.tables}
        for item in data["tables"]:
            target = by_name.get(item.get("name"))
            if not target:
                continue
            changed = _merge_fields(target, item, [
                "description",
            ], overwrite_existing)
            if changed:
                summary["tables_updated"] += 1
                summary["fields_enriched"] += changed

    # ── KPIs ────────────────────────────────────────────────
    if "kpis" in data:
        by_id = {k.id: k for k in project.kpis}
        by_name = {k.name: k for k in project.kpis}
        for item in data["kpis"]:
            target = by_id.get(item.get("id")) or by_name.get(item.get("name"))
            if not target:
                continue
            changed = _merge_fields(target, item, [
                "business_description", "caveats",
            ], overwrite_existing)
            if changed:
                summary["kpis_updated"] += 1
                summary["fields_enriched"] += changed

    # ── Report Pages ────────────────────────────────────────
    if "report_pages" in data:
        by_id = {p.id: p for p in project.report_pages}
        by_name = {p.page_name: p for p in project.report_pages}
        for item in data["report_pages"]:
            target = by_id.get(item.get("id")) or by_name.get(item.get("page_name"))
            if not target:
                continue
            changed = _merge_fields(target, item, [
                "purpose", "notes",
            ], overwrite_existing)
            # Also merge visual descriptions
            if "visuals" in item and target.visuals:
                vis_by_name = {v.name: v for v in target.visuals}
                for v_item in item["visuals"]:
                    v_target = vis_by_name.get(v_item.get("name"))
                    if v_target:
                        changed += _merge_fields(v_target, v_item, [
                            "description",
                        ], overwrite_existing)
            if changed:
                summary["report_pages_updated"] += 1
                summary["fields_enriched"] += changed

    # ── Governance ──────────────────────────────────────────
    if "governance" in data:
        gov = project.governance
        changed = _merge_fields(gov, data["governance"], [
            "refresh_schedule", "monitoring_notes", "rls_notes",
            "performance_notes", "assumptions", "limitations",
        ], overwrite_existing)
        if changed:
            summary["governance_updated"] = 1
            summary["fields_enriched"] += changed

    return summary


def _merge_fields(target, source: dict, fields: list, overwrite: bool) -> int:
    """
    Merge description fields from source dict into target object.
    Only overwrites if target field is empty OR overwrite=True.
    Returns number of fields changed.
    """
    changed = 0
    for field_name in fields:
        new_val = source.get(field_name, "")
        if not new_val:
            continue
        current = getattr(target, field_name, "")
        if not current or overwrite:
            setattr(target, field_name, new_val)
            changed += 1
    return changed


def format_import_summary(summary: dict) -> str:
    """Format the import summary as human-readable text."""
    lines = ["AI-Anreicherung abgeschlossen:", ""]
    section_labels = {
        "measures_updated": "Measures",
        "data_sources_updated": "Datenquellen",
        "power_queries_updated": "Power Queries",
        "tables_updated": "Tabellen",
        "kpis_updated": "KPIs",
        "report_pages_updated": "Berichtsseiten",
        "governance_updated": "Governance",
    }
    any_update = False
    for key, label in section_labels.items():
        count = summary.get(key, 0)
        if count:
            lines.append(f"  • {label}: {count} aktualisiert")
            any_update = True

    if not any_update:
        lines.append("  Keine Felder wurden aktualisiert.")
        lines.append("  (Alle Beschreibungen waren bereits gefüllt oder")
        lines.append("   die JSON-Daten enthielten keine Änderungen.)")
    else:
        total = summary.get("fields_enriched", 0)
        lines.append(f"\n  Insgesamt {total} Feld(er) angereichert.")

    return "\n".join(lines)
