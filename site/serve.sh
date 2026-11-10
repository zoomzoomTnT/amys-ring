#!/usr/bin/env bash
# Serve this folder as a static site.
#
# Public site at http://amysring.duckdns.org  (port 80; needs root and
# a router port-forward of 80 to this machine):
#   sudo ./serve.sh 80
#
# Local preview:
#   ./serve.sh 8080
#
# To use the finished Blender model, replace ring.glb in this folder
# with the real file (for example copy /workspace/ring/ring.glb here).
set -euo pipefail
PORT="${1:-80}"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
exec python3 - "$PORT" << 'PY'
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".glb": "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".hdr": "image/vnd.radiance",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".html": "text/html",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

port = int(sys.argv[1])
server = HTTPServer(("0.0.0.0", port), Handler)
print(f"Serving {os.getcwd()} at http://0.0.0.0:{port}", flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopped.")
PY
