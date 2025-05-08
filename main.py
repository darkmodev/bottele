import os
import logging
import random
import asyncio
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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Gemini 2.0 Flash
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

LOVE_QUOTES = [
    "Cinta itu bukan tentang memiliki, tapi menghargai. 💞",
    "Aku nggak butuh alasan untuk mencintaimu. Kamu cukup jadi kamu. ❤️",
    "Jarak bukan masalah kalau hati tetap dekat. ✨",
    "Kalau aku harus memilih antara napas dan kamu, aku akan pilih kamu. Karena kamu adalah hidupku. 🫶",
]

# State
user_states = {}

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo sayangku 😘 pami gabutmah kadie we nya cantik\nKetik /help untuk lihat semua fitur 💕")

# Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💌 *Daftar Perintah Bot sayang:*\n"
        "/start - Mulai ngobrol\n"
        "/help - Lihat menu bantuan\n"
        "/surat - Tulis surat cinta \n"
        "/quotes - Dapatkan kutipan cinta acak \n"
        "/rindu - Ekspresikan rasa rindu \n"
        "/nembak - Kata-kata untuk menyatakan cinta\n"
        "/puisi - Buat puisi cinta \n"
        "/chatbucin - Ngobrol roleplay sama AI pacar\n"
        "/stopchat - Akhiri mode pacar bucin\n"
        "/diary - Tulis isi hati\n",
        parse_mode="Markdown"
    )

# Surat cinta
async def surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_love_letter"] = True
    await update.message.reply_text("Apa tema surat cintamu? Contoh: LDR, ulang tahun, patah hati...")

async def handle_love_letter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        context.user_data["awaiting_love_letter"] = False
        topic = update.message.text
        await update.message.reply_text("ngetik hela kedapnya cantik 🥰💌")
        prompt = f"Buatkan surat cinta romantis dalam bahasa Indonesia tambahkan tanda tangan kekasih tercinta dan penerima dengan nama eca nur aisyah kekasihku dengan tema: {topic}."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

# Quotes cinta
async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.5:
        quote = random.choice(LOVE_QUOTES)
    else:
        response = await model.generate_content_async(["Beri aku kutipan cinta romantis dalam bahasa Indonesia."])
        quote = response.text.strip()
    await update.message.reply_text(f"💘 {quote}")

# Rindu
async def rindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.5:
        msg = "Aku kangen kamu 😢 Tapi jarak ini cuma bikin aku makin cinta..."
    else:
        response = await model.generate_content_async(["Buatkan ungkapan rindu romantis dalam bahasa Indonesia."])
        msg = response.text.strip()
    await update.message.reply_text(msg)

# Nembak
async def nembak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lagi nyiapin kata-kata buat nembak... ❤️‍🔥")
    prompt = "Buatkan kata-kata romantis untuk menyatakan cinta pertama kali dalam bahasa Indonesia."
    response = await model.generate_content_async([prompt])
    await update.message.reply_text(response.text.strip())

# Puisi
async def puisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_puisi"] = True
    await update.message.reply_text("Ketik topik puisi cintamu. Misalnya: hujan, senyuman, malam...")

async def handle_puisi_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_puisi"):
        context.user_data["awaiting_puisi"] = False
        topic = update.message.text
        await update.message.reply_text("Menulis puisi cinta... ✍️")
        prompt = f"Buatkan puisi cinta romantis bertema '{topic}' dalam bahasa Indonesia yang pendek tapi romantis."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

# /chatbucin - Aktifkan mode pacar bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

# /stopchat - Nonaktifkan mode pacar bucin
async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

# Menangani semua pesan teks untuk chat bucin
async def handle_chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_bucin", False):
        user_text = update.message.text
        prompt = f"Kamu adalah pacar bucin yang sangat romantis. Balas pesan ini dengan penuh cinta: {user_text}"
        try:
            response = await model.generate_content_async(prompt)
            ai_reply = response.text.strip()
            await update.message.reply_text(ai_reply)
        except Exception as e:
            await update.message.reply_text("Lagi bingung jawabnya 😅 coba lagi bentar ya!")

# Diary
async def diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_diary"] = True
    await update.message.reply_text("Tulis isi hatimu hari ini. Kamu lagi sedih? senang? galau? Ceritain ke aku ya 💕")

async def handle_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_diary"):
        context.user_data["awaiting_diary"] = False
        mood_input = update.message.text
        prompt = f"Seseorang menulis diary seperti ini: '{mood_input}'. Tanggapi dengan empati dan berikan semangat atau hiburan ringan agar suasana hatinya membaik."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

# Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("surat", surat))
    app.add_handler(CommandHandler("quotes", quotes))
    app.add_handler(CommandHandler("rindu", rindu))
    app.add_handler(CommandHandler("nembak", nembak))
    app.add_handler(CommandHandler("puisi", puisi))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(CommandHandler("diary", diary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_love_letter_topic))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_puisi_topic))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_diary))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chatbucin))

    print("Bot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
