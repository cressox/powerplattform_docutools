#!/usr/bin/env python3
"""
Power BI Documentation Generator – Main CLI entry point.

Run:  python -m src.main
      python main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as `python main.py` from project root
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "src"

from .models import Project
from .storage import save_project, load_project, project_exists, DEFAULT_PROJECT_FILE
from .generator import generate_docs
from .prompts import (
    prompt_project_meta, prompt_kpi, prompt_data_source,
    prompt_power_query, prompt_data_model, prompt_measure,
    prompt_report_page, prompt_governance, prompt_change_log_entry,
)
from .importers import import_measures_from_file, import_queries_from_file, export_measures_to_file
from .ai_metadata import (
    export_metadata_to_file, export_prompt_to_file,
    import_enriched_metadata, format_import_summary,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║   Power BI Documentation Generator                   ║
║   ─────────────────────────────────                  ║
║   Standardisierte Dokumentation für Power BI Reports ║
╚══════════════════════════════════════════════════════╝
"""

MENU = """
┌──────────────────────────────────────────┐
│  Hauptmenü                               │
├──────────────────────────────────────────┤
│  1  Neues Projekt anlegen                │
│  2  Projekt-Metadaten bearbeiten         │
│  3  KPI hinzufügen                       │
│  4  Datenquelle hinzufügen               │
│  5  Power Query (M) dokumentieren        │
│  6  Datenmodell bearbeiten               │
│  7  Measure (DAX) hinzufügen             │
│  8  Berichtsseite / Visuals hinzufügen   │
│  9  Governance bearbeiten                │
│ 10  Änderungsprotokoll-Eintrag           │
│ 11  ▶ Dokumentation generieren           │
│ 12  Import / Export Helfer               │
│  0  Beenden                              │
└──────────────────────────────────────────┘
"""


def _autosave(project: Project, path: Path = DEFAULT_PROJECT_FILE) -> None:
    """Save project after each completed action."""
    saved = save_project(project, path)
    print(f"\n  💾 Gespeichert: {saved}")


def _load_or_new() -> Project:
    """Load existing project or return a new one."""
    if project_exists():
        print(f"  ℹ  Vorhandenes Projekt gefunden: {DEFAULT_PROJECT_FILE}")
        return load_project()
    return Project()


# ---------------------------------------------------------------------------
# Import / Export sub-menu
# ---------------------------------------------------------------------------

def import_export_menu(project: Project) -> None:
    print("""
  ┌──────────────────────────────────────────────────┐
  │  Import / Export                                  │
  ├──────────────────────────────────────────────────┤
  │  1  Measures aus Datei importieren               │
  │  2  Queries aus Datei importieren                │
  │  3  Measures in Datei exportieren                │
  │  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─               │
  │  4  🤖 AI-Metadaten exportieren (JSON)            │
  │  5  🤖 AI-Prompt exportieren (zum Einfügen)       │
  │  6  🤖 AI-angereicherte Daten importieren         │
  │  0  Zurück                                       │
  └──────────────────────────────────────────────────┘""")
    choice = input("\n  Auswahl: ").strip()

    if choice == "1":
        fp = input("  Dateipfad zur Measures-Datei: ").strip()
        path = Path(fp)
        if not path.exists():
            print(f"  ⚠  Datei nicht gefunden: {path}")
            return
        measures = import_measures_from_file(path)
        project.measures.extend(measures)
        print(f"  ✅ {len(measures)} Measure(s) importiert.")

    elif choice == "2":
        fp = input("  Dateipfad zur Queries-Datei: ").strip()
        path = Path(fp)
        if not path.exists():
            print(f"  ⚠  Datei nicht gefunden: {path}")
            return
        queries = import_queries_from_file(path)
        project.power_queries.extend(queries)
        print(f"  ✅ {len(queries)} Query/Queries importiert.")

    elif choice == "3":
        fp = input("  Ziel-Dateipfad [data/measures_export.txt]: ").strip()
        path = Path(fp) if fp else Path("data/measures_export.txt")
        export_measures_to_file(project.measures, path)
        print(f"  ✅ {len(project.measures)} Measure(s) exportiert nach {path}.")

    elif choice == "4":
        fp = input("  Ziel-Dateipfad [data/ai_metadata_export.json]: ").strip()
        path = Path(fp) if fp else Path("data/ai_metadata_export.json")
        result = export_metadata_to_file(project, path)
        print(f"  ✅ AI-Metadaten exportiert nach {result}.")
        print("     Enthält JSON + AI-Prompt. Öffne die Datei und kopiere")
        print("     den Inhalt in Claude / ChatGPT.")

    elif choice == "5":
        fp = input("  Ziel-Dateipfad [data/ai_prompt.txt]: ").strip()
        path = Path(fp) if fp else Path("data/ai_prompt.txt")
        result = export_prompt_to_file(project, path)
        print(f"  ✅ AI-Prompt exportiert nach {result}.")
        print("     Kopiere den gesamten Inhalt in Claude / ChatGPT.")
        print("     Die KI gibt ein angereichertes JSON zurück.")
        print("     Speichere dieses als .json und importiere es mit Option 6.")

    elif choice == "6":
        fp = input("  Dateipfad zur angereicherten JSON-Datei: ").strip()
        path = Path(fp)
        if not path.exists():
            print(f"  ⚠  Datei nicht gefunden: {path}")
            return
        overwrite = input("  Bestehende Beschreibungen überschreiben? (j/N): ").strip().lower()
        overwrite = overwrite in ("j", "ja", "y")
        try:
            summary = import_enriched_metadata(path, project, overwrite_existing=overwrite)
            print(f"\n  {format_import_summary(summary)}")
        except Exception as e:
            print(f"  ❌ Import fehlgeschlagen: {e}")

    elif choice == "0":
        return


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    print(BANNER)
    project = _load_or_new()

    while True:
        print(MENU)
        choice = input("  Auswahl: ").strip()

        try:
            if choice == "1":
                # New project (resets meta, keeps option to overwrite)
                if project.meta.report_name:
                    confirm = input(
                        f"  ⚠  Projekt '{project.meta.report_name}' existiert bereits. "
                        "Überschreiben? (j/N): "
                    ).strip().lower()
                    if confirm not in ("j", "ja", "y"):
                        continue
                    project = Project()
                project.meta = prompt_project_meta()
                _autosave(project)

            elif choice == "2":
                project.meta = prompt_project_meta(project.meta)
                _autosave(project)

            elif choice == "3":
                kpi = prompt_kpi()
                project.kpis.append(kpi)
                _autosave(project)
                if _ask_another("KPI"):
                    continue  # re-enter loop, user picks 3 again

            elif choice == "4":
                ds = prompt_data_source()
                project.data_sources.append(ds)
                _autosave(project)

            elif choice == "5":
                q = prompt_power_query()
                project.power_queries.append(q)
                _autosave(project)

            elif choice == "6":
                project.data_model = prompt_data_model(project.data_model)
                _autosave(project)

            elif choice == "7":
                ms = prompt_measure()
                project.measures.append(ms)
                _autosave(project)

            elif choice == "8":
                pg = prompt_report_page()
                project.report_pages.append(pg)
                _autosave(project)

            elif choice == "9":
                project.governance = prompt_governance(project.governance)
                _autosave(project)

            elif choice == "10":
                entry = prompt_change_log_entry()
                project.change_log.append(entry)
                _autosave(project)

            elif choice == "11":
                print("\n  ⏳ Generiere Dokumentation …")
                out = generate_docs(project)
                print(f"  ✅ Dokumentation generiert in: {out.resolve()}")
                print("     Öffne docs/index.md als Einstiegspunkt.")

            elif choice == "12":
                import_export_menu(project)
                _autosave(project)

            elif choice == "0":
                _autosave(project)
                print("\n  Auf Wiedersehen! 👋\n")
                break

            else:
                print("  ⚠  Ungültige Auswahl.")

        except KeyboardInterrupt:
            print("\n\n  Abgebrochen. Speichere aktuellen Stand …")
            _autosave(project)
            break
        except Exception as e:
            print(f"\n  ❌ Fehler: {e}")
            _autosave(project)


def _ask_another(item_type: str) -> bool:
    val = input(f"\n  Weiteren {item_type} hinzufügen? (j/N): ").strip().lower()
    return val in ("j", "ja", "y", "yes")


if __name__ == "__main__":
    main()
