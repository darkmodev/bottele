import os
import logging
import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from hijri_converter import convert
import openai
import requests

# Logging
logging.basicConfig(level=logging.INFO)

# Inisialisasi bot
API_TOKEN = os.getenv("API_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # OpenRouter API key
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Konfigurasi OpenRouter API
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# ===== FITUR CHAT AI =====
@dp.message(Command("chat"))
async def ai_chat(message: types.Message):
    await message.reply("Kirimkan pertanyaanmu...")

# ===== FITUR MATEMATIKA =====
@dp.message(Command("math"))
async def handle_math(message: types.Message):
    await message.reply("Ketik soal matematika yang ingin kamu selesaikan.")

@dp.message(F.text.regexp(r"^\d+[\s\+\-\*/\d]*$"))
async def solve_math(message: types.Message):
    try:
        result = eval(message.text)
        await message.reply(f"Hasil: {result}")
    except Exception:
        await message.reply("Terjadi kesalahan dalam perhitungan.")

# ===== FITUR TRANSLATE =====
@dp.message(Command("translate"))
async def handle_translate(message: types.Message):
    langs = ["English", "Indonesian", "Sundanese", "Arabic", "Japanese"]
    builder = InlineKeyboardBuilder()
    for lang in langs:
        builder.button(text=lang, callback_data=f"translate_to_{lang.lower()}")
    await message.reply("Pilih bahasa tujuan:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("translate_to_"))
async def translate_to(callback: types.CallbackQuery):
    lang = callback.data.split("_to_")[1]
    await callback.message.reply(f"Ketik teks yang ingin diterjemahkan ke {lang.capitalize()}.")

# ===== FITUR KESEHATAN =====
@dp.message(Command("health"))
async def handle_health(message: types.Message):
    text = (
        "\U0001FA7A *Fitur Kesehatan*:\n"
        "- Ketik berat dan tinggi badanmu (misal: 60 170) untuk hitung BMI.\n"
        "- Ketik /tips untuk tips kesehatan harian."
    )
    await message.reply(text, parse_mode="Markdown")

@dp.message(Command("tips"))
async def health_tips(message: types.Message):
    tips = [
        "Minum air putih cukup setiap hari",
        "Olahraga 3x seminggu",
        "Tidur minimal 7 jam",
        "Kurangi gula dan garam",
        "Kelola stres dengan baik"
    ]
    await message.reply("\uD83D\uDCA1 Tips: " + tips[datetime.datetime.now().day % len(tips)])

# ===== FITUR ISLAM =====
@dp.message(Command("hijri"))
async def hijri_calendar(message: types.Message):
    today = datetime.date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()
    await message.reply(f"\uD83D\uDCC5 Tanggal Hijriyah: {hijri.day}-{hijri.month}-{hijri.year}H")

@dp.message(Command("fiqih"))
async def fiqih_wanita(message: types.Message):
    await message.reply("\ud83d\udcd8 Topik Fiqih Wanita:\n- Haid & Nifas\n- Aurat\n- Puasa dan Shalat\n- Kewanitaan lainnya")

# ===== FITUR AI DENGAN OPENROUTER =====
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_chat(message: types.Message):
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        chat_response = response["choices"][0]["message"]["content"]
        await message.reply(chat_response)
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {str(e)}")

# ===== START BOT =====
@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Chat AI", callback_data="chat")
    builder.button(text="Matematika", callback_data="math")
    builder.button(text="Translate", callback_data="translate")
    builder.button(text="Kesehatan", callback_data="health")
    await message.reply("Halo! Saya bot AI dengan fitur Chat, Translate, Matematika, Kesehatan, dan Edukasi Islam.", reply_markup=builder.as_markup())

if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
