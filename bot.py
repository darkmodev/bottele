import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai
from datetime import datetime

# Konfigurasi Token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY'

# Memory obrolan per user
user_histories = {}

# Setup logging
logging.basicConfig(level=logging.INFO)

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Mulai dan bantuan
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Saya adalah bot AI berbasis Gemini.\nKetik pertanyaanmu, dan saya akan menjawab.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cukup kirim pertanyaanmu. Saya akan mencoba membantu sebisanya!")

# Tangani pesan
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    # Ambil riwayat user, atau buat baru
    history = user_histories.get(user_id, [])
    history.append({"role": "user", "parts": [message]})

    try:
        response = model.generate_content(history)
        answer = response.text
        history.append({"role": "model", "parts": [answer]})

        # Simpan kembali
        user_histories[user_id] = history[-10:]  # simpan maksimal 10 pesan terakhir

        await update.message.reply_text(answer)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan. Coba lagi nanti.")

# Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot berjalan...")
    app.run_polling()

if __name__ == '__main__':
    main()
