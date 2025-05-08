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
        "Gunakan /chatbucin untuk mulai ngobrol, /bahasa untuk ganti bahasa, dan /help untuk bantuan."
    )

# Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bantuan Perintah:\n"
        "/start - Mulai obrolan\n"
        "/chatbucin - Ngobrol sama AI pacar bucin\n"
        "/stopchat - Akhiri mode pacar bucin\n"
        "/bahasa - Pilih bahasa (Indonesia atau Sunda)\n"
        "/help - Tampilkan bantuan"
    )

# Pilih Bahasa
async def bahasa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Indonesia", "Sunda"]]
    await update.message.reply_text(
        "Pilih bahasa yang kamu inginkan:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

async def set_bahasa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in ["Indonesia", "Sunda"]:
        context.user_data["language"] = update.message.text
        await update.message.reply_text(f"Bahasa diatur ke {update.message.text}!")

# Chat Bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    context.user_data["tipe"] = "manja"  # default tipe
    await update.message.reply_text(
        "💖 Mode pacar bucin diaktifkan!\n"
        "Ketik apa aja ke aku~\n"
        "Kamu bisa ganti karakter pacarku nanti (manja, serius, humoris, cuek, penyayang, mesum)"
    )

# Stop Chat
async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 Mode pacar bucin dimatikan. Sampai jumpa lagi yaa~")

# Chat Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_bucin"):
        pesan = update.message.text
        tipe = context.user_data.get("tipe", "manja")
        bahasa = context.user_data.get("language", "Indonesia")

        if bahasa == "Sunda":
            prompt = f"Jieun obrolan pacar bucin nu gaya {tipe} kana pesen ieu: '{pesan}' dina Basa Sunda."
        else:
            prompt = f"Balas sebagai pacar {tipe} terhadap pesan ini: '{pesan}' dalam gaya romantis dan bucin."

        try:
            response = await model.generate_content_async(prompt)
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("Lagi error nih sayang 😢")
    elif update.message.text in ["Indonesia", "Sunda"]:
        await set_bahasa(update, context)

# Setup
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(CommandHandler("bahasa", bahasa))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
tesq
