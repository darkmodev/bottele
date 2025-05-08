import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import random
import nest_asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi dari environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Quotes cinta
LOVE_QUOTES = [
    "Cinta itu bukan tentang memiliki, tapi menghargai. 💞",
    "Aku nggak butuh alasan untuk mencintaimu. Kamu cukup jadi kamu. ❤️",
    "Jarak bukan masalah kalau hati tetap dekat. ✨",
    "Kalau aku harus memilih antara napas dan kamu, aku akan pilih kamu. Karena kamu adalah hidupku. 🫶",
]

# Handler start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, aku BucinBot 🤖 Siap bantu kamu jadi lebih bucin!\n"
        "Ketik /surat, /quotes, /rindu, /nembak, atau /puisi untuk mulai."
    )

# Handler surat cinta AI
async def surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_love_letter"] = True
    await update.message.reply_text("Apa tema surat cintamu? Contoh: LDR, ulang tahun, patah hati...")

# Surat cinta berdasarkan input
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
            await update.message.reply_text("Maaf, AI gagal bikin suratnya 😢 Coba lagi ya!")

# Quotes cinta acak
async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(LOVE_QUOTES)
    await update.message.reply_text(f"💘 {quote}")

# Pesan rindu bucin
async def rindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aku kangen kamu 😢 Tapi jarak ini cuma bikin aku makin cinta...")

# Nembak pakai AI
async def nembak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lagi nyiapin kata-kata buat nembak... ❤️‍🔥")
    prompt = "Buatkan kata-kata romantis untuk menyatakan cinta pertama kali dalam bahasa Indonesia."
    try:
        response = await model.generate_content_async(prompt)
        teks = response.text.strip()
        await update.message.reply_text(teks)
    except Exception as e:
        await update.message.reply_text("AI lagi bingung nulisnya 😅 Coba nanti lagi ya!")

# Puisi AI
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
            response = await model.generate_content_async(prompt)
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            await update.message.reply_text("Puisi gagal dibuat. AI lagi galau 😅")

# Main bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("surat", surat))
    app.add_handler(CommandHandler("quotes", quotes))
    app.add_handler(CommandHandler("rindu", rindu))
    app.add_handler(CommandHandler("nembak", nembak))
    app.add_handler(CommandHandler("puisi", puisi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_love_letter_topic))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_puisi_topic))

    print("Bot berjalan...")

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    import nest_asyncio

    # Apply nest_asyncio to handle already running loop
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
