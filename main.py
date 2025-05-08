import google.generativeai as genai
import os
from telegram import Update
from telegram.ext import ContextTypes

# Konfigurasi API Gemini dari environment variable
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

async def handle_love_letter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_love_letter"):
        topic = update.message.text
        context.user_data["awaiting_love_letter"] = False
        await update.message.reply_text("Menulis surat cinta dengan AI... 💌")

        # Prompt AI
        prompt = f"Tolong buatkan surat cinta romantis dengan tema '{topic}' dalam bahasa Indonesia."
        try:
            response = await model.generate_content_async(prompt)
            letter = response.text.strip()
            await update.message.reply_text(letter)
        except Exception as e:
            await update.message.reply_text("Maaf, AI gagal membuat surat cinta. Coba lagi nanti ya! 😢")
