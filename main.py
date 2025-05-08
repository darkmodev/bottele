import logging
import datetime
import openai
from ummalqura.hijri_date import HijriDate
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from requests import get

# Set up logging
logging.basicConfig(level=logging.INFO)

# API key dan bot token (gunakan langsung dari environment Railway)
openai.api_key = 'sk-2eadbe1de11145ddb6cb75b4e00987cc'
API_TOKEN = 'YOUR_BOT_TOKEN'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Helper function untuk request jadwal adzan
def get_adzan_times(lat, lon):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
    response = get(url).json()
    if response['code'] == 200:
        return response['data']['timings']
    return None

# /start command - Inline menu
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🕌 Edukasi Islam", callback_data="menu_islam"))
    markup.add(InlineKeyboardButton("🗓️ Kalender Hijriyah", callback_data="menu_hijri"))
    markup.add(InlineKeyboardButton("📚 Matematika", callback_data="menu_math"))
    markup.add(InlineKeyboardButton("🌐 Translate", callback_data="menu_translate"))
    await message.reply("Selamat datang! Pilih menu berikut:", reply_markup=markup)

# Handler untuk fitur Edukasi Islam
@dp.message_handler(commands=['islam'])
async def handle_islam(message: types.Message):
    question = message.get_args()
    if not question:
        await message.reply("Ketik seperti ini:\n`/islam apa itu sholat tahajud?`\n`/islam penjelasan zakat fitrah`")
        return

    prompt = f"""
    Kamu adalah asisten edukasi Islam. Jelaskan secara sopan, akurat, dan tidak menyinggung. Jangan mengeluarkan fatwa. Jika perlu, sarankan bertanya ke ustadz/ulama langsung.

    Pertanyaan:
    {question}

    Jawabanmu harus informatif, ringkas, dan sesuai dengan sumber ajaran Islam (Al-Qur’an dan Hadits), namun tetap sopan dan inklusif.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    answer = response['choices'][0]['message']['content']
    await message.reply(answer)

# Handler untuk fitur Kalender Hijriyah
@dp.message_handler(commands=['hijri'])
async def handle_hijri(message: types.Message):
    today_gregorian = datetime.date.today()
    hijri = HijriDate.today()
    await message.reply(f"📅 *Tanggal Hijriyah Hari Ini:* {hijri.strftime('%d %B %Y')} (H {hijri.year})\nGregorian: {today_gregorian.strftime('%d-%m-%Y')}")

@dp.message_handler(commands=['hijri_convert'])
async def convert_gregorian_to_hijri(message: types.Message):
    date_input = message.get_args().strip()
    if not date_input:
        await message.reply("Ketik tanggal Gregorian dalam format DD-MM-YYYY. Contoh: `/hijri_convert 09-05-2025`")
        return
    
    try:
        day, month, year = map(int, date_input.split("-"))
        gregorian_date = datetime.date(year, month, day)
        hijri = HijriDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        await message.reply(f"Tanggal Gregorian: {gregorian_date.strftime('%d-%m-%Y')}\nTanggal Hijriyah: {hijri.strftime('%d %B %Y')} (H {hijri.year})")
    except ValueError:
        await message.reply("Format tanggal tidak valid. Gunakan format: DD-MM-YYYY")

# Handler untuk fitur Jadwal Adzan
@dp.message_handler(commands=['adzan'])
async def handle_adzan(message: types.Message):
    await message.reply("Silakan kirim lokasi kamu agar saya bisa menampilkan jadwal adzan.", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Kirim Lokasi", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))

@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    timings = get_adzan_times(lat, lon)
    if timings:
        jadwal = "\n".join([f"{k}: {v}" for k, v in timings.items() if k in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]])
        await message.reply(f"🕌 Jadwal Sholat Hari Ini:\n{jadwal}")
    else:
        await message.reply("Gagal mengambil jadwal. Coba lagi nanti.")

# Handler untuk fitur Al-Qur'an
@dp.message_handler(commands=['quran'])
async def handle_quran(message: types.Message):
    args = message.get_args().strip()
    if not args:
        await message.reply("Contoh: `/quran 2:255`", parse_mode="Markdown")
        return

    try:
        surah, ayat = args.split(":")
        url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayat}/editions/quran-simple,id.indonesian"
        data = get(url).json()['data']
        arabic = data[0]['text']
        translation = data[1]['text']
        await message.reply(f"📖 *Q.S {surah}:{ayat}*\n\n🕋 {arabic}\n\n🇮🇩 {translation}", parse_mode="Markdown")
    except:
        await message.reply("Format salah atau ayat tidak ditemukan. Gunakan format: `/quran 2:255`", parse_mode="Markdown")

# Handler untuk fitur Translate
@dp.message_handler(commands=['translate'])
async def handle_translate(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("Ketik: `/translate aku lapar` atau `/translate en id I am tired`", parse_mode="Markdown")
        return

    parts = args.split()
    if len(parts) >= 3 and parts[0] in ['id', 'en', 'fr', 'es', 'de']:  # kode bahasa tersedia
        src, dest = parts[0], parts[1]
        text = " ".join(parts[2:])
    else:
        text = args
        src = 'auto'  # Biarkan OpenAI mendeteksi bahasa secara otomatis
        dest = "id" if src != "id" else "en"

    prompt = f"Terjemahkan dari {src} ke {dest}:\n{text}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    translated = response['choices'][0]['message']['content']
    await message.reply(f"🌐 Terjemahan ({src} → {dest}):\n{translated}")

# Menjalankan bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
