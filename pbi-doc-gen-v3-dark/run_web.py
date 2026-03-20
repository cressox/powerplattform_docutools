#!/usr/bin/env python3
"""
Start the Power BI Documentation Generator as a local web application.

Usage:
    python run_web.py [--port PORT] [--host HOST] [--no-open]

Opens the browser automatically at http://localhost:5000.
"""

from __future__ import annotations

import argparse
import threading
import webbrowser
from pathlib import Path

from src.web.app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Power BI Documentation Generator – Web Edition",
    )
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-open", action="store_true",
                        help="Don't open the browser automatically")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    app = create_app(project_dir)

    url = f"http://{args.host}:{args.port}"
    print(f"\n  Power BI Documentation Generator – Web Edition")
    print(f"  Running at {url}")
    print(f"  Press Ctrl+C to stop.\n")

    if not args.no_open:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(host=args.host, port=args.port, debug=True, use_reloader=True)


if __name__ == "__main__":
    main()
