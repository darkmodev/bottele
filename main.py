import os
import logging
import random
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          ContextTypes, filters)
import google.generativeai as genai

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key dan Token dari environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Konfigurasi Gemini 2.0 Flash
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# ===== Handler Start dan Help =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Aku BucinBot 💘\nKetik /help untuk lihat fitur-fitur bucin yang tersedia."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❤️ *Fitur BucinBot* ❤️\n"
        "/start - Mulai obrolan\n"
        "/help - Lihat semua fitur\n"
        "/chatbucin - Mode pacar bucin roleplay\n"
        "/stopchat - Keluar dari mode pacar\n"
        "\nFitur spesial:\n"
        "- Deteksi mood dari pesanmu\n"
        "- Panggilan khusus dengan respons manja\n"
        "- Simulasi suasana (seperti hujan, malam, dll)"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===== Chat Bucin Mode =====
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

# ===== Chat Handler =====
async def handle_chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_bucin"):
        user_input = update.message.text.lower()

        # Fitur 1: Mood detector
        mood_prompts = [
            "senang", "sedih", "marah", "kesepian", "bahagia", "capek", "kesal"
        ]
        mood_detected = next((m for m in mood_prompts if m in user_input), None)

        # Fitur 2: Panggilan sayang
        panggilan_khusus = ["sayang", "beb", "ayang", "cinta"]
        panggilan = next((p for p in panggilan_khusus if p in user_input), None)

        # Fitur 3: Simulasi suasana
        if "hujan" in user_input:
            suasana = "Bayangin kita lagi pelukan sambil dengerin hujan, hangat banget..."
        elif "malam" in user_input:
            suasana = "Malam ini cuma kamu yang ada di pikiranku. Peluk dari jauh ya... 🥺"
        else:
            suasana = None

        # Prompt AI gabungan
        prompt = "Jadilah pacar bucin yang perhatian dan manja."
        if mood_detected:
            prompt += f" Pasangannya sedang merasa {mood_detected}, hibur dia."
        if panggilan:
            prompt += f" Gunakan kata panggilan '{panggilan}' dalam balasan."
        if suasana:
            prompt += f" Tambahkan suasana: {suasana}"

        prompt += f"\n\nBalas ini dengan gaya manja dan bucin: {user_input}"

        try:
            response = await model.generate_content_async([prompt])
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Maaf, AI pacarmu lagi error 😢")

# ===== Main =====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chatbucin))

    print("BucinBot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    import nest_asyncio

    nest_asyncio.apply()
    asyncio.run(main())
