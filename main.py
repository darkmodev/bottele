import os
import logging
import random
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import nest_asyncio
import asyncio

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi API
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Konfigurasi Gemini 2.0 Flash
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")  # Menggunakan Gemini 2.0 Flash

# Quotes cinta
LOVE_QUOTES = [
    "Cinta itu bukan tentang memiliki, tapi menghargai. 💞",
    "Aku nggak butuh alasan untuk mencintaimu. Kamu cukup jadi kamu. ❤️",
    "Jarak bukan masalah kalau hati tetap dekat. ✨",
    "Kalau aku harus memilih antara napas dan kamu, aku akan pilih kamu. Karena kamu adalah hidupku. 🫶",
]

# ==================== HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, aku BucinBot 🤖 Siap bantu kamu jadi lebih bucin!\n"
        "Ketik /help untuk lihat semua fitur 💕"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💌 *Daftar Perintah BucinBot:*\n"
        "/start - Mulai ngobrol\n"
        "/surat - Buat surat cinta AI\n"
        "/quotes - Dapatkan kutipan cinta\n"
        "/rindu - Kirim pesan rindu\n"
        "/nembak - Simulasi nembak pakai AI\n"
        "/puisi - Buat puisi cinta AI\n",
        parse_mode="Markdown"
    )

# Surat cinta
async def surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_love_letter"] = True
    await update.message.reply_text("Apa tema surat cintamu? (Contoh: LDR, ulang tahun, patah hati...)")

async def handle_love_letter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        topic = update.message.text
        context.user_data["awaiting_love_letter"] = False
        await update.message.reply_text("Sedang menulis surat cinta... 💌")

        prompt = f"Buatkan surat cinta romantis dalam bahasa Indonesia dengan tema: {topic}."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Maaf, AI gagal bikin suratnya 😢 Coba lagi ya!")

# Quotes cinta
async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(LOVE_QUOTES)
    await update.message.reply_text(f"💘 {quote}")

# Rindu
async def rindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aku kangen kamu 😢 Tapi jarak ini cuma bikin aku makin cinta...")

# Nembak
async def nembak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lagi nyiapin kata-kata buat nembak... ❤️‍🔥")
    prompt = "Buatkan kata-kata romantis untuk menyatakan cinta pertama kali dalam bahasa Indonesia."
    try:
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("AI lagi bingung nulisnya 😅 Coba nanti lagi ya!")

# Puisi cinta
async def puisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_puisi"] = True
    await update.message.reply_text("Ketik topik puisi cintamu. Misalnya: hujan, senyuman, malam...")

async def handle_puisi_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_puisi"):
        topic = update.message.text
        context.user_data["awaiting_puisi"] = False
        await update.message.reply_text("Menulis puisi cinta... ✍️")

        prompt = f"Buatkan puisi cinta dalam bahasa Indonesia dengan tema '{topic}'."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Puisi gagal dibuat. AI lagi galau 😅")

# ==================== MAIN ====================

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("surat", surat))
    app.add_handler(CommandHandler("quotes", quotes))
    app.add_handler(CommandHandler("rindu", rindu))
    app.add_handler(CommandHandler("nembak", nembak))
    app.add_handler(CommandHandler("puisi", puisi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_love_letter_topic))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_puisi_topic))

    print("Bot berjalan...")
    await app.run_polling()

# Untuk Jupyter/Colab/docker
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
