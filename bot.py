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

# Load token dari environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi log
logging.basicConfig(level=logging.INFO)

# Konfigurasi Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Memory per pengguna
user_histories = {}

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Saya adalah bot AI berbasis Gemini.\n"
        "Ketik pertanyaanmu dan saya akan bantu.\n\n"
        "Perintah:\n/start - Mulai ulang\n/help - Bantuan\n/clear - Hapus memori"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 Bantuan Bot:\n/start - Mulai ulang bot\n/help - Tampilkan perintah\n/clear - Hapus ingatan obrolan"
    )

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories.pop(user_id, None)
    await update.message.reply_text("✅ Ingatan obrolan kamu telah dihapus.")

# --- Pesan Biasa Handler ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    message = update.message.text

    history = user_histories.get(user_id, [])
    history.append({"role": "user", "parts": [message]})

    try:
        response = model.generate_content(history)
        reply = response.text.strip()
        history.append({"role": "model", "parts": [reply]})
        user_histories[user_id] = history[-10:]  # Maksimal 10 pesan terakhir

        await update.message.reply_text(reply)

        # Logging ke file
        with open("chat_log.txt", "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now()}] {user.full_name} ({user_id})\n")
            log.write(f"You: {message}\nBot: {reply}\n\n")

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Maaf, terjadi kesalahan. Coba lagi nanti.")

# --- Main App ---

def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise EnvironmentError("❌ Token belum diatur di environment variable.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_memory))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot aktif...")
    app.run_polling()

if __name__ == "__main__":
    main()
