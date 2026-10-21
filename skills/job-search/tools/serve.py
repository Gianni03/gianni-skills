#!/usr/bin/env python3
"""Serve the report locally so the buttons can write straight to disk.

    serve.py [--out-dir ofertas] [--port 8765] [--no-open]

Open the report through this server and every "Aplicado" / "Fuera de rango" click is
appended to `state/feedback.jsonl` immediately — no export, no download folder.

The same HTML still works if you open the file directly: it falls back to
`localStorage` and the "Exportar feedback" button. The server is convenience, not a
requirement.
"""

import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SKILL))
FEEDBACK = os.path.join(SKILL, "state", "feedback.jsonl")


def make_handler(directory):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # keep the console clean

        def _resolve(self, path):
            clean = path.split("?")[0].lstrip("/") or "index.html"
            if clean.startswith("..") or os.path.isabs(clean):
                return None
            return os.path.join(directory, clean)

        def do_GET(self):
            target = self._resolve(self.path)
            if not target or not os.path.isfile(target):
                self.send_error(404, "not found")
                return
            if target.endswith(".html"):
                ctype = "text/html; charset=utf-8"
            elif target.endswith(".json"):
                ctype = "application/json; charset=utf-8"
            else:
                ctype = "application/octet-stream"
            with open(target, "rb") as handle:
                body = handle.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path.split("?")[0] != "/feedback":
                self.send_error(404, "not found")
                return
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length)
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                self.send_error(400, "invalid JSON")
                return
            if not entry.get("url") or entry.get("action") not in ("applied", "dropped"):
                self.send_error(400, "url and action are required")
                return

            entry.setdefault("ts", datetime.now().isoformat(timespec="seconds"))
            os.makedirs(os.path.dirname(FEEDBACK), exist_ok=True)
            with open(FEEDBACK, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def latest_report(directory):
    if not os.path.isdir(directory):
        return None
    html = [f for f in os.listdir(directory) if f.endswith(".html")]
    if not html:
        return None
    return sorted(html)[-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=os.path.join(ROOT, "ofertas"))
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    directory = os.path.abspath(args.out_dir)
    report = latest_report(directory)
    if not report:
        print(f"no HTML report in {directory} — run tools/run.py first", file=sys.stderr)
        sys.exit(1)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(directory))
    url = f"http://127.0.0.1:{args.port}/{report}"
    print(f"serving {directory}")
    print(f"report: {url}")
    print(f"feedback -> {FEEDBACK}")
    print("Ctrl+C to stop")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
