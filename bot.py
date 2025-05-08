import os
import logging
import datetime
from aiogram import Bot, Dispatcher, types
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
openai.api_base = "https://openrouter.ai/api/v1"  # Base URL untuk OpenRouter API

# ===== FITUR CHAT AI =====
@dp.message(Command("chat"))
async def ai_chat(message: types.Message):
    await message.reply("Kirimkan pertanyaanmu...")

@dp.message()
async def handle_chat(message: types.Message):
    if message.text.startswith("/chat"):
        return

    try:
        # Menggunakan OpenRouter GPT-4 untuk mengirimkan pesan
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Menggunakan model GPT-4 yang valid
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text}
            ]
        )
        await message.reply(response['choices'][0]['message']['content'])
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {str(e)}")

# ===== FITUR MATEMATIKA =====
@dp.message(Command("math"))
async def handle_math(message: types.Message):
    await message.reply("Ketik soal matematika yang ingin kamu selesaikan.")

@dp.message(lambda message: message.text and message.text.isdigit())
async def solve_math(message: types.Message):
    try:
        result = eval(message.text)  # Eksekusi soal matematika
        await message.reply(f"Hasil: {result}")
    except Exception as e:
        await message.reply("Terjadi kesalahan dalam perhitungan.")

# ===== FITUR TRANSLATE =====
@dp.message(Command("translate"))
async def handle_translate(message: types.Message):
    langs = ["English", "Indonesian", "Sundanese", "Arabic", "Japanese"]
    builder = InlineKeyboardBuilder()
    for lang in langs:
        builder.button(text=lang, callback_data=f"translate_to_{lang.lower()}")
    await message.reply("Pilih bahasa tujuan:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("translate_to_"))
async def translate_to(callback: types.CallbackQuery):
    lang = callback.data.split("_to_")[1]
    await callback.message.reply(f"Ketik teks yang ingin diterjemahkan ke {lang.capitalize()}.")

# ===== FITUR KESEHATAN =====
@dp.message(Command("health"))
async def handle_health(message: types.Message):
    text = (
        "🩺 *Fitur Kesehatan*:\n"
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
    await message.reply("💡 Tips: " + requests.utils.quote(tips[datetime.datetime.now().day % len(tips)]))

# ===== FITUR ISLAM =====
@dp.message(Command("hijri"))
async def hijri_calendar(message: types.Message):
    today = datetime.date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()
    await message.reply(f"📅 Tanggal Hijriyah: {hijri.day}-{hijri.month}-{hijri.year}H")

@dp.message(Command("fiqih"))
async def fiqih_wanita(message: types.Message):
    await message.reply("📘 Topik Fiqih Wanita:\n- Haid & Nifas\n- Aurat\n- Puasa dan Shalat\n- Kewanitaan lainnya")

# ===== START BOT =====
@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Chat dengan AI", callback_data="chat")
    builder.button(text="Lihat Tips Kesehatan", callback_data="tips")
    builder.button(text="Lihat Jadwal Hijriyah", callback_data="hijri")

    await message.reply(
        "Halo! Saya bot AI dengan fitur Chat, Translate, Matematika, Kesehatan, dan Edukasi Islam. "
        "Pilih fitur yang ingin Anda gunakan:",
        reply_markup=builder.as_markup()
    )

# Menangani tombol inline
@dp.callback_query(lambda c: c.data == "chat")
async def chat_button(callback: types.CallbackQuery):
    await callback.message.answer("Kirimkan pertanyaanmu untuk memulai percakapan AI.")

@dp.callback_query(lambda c: c.data == "tips")
async def tips_button(callback: types.CallbackQuery):
    await callback.message.answer("Ketik /tips untuk mendapatkan tips kesehatan.")

@dp.callback_query(lambda c: c.data == "hijri")
async def hijri_button(callback: types.CallbackQuery):
    today = datetime.date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()
    await callback.message.answer(f"📅 Tanggal Hijriyah: {hijri.day}-{hijri.month}-{hijri.year}H")

if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
