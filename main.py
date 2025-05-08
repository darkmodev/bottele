import os
import logging
import random
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import google.generativeai as genai

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi API
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Quotes cinta statis
LOVE_QUOTES = [
    "Cinta itu bukan tentang memiliki, tapi menghargai. 💞",
    "Aku nggak butuh alasan untuk mencintaimu. Kamu cukup jadi kamu. ❤️",
    "Jarak bukan masalah kalau hati tetap dekat. ✨",
    "Kalau aku harus memilih antara napas dan kamu, aku akan pilih kamu. Karena kamu adalah hidupku. 🫶",
]

# ====================== HANDLER ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo, aku BucinBot 🤖 Siap bantu kamu jadi lebih bucin! Ketik /help untuk lihat fitur.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💘 *Daftar Perintah BucinBot:*\n"
        "/start - Mulai obrolan\n"
        "/help - Lihat semua fitur\n"
        "/surat - Tulis surat cinta AI\n"
        "/quotes - Dapatkan kutipan cinta (AI atau statis)\n"
        "/rindu - Ekspresikan rasa rindu\n"
        "/nembak - Kata-kata buat nembak\n"
        "/puisi - Buat puisi cinta AI\n"
        "/chatbucin - Mode pacar bucin (chat)\n"
        "/stopchat - Akhiri mode pacar bucin\n"
        "/diary - Curhat dan simpan di AI Diary\n"
        "/mood - Ceritakan mood kamu (AI bantu hibur)\n"
        "/tebakperasaan - Tebak isi hati kamu 😳"
    )
    await update.message.reply_text(help_text)

async def surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_love_letter"] = True
    await update.message.reply_text("Apa tema surat cintamu? Contoh: LDR, ulang tahun, patah hati...")

async def handle_surat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        context.user_data["awaiting_love_letter"] = False
        topic = update.message.text
        await update.message.reply_text("Sedang menulis surat cinta AI... 💌")
        prompt = f"Buatkan surat cinta romantis bertema '{topic}' dalam bahasa Indonesia."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.choice([True, False]):
        quote = random.choice(LOVE_QUOTES)
        await update.message.reply_text(f"💘 {quote}")
    else:
        prompt = "Beri aku kutipan cinta romantis dalam bahasa Indonesia."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text("💘 " + response.text.strip())

async def rindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.choice([True, False]):
        await update.message.reply_text("Aku kangen kamu 😢 Tapi jarak ini cuma bikin aku makin cinta...")
    else:
        response = await model.generate_content_async(["Buatkan ungkapan rindu yang romantis dalam bahasa Indonesia."])
        await update.message.reply_text(response.text.strip())

async def nembak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lagi nyiapin kata-kata buat nembak... ❤️‍🔥")
    prompt = "Buatkan kata-kata romantis untuk menyatakan cinta pertama kali dalam bahasa Indonesia."
    response = await model.generate_content_async([prompt])
    await update.message.reply_text(response.text.strip())

async def puisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_puisi"] = True
    await update.message.reply_text("Ketik topik puisi cintamu. Misalnya: hujan, senyuman, malam...")

async def handle_puisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_puisi"):
        context.user_data["awaiting_puisi"] = False
        topic = update.message.text
        await update.message.reply_text("Menulis puisi cinta... ✍️")
        prompt = f"Buatkan puisi cinta romantis bertema '{topic}' dalam bahasa Indonesia yang pendek tapi menyentuh."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_bucin"):
        text = update.message.text
        prompt = f"Kamu adalah pacar romantis dan bucin. Balas pesan ini secara manja dan bucin: {text}"
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

async def diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_diary"] = True
    await update.message.reply_text("Ceritakan isi hati kamu hari ini... Aku jadi tempat curhat kamu yaa~")

async def handle_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_diary"):
        context.user_data["awaiting_diary"] = False
        entry = update.message.text
        prompt = f"Aku curhat: {entry}\nTolong beri respon suportif dan penuh cinta, seolah kamu pacarku."
        response = await model.generate_content_async([prompt])
        await update.message.reply_text("💌 Catatan tersimpan! Ini balasan buat kamu:\n" + response.text.strip())

# Fitur mood
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ceritakan tentang moodmu, dan biar aku bantu nenangin 💗")

    # Mengambil cerita mood dan menanggapi dengan AI
    user_mood = update.message.text
    prompt = f"Bantu pacarku menenangkan dia yang sedang moodnya: {user_mood}. Buat pesan yang menenangkan dan penuh cinta."

    try:
        response = await model.generate_content_async(prompt)
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        await update.message.reply_text("Maaf, AI gagal nenangin mood kamu 😞 Coba lagi nanti ya!")

async def tebakperasaan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Kamu adalah AI yang bisa membaca hati. Buat tebakan lucu dan romantis tentang isi hati user."
    response = await model.generate_content_async([prompt])
    await update.message.reply_text(response.text.strip())

# ====================== MAIN ======================

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
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("tebakperasaan", tebakperasaan))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_surat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_puisi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_diary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mood))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("💘 BucinBot aktif...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
