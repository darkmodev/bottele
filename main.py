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
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi API
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

user_moods = {}

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "hai sayangku cintaku cantiku 🥰💘\n"
        "ango /chatbucin kango ngamimitian ngobrol, sareng /help pami peryogi bantosan."
    )

# Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bantuan Perintah:\n"
        "/start - hayu chatan\n"
        "/chatbucin - chatan sareng kabogoh\n"
        "/stopchat - atosan chatana☺️\n"
        "/tipe - Ganti karakter kabogoh\n"
        "/dailymsg - Pesan cinta harian\n"
        "/poem - Buat puisi cinta\n"
        "/countdown - Hitung hari penting\n"
        "/mood - Catat mood anjeun ayeuna\n"
        "/help - kango babantos"
    )

# Chat Bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = True
    context.user_data["tipe"] = "manja"
    await update.message.reply_text(
        "💖 hoyong anu type anu kumaha cantik🥰!\n"
        "manga bade nyarios naon sayangku😉~\n"
        "ango /tipe kango ngagentos type nu kmaha (manja, serius, humoris, cuek, romantis, genit)."
    )

# Ganti Tipe Pacar
async def tipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["manja", "serius"], ["humoris", "cuek"], ["romantis", "genit"]]
    await update.message.reply_text(
        "pilihnya sesuai kahoyong typena😉 :",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

# Stop Chat
async def stopchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_bucin"] = False
    await update.message.reply_text("💔 kabogohna di paehan😁~")

# Daily Love Message
async def dailymsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌞 Selamat pagi cintaku! Hari ini aku harap kamu bahagia, sehat, dan tetap manis yaa 💖")

# Poem Generator
async def poem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (
        "Buatkan puisi cinta pendek, tulus, puitis, dan menyentuh hati untuk kekasih. "
        "Tambahkan emosi, rindu, dan cinta dalam kata-kata yang indah. Jangan beri nomor, hanya satu paragraf penuh perasaan."
    )
    try:
        response = await model.generate_content_async(prompt)
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("🥺 puisina kabobolan... coba deui engké")

# Countdown
async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_date = datetime(2025, 6, 14)  # Ganti sesuai tanggal spesial
    now = datetime.now()
    days_left = (target_date - now).days
    if days_left >= 0:
        await update.message.reply_text(f"📅 Tersisa {days_left} hari menuju hari jadian kita! 🥰")
    else:
        await update.message.reply_text("🎉 Hari jadian kita sudah lewat tapi cintaku ka anjeun mah langgeng 😘")

# Mood Tracker
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("📝 Kumaha mood anjeun ayeuna cantik? (senang, sedih, lelah, semangat...)")
    context.user_data["awaiting_mood"] = True

# Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if context.user_data.get("awaiting_mood"):
        user_moods[update.effective_user.id] = text
        context.user_data["awaiting_mood"] = False
        await update.message.reply_text(f"❤️ Mood kamu '{text}' disimpen. Nuhun udah curhat yaa 😚")
        return

    if text in ["manja", "serius", "humoris", "cuek", "penyayang", "genit"]:
        context.user_data["tipe"] = text
        await update.message.reply_text(f"✅ Karakter kabogoh di robih kana type: {text}")
        return

    if context.user_data.get("chat_bucin"):
        pesan = update.message.text
        tipe = context.user_data.get("tipe", "manja")
        prompt = (
            f"Kamu adalah pacar yang {tipe}, sedang ngobrol dengan kekasihmu melalui chat. "
            f"Balas pesan ini: '{pesan}' dengan gaya bucin yang romantis, manja, tulus, dan mengalir seperti percakapan nyata. "
            f"Jangan gunakan daftar, jangan beri nomor atau opsi. Balasanmu harus terdengar alami, emosional, dan penuh perasaan. "
            f"Gunakan gaya bahasa pacaran yang bikin pasangan meleleh, dan tambahkan emoji jika perlu agar terasa lebih hangat."
        )

        try:
            response = await model.generate_content_async(prompt)
            await update.message.reply_text(response.text.strip())
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("nuju rieut kela kedapnya 😢")

# Setup & Run
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("stopchat", stopchat))
    app.add_handler(CommandHandler("tipe", tipe))
    app.add_handler(CommandHandler("dailymsg", dailymsg))
    app.add_handler(CommandHandler("poem", poem))
    app.add_handler(CommandHandler("countdown", countdown))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
