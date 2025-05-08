# bot.py
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

# Inisialisasi bot dan Dispatcher
API_TOKEN = os.getenv("API_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Konfigurasi OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# ===== COMMAND /start =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Chat AI", callback_data="menu_chat")
    builder.button(text="🧮 Math", callback_data="menu_math")
    builder.button(text="🌐 Translate", callback_data="menu_translate")
    builder.button(text="🩺 Kesehatan", callback_data="menu_health")
    builder.button(text="📿 Hijriyah", callback_data="menu_hijri")
    builder.button(text="📘 Fiqih Wanita", callback_data="menu_fiqih")
    await message.answer("Halo! Pilih fitur yang ingin kamu gunakan:", reply_markup=builder.as_markup())

# ===== Callback Menu =====
@dp.callback_query(F.data == "menu_chat")
async def cb_chat(callback: types.CallbackQuery):
    await callback.message.answer("Ketik pertanyaanmu ke AI:")
    await callback.answer()

@dp.callback_query(F.data == "menu_math")
async def cb_math(callback: types.CallbackQuery):
    await callback.message.answer("Ketik soal matematika yang ingin diselesaikan:")
    await callback.answer()

@dp.callback_query(F.data == "menu_translate")
async def cb_translate(callback: types.CallbackQuery):
    langs = ["English", "Indonesian", "Sundanese", "Arabic", "Japanese"]
    builder = InlineKeyboardBuilder()
    for lang in langs:
        builder.button(text=lang, callback_data=f"translate_to_{lang.lower()}")
    await callback.message.answer("Pilih bahasa tujuan:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "menu_health")
async def cb_health(callback: types.CallbackQuery):
    text = (
        "🩺 *Fitur Kesehatan*:\n"
        "- Ketik berat dan tinggi badanmu (misal: 60 170) untuk hitung BMI.\n"
        "- Ketik /tips untuk tips kesehatan harian."
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "menu_hijri")
async def cb_hijri(callback: types.CallbackQuery):
    today = datetime.date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()
    await callback.message.answer(f"📅 Tanggal Hijriyah: {hijri.day}-{hijri.month}-{hijri.year}H")
    await callback.answer()

@dp.callback_query(F.data == "menu_fiqih")
async def cb_fiqih(callback: types.CallbackQuery):
    await callback.message.answer("📘 Topik Fiqih Wanita:\n- Haid & Nifas\n- Aurat\n- Puasa dan Shalat\n- Kewanitaan lainnya")
    await callback.answer()

# ===== Fitur Chat AI =====
@dp.message(F.text)
async def handle_text(message: types.Message):
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        await message.reply(reply)
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {str(e)}")

# ===== Fitur Tips Kesehatan =====
@dp.message(Command("tips"))
async def tips_health(message: types.Message):
    tips = [
        "Minum air putih cukup setiap hari",
        "Olahraga 3x seminggu",
        "Tidur minimal 7 jam",
        "Kurangi gula dan garam",
        "Kelola stres dengan baik"
    ]
    idx = datetime.datetime.now().day % len(tips)
    await message.reply(f"💡 Tips: {tips[idx]}")

# ===== Jalankan Bot =====
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
