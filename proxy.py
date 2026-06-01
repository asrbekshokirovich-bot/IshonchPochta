#!/usr/bin/env python3
"""Ishonch Logistics — UzPost tracking CORS proxy.

The UzPost public API (prodapi.pochta.uz) does not send CORS headers, so the
browser cannot call it directly from track.html. This tiny Flask service sits
in front of it: the frontend calls `/track?code=XXXX`, we fetch the upstream
order server-side and return its JSON with permissive CORS headers.

Run locally:   python proxy.py            # listens on :10000
Run on Render: gunicorn proxy:app --bind 0.0.0.0:$PORT
"""

import os
import re

import httpx
from flask import Flask, Response, jsonify, request

UZPOST_URL = "https://prodapi.pochta.uz/api/v1/public/order"

# Restrict to your site's origin in production by setting ALLOWED_ORIGIN.
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

# Tracking codes: letters, digits and hyphens only (max 50). Mirrors the
# VALID_TRACKING check used in admin.html / track.html.
VALID_TRACKING = re.compile(r"^[A-Z0-9\-]{1,50}$")

app = Flask(__name__)


def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type"
    resp.headers["Vary"] = "Origin"
    return resp


@app.route("/", methods=["GET"])
def health():
    return _cors(jsonify({"status": "ok", "service": "ishonch-uzpost-proxy"}))


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

    # Pass the upstream body and status straight through (incl. 404), but with
    # our CORS headers attached so the browser accepts the response.
    resp = Response(
        upstream.content,
        status=upstream.status_code,
        mimetype=upstream.headers.get("Content-Type", "application/json"),
    )
    return _cors(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
