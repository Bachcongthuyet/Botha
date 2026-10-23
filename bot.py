import logging
import os
import re
import sqlite3
from urllib.parse import urlparse

import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Required environment variables:
# TELEGRAM_BOT_TOKEN, MUALIKE_API_KEY, MUALIKE_SERVICE_ID
# Optional: MUALIKE_API_URL, VIEW_QUANTITY, ADMIN_CHAT_ID
API_URL = os.getenv("MUALIKE_API_URL", "https://mualike1s.com/api/v3")
API_KEY = os.getenv("MUALIKE_API_KEY", "")
SERVICE_ID = os.getenv("MUALIKE_SERVICE_ID", "3284")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
QUANTITY = int(os.getenv("VIEW_QUANTITY", "80"))
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
DB_PATH = os.getenv("DB_PATH", "orders.sqlite3")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
log = logging.getLogger("view-bot")


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS processed_posts (
                chat_id TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                target_link TEXT NOT NULL,
                order_id TEXT,
                status TEXT NOT NULL,
                PRIMARY KEY(chat_id, message_id)
            )
        """)


def post_link(message) -> str | None:
    chat = message.chat
    msg_id = message.message_id
    if chat.username:
        return f"https://t.me/{chat.username}/{msg_id}"
    # Telegram's private-channel message link form requires the internal channel id.
    chat_id = str(chat.id)
    if chat_id.startswith("-100"):
        internal_id = chat_id[4:]
        return f"https://t.me/c/{internal_id}/{msg_id}"
    return None


def api_call(data: dict):
    if not API_KEY:
        raise RuntimeError("MUALIKE_API_KEY is not configured")
    payload = {"key": API_KEY, **data}
    response = requests.post(API_URL, data=payload, timeout=25)
    response.raise_for_status()
    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("API returned a non-JSON response") from exc
    return result


def notify_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    # Reply in channel is avoided; notify a configured admin chat if provided.
    if ADMIN_CHAT_ID:
        context.application.create_task(
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        )


async def on_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return

    link = post_link(message)
    if not link:
        notify_text(update, context,
                    f"Không lấy được link bài đăng trong kênh {message.chat.title!r}. "
                    "Hãy dùng kênh công khai hoặc kiểm tra quyền bot.")
        return

    # Ignore duplicate updates using a persistent SQLite key.
    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute(
            "INSERT OR IGNORE INTO processed_posts(chat_id,message_id,target_link,status) "
            "VALUES(?,?,?,'processing')",
            (str(message.chat.id), message.message_id, link),
        )
        if cur.rowcount == 0:
            return

    if not SERVICE_ID:
        with sqlite3.connect(DB_PATH) as db:
            db.execute(
                "UPDATE processed_posts SET status='needs_service_id' "
                "WHERE chat_id=? AND message_id=?",
                (str(message.chat.id), message.message_id),
            )
        notify_text(update, context,
                    f"Chưa đặt MUALIKE_SERVICE_ID. Bài đăng: {link}. Chưa tạo đơn.")
        return

    try:
        result = api_call({
            "action": "add",
            "service": SERVICE_ID,
            "link": link,
            "quantity": QUANTITY,
        })
        # Typical SMM panel response uses "order", but preserve safe handling.
        order_id = result.get("order") if isinstance(result, dict) else None
        if order_id is not None:
            status = "submitted"
            report = (
                f"Đã gửi yêu cầu tăng view.\nLink: {link}\n"
                f"Số lượng: {QUANTITY}\nMã đơn: {order_id}"
            )
        else:
            status = "api_response"
            # Do not print secrets; response body is useful for diagnosing service errors.
            report = (
                f"API chưa trả về mã đơn rõ ràng.\nLink: {link}\n"
                f"Phản hồi: {str(result)[:1200]}"
            )
        with sqlite3.connect(DB_PATH) as db:
            db.execute(
                "UPDATE processed_posts SET order_id=?, status=? "
                "WHERE chat_id=? AND message_id=?",
                (str(order_id) if order_id is not None else None, status,
                 str(message.chat.id), message.message_id),
            )
        notify_text(update, context, report)
    except Exception as exc:
        log.exception("Order request failed")
        with sqlite3.connect(DB_PATH) as db:
            db.execute(
                "UPDATE processed_posts SET status='error' "
                "WHERE chat_id=? AND message_id=?",
                (str(message.chat.id), message.message_id),
            )
        notify_text(update, context,
                    f"Lỗi khi xử lý bài đăng: {link}\nChi tiết: {str(exc)[:500]}")


def main():
    if not BOT_TOKEN:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN environment variable")
    if QUANTITY != 80:
        log.warning("VIEW_QUANTITY is %s (requested default is 80)", QUANTITY)
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, on_channel_post))
    log.info("Bot started; quantity=%s; service_id_configured=%s",
             QUANTITY, bool(SERVICE_ID))
    app.run_polling(allowed_updates=["channel_post", "message"])


if __name__ == "__main__":
    main()
