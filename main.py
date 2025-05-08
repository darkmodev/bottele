import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters)
import nest_asyncio
import asyncio

# Konfigurasi
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi Gemini Flash
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Inisialisasi panggilan khusus pengguna
user_nicknames = {}

# Mood keywords
MOOD_RESPONSES = {
    "sedih": "Sayang jangan sedih ya, sini peluk dulu 🤗💕",
    "senang": "Aku ikut senang dengarnya, sayang! 😘✨",
    "marah": "Tenang ya, aku di sini buat nenangin kamu 😔💖",
    "kesepian": "Aku selalu ada buat nemenin kamu, ayang... 🤍",
    "capek": "Istirahat dulu ya, aku temenin di sini 😌🫶",
    "bahagia": "Yey! Aku ikut bahagia dengar kabar baik dari kamu! 🎉💖"
}

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Aku BucinBot 💘
Gunakan /chatbucin untuk ngobrol ala pacar, dan /help untuk lihat semua perintah.")

# Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
❤️ Perintah BucinBot:
/start - Mulai obrolan
/help - Lihat daftar perintah
/chatbucin - Ngobrol roleplay sama AI pacar
/stopchat - Akhiri mode pacar bucin
""")

# Mode Chat Bucin ON
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

# Mode Chat Bucin OFF
async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

# Deteksi Mood dan Panggilan Khusus
async def chatbucin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_bucin"):
        user_id = update.effective_user.id
        text = update.message.text.lower()

        # Simpan panggilan khusus jika ada
        if any(nick in text for nick in ["sayang", "ayang", "cinta", "beb"]):
            for nick in ["sayang", "ayang", "cinta", "beb"]:
                if nick in text:
                    user_nicknames[user_id] = nick

        nickname = user_nicknames.get(user_id, "sayang")

        # Deteksi mood
        for mood, response in MOOD_RESPONSES.items():
            if mood in text:
                await update.message.reply_text(response.replace("sayang", nickname))
                return

        # Simulasi suasana (contoh sederhana)
        if "hujan" in text:
            await update.message.reply_text(f"Udara dingin ya {nickname}, sini aku peluk biar hangat ☔❤️")
            return

        # Jika tidak terdeteksi mood/suasana, lanjut ke AI
        prompt = f"Kamu adalah pacar bucin yang romantis. Balas pesan ini dengan nada manja dan cinta: '{text}'"
        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Maaf ya, AI-nya lagi error 😢")

# Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbucin_handler))

    print("🤖 BucinBot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
