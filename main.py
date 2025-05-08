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
from google.generativeai import configure, GenerativeModel

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment config
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Gemini 2.0 Flash config
configure(api_key=GENAI_API_KEY)
model = GenerativeModel("models/gemini-1.5-flash")

LOVE_QUOTES = [
    "Cinta itu bukan tentang memiliki, tapi menghargai. 💞",
    "Aku nggak butuh alasan untuk mencintaimu. Kamu cukup jadi kamu. ❤️",
    "Jarak bukan masalah kalau hati tetap dekat. ✨",
    "Kalau aku harus memilih antara napas dan kamu, aku akan pilih kamu. Karena kamu adalah hidupku. 🫶",
]

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, aku BucinBot 🤖 Siap bantu kamu jadi lebih bucin!\n"
        "Ketik /help untuk lihat semua fitur."
    )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Mulai obrolan
"
        "/help - Daftar semua fitur
"
        "/surat - Tulis surat cinta AI
"
        "/quotes - Dapatkan kutipan cinta acak (dari AI atau kekasih)
"
        "/rindu - Ekspresikan rasa rindu (pilihan dari AI/kekasih)
"
        "/nembak - Kata-kata untuk menyatakan cinta
"
        "/puisi - Buat puisi cinta AI
"
        "/chatbucin - Ngobrol roleplay sama AI pacar
"
        "/stopchat - Akhiri mode pacar bucin
"
        "/diary - Curhat harian ke AI
"
        "/tebakperasaan - Tebak suasana hatimu lewat AI"
    )
    await update.message.reply_text(help_text)

# Quotes
async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.5:
        quote = random.choice(LOVE_QUOTES)
        await update.message.reply_text(f"💘 {quote}")
    else:
        try:
            response = await model.generate_content_async([
                "Buatkan satu kutipan cinta pendek yang manis dalam bahasa Indonesia."
            ])
            await update.message.reply_text("💘 " + response.text.strip())
        except Exception:
            await update.message.reply_text(random.choice(LOVE_QUOTES))

# Surat cinta
async def surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_love_letter"] = True
    await update.message.reply_text("Apa tema surat cintamu? Contoh: LDR, ulang tahun, patah hati...")

async def handle_love_letter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        context.user_data["awaiting_love_letter"] = False
        topic = update.message.text
        prompt = f"Buatkan surat cinta romantis dalam bahasa Indonesia dengan tema: {topic}."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception:
            await update.message.reply_text("Maaf, AI gagal bikin suratnya 😢 Coba lagi ya!")

# Rindu
async def rindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.5:
        await update.message.reply_text("Aku kangen kamu 😢 Tapi jarak ini cuma bikin aku makin cinta...")
    else:
        prompt = "Buatkan satu kalimat rindu romantis pendek dalam bahasa Indonesia."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception:
            await update.message.reply_text("Aku rindu, beneran... 💔")

# Nembak
async def nembak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Buatkan kata-kata romantis untuk menyatakan cinta pertama kali dalam bahasa Indonesia."
    try:
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())
    except Exception:
        await update.message.reply_text("AI lagi bingung nulisnya 😅 Coba nanti lagi ya!")

# Puisi
async def puisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_puisi"] = True
    await update.message.reply_text("Ketik topik puisi cintamu. Misalnya: hujan, senyuman, malam...")

async def handle_puisi_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_puisi"):
        context.user_data["awaiting_puisi"] = False
        topic = update.message.text
        prompt = f"Buatkan puisi cinta romantis bertema '{topic}' dalam bahasa Indonesia yang pendek tapi romantis."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception:
            await update.message.reply_text("Puisi gagal dibuat. AI lagi galau 😅")

# Chat Bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

# Diary
async def diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_diary"] = True
    await update.message.reply_text("Tulis isi hati kamu hari ini 💌")

async def handle_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_diary"):
        context.user_data["awaiting_diary"] = False
        curhat = update.message.text
        prompt = f"Seseorang curhat: '{curhat}'. Berikan tanggapan suportif dan romantis sebagai pasangan."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception:
            await update.message.reply_text("AI-nya lagi baper, coba lagi nanti ya~ 😅")

# Tebak Perasaan
async def tebakperasaan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_tebakan"] = True
    await update.message.reply_text("Ketik sesuatu, dan aku coba tebak kamu lagi merasa apa 🧠❤️")

async def handle_tebakan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_tebakan"):
        context.user_data["awaiting_tebakan"] = False
        teks = update.message.text
        prompt = f"Analisis kalimat berikut dan tebak perasaan pengirimnya: '{teks}'. Pilih satu: senang, sedih, jatuh cinta, galau. Jelaskan kenapa."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception:
            await update.message.reply_text("Hmm... aku bingung nebak perasaanmu. 😶 Coba lagi yaa.")

# General handler
async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        await handle_love_letter_topic(update, context)
    elif context.user_data.get("awaiting_puisi"):
        await handle_puisi_topic(update, context)
    elif context.user_data.get("awaiting_diary"):
        await handle_diary(update, context)
    elif context.user_data.get("awaiting_tebakan"):
        await handle_tebakan(update, context)
    elif context.user_data.get("chat_bucin"):
        teks = update.message.text
        prompt = f"Sebagai pacar yang bucin dan romantis, balas pesan ini: '{teks}' dalam gaya manja dan manis."
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception:
            await update.message.reply_text("Aku bingung jawabnya 😅 Tapi aku tetep sayang kamu kok~")

# Main function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quotes", quotes))
    app.add_handler(CommandHandler("surat", surat))
    app.add_handler(CommandHandler("rindu", rindu))
    app.add_handler(CommandHandler("nembak", nembak))
    app.add_handler(CommandHandler("puisi", puisi))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(CommandHandler("diary", diary))
    app.add_handler(CommandHandler("tebakperasaan", tebakperasaan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))

    print("Bot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
