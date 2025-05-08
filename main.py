import os
import logging
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import google.generativeai as genai

# Konfigurasi API
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== COMMAND HANDLER ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Aku BucinBot 🤖 Siap nemenin kamu bucin! 💕")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💘 *Fitur BucinBot:*\n"
        "/start - Mulai obrolan\n"
        "/help - Lihat semua fitur\n"
        "/chatbucin - Ngobrol roleplay sama AI pacar\n"
        "/stopchat - Akhiri mode pacar bucin\n"
    )
    await update.message.reply_text(help_text)

async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    await update.message.reply_text("💖 Mode pacar bucin diaktifkan! Ketik apa aja ke aku~")

async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Kapan-kapan kita ngobrol lagi yaa...")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_bucin"):
        user_message = update.message.text
        prompt = f"Kamu adalah pacar romantis dan bucin. Balas pesan ini dengan manja dan cinta: {user_message}"
        response = await model.generate_content_async([prompt])
        await update.message.reply_text(response.text.strip())

# ==================== MAIN ====================

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("💘 BucinBot aktif hanya dengan fitur chat bucin!")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
