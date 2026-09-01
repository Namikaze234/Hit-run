import os
import logging

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")

API_URL = f"http://{API_HOST}:{API_PORT}/message"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")

if not TELEGRAM_ALLOWED_USER_ID:
    raise RuntimeError("TELEGRAM_ALLOWED_USER_ID is not configured.")


ALLOWED_USER_ID = int(TELEGRAM_ALLOWED_USER_ID)


def is_allowed(user_id: int) -> bool:
    return user_id == ALLOWED_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id

    if not is_allowed(user_id):
        logger.warning("Unauthorized user attempted /start: %s", user_id)
        return

    await update.message.reply_text(
        "HT-Run is online. Send me a message."
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    message = update.message.text

    if not is_allowed(user_id):
        logger.warning(
            "Unauthorized message from Telegram user: %s",
            user_id,
        )
        return

    if not message:
        return

    payload = {
        "user_id": user_id,
        "message": message,
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                API_URL,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        await update.message.reply_text(
            f"Received: {data['message']}"
        )

    except httpx.HTTPError as exc:
        logger.exception("API request failed: %s", exc)

        await update.message.reply_text(
            "The internal API is currently unavailable."
        )


def main():
    application = Application.builder().token(
        TELEGRAM_BOT_TOKEN
    ).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    logger.info("Telegram bot starting...")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
