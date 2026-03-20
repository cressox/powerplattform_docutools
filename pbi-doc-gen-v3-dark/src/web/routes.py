"""
Flask routes – REST API for the SPA frontend.

All data flows as JSON between browser and server.
The project YAML is the single source of truth on disk.
"""

from __future__ import annotations

import io
import os
import shutil
import zipfile
import tempfile
from pathlib import Path

from flask import (
    Flask, jsonify, request, render_template,
    send_file, current_app,
)

from ..models import Project
from ..storage import save_project, load_project, project_exists
from ..generator import (
    generate_docs, gen_index, gen_overview, gen_kpis, gen_data_sources,
    gen_queries, gen_data_model, gen_measures, gen_pages_visuals,
    gen_refresh_gateway_rls, gen_assumptions_limitations, gen_change_log,
    gen_permissions, gen_storage, gen_naming_conventions, gen_change_guidance,
)


# ── Section → generator mapping ─────────────────────────────────

SECTION_GENERATORS = {
    "index":            gen_index,
    "overview":         gen_overview,
    "kpis":             gen_kpis,
    "data_sources":     gen_data_sources,
    "power_query":      gen_queries,
    "data_model":       gen_data_model,
    "measures":         gen_measures,
    "report_pages":     gen_pages_visuals,
    "governance":       gen_refresh_gateway_rls,
    "assumptions":      gen_assumptions_limitations,
    "change_log":       gen_change_log,
    "permissions":      gen_permissions,
    "storage":          gen_storage,
    "naming":           gen_naming_conventions,
    "change_guidance":  gen_change_guidance,
}

# Section key → (subfolder, filename) for modular export
SECTION_FILES = {
    "index":            ("",                   "index.md"),
    "overview":         ("01_overview",        "overview.md"),
    "kpis":             ("01_overview",        "kpis.md"),
    "data_sources":     ("02_data_sources",    "data_sources.md"),
    "power_query":      ("03_power_query",     "queries.md"),
    "data_model":       ("04_data_model",      "data_model.md"),
    "measures":         ("05_measures",        "measures.md"),
    "report_pages":     ("06_report_design",   "pages_visuals.md"),
    "governance":       ("07_governance",      "refresh_gateway_rls.md"),
    "assumptions":      ("07_governance",      "assumptions_limitations.md"),
    "change_log":       ("08_change_log",      "change_log.md"),
    "permissions":      ("09_permissions",     "permissions.md"),
    "storage":          ("10_storage",         "storage.md"),
    "naming":           ("11_naming",          "naming_conventions.md"),
    "change_guidance":  ("12_change_guidance",  "change_guidance.md"),
}


def _data_dir() -> Path:
    return Path(current_app.config["DATA_DIR"])


def _project_path() -> Path:
    return _data_dir() / "project.yml"


def _docs_dir() -> Path:
    return Path(current_app.config["DOCS_DIR"])


def _get_project() -> Project:
    p = _project_path()
    if project_exists(p):
        return load_project(p)
    return Project()


def _save(project: Project) -> Path:
    return save_project(project, _project_path())


def register_routes(app: Flask) -> None:
    """Register all routes on the Flask app."""

    # ── Serve SPA ────────────────────────────────────────────────

    @app.route("/")
    def index():
        return render_template("index.html")

    # ── Project CRUD ─────────────────────────────────────────────

    @app.route("/api/project", methods=["GET"])
    def get_project():
        project = _get_project()
        return jsonify(project.to_dict())

    @app.route("/api/project", methods=["POST"])
    def save_project_api():
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid data"}), 400
        project = Project.from_dict(data)
        path = _save(project)
        return jsonify({"ok": True, "path": str(path)})

    @app.route("/api/project/upload", methods=["POST"])
    def upload_project():
        """Load a project YAML/JSON file from upload."""
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        f = request.files["file"]
        if not f.filename:
            return jsonify({"error": "Empty filename"}), 400

        dest = _project_path()
        dest.parent.mkdir(parents=True, exist_ok=True)
        f.save(str(dest))

        project = _get_project()
        return jsonify(project.to_dict())

    # ── Import PBIX / BIM ───────────────────────────────────────

    @app.route("/api/import", methods=["POST"])
    def import_file_route():
        """Import a .pbix, .bim, .pbit, or .json file."""
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        f = request.files["file"]
        if not f.filename:
            return jsonify({"error": "Empty filename"}), 400

        merge_mode = request.form.get("merge_mode", "replace")
        skip_hidden = request.form.get("skip_hidden", "true") == "true"

        # Save upload to temp file
        suffix = Path(f.filename).suffix
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            f.save(tmp.name)
            tmp.close()

            from ..import_manager import (
                ImportOptions, import_file, detect_file_type,
            )

            opts = ImportOptions(
                merge_mode=merge_mode,
                skip_hidden_tables=skip_hidden,
            )

            project = _get_project()
            report = import_file(Path(tmp.name), project, opts)
            _save(project)

            return jsonify({
                "ok": True,
                "project": project.to_dict(),
                "report": report.summary_text(),
            })
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
        finally:
            os.unlink(tmp.name)

    # ── Preview ──────────────────────────────────────────────────

    @app.route("/api/preview/<section>", methods=["GET"])
    def preview_section(section: str):
        gen = SECTION_GENERATORS.get(section)
        if not gen:
            return jsonify({"error": f"Unknown section: {section}"}), 404

        project = _get_project()
        md = gen(project)
        return jsonify({"markdown": md})

    # ── Modular Markdown Export ──────────────────────────────────

    @app.route("/api/export/markdown", methods=["POST"])
    def export_markdown():
        """Generate Markdown docs, respecting selected sections."""
        data = request.get_json(force=True)
        sections = data.get("sections", list(SECTION_FILES.keys()))

        project = _get_project()
        out_dir = _docs_dir()

        # Always write index
        if "index" not in sections:
            sections = ["index"] + list(sections)

        for key in sections:
            gen = SECTION_GENERATORS.get(key)
            info = SECTION_FILES.get(key)
            if not gen or not info:
                continue
            subfolder, filename = info
            target = out_dir / subfolder / filename if subfolder else out_dir / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(gen(project), encoding="utf-8")

        return jsonify({
            "ok": True,
            "path": str(out_dir.resolve()),
            "sections": sections,
        })

    @app.route("/api/export/markdown/zip", methods=["POST"])
    def export_markdown_zip():
        """Generate and download a ZIP of the selected Markdown docs."""
        data = request.get_json(force=True)
        sections = data.get("sections", list(SECTION_FILES.keys()))

        project = _get_project()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for key in sections:
                gen = SECTION_GENERATORS.get(key)
                info = SECTION_FILES.get(key)
                if not gen or not info:
                    continue
                subfolder, filename = info
                arc_name = f"{subfolder}/{filename}" if subfolder else filename
                zf.writestr(arc_name, gen(project))

        buf.seek(0)
        report_name = project.meta.report_name or "pbi-docs"
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in report_name).strip()
        return send_file(
            buf,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{safe_name}_docs.zip",
        )

    # ── PDF Export ───────────────────────────────────────────────

    @app.route("/api/export/pdf", methods=["POST"])
    def export_pdf():
        """Generate PDF with selected sections."""
        from ..pdf_export import generate_pdf, default_pdf_filename

        data = request.get_json(force=True)
        sections = data.get("sections", None)
        project = _get_project()

        out_dir = _data_dir() / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        pdf_file = out_dir / default_pdf_filename(project)

        try:
            result_path = generate_pdf(project, pdf_file, sections)
            return send_file(
                str(result_path),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=Path(str(result_path)).name,
            )
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # ── AI Metadata Export / Import ─────────────────────────────

    @app.route("/api/ai/export", methods=["GET"])
    def ai_export():
        """Export all report metadata as JSON for AI enrichment."""
        from ..ai_metadata import export_metadata

        project = _get_project()
        data = export_metadata(project, include_prompt=False)
        return jsonify(data)

    @app.route("/api/ai/export/download", methods=["GET"])
    def ai_export_download():
        """Download AI metadata as a JSON file."""
        import json as _json
        from ..ai_metadata import export_metadata

        project = _get_project()
        data = export_metadata(project, include_prompt=True)

        buf = io.BytesIO()
        buf.write(_json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"))
        buf.seek(0)

        report_name = project.meta.report_name or "pbi-report"
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in report_name).strip()
        return send_file(
            buf,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"{safe_name}_ai_metadata.json",
        )

    @app.route("/api/ai/prompt/download", methods=["GET"])
    def ai_prompt_download():
        """Download a ready-to-paste AI prompt as text file."""
        import json as _json
        from ..ai_metadata import export_metadata, AI_PROMPT

        project = _get_project()
        data = export_metadata(project, include_prompt=False)
        prompt_text = AI_PROMPT + _json.dumps(data["metadata"], indent=2, ensure_ascii=False)

        buf = io.BytesIO()
        buf.write(prompt_text.encode("utf-8"))
        buf.seek(0)

        report_name = project.meta.report_name or "pbi-report"
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in report_name).strip()
        return send_file(
            buf,
            mimetype="text/plain",
            as_attachment=True,
            download_name=f"{safe_name}_ai_prompt.txt",
        )

    @app.route("/api/ai/import", methods=["POST"])
    def ai_import():
        """Import AI-enriched metadata JSON back into the project."""
        from ..ai_metadata import import_enriched_metadata, format_import_summary

        data = request.get_json(force=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Ungültiges JSON"}), 400

        overwrite = data.get("overwrite", False)
        enriched = data.get("enriched")
        if not enriched or not isinstance(enriched, dict):
            return jsonify({"error": "Kein 'enriched' Objekt im JSON gefunden"}), 400

        project = _get_project()

        # Write enriched data to temp file for import
        import json as _json
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        try:
            _json.dump(enriched, tmp, ensure_ascii=False)
            tmp.close()

            summary = import_enriched_metadata(
                Path(tmp.name), project, overwrite_existing=overwrite,
            )
            _save(project)

            return jsonify({
                "ok": True,
                "summary": format_import_summary(summary),
                "project": project.to_dict(),
            })
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
        finally:
            os.unlink(tmp.name)
