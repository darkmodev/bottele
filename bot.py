import logging
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

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOG_FILE = "chat_log.txt"

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Setup Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Memory per user
user_histories = {}

# === COMMAND HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Saya adalah bot AI berbasis Gemini.\n"
        "Ketik pertanyaanmu dan saya akan membantu.\n\n"
        "Ketik /help untuk lihat perintah."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Perintah yang tersedia:\n"
        "/start - Mulai obrolan\n"
        "/help - Tampilkan bantuan\n"
        "/clear - Hapus ingatan obrolanmu"
    )

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories.pop(user_id, None)
    await update.message.reply_text("🧹 Ingatan obrolan kamu telah dihapus.")

# === MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text

    # Ambil histori user
    history = user_histories.get(user_id, [])
    history.append({"role": "user", "parts": [text]})

    try:
        response = model.generate_content(history)
        answer = response.text.strip()
        history.append({"role": "model", "parts": [answer]})

        # Simpan kembali (maks 10 interaksi)
        user_histories[user_id] = history[-10:]

        await update.message.reply_text(answer)

        # Logging ke file
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {user.full_name} ({user_id})\n")
            f.write(f"You: {text}\nBot: {answer}\n\n")

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan, coba lagi nanti.")

# === MAIN ===

def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise EnvironmentError("❌ Token belum diset di environment variable.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_memory))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot aktif...")
    app.run_polling()

if __name__ == "__main__":
    main()
