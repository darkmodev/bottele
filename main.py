import requests
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token API Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Token API Gemini 2.0 Flash (harus diganti dengan API key yang benar)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://gemini.googleapis.com/v1beta2/projects/your-project-id/models/gemini2.0flash:predict"

# Fungsi untuk berkomunikasi dengan API Gemini 2.0 Flash
async def get_ai_response(user_message: str):
    try:
        headers = {
            'Authorization': f'Bearer {GEMINI_API_KEY}',
            'Content-Type': 'application/json',
        }

        data = {
            "instances": [
                {
                    "input": user_message
                }
            ]
        }

        response = requests.post(GEMINI_API_URL, json=data, headers=headers)
        response.raise_for_status()
        ai_response = response.json()['predictions'][0]['output']
        return ai_response.strip()
    except Exception as e:
        logger.error(f"Error saat memanggil API Gemini: {e}")
        return "Maaf, saya mengalami masalah saat mencoba merespon. Coba lagi nanti."

# Fitur Chat Bucin dengan model AI (Gemini 2.0 Flash)
async def handle_chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    if "chat_bucin" in user_data and user_data["chat_bucin"]:
        user_message = update.message.text

        ai_response = await get_ai_response(user_message)
        await update.message.reply_text(ai_response)

# Handler Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Aku BucinBot 💘\n\n"
        "Aku bisa bantu kamu jadi lebih bucin! Berikut adalah beberapa perintah yang bisa kamu coba:\n"
        "/chatbucin - Ngobrol sama pacar AI\n"
        "/stopchat - Matikan mode pacar AI\n"
        "/help - Lihat bantuan lagi"
    )

# Handler Help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Berikut adalah beberapa perintah yang bisa kamu gunakan:\n"
        "/chatbucin - Ngobrol sama pacar AI\n"
        "/stopchat - Matikan mode pacar AI\n"
        "/help - Lihat bantuan ini lagi"
    )

# Fitur Chat Bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

# Main bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chatbucin))

    print("Bot berjalan...")

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    # Apply nest_asyncio to handle already running loop
    import nest_asyncio
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
