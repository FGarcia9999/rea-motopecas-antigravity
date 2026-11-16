"""PUBLIC demonstration mutant: deliberately breaks RF-03 category filtering.

Local-only server, not a realistic benchmark mutant or independent assessor.
"""
from __future__ import annotations
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

class MutantHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlsplit(self.path).path
        if path == "/api/products":
            raw=b"[]"  # deliberately defective: Freios should return two products.
            status=200
        elif path == "/api/health":
            raw=json.dumps({"status":"ok","mode":"demo","payments":False}).encode()
            status=200
        else:
            raw=b'{"detail":"unknown"}'
            status=404
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        raw=b'{"detail":"not implemented in demo mutant"}'
        self.send_response(501)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format, *args):
        return


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=8001)
    a=p.parse_args()
    if not 8000 <= a.port <= 8999:
        raise SystemExit("Only local evaluator test ports 8000–8999 permitted")
    server=ThreadingHTTPServer(("127.0.0.1",a.port),MutantHandler)
    print("PUBLIC_TOY_MUTANT_RUNNING",a.port,flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
