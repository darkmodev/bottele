import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import google.generativeai as genai

import logging

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Saya adalah bot Gemini AI.\nTanyakan apa saja!\n\nKetik /clear untuk hapus ingatan."
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories.pop(user_id, None)
    await update.message.reply_text("🧠 Ingatanmu telah dihapus.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    history = user_histories.get(user_id, [])
    history.append({"role": "user", "parts": [text]})

    try:
        response = model.generate_content(history)
        reply = response.text
        history.append({"role": "model", "parts": [reply]})
        user_histories[user_id] = history[-10:]

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Terjadi kesalahan.")

def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise ValueError("TELEGRAM_TOKEN dan GEMINI_API_KEY harus diatur.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot aktif.")
    app.run_polling()

if __name__ == "__main__":
    main()
