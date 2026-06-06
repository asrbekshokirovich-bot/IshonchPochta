#!/usr/bin/env python3
"""Ishonch Logistics — UzPost tracking CORS proxy + static file server.

Two jobs, one Render web service:

  1. /track?code=XXXX  — proxies the UzPost public API server-side (it sends no
     CORS headers, so the browser can't call it directly) and returns the JSON
     with permissive CORS headers.
  2. everything else   — serves the static frontend (track.html, admin.html,
     track.html, css, jsx, images). This puts the site and the API on the SAME
     Render domain, so track.html can reach /track without cross-origin issues.

Run locally:   python proxy.py            # listens on :10000
Run on Render: gunicorn proxy:app --bind 0.0.0.0:$PORT
"""

import os
import re

import httpx
from flask import Flask, Response, abort, jsonify, request, send_from_directory

UZPOST_URL = "https://prodapi.pochta.uz/api/v1/public/order"

# Restrict to your site's origin in production by setting ALLOWED_ORIGIN.
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

# Tracking codes: letters, digits and hyphens only (max 50).
VALID_TRACKING = re.compile(r"^[A-Z0-9\-]{1,50}$")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Only these extensions may be served as static files. This is a security
# boundary: it prevents the source of bot.py / proxy.py / main.py, setup.sql,
# render.yaml, requirements.txt, etc. (which sit in the same directory) from
# being downloaded — they would leak the bot token and other internals.
STATIC_EXTS = {
    ".html", ".css", ".js", ".jsx", ".map", ".json",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".woff", ".woff2", ".ttf",
}

# static_folder=None: we handle static serving ourselves with the whitelist.
app = Flask(__name__, static_folder=None)


def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type"
    resp.headers["Vary"] = "Origin"
    return resp


# ───────────────────────── UzPost proxy API ─────────────────────────
@app.route("/track", methods=["GET", "OPTIONS"])
def track():
    if request.method == "OPTIONS":
        return _cors(Response(status=204))

    code = (request.args.get("code") or "").strip().upper()
    if not VALID_TRACKING.match(code):
        return _cors(jsonify({"error": "invalid tracking code"})), 400

    try:
        upstream = httpx.get(
            f"{UZPOST_URL}/{code}",
            headers={"Accept": "application/json"},
            timeout=10.0,
        )
    except httpx.TimeoutException:
        return _cors(jsonify({"error": "upstream timeout"})), 504
    except httpx.RequestError:
        return _cors(jsonify({"error": "upstream unreachable"})), 502

    # Pass the upstream body and status straight through (incl. 404), with our
    # CORS headers attached so the browser accepts the response.
    resp = Response(
        upstream.content,
        status=upstream.status_code,
        mimetype=upstream.headers.get("Content-Type", "application/json"),
    )
    return _cors(resp)


@app.route("/healthz", methods=["GET"])
def healthz():
    return _cors(jsonify({"status": "ok", "service": "ishonch-uzpost-proxy"}))


# ───────────────────────── Static frontend ─────────────────────────
def _send_static(filename):
    _, ext = os.path.splitext(filename)
    if ext.lower() not in STATIC_EXTS:
        abort(404)
    full = os.path.normpath(os.path.join(BASE_DIR, filename))
    # Guard against path traversal escaping BASE_DIR.
    if not full.startswith(BASE_DIR + os.sep) or not os.path.isfile(full):
        abort(404)
    return send_from_directory(BASE_DIR, filename)


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(BASE_DIR, "track.html")


@app.route("/<path:filename>", methods=["GET"])
def static_files(filename):
    return _send_static(filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
