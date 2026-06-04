#!/usr/bin/env python3
"""Ishonch Logistics Courier Bot.

Couriers only — no support handler. Couriers log in with a username +
password, see shipments for their own region (ilike match on
receiver_city), and step through pickup / in-transit / delivery with
photo evidence stored in the public `shipment-photos` Supabase
Storage bucket.
"""

import logging
import os
from datetime import datetime, timezone

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ───────────────────────── Config ─────────────────────────
# Token for @ishonchlogistics_bot — set TELEGRAM_BOT_TOKEN in .env (local)
# or in Render's Environment settings. main.py may also override bot.TOKEN
# from TELEGRAM_TOKEN / BOT_TOKEN after import, so don't crash here.
TOKEN = (
    os.environ.get("TELEGRAM_BOT_TOKEN")
    or os.environ.get("TELEGRAM_TOKEN")
    or os.environ.get("BOT_TOKEN")
    or ""
)

SUPABASE_URL = "https://dhqzairyxzoppskzpzxr.supabase.co"
SUPABASE_KEY = "sb_publishable_pjDSopKeZlYFqToEBDrvLw_Q7QO_IOd"
STORAGE_BUCKET = "shipment-photos"

COURIERS = {
    "samarqand_001": {"name": "Samarqand Kuryer 1", "region": "Samarqand", "password": "sam123"},
    "samarqand_002": {"name": "Samarqand Kuryer 2", "region": "Samarqand", "password": "sam456"},
    "navoiy_001":    {"name": "Navoiy Kuryer 1",    "region": "Navoiy",    "password": "nav123"},
    "navoiy_002":    {"name": "Navoiy Kuryer 2",    "region": "Navoiy",    "password": "nav456"},
    "andijon_001":   {"name": "Andijon Kuryer 1",   "region": "Andijon",   "password": "and123"},
    "andijon_002":   {"name": "Andijon Kuryer 2",   "region": "Andijon",   "password": "and456"},
}

# Conversation states
S_USERNAME, S_PASSWORD, S_MAIN, S_SHIPMENTS, S_DETAIL, S_PHOTO_PICKUP, S_PHOTO_DELIVER, S_CONFIRM = range(8)

STATUS_LABELS = {
    "accepted":         "🔵 Qabul qilindi",
    "picked_up":        "🟡 Kuryer oldi",
    "in_transit":       "🚚 Yo'lda",
    "out_for_delivery": "🟠 Yetkazib berishda",
    "delivered":        "✅ Yetkazildi",
}

LIST_ICONS = {"accepted": "🔵", "picked_up": "🟡", "in_transit": "🚚"}

LINE = "━━━━━━━━━━━━━━━━━━━━"

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("courier-bot")


# ───────────────────────── Supabase helpers ─────────────────────────
async def sb_get(path, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{path}?{params}"
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, headers=h)
        return r.json() if r.status_code == 200 else []


async def sb_patch(sid, data):
    url = f"{SUPABASE_URL}/rest/v1/shipments?id=eq.{sid}"
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
         "Content-Type": "application/json", "Prefer": "return=minimal"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.patch(url, headers=h, json=data)
        return r.status_code in (200, 204)


async def upload_photo(file_bytes, filename):
    url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
         "Content-Type": "image/jpeg"}
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(url, headers=h, content=file_bytes)
        if r.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"
    return None


# ───────────────────────── UI helpers ─────────────────────────
def main_menu_text(name, region):
    return (
        f"👋 Xush kelibsiz, {name}!\n"
        f"{LINE}\n"
        f"📍 Viloyat: {region}"
    )


def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Yuklarim ro'yxati", callback_data="show_shipments")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("🚪 Chiqish", callback_data="logout")],
    ])


async def safe_edit(query, text, kb=None):
    try:
        await query.edit_message_text(text, reply_markup=kb)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


async def shipments_view(region):
    """Build (text, keyboard) for the active-shipments list of a region."""
    rows = await sb_get(
        "shipments",
        f"receiver_city=ilike.*{region}*&status=neq.delivered&select=*&order=created_at.desc",
    )
    text = f"📦 {region} — {len(rows)} ta yuk"
    buttons = []
    for s in rows:
        icon = LIST_ICONS.get(s.get("status"), "📦")
        receiver = (s.get("receiver_name") or "")[:18]
        buttons.append([InlineKeyboardButton(
            f"{icon} {s.get('tracking_code')} | {receiver}",
            callback_data=f"ship_{s['id']}",
        )])
    buttons.append([InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_main")])
    return text, InlineKeyboardMarkup(buttons)


def detail_text(s):
    status = s.get("status", "")
    return (
        f"{LINE}\n"
        f"📦 {s.get('tracking_code')}\n"
        f"{LINE}\n"
        f"👤 Mijoz: {s.get('receiver_name')}\n"
        f"📍 Manzil: {s.get('receiver_city')}\n"
        f"📞 Tel: {s.get('receiver_phone')}\n"
        f"⚖️ Vazn: {s.get('weight_kg')} kg\n"
        f"📊 Status: {STATUS_LABELS.get(status, status)}\n"
        f"{LINE}"
    )


def detail_kb(s):
    sid = s["id"]
    status = s.get("status")
    back = [InlineKeyboardButton("🔙 Orqaga", callback_data="back_list")]
    if status == "accepted":
        rows = [[InlineKeyboardButton("🟡 Yukni oldim 📸", callback_data=f"pickup_{sid}")], back]
    elif status == "picked_up":
        rows = [
            [InlineKeyboardButton("🚚 Yo'lda", callback_data=f"transit_{sid}")],
            [InlineKeyboardButton("✅ Topshirdim 📸", callback_data=f"deliver_{sid}")],
            back,
        ]
    elif status == "in_transit":
        rows = [[InlineKeyboardButton("✅ Topshirdim 📸", callback_data=f"deliver_{sid}")], back]
    else:
        rows = [back]
    return InlineKeyboardMarkup(rows)


# ───────────────────────── Login ─────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Foydalanuvchi nomingizni kiriting:")
    return S_USERNAME


async def got_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username_attempt"] = update.message.text.strip()
    await update.message.reply_text("Parolni kiriting:")
    return S_PASSWORD


async def got_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.get("username_attempt", "")
    password = update.message.text.strip()
    courier = COURIERS.get(username)
    if not courier or courier["password"] != password:
        await update.message.reply_text("❌ Noto'g'ri. /start")
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data["courier"] = {
        "username": username,
        "name": courier["name"],
        "region": courier["region"],
    }
    await update.message.reply_text(
        main_menu_text(courier["name"], courier["region"]),
        reply_markup=main_menu_kb(),
    )
    return S_MAIN


def get_courier(context):
    return context.user_data.get("courier")


# ───────────────────────── Main menu ─────────────────────────
async def on_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    courier = get_courier(context)
    if not courier:
        await safe_edit(q, "Iltimos, /start orqali tizimga kiring.")
        return ConversationHandler.END

    if q.data == "show_shipments":
        text, kb = await shipments_view(courier["region"])
        await safe_edit(q, text, kb)
        return S_SHIPMENTS

    if q.data == "stats":
        return await show_stats(q, courier["region"])

    if q.data == "logout":
        context.user_data.clear()
        await safe_edit(q, "👋 Xayr! Qayta kirish uchun /start bosing.")
        return ConversationHandler.END

    if q.data == "back_main":
        await safe_edit(q, main_menu_text(courier["name"], courier["region"]), main_menu_kb())
        return S_MAIN

    return S_MAIN


async def show_stats(q, region):
    counts = {}
    for s in ("accepted", "picked_up", "in_transit", "delivered"):
        rows = await sb_get(
            "shipments", f"receiver_city=ilike.*{region}*&status=eq.{s}&select=id"
        )
        counts[s] = len(rows)
    total = counts["accepted"] + counts["picked_up"] + counts["in_transit"]
    text = (
        f"📊 {region} — Statistika\n"
        f"{LINE}\n"
        f"🔵 Qabul qilindi: {counts['accepted']}\n"
        f"🟡 Kuryer oldi: {counts['picked_up']}\n"
        f"🚚 Yo'lda: {counts['in_transit']}\n"
        f"✅ Yetkazildi (bugun): {counts['delivered']}\n"
        f"{LINE}\n"
        f"📦 Jami faol: {total}"
    )
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_main")]]
    )
    await safe_edit(q, text, kb)
    return S_MAIN


# ───────────────────────── Shipments list / detail ─────────────────────────
async def on_shipments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    courier = get_courier(context)
    if not courier:
        await safe_edit(q, "Iltimos, /start orqali tizimga kiring.")
        return ConversationHandler.END

    if q.data == "back_main":
        await safe_edit(q, main_menu_text(courier["name"], courier["region"]), main_menu_kb())
        return S_MAIN

    if q.data.startswith("ship_"):
        sid = q.data.removeprefix("ship_")
        rows = await sb_get("shipments", f"id=eq.{sid}&select=*")
        if not rows:
            text, kb = await shipments_view(courier["region"])
            await safe_edit(q, f"❌ Yuk topilmadi.\n\n{text}", kb)
            return S_SHIPMENTS
        s = rows[0]
        await safe_edit(q, detail_text(s), detail_kb(s))
        return S_DETAIL

    return S_SHIPMENTS


async def on_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    courier = get_courier(context)
    if not courier:
        await safe_edit(q, "Iltimos, /start orqali tizimga kiring.")
        return ConversationHandler.END

    if q.data == "back_list":
        text, kb = await shipments_view(courier["region"])
        await safe_edit(q, text, kb)
        return S_SHIPMENTS

    action, _, sid = q.data.partition("_")
    rows = await sb_get("shipments", f"id=eq.{sid}&select=*")
    if not rows:
        text, kb = await shipments_view(courier["region"])
        await safe_edit(q, f"❌ Yuk topilmadi.\n\n{text}", kb)
        return S_SHIPMENTS
    s = rows[0]
    tracking = s.get("tracking_code", "")

    if action == "pickup":
        context.user_data["action_shipment_id"] = sid
        context.user_data["action_type"] = "pickup"
        context.user_data["action_tracking"] = tracking
        await safe_edit(q, "📸 Yukni olganda rasm yuboring:")
        return S_PHOTO_PICKUP

    if action == "transit":
        ok = await sb_patch(sid, {"status": "in_transit"})
        if ok:
            await safe_edit(q, f"✅ Status yangilandi!\n🚚 {tracking} — Yo'lda")
        else:
            await safe_edit(q, "❌ Xato: status yangilanmadi.")
        text, kb = await shipments_view(courier["region"])
        await q.message.reply_text(text, reply_markup=kb)
        return S_SHIPMENTS

    if action == "deliver":
        context.user_data["action_shipment_id"] = sid
        context.user_data["action_type"] = "deliver"
        context.user_data["action_tracking"] = tracking
        await safe_edit(q, "📸 Yukni topshirganda rasm yuboring:")
        return S_PHOTO_DELIVER

    return S_DETAIL


# ───────────────────────── Photo + confirm ─────────────────────────
async def got_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    courier = get_courier(context)
    if not courier:
        await update.message.reply_text("Iltimos, /start orqali tizimga kiring.")
        return ConversationHandler.END

    action = context.user_data.get("action_type")
    tracking = context.user_data.get("action_tracking", "")

    tg_file = await update.message.photo[-1].get_file()
    file_bytes = bytes(await tg_file.download_as_bytearray())

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{tracking}_{action}_{ts}.jpg"
    photo_url = await upload_photo(file_bytes, filename)
    if not photo_url:
        await update.message.reply_text("❌ Rasm yuklanmadi. Qayta yuboring:")
        return S_PHOTO_PICKUP if action == "pickup" else S_PHOTO_DELIVER

    context.user_data["photo_url"] = photo_url
    state_label = "🟡 Yukni oldim" if action == "pickup" else "✅ Topshirildi"
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm"),
        InlineKeyboardButton("❌ Bekor", callback_data="cancel"),
    ]])
    await update.message.reply_text(
        f"📸 Rasm qabul qilindi!\n\n📦 {tracking}\nHolat: {state_label}\n\nTasdiqlaysizmi?",
        reply_markup=kb,
    )
    return S_CONFIRM


async def on_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    courier = get_courier(context)
    if not courier:
        await safe_edit(q, "Iltimos, /start orqali tizimga kiring.")
        return ConversationHandler.END

    sid = context.user_data.get("action_shipment_id")
    action = context.user_data.get("action_type")
    tracking = context.user_data.get("action_tracking", "")
    photo_url = context.user_data.get("photo_url", "")

    if q.data == "confirm" and sid:
        if action == "pickup":
            ok = await sb_patch(sid, {
                "status": "picked_up",
                "notes": f"Kuryer oldi. Rasm: {photo_url}",
            })
            msg = f"✅ {tracking} — Yukni oldi deb belgilandi!"
        else:
            ok = await sb_patch(sid, {
                "status": "delivered",
                "notes": f"Topshirildi. Rasm: {photo_url}",
            })
            msg = f"✅ {tracking} — Topshirildi deb belgilandi!"
        await safe_edit(q, msg if ok else "❌ Xato: status yangilanmadi.")
    else:
        await safe_edit(q, "❌ Bekor qilindi.")

    for key in ("action_shipment_id", "action_type", "action_tracking", "photo_url"):
        context.user_data.pop(key, None)

    text, kb = await shipments_view(courier["region"])
    await q.message.reply_text(text, reply_markup=kb)
    return S_SHIPMENTS


# ───────────────────────── Wiring ─────────────────────────
conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        S_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_username)],
        S_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_password)],
        S_MAIN: [CallbackQueryHandler(on_main_menu)],
        S_SHIPMENTS: [CallbackQueryHandler(on_shipments)],
        S_DETAIL: [CallbackQueryHandler(on_detail)],
        S_PHOTO_PICKUP: [MessageHandler(filters.PHOTO, got_photo)],
        S_PHOTO_DELIVER: [MessageHandler(filters.PHOTO, got_photo)],
        S_CONFIRM: [CallbackQueryHandler(on_confirm)],
    },
    fallbacks=[],
    per_user=True,
    per_chat=True,
    allow_reentry=True,
)


def main():
    if not TOKEN:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN o'rnatilmagan. Lokal: .env faylga yozing; "
            "Render: Environment sozlamalariga qo'shing."
        )
    app = Application.builder().token(TOKEN).build()
    app.add_handler(conv)
    print("Ishonch Logistics Courier Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True, stop_signals=[])


if __name__ == "__main__":
    main()
