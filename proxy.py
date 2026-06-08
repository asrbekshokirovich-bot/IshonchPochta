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
from datetime import datetime, timezone

import httpx
from flask import Flask, Response, abort, jsonify, request, send_from_directory

UZPOST_URL = "https://prodapi.pochta.uz/api/v1/public/order"

# ─────────────────────── UzPost status mapping ───────────────────────
# UzPost's public order API returns a single raw status code (e.g. "dispatched").
# We collapse its ~60 internal codes into the 4 statuses the Ishonch frontend and
# courier bot understand: accepted / in_transit / out_for_delivery / delivered.
#
# Mapping follows the labels the user specified (UzPost UZ label → our status):
#   "Yangi jo'natma" / "Saralanmoqda"  → accepted          (Qabul qilindi)
#   "Yo'lda" / Tranzit                 → in_transit        (Yo'lda)
#   "Yetkazib berishga tayyor"         → out_for_delivery  (Yetkazib berishda)
#   "Yuborilgan" / "Topshirildi"       → delivered         (Yetkazildi)
UZPOST_STATUS_MAP = {
    # accepted — newly registered, courier-assigned, sorting / warehouse
    "created": "accepted",
    "unassigned": "accepted",
    "accepted": "accepted",
    "assigned_to_courier": "accepted",
    "pending_assign_to_courier": "accepted",
    "in_sorting_facility": "accepted",
    "in_sorting_facility_public": "accepted",
    "inbound_sorting": "accepted",
    "inbound_sorting_for_uzum": "accepted",
    "order_sorting": "accepted",
    "processing_at_warehouse": "accepted",
    "to_warehouse": "accepted",
    "warehouse": "accepted",
    "in_different_warehouse": "accepted",
    "partially_in_sorting_facility": "accepted",
    "prepared_for_transit_public": "accepted",
    "first_pickup_attempt": "accepted",
    "second_pickup_attempt": "accepted",
    "third_pickup_attempt": "accepted",
    "other_pickup_attempt": "accepted",
    # in_transit — moving between facilities / customs / returns in motion
    "in_transit": "in_transit",
    "in_transit_public": "in_transit",
    "in_transit_to_supplier": "in_transit",
    "transited_to_supplier": "in_transit",
    "arrived": "in_transit",
    "sent_to_customs": "in_transit",
    "returned_from_customs": "in_transit",
    "returning_to_origin": "in_transit",
    "returned_to_origin": "in_transit",
    "to_be_returned": "in_transit",
    "out_for_return": "in_transit",
    "returned_from_locker_post": "in_transit",
    # out_for_delivery — ready for / on the way to the recipient, delivery attempts
    "ready_for_delivery": "out_for_delivery",
    "ready_for_issue": "out_for_delivery",
    "out_for_delivery": "out_for_delivery",
    "arrived_to_delivery_address": "out_for_delivery",
    "delivery_scheduled": "out_for_delivery",
    "delivery_on_hold": "out_for_delivery",
    "future_delivery_requested": "out_for_delivery",
    "delivery_attempt": "out_for_delivery",
    "first_delivery_attempt": "out_for_delivery",
    "second_delivery_attempt": "out_for_delivery",
    "third_delivery_attempt": "out_for_delivery",
    "other_delivery_attempt": "out_for_delivery",
    "delivery_failed": "out_for_delivery",
    "no_time_for_delivery": "out_for_delivery",
    "no_capacity_for_delivery": "out_for_delivery",
    "out_of_delivery_area": "out_for_delivery",
    "recipient_not_available": "out_for_delivery",
    # delivered — dispatched ("Yuborilgan"), issued to recipient, completed
    "dispatched": "delivered",
    "dispatch": "delivered",
    "issued_to_recipient": "delivered",
    "delivered": "delivered",
    "completed": "delivered",
    "partially_completed": "delivered",
    "partial_complete": "delivered",
}

# Uzbek display label for the raw UzPost code (the public API returns only the
# code, not a localised label). Falls back to the raw code if unknown.
UZPOST_LABELS_UZ = {
    "created": "Yaratilgan",
    "unassigned": "Yangi jo'natma",
    "accepted": "Kuryerga biriktirildi",
    "assigned_to_courier": "Kuryerga tayinlangan",
    "in_sorting_facility": "Saralash bo'limida",
    "in_sorting_facility_public": "Saralash bo'limida",
    "order_sorting": "Saralanmoqda",
    "processing_at_warehouse": "Omborda qayta ishlanmoqda",
    "to_warehouse": "Omborga yo'lda",
    "warehouse": "Omborda",
    "in_transit": "Tranzitda",
    "in_transit_public": "Yo'lda",
    "arrived": "Keldi",
    "ready_for_delivery": "Yetkazib berishga tayyor",
    "ready_for_issue": "Berishga tayyor",
    "out_for_delivery": "Yetkazib berishda",
    "arrived_to_delivery_address": "Yetkazish manziliga keldi",
    "delivery_failed": "Yetkazib berilmadi",
    "recipient_not_available": "Qabul qiluvchi mavjud emas",
    "dispatched": "Yuborilgan",
    "issued_to_recipient": "Qabul qiluvchiga topshirildi",
    "delivered": "Yetkazib berildi",
    "completed": "Yakunlandi",
    "returned_to_origin": "Jo'natuvchiga qaytarildi",
}

# A UzPost tracking number: 2 letters, 9 digits, 2 letters (e.g. LA193723275UZ),
# or any code beginning with LA / UZ.
UZPOST_CODE = re.compile(r"^([A-Z]{2}\d{9}[A-Z]{2}|(LA|UZ)[A-Z0-9]+)$")


def is_uzpost_code(code):
    """True if `code` looks like a UzPost tracking number."""
    return bool(UZPOST_CODE.match((code or "").strip().upper()))


def map_uzpost_status(raw):
    """Collapse a raw UzPost status code to one of our 4 internal statuses."""
    return UZPOST_STATUS_MAP.get((raw or "").strip().lower(), "accepted")


def fetch_uzpost(code):
    """Fetch a tracking record from UzPost and normalise it.

    Returns a dict the frontend can consume directly:
      {found, code, raw_status, status, status_label_uz,
       origin{city,address,postcode}, dest{...}, package, synced_at}
    Raises httpx.TimeoutException / httpx.RequestError on network failure;
    returns {"found": False} when UzPost has no record (404).
    """
    upstream = httpx.get(
        f"{UZPOST_URL}/{code}",
        headers={"Accept": "application/json"},
        timeout=10.0,
    )
    # UzPost answers an unknown tracking number with 400/404 — treat any 4xx as
    # "no record". 5xx is a real upstream failure, so let it raise.
    if 400 <= upstream.status_code < 500:
        return {"found": False, "code": code}
    upstream.raise_for_status()

    payload = upstream.json()
    d = payload.get("data", payload) if isinstance(payload, dict) else {}
    locations = d.get("locations") or []
    pickup = next((l for l in locations if l.get("pickup") is True), {})
    dest = next((l for l in locations if l.get("pickup") is False), {})
    raw_status = d.get("status") or ""
    pkg = d.get("package") or {}

    def loc(l):
        return {
            "city": l.get("address_city") or "",
            "address": l.get("address") or "",
            "postcode": l.get("postcode") or "",
        }

    return {
        "found": True,
        "code": d.get("order_number") or code,
        "raw_status": raw_status,
        "status": map_uzpost_status(raw_status),
        "status_label_uz": UZPOST_LABELS_UZ.get(
            raw_status.lower(), raw_status or "—"
        ),
        "origin": loc(pickup),
        "dest": loc(dest),
        "package": pkg.get("name") or "",
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }

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
    """Fetch a UzPost tracking record and return it normalised.

    Response shape:
      200 {"ok": true,  "found": true,  ...normalised fields...}
      200 {"ok": true,  "found": false, "code": "..."}      # no UzPost record
      400 {"ok": false, "error": "invalid tracking code"}
      502 {"ok": false, "error": "upstream unreachable"}
      504 {"ok": false, "error": "upstream timeout"}
    """
    if request.method == "OPTIONS":
        return _cors(Response(status=204))

    code = (request.args.get("code") or "").strip().upper()
    if not VALID_TRACKING.match(code):
        return _cors(jsonify({"ok": False, "error": "invalid tracking code"})), 400

    try:
        result = fetch_uzpost(code)
    except httpx.TimeoutException:
        return _cors(jsonify({"ok": False, "error": "upstream timeout"})), 504
    except (httpx.RequestError, httpx.HTTPStatusError):
        return _cors(jsonify({"ok": False, "error": "upstream unreachable"})), 502

    return _cors(jsonify({"ok": True, **result}))


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
