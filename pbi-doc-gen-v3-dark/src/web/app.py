"""
Flask web application for Power BI Documentation Generator.

Locally hosted interactive web UI replacing the PySide6 desktop application.
Run with: python run_web.py
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from flask import Flask

from .routes import register_routes


def create_app(project_dir: Path | None = None) -> Flask:
    """Application factory."""
    base_dir = project_dir or Path(__file__).resolve().parents[2]

    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().parent.parent / "templates"),
        static_folder=str(Path(__file__).resolve().parent / "static"),
    )

    app.secret_key = secrets.token_hex(32)
    app.config["PROJECT_DIR"] = str(base_dir)
    app.config["DATA_DIR"] = str(base_dir / "data")
    app.config["DOCS_DIR"] = str(base_dir / "docs")
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB upload limit

    register_routes(app)

    return app
