import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import google.generativeai as genai

# Logging
logging.basicConfig(level=logging.INFO)

# Token dari environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Penyimpanan histori obrolan per user
user_histories = {}

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌹 Selamat datang di LoveBot AI!\n\n"
        "Gunakan perintah berikut:\n"
        "/pair - Pasangkan dengan pasangan\n"
        "/diary - Tulis & baca diary cinta\n"
        "/schedule - Atur pesan otomatis harian\n"
        "/countdown - Lihat hari-hari penting\n"
        "/quizlove - Main kuis cinta\n"
        "/poem - Buat puisi/surat cinta otomatis\n"
        "/mood - Catat mood pasangan\n"
        "/settings - Privasi & pengaturan\n\n"
        "Ketik apa pun untuk bicara dengan AI romantis ❤️"
    )

async def pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💑 Siapa nama pasanganmu? (Fitur pairing belum lengkap)")

async def diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Apa yang ingin kamu tulis hari ini? (Fitur diary belum lengkap)")

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕰️ Mau kirim pesan otomatis jam berapa? (Fitur jadwal belum lengkap)")

async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Hari jadian, ulang tahun, atau tanggal penting? (Fitur countdown belum lengkap)")

async def quizlove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❤️ Siap main kuis cinta? (Fitur quiz belum lengkap)")

async def poem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Ketik tema puisi atau surat cintamu!")

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😊 Bagaimana mood kamu hari ini? (Fitur mood belum lengkap)")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ Belum ada pengaturan tersedia. (Fitur pengaturan belum lengkap)")

# --- AI Handler (Chat dengan Gemini) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    history = user_histories.get(user_id, [])
    history.append({"role": "user", "parts": [text]})

    try:
        response = model.generate_content(history)
        reply = response.text
        history.append({"role": "model", "parts": [reply]})
        user_histories[user_id] = history[-10:]  # Simpan hingga 10 pesan terakhir

        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Terjadi kesalahan saat menghubungi AI.")

# --- Main Function ---
def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise ValueError("TELEGRAM_TOKEN dan GEMINI_API_KEY harus diatur.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    commands = [
        ("start", start), ("pair", pair), ("diary", diary),
        ("schedule", schedule), ("countdown", countdown),
        ("quizlove", quizlove), ("poem", poem),
        ("mood", mood), ("settings", settings)
    ]

    for name, handler in commands:
        app.add_handler(CommandHandler(name, handler))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("💘 LoveBot AI is running.")
    app.run_polling()

if __name__ == "__main__":
    main()
