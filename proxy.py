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

import html
import json
import os
import re
from datetime import datetime, timezone

import httpx
from flask import Flask, Response, abort, jsonify, request, send_from_directory

UZPOST_URL = "https://prodapi.pochta.uz/api/v1/public/order"

# ─────────────────────── AI support assistant ───────────────────────
# The browser must NOT call api.anthropic.com directly: that would ship the
# Anthropic API key in public page source. Instead track.html POSTs to /chat
# here, and this server adds the key (from the ANTHROPIC_API_KEY env var) and
# streams Claude's reply back. Set ANTHROPIC_API_KEY in the Render dashboard.
ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL   = "claude-sonnet-4-6"   # current Sonnet (claude-sonnet-4-20250514 retires 2026-06-15)
ANTHROPIC_VERSION = "2023-06-01"
CHAT_MAX_TOKENS   = 200
CHAT_SYSTEM = (
    "You are Ishonch Logistics customer support assistant. Answer in Uzbek. "
    "Help with: shipment tracking, delivery times (24 hours within Uzbekistan), "
    "pricing (1-2 kg = 28,000 so'm), 14 regions coverage, 180+ delivery points. "
    "Be friendly and helpful. Keep answers short (2-3 sentences max). If asked "
    "about specific tracking, tell them to enter the tracking number in the "
    "search box above."
)
# Abuse guards for the public endpoint.
CHAT_MAX_MESSAGES    = 16      # only keep the most recent turns
CHAT_MAX_CHARS       = 2000    # per message

# ─────────────────────── Pickup points (pochtamats) ───────────────────────
# Served as shareable pages at /p/<code> (e.g. /p/P-0140). Coordinates are
# approximate (district/town level) — refine per address as needed.
SUPPORT_PHONE    = "+998 XX XXX XX XX"   # TODO: set the real support number
TELEGRAM_LINK    = "https://t.me/Ishonchlogistics"
INSTAGRAM_LINK   = "https://www.instagram.com/ishonch_logistics2026"

pickup_points = {
    "P-0140": {"name": "Namangan shahar", "address": "улица Амира Темура, 54, МФЙ Оби Хаёт, Наманган", "lat": 41.003695, "lng": 71.606214},
    "P-0141": {"name": "Pop tumani", "address": "МФЙ Алишер Навоий, Поп, Наманганская область", "lat": 40.874712, "lng": 71.104497},
    "P-0142": {"name": "Turakurgan", "address": "улица Туракурган, 23, МФЙ Янгиобод, Туракурган", "lat": 40.974399, "lng": 71.453684},
    "P-0143": {"name": "Yangikurgan", "address": "улица Наманган, 2, городской посёлок Янгикурган", "lat": 41.198677, "lng": 71.720727},
    "P-0144": {"name": "Narin tumani", "address": "улица Беруний, МФЙ Бобур, Хаккулабад, Нарынский район", "lat": 40.996031, "lng": 71.612863},
    "P-0145": {"name": "Uychi", "address": "улица А.Темур, 1А, МФЙ Хуррият, городской посёлок Уйчи", "lat": 41.1119, "lng": 71.9247},
    "P-0146": {"name": "Kasansay", "address": "МФЙ Абдурахмон Жомий, Касансайский район", "lat": 41.2471, "lng": 71.5427},
    "P-0147": {"name": "Chust", "address": "МФЙ Камарсада, Чустский район", "lat": 40.9937, "lng": 71.2322},
    "P-0148": {"name": "Chartak", "address": "Истиклол кўчаси, 24, Чартак", "lat": 41.0768, "lng": 71.8151},
}

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
    # "Yuborilgan" — dispatched FOR delivery, i.e. out for delivery, NOT yet
    # delivered. Only "Topshirildi" (issued to recipient) counts as delivered.
    "dispatched": "out_for_delivery",
    "dispatch": "out_for_delivery",
    # delivered — issued to recipient ("Topshirildi"), completed
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


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    """Proxy a streaming chat completion from Claude.

    Request:  POST {"messages": [{"role": "user"|"assistant", "content": "..."}]}
    Response: text/event-stream — raw Anthropic SSE relayed to the browser, which
              reads `content_block_delta` text_delta events to render tokens.
    The system prompt, model, and API key live server-side and are not client-set.
    """
    if request.method == "OPTIONS":
        resp = _cors(Response(status=204))
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return _cors(jsonify({"ok": False, "error": "AI yordamchi sozlanmagan"})), 503

    body = request.get_json(silent=True) or {}
    raw_messages = body.get("messages")
    if not isinstance(raw_messages, list) or not raw_messages:
        return _cors(jsonify({"ok": False, "error": "messages kerak"})), 400

    # Sanitise: keep only valid user/assistant turns, cap count and length.
    messages = []
    for m in raw_messages[-CHAT_MAX_MESSAGES:]:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()[:CHAT_MAX_CHARS]})
    if not messages or messages[0]["role"] != "user":
        return _cors(jsonify({"ok": False, "error": "noto'g'ri suhbat"})), 400

    upstream_payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": CHAT_MAX_TOKENS,
        "system": CHAT_SYSTEM,
        "messages": messages,
        "stream": True,
    }

    def generate():
        try:
            with httpx.stream(
                "POST",
                ANTHROPIC_URL,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": ANTHROPIC_VERSION,
                    "content-type": "application/json",
                },
                json=upstream_payload,
                timeout=30.0,
            ) as upstream:
                if upstream.status_code != 200:
                    upstream.read()
                    yield "event: error\ndata: " + json.dumps(
                        {"error": "AI xizmatida xatolik"}
                    ) + "\n\n"
                    return
                for chunk in upstream.iter_raw():
                    if chunk:
                        yield chunk.decode("utf-8", "replace")
        except (httpx.TimeoutException, httpx.RequestError):
            yield "event: error\ndata: " + json.dumps(
                {"error": "AI yordamchiga ulanib bo'lmadi"}
            ) + "\n\n"

    resp = _cors(Response(generate(), mimetype="text/event-stream"))
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"  # disable proxy buffering for streaming
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp


# ───────────────────────── Pickup point pages ─────────────────────────
# Shared <head> + navy header. %%TITLE%% is replaced per page; CSS braces are
# why this is a plain string, not an f-string.
_PAGE_HEAD = """<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>%%TITLE%% — Ishonch Logistics</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script>
  tailwind.config = { theme: { extend: {
    fontFamily: { sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
    colors: { navy: { 900: '#07173a', 800: '#0c2454', 700: '#133068' },
              brand: { 500: '#2b7fd8', 400: '#3fa3e3' } },
  } } };
</script>
<style>
  body { font-family: 'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif;
         background: linear-gradient(180deg, #f9f8fd 0%, #f0f4fa 100%); }
  .hero-gradient { background: linear-gradient(135deg, #0a1628 0%, #0d2550 40%, #1a4480 70%, #1e5799 100%); }
  .map-wrap { position: relative; width: 100%; aspect-ratio: 16/11; border-radius: 14px; overflow: hidden; }
  .map-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
</style>
</head>
<body class="min-h-screen text-slate-900 antialiased flex flex-col">
  <header class="hero-gradient">
    <div class="max-w-2xl mx-auto px-6 py-5 flex items-center justify-between">
      <a href="/" class="text-white font-extrabold text-lg tracking-tight">Ishonch Logistics</a>
      <a href="%%TG%%" target="_blank" rel="noopener noreferrer"
         class="text-white/85 hover:text-white text-sm font-semibold">Telegram</a>
    </div>
  </header>
  <main class="flex-1 w-full max-w-2xl mx-auto px-5 py-7">
"""


def _page_foot():
    tel = re.sub(r"[^\d+]", "", SUPPORT_PHONE)
    return f"""  </main>
  <footer class="hero-gradient mt-auto">
    <div class="max-w-2xl mx-auto px-6 py-8 text-center">
      <div class="text-white font-extrabold text-lg tracking-tight">Ishonch Logistics</div>
      <p class="mt-1 text-white/60 text-[13px]">Yukingiz ishonchli qo'llarda.</p>
      <div class="mt-4 flex flex-col items-center gap-2 text-white/85 text-sm">
        <a href="tel:{html.escape(tel)}" class="hover:text-white">📞 {html.escape(SUPPORT_PHONE)}</a>
        <a href="{html.escape(TELEGRAM_LINK)}" target="_blank" rel="noopener noreferrer" class="hover:text-white">✈️ Telegram</a>
        <a href="{html.escape(INSTAGRAM_LINK)}" target="_blank" rel="noopener noreferrer" class="hover:text-white">📸 Instagram</a>
      </div>
      <p class="mt-5 text-white/40 text-[12px]">&copy; 2026 Ishonch Logistics. Barcha huquqlar himoyalangan.</p>
    </div>
  </footer>
</body>
</html>"""


def _shell(title, inner):
    return _PAGE_HEAD.replace("%%TITLE%%", html.escape(title)).replace("%%TG%%", html.escape(TELEGRAM_LINK)) \
        + inner + _page_foot()


def _pickup_page(code, p):
    name = html.escape(p["name"])
    addr = html.escape(p["address"])
    lat, lng = p["lat"], p["lng"]
    coords = f"{lat},{lng}"           # lat,lng — Google Maps & 2GIS
    coords_lnglat = f"{lng},{lat}"    # lng,lat — Yandex expects longitude first
    inner = f"""
    <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
      <span class="inline-block bg-[#FF6B35] text-white text-xs font-extrabold px-3 py-1 rounded-full tracking-wider">{html.escape(code)}</span>
      <h1 class="mt-3 text-2xl sm:text-3xl font-extrabold text-navy-800 tracking-tight">{name}</h1>
      <p class="mt-2 text-slate-600 text-[15px] leading-relaxed">{addr}</p>

      <div class="map-wrap mt-5 border border-slate-100 shadow">
        <iframe loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen
          src="https://maps.google.com/maps?q={coords}&z=16&output=embed"
          title="{name} — xarita"></iframe>
      </div>

      <div class="mt-5 grid gap-3">
        <a href="https://www.google.com/maps/search/?api=1&query={coords}" target="_blank" rel="noopener noreferrer"
           class="w-full text-center py-3.5 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition">
           📍 Google Maps da ochish
        </a>
        <a href="https://yandex.uz/maps/?pt={coords_lnglat}&z=16&l=map" target="_blank" rel="noopener noreferrer"
           class="w-full text-center py-3.5 rounded-xl font-bold text-navy-800 bg-white border-2 border-navy-800 hover:bg-navy-800 hover:text-white transition">
           🧭 Yandex Navigator
        </a>
        <a href="https://2gis.uz/search/{coords}" target="_blank" rel="noopener noreferrer"
           class="w-full text-center py-3.5 rounded-xl font-bold text-white bg-[#FF6B35] hover:opacity-90 transition">
           🗺️ 2GIS
        </a>
      </div>
    </div>
"""
    return _shell(f"{p['name']} ({code})", inner)


def _pickup_not_found(code):
    inner = f"""
    <div class="bg-white rounded-2xl shadow-xl p-8 text-center">
      <div class="text-5xl">📍</div>
      <h1 class="mt-4 text-2xl font-extrabold text-navy-800">Bekat topilmadi</h1>
      <p class="mt-2 text-slate-600 text-[15px]">"{html.escape(code)}" kodli bekat mavjud emas yoki noto'g'ri kiritilgan.</p>
      <a href="/" class="inline-block mt-6 py-3 px-6 rounded-xl font-bold text-white bg-[#FF6B35] hover:opacity-90 transition">Bosh sahifaga qaytish</a>
    </div>
"""
    return _shell("Bekat topilmadi", inner)


@app.route("/p/<code>", methods=["GET"])
def pickup_point(code):
    """Public pickup-point (pochtamat) page: /p/P-0140."""
    key = (code or "").strip().upper()
    p = pickup_points.get(key)
    if not p:
        return Response(_pickup_not_found(key), mimetype="text/html"), 404
    return Response(_pickup_page(key, p), mimetype="text/html")


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
