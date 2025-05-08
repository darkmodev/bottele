import os
import logging
import random
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mendapatkan token dan API key dari environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Konfigurasi Gemini API
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Daftar kutipan cinta
LOVE_QUOTES = [
    "Cinta itu bukan tentang memiliki, tapi menghargai. 💞",
    "Aku nggak butuh alasan untuk mencintaimu. Kamu cukup jadi kamu. ❤️",
    "Jarak bukan masalah kalau hati tetap dekat. ✨",
    "Kalau aku harus memilih antara napas dan kamu, aku akan pilih kamu. Karena kamu adalah hidupku. ��",
]

# Handler untuk perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, aku BucinBot 🤖 Siap bantu kamu jadi lebih bucin!\n"
        "Ketik /surat, /quotes, /rindu, /nembak, /puisi, atau /help untuk mulai."
    )

# Handler untuk perintah /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Berikut adalah perintah yang tersedia:\n"
        "/start - Memulai interaksi dengan bot\n"
        "/surat - Membuat surat cinta dengan bantuan AI\n"
        "/quotes - Menampilkan kutipan cinta acak\n"
        "/rindu - Mengungkapkan rasa rindu\n"
        "/nembak - Membantu menyatakan cinta\n"
        "/puisi - Membuat puisi cinta dengan bantuan AI\n"
        "/help - Menampilkan daftar perintah"
    )

# Handler untuk perintah /surat
async def surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_love_letter"] = True
    await update.message.reply_text("Apa tema surat cintamu? Contoh: LDR, ulang tahun, patah hati...")

# Handler untuk perintah /quotes
async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(LOVE_QUOTES)
    await update.message.reply_text(f"💘 {quote}")

# Handler untuk perintah /rindu
async def rindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aku kangen kamu 😢 Tapi jarak ini cuma bikin aku makin cinta...")

# Handler untuk perintah /nembak
async def nembak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lagi nyiapin kata-kata buat nembak... ❤️‍🔥")
    prompt = "Buatkan kata-kata romantis untuk menyatakan cinta pertama kali dalam bahasa Indonesia."
    try:
        response = await model.generate_content_async(prompt)
        teks = response.text.strip()
        await update.message.reply_text(teks)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("AI lagi bingung nulisnya 😅 Coba nanti lagi ya!")

# Handler untuk perintah /puisi
async def puisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_puisi"] = True
    await update.message.reply_text("Ketik topik puisi cintamu. Misalnya: hujan, senyuman, malam...")

# Handler untuk menangani input tema surat cinta
async def handle_love_letter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        topic = update.message.text
        context.user_data["awaiting_love_letter"] = False
        await update.message.reply_text("Sedang menulis surat cinta AI... 💌")

        prompt = f"Buatkan surat cinta romantis dalam bahasa Indonesia dengan tema: {topic}."
        try:
            response = await model.generate_content_async(prompt)
            letter = response.text.strip()
            await update.message.reply_text(letter)
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Maaf, AI gagal bikin suratnya 😥 Coba lagi ya!")

# Handler untuk menangani input tema puisi
async def handle_puisi_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_puisi"):
        topic = update.message.text
        context.user_data["awaiting_puisi"] = False
        await update.message.reply_text("Menulis puisi cinta... ✍️")

        prompt = f"Buatkan puisi cinta dalam bahasa Indonesia dengan tema '{topic}'."
        try:
            response = await model.generate_content_async(prompt)
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Puisi gagal dibuat. AI lagi galau 😅")

# Fungsi utama untuk menjalankan bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Menambahkan handler untuk setiap perintah
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("surat", surat))
    app.add_handler(CommandHandler("quotes", quotes))
    app.add_handler(CommandHandler("rindu", rindu))
    app.add_handler(CommandHandler("nembak", nembak))
    app.add_handler(CommandHandler("puisi", puisi))

    # Menambahkan handler untuk menangani input teks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_love_letter_topic))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_puisi_topic))

    print("Bot berjalan...")

    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
