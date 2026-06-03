#!/usr/bin/env python3
"""Ishonch Logistics Courier Bot.

Couriers log in with a hardcoded username + password, see a region
selection menu, view shipments for their own region (ilike match on
receiver_city), and step through pickup/in-transit/delivery with
photo evidence stored in the public `shipment-photos` Supabase
Storage bucket.
"""

import logging
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

# ───────────────────────── Config ─────────────────────────
TOKEN = "8996511571:AAGRTtb-iPsltBqZ-XX2yGwBCXfVcs7PSy8"

SUPABASE_URL = "https://dhqzairyxzoppskzpzxr.supabase.co"
SUPABASE_KEY = "sb_publishable_pjDSopKeZlYFqToEBDrvLw_Q7QO_IOd"
STORAGE_BUCKET = "shipment-photos"

ADMIN_CHAT_ID = 5775836728

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

COURIERS = {
    # Samarqand
    "samarqand_001": {"name": "Samarqand Kuryer 1", "region": "Samarqand", "password": "sam123"},
    "samarqand_002": {"name": "Samarqand Kuryer 2", "region": "Samarqand", "password": "sam456"},
    # Navoiy
    "navoiy_001":    {"name": "Navoiy Kuryer 1",    "region": "Navoiy",    "password": "nav123"},
    "navoiy_002":    {"name": "Navoiy Kuryer 2",    "region": "Navoiy",    "password": "nav456"},
    # Andijon
    "andijon_001":   {"name": "Andijon Kuryer 1",   "region": "Andijon",   "password": "and123"},
    "andijon_002":   {"name": "Andijon Kuryer 2",   "region": "Andijon",   "password": "and456"},
}

REGIONS = [
    ("Samarqand", "🏛"),
    ("Navoiy",    "🏜"),
    ("Andijon",   "🌿"),
]

STATUS_LABEL = {
    "accepted":         "Qabul qilindi",
    "picked_up":        "Kuryer oldi",
    "in_transit":       "Yo'lda",
    "out_for_delivery": "Yetkazib berishda",
    "delivered":        "Yetkazildi",
}
STATUS_EMOJI = {
    "accepted":         "🔵",
    "picked_up":        "🟡",
    "in_transit":       "🚚",
    "out_for_delivery": "🟠",
    "delivered":        "✅",
}

(
    AWAIT_USERNAME,
    AWAIT_PASSWORD,
    MAIN_MENU,
    SHIPMENT_LIST,
    SHIPMENT_DETAIL,
    AWAIT_PHOTO_PICKUP,
    CONFIRM_PICKUP,
    AWAIT_PHOTO_DELIVER,
    CONFIRM_DELIVER,
) = range(9)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
log = logging.getLogger("ishonch-bot")


# ─────────────────── Supabase REST helpers ───────────────────
async def sb_list_shipments(region: str):
    # PostgREST accepts `*` as the ilike wildcard (maps to SQL `%`).
    # We use `*` instead of `%` because httpx will not URL-encode `%`
    # inside param values, which produces a malformed URL and 500.
    params = {
        "select": "*",
        "receiver_city": f"ilike.*{region}*",
        "status": "neq.delivered",
        "order": "created_at.desc",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/shipments",
            headers=SUPABASE_HEADERS,
            params=params,
        )
        if r.status_code >= 400:
            log.error("sb_list_shipments HTTP %s: %s", r.status_code, r.text[:400])
        r.raise_for_status()
        return r.json()


async def sb_get_shipment(shipment_id: int):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/shipments",
            headers=SUPABASE_HEADERS,
            params={"id": f"eq.{shipment_id}", "select": "*"},
        )
        r.raise_for_status()
        rows = r.json()
        return rows[0] if rows else None


async def sb_update_status(shipment_id: int, status: str, notes: str | None = None):
    body = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if notes is not None:
        body["notes"] = notes
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.patch(
            f"{SUPABASE_URL}/rest/v1/shipments",
            headers={
                **SUPABASE_HEADERS,
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            params={"id": f"eq.{shipment_id}"},
            json=body,
        )
        if r.status_code >= 400:
            log.error("sb_update_status HTTP %s: %s", r.status_code, r.text[:400])
        r.raise_for_status()


async def sb_count(region: str, status: str | None) -> int:
    params = {
        "select": "id",
        "receiver_city": f"ilike.*{region}*",
    }
    if status is not None:
        params["status"] = f"eq.{status}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/shipments",
            headers={**SUPABASE_HEADERS, "Prefer": "count=exact", "Range-Unit": "items", "Range": "0-0"},
            params=params,
        )
        if r.status_code >= 400:
            log.error("sb_count HTTP %s: %s", r.status_code, r.text[:400])
        r.raise_for_status()
        rng = r.headers.get("Content-Range", "*/0")
        try:
            return int(rng.split("/")[1])
        except (ValueError, IndexError):
            return 0


async def sb_upload_photo(photo_bytes: bytes, tracking_code: str, action: str) -> str | None:
    ts = int(datetime.now(timezone.utc).timestamp())
    safe = "".join(c if c.isalnum() else "_" for c in (tracking_code or "unknown"))
    filename = f"{safe}_{action}_{ts}.jpg"
    url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                url,
                headers={
                    **SUPABASE_HEADERS,
                    "Content-Type": "image/jpeg",
                    "x-upsert": "true",
                },
                content=photo_bytes,
            )
            if r.status_code >= 400:
                log.warning("Storage upload failed (%s): %s", r.status_code, r.text[:200])
                return None
        return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"
    except Exception:
        log.exception("Storage upload exception")
        return None


# ─────────────────────── HTML helpers ───────────────────────
def h(s) -> str:
    """Escape a value for parse_mode=HTML output."""
    return str("" if s is None else s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def safe_edit(query, text, kb=None, parse_mode="HTML"):
    """edit_message_text that swallows the harmless "Message is not modified" error."""
    try:
        await query.edit_message_text(text, reply_markup=kb, parse_mode=parse_mode)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


# ─────────────────────── UI builders ───────────────────────
def main_menu_kb(own_region: str) -> InlineKeyboardMarkup:
    def row_button(region, emoji):
        prefix = "► " if region == own_region else ""
        return InlineKeyboardButton(f"{prefix}{emoji} {region}", callback_data=f"region:{region}")
    return InlineKeyboardMarkup([
        [row_button("Samarqand", "🏛"), row_button("Navoiy", "🏜")],
        [row_button("Andijon",   "🌿")],
        [InlineKeyboardButton("📊 Statistika", callback_data="menu:stats"),
         InlineKeyboardButton("🔄 Yangilash",  callback_data="menu:refresh")],
        [InlineKeyboardButton("🚪 Chiqish",     callback_data="menu:exit")],
    ])


def main_menu_text(name: str, region: str) -> str:
    return (
        f"👋 Xush kelibsiz, <b>{h(name)}</b>!\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Sizning viloyatingiz: <b>{h(region)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Quyidagi bo'limdan tanlang:"
    )


def shipments_kb(rows) -> InlineKeyboardMarkup:
    buttons = []
    for r in rows:
        emoji = STATUS_EMOJI.get(r.get("status"), "🔵")
        code = r.get("tracking_code", "—")
        name = (r.get("receiver_name") or "—")[:15]
        buttons.append([InlineKeyboardButton(
            f"{emoji} {code} | {name}",
            callback_data=f"ship:{r['id']}",
        )])
    buttons.append([InlineKeyboardButton("🔙 Asosiy menyu", callback_data="menu:home")])
    return InlineKeyboardMarkup(buttons)


def detail_kb(row) -> InlineKeyboardMarkup:
    status = row.get("status")
    sid = row["id"]
    rows = []
    if status == "accepted":
        rows.append([InlineKeyboardButton("🟡 Yukni oldim 📸", callback_data=f"act:pickup:{sid}")])
        rows.append([InlineKeyboardButton("🚚 Yo'lda",         callback_data=f"act:onway:{sid}")])
    elif status == "picked_up":
        rows.append([InlineKeyboardButton("🚚 Yo'lda",            callback_data=f"act:onway:{sid}")])
        rows.append([InlineKeyboardButton("✅ Topshirdim 📸",     callback_data=f"act:deliver:{sid}")])
    elif status == "in_transit":
        rows.append([InlineKeyboardButton("✅ Topshirdim 📸",     callback_data=f"act:deliver:{sid}")])
    rows.append([InlineKeyboardButton("🔙 Yuklarga qaytish", callback_data="back:list")])
    return InlineKeyboardMarkup(rows)


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm:yes"),
        InlineKeyboardButton("❌ Bekor",      callback_data="confirm:no"),
    ]])


def stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Asosiy menyu", callback_data="menu:home")],
    ])


def format_shipment(row) -> str:
    s = row.get("status") or "—"
    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>{h(row.get('tracking_code') or '—')}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Mijoz: {h(row.get('receiver_name') or '—')}\n"
        f"📍 Manzil: {h(row.get('receiver_city') or '—')}\n"
        f"📞 Tel: {h(row.get('receiver_phone') or '—')}\n"
        f"⚖️ Vazn: {h(row.get('weight_kg') or 0)} kg\n"
        f"📋 Turi: {h(row.get('package_type') or '—')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Status: {STATUS_EMOJI.get(s, '•')} {h(STATUS_LABEL.get(s, s))}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


def format_stats(region: str, counts: dict) -> str:
    total = sum(counts.values())
    return (
        f"📊 <b>{h(region)} Statistika</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🔵 Qabul qilindi: <b>{counts.get('accepted', 0)}</b>\n"
        f"🟡 Kuryer oldi:   <b>{counts.get('picked_up', 0)}</b>\n"
        f"🚚 Yo'lda:        <b>{counts.get('in_transit', 0)}</b>\n"
        f"✅ Yetkazildi:    <b>{counts.get('delivered', 0)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Jami: <b>{total}</b>"
    )


# ─────────────────────── Handlers ───────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Salom! Ishonch Logistics kuryer bot.\nFoydalanuvchi nomingizni kiriting:"
    )
    return AWAIT_USERNAME


async def got_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username_attempt"] = update.message.text.strip()
    await update.message.reply_text("Parolni kiriting:")
    return AWAIT_PASSWORD


async def got_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.get("username_attempt", "")
    password = update.message.text.strip()
    courier = COURIERS.get(username)
    if not courier or courier["password"] != password:
        await update.message.reply_text("❌ Xato. /start")
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data["session"] = {
        "username": username,
        "name": courier["name"],
        "region": courier["region"],
    }
    await update.message.reply_text(
        main_menu_text(courier["name"], courier["region"]),
        reply_markup=main_menu_kb(courier["region"]),
        parse_mode="HTML",
    )
    return MAIN_MENU


async def show_main_menu(query, context):
    session = context.user_data.get("session") or {}
    name = session.get("name", "Kuryer")
    region = session.get("region", "")
    await safe_edit(
        query,
        main_menu_text(name, region),
        kb=main_menu_kb(region),
    )
    return MAIN_MENU


async def show_list(query, context):
    session = context.user_data.get("session")
    if not session:
        await safe_edit(query, "Iltimos, /start orqali tizimga kiring.", kb=None)
        return ConversationHandler.END
    region = session["region"]
    try:
        rows = await sb_list_shipments(region)
    except Exception as e:
        log.exception("show_list error")
        await safe_edit(
            query,
            f"❌ Xato: {h(e)}",
            kb=main_menu_kb(region),
        )
        return MAIN_MENU
    if not rows:
        await safe_edit(
            query,
            f"📍 <b>{h(region)}</b> — hozircha faol yuk yo'q.",
            kb=main_menu_kb(region),
        )
        return MAIN_MENU
    await safe_edit(
        query,
        f"📦 <b>{h(region)} yuklar ro'yxati ({len(rows)} ta)</b>",
        kb=shipments_kb(rows),
    )
    return SHIPMENT_LIST


async def show_detail(query, context, shipment_id: int):
    session = context.user_data.get("session") or {}
    region = session.get("region", "")
    try:
        row = await sb_get_shipment(shipment_id)
    except Exception as e:
        log.exception("show_detail error")
        await safe_edit(query, f"❌ Xato: {h(e)}", kb=main_menu_kb(region))
        return MAIN_MENU
    if not row:
        await safe_edit(query, "Yuk topilmadi.", kb=main_menu_kb(region))
        return MAIN_MENU
    context.user_data["current_shipment"] = row
    await safe_edit(query, format_shipment(row), kb=detail_kb(row))
    return SHIPMENT_DETAIL


async def show_stats(query, context):
    session = context.user_data.get("session") or {}
    region = session.get("region", "")
    try:
        counts = {}
        for status in ("accepted", "picked_up", "in_transit", "delivered"):
            counts[status] = await sb_count(region, status)
    except Exception as e:
        log.exception("show_stats error")
        await safe_edit(query, f"❌ Xato: {h(e)}", kb=main_menu_kb(region))
        return MAIN_MENU
    await safe_edit(query, format_stats(region, counts), kb=stats_kb())
    return MAIN_MENU


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    session = context.user_data.get("session") or {}
    own_region = session.get("region", "")

    if data.startswith("region:"):
        chosen = data.split(":", 1)[1]
        if chosen != own_region:
            await q.answer(
                f"❌ Siz faqat {own_region} viloyati uchun ishlaysiz.",
                show_alert=True,
            )
            return MAIN_MENU
        await q.answer()
        return await show_list(q, context)

    if data == "menu:stats":
        await q.answer()
        return await show_stats(q, context)

    if data in ("menu:refresh", "menu:home"):
        await q.answer()
        return await show_main_menu(q, context)

    if data == "menu:exit":
        await q.answer()
        context.user_data.clear()
        await safe_edit(q, "👋 Xayr! Qayta kirish uchun /start bosing.", kb=None)
        return ConversationHandler.END

    await q.answer()
    return MAIN_MENU


async def list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "menu:home":
        return await show_main_menu(q, context)
    if q.data.startswith("ship:"):
        sid = int(q.data.split(":", 1)[1])
        return await show_detail(q, context, sid)
    return SHIPMENT_LIST


async def detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "back:list":
        return await show_list(q, context)
    if data.startswith("act:"):
        _, action, sid = data.split(":", 2)
        sid = int(sid)
        context.user_data["current_shipment_id"] = sid
        if action == "onway":
            try:
                await sb_update_status(sid, "in_transit")
            except Exception as e:
                log.exception("status update failed")
                await safe_edit(q, f"❌ Xato: {h(e)}", kb=main_menu_kb(
                    (context.user_data.get("session") or {}).get("region", "")))
                return MAIN_MENU
            return await show_list(q, context)
        if action == "pickup":
            await safe_edit(q, "Yukni olganingizni tasdiqlash uchun rasm yuboring.", kb=None)
            return AWAIT_PHOTO_PICKUP
        if action == "deliver":
            await safe_edit(q, "Topshirilganini tasdiqlash uchun rasm yuboring.", kb=None)
            return AWAIT_PHOTO_DELIVER
    return SHIPMENT_DETAIL


async def _grab_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    f = await photo.get_file()
    buf = await f.download_as_bytearray()
    context.user_data["pending_photo"] = bytes(buf)
    await update.message.reply_text(
        "Rasm qabul qilindi. Tasdiqlaysizmi?",
        reply_markup=confirm_kb(),
    )


async def photo_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _grab_photo(update, context)
    return CONFIRM_PICKUP


async def photo_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _grab_photo(update, context)
    return CONFIRM_DELIVER


async def _finalize(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    action: str, new_status: str, success_msg: str):
    q = update.callback_query
    await q.answer()
    shipment = context.user_data.get("current_shipment", {}) or {}
    sid = context.user_data.get("current_shipment_id") or shipment.get("id")
    tracking = shipment.get("tracking_code") or str(sid)
    region = (context.user_data.get("session") or {}).get("region", "")

    if q.data == "confirm:no":
        await safe_edit(q, "Bekor qilindi.", kb=detail_kb(shipment))
        return SHIPMENT_DETAIL

    photo_bytes = context.user_data.pop("pending_photo", None)
    photo_url = await sb_upload_photo(photo_bytes, tracking, action) if photo_bytes else None
    notes = "Kuryer oldi" if action == "pickup" else "Topshirildi"
    if photo_url:
        notes += f". Photo: {photo_url}"

    try:
        await sb_update_status(sid, new_status, notes=notes)
    except Exception as e:
        log.exception("status update failed")
        await safe_edit(q, f"❌ Xato: {h(e)}", kb=main_menu_kb(region))
        return MAIN_MENU

    await q.message.reply_text(success_msg)
    return await show_list(q, context)


async def confirm_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _finalize(update, context, "pickup", "picked_up", "✅ Yuk olindi.")


async def confirm_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _finalize(update, context, "deliver", "delivered", "✅ Yuk topshirildi.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("/start orqali boshlang.")
    return ConversationHandler.END


async def handle_support(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text

    # Send to admin
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"📨 *Yangi xabar (Support)*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Ism: {user.full_name}\n"
                f"🔗 Username: @{user.username or 'yoq'}\n"
                f"🆔 ID: {user.id}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💬 *Xabar:*\n{text}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        import logging
        logging.error(f"Admin forward error: {e}")

    # Reply to user
    await update.message.reply_text(
        "✅ Xabaringiz qabul qilindi!\n\n"
        "Ishonch Logistics xodimi tez orada siz bilan bog'lanadi. 🙏\n\n"
        "Kuryer bo'lsangiz /start bosing."
    )


# ─────────────────────────── Main ─────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AWAIT_USERNAME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, got_username)],
            AWAIT_PASSWORD:      [MessageHandler(filters.TEXT & ~filters.COMMAND, got_password)],
            MAIN_MENU:           [CallbackQueryHandler(menu_callback)],
            SHIPMENT_LIST:       [CallbackQueryHandler(list_callback)],
            SHIPMENT_DETAIL:     [CallbackQueryHandler(detail_callback)],
            AWAIT_PHOTO_PICKUP:  [MessageHandler(filters.PHOTO, photo_pickup)],
            CONFIRM_PICKUP:      [CallbackQueryHandler(confirm_pickup)],
            AWAIT_PHOTO_DELIVER: [MessageHandler(filters.PHOTO, photo_deliver)],
            CONFIRM_DELIVER:     [CallbackQueryHandler(confirm_deliver)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
        name="courier_conv",
    )
    app.add_handler(conv)
    from telegram.ext import MessageHandler as MH, filters as F
    app.add_handler(MH(F.TEXT & ~F.COMMAND, handle_support))
    log.info("Bot starting…")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        stop_signals=[],
    )


if __name__ == "__main__":
    main()
