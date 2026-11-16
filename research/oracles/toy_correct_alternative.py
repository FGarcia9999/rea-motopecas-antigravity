"""Public, intentionally different implementation of the PUBLIC Rota 2 demo suite.

Does not establish equivalence to the whole Rota 2 application or to any private
reference. Intended solely as an oracle false-rejection POSITIVE CONTROL.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from threading import Lock

REPLAY: dict[str, str] = {}
GUARD = Lock()


class Handler(BaseHTTPRequestHandler):
    def respond(self, status: int, data: object) -> None:
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        query = urlsplit(self.path)
        if query.path == "/api/health":
            self.respond(200, {"payments": False, "status": "ok", "implementation": "PUBLIC_ALT"})
        elif query.path == "/api/products":
            cat = parse_qs(query.query).get("category", [""])[0]
            if cat == "Freios":
                self.respond(200, [
                    {"id": 321, "category": "Freios", "title": "Peça sintética A"},
                    {"id": 322, "category": "Freios", "title": "Peça sintética B"},
                ])
            else:
                self.respond(200, [])
        else:
            self.respond(404, {"detail": "not found"})

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/orders":
            self.respond(404, {"detail": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.respond(400, {"detail": "bad length"})
            return
        if length > 4096 or length < 2:
            self.respond(400, {"detail": "invalid request"})
            return
        try:
            body = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            self.respond(400, {"detail": "invalid json"})
            return
        if body != {"items": [{"product_id": 1, "quantity": 1}]}:
            self.respond(422, {"detail": "unsupported public toy request"})
            return
        token = self.headers.get("Idempotency-Key", "")
        if not token or len(token) > 120:
            self.respond(400, {"detail": "missing key"})
            return
        with GUARD:
            prior = token in REPLAY
            if not prior:
                REPLAY[token] = "ALT-" + str(len(REPLAY) + 1)
            identifier = REPLAY[token]
        self.respond(201, {"order_id": identifier, "replayed": prior, "payment_processed": False})

    def log_message(self, *args) -> None:
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8002)
    args = ap.parse_args()
    if not 8000 <= args.port <= 8999:
        raise SystemExit("Only own local ports 8000–8999 are allowed")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
