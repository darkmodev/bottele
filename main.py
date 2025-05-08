import os
import logging
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
import nest_asyncio

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi API
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Aku BucinBot 💘\n"
        "Gunakan /chatbucin untuk mulai ngobrol, dan /help untuk bantuan."
    )

# Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bantuan Perintah:\n"
        "/start - Mulai obrolan\n"
        "/chatbucin - Ngobrol sama AI pacar bucin\n"
        "/stopchat - Akhiri mode pacar bucin\n"
        "/tipe - Ganti karakter pacar bucin\n"
        "/help - Tampilkan bantuan"
    )

# Chat Bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    context.user_data["tipe"] = "manja"
    await update.message.reply_text(
        "💖 Mode pacar bucin diaktifkan!\n"
        "Ketik apa aja ke aku~\n"
        "Gunakan /tipe untuk ganti karakter pacarku (manja, serius, humoris, cuek, penyayang, mesum)."
    )

# Ganti Tipe Pacar
async def tipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["manja", "serius"], ["humoris", "cuek"], ["penyayang", "mesum"]]
    await update.message.reply_text(
        "Pilih tipe pacar bucin yang kamu mau:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

# Stop Chat
async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Sampai jumpa lagi yaa~")

# Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text in ["manja", "serius", "humoris", "cuek", "penyayang", "mesum"]:
        context.user_data["tipe"] = text
        await update.message.reply_text(f"✅ Karakter pacar diubah ke: {text}")
        return

    if context.user_data.get("chat_bucin"):
        pesan = update.message.text
        tipe = context.user_data.get("tipe", "manja")
        prompt = f"Balas sebagai pacar {tipe} terhadap pesan ini: '{pesan}' dalam gaya romantis dan bucin."

        try:
            response = await model.generate_content_async(prompt)
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Lagi error nih sayang 😢")

# Setup
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(CommandHandler("tipe", tipe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
