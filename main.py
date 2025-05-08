import json
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random
import nest_asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path untuk menyimpan data user
USER_DATA_FILE = "user_data.json"

# Fungsi untuk memuat data dari file JSON
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

# Fungsi untuk menyimpan data ke file JSON
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=4)

# Mendapatkan data user (atau buat baru jika belum ada)
def get_user_data(user_id):
    user_data = load_user_data()
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "nama_panggilan": "",
            "tipe_chat": "manja",  # default tipe chat
            "mood": "baik",  # default mood
            "bahasa": "id"  # default bahasa adalah Bahasa Indonesia
        }
        save_user_data(user_data)
    return user_data[str(user_id)]

# Simpan nama panggilan user
def save_nama_panggilan(user_id, nama_panggilan):
    user_data = load_user_data()
    user_data[str(user_id)]["nama_panggilan"] = nama_panggilan
    save_user_data(user_data)

# Simpan tipe chat user
def save_tipe_chat(user_id, tipe_chat):
    user_data = load_user_data()
    user_data[str(user_id)]["tipe_chat"] = tipe_chat
    save_user_data(user_data)

# Simpan mood user
def save_mood(user_id, mood):
    user_data = load_user_data()
    user_data[str(user_id)]["mood"] = mood
    save_user_data(user_data)

# Simpan bahasa user
def save_bahasa(user_id, bahasa):
    user_data = load_user_data()
    user_data[str(user_id)]["bahasa"] = bahasa
    save_user_data(user_data)

# Fungsi untuk memilih bahasa
def get_bahasa(user_id):
    user_data = get_user_data(user_id)
    return user_data["bahasa"]

# Handler start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Aku BucinBot 💘\nKetik /help untuk melihat daftar perintah.")

# Handler /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
    Berikut adalah beberapa perintah yang bisa kamu gunakan:
    /start - Mulai obrolan
    /help - Menampilkan daftar perintah
    /chatbucin - Ngobrol dengan AI pacar
    /stopchat - Menghentikan mode pacar bucin
    /setnama - Menyetting nama panggilanmu
    /settipechat - Menyetting tipe chat (manja, serius, humoris, dll)
    /setmood - Menyetting mood (baik, buruk, senang, dsb)
    /setbahasa - Menyetting bahasa yang digunakan (id untuk Bahasa Indonesia, su untuk Bahasa Sunda)
    """)

# Handler untuk set bahasa
async def setbahasa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pilih bahasa yang digunakan: id (Bahasa Indonesia) atau su (Bahasa Sunda).")
    
    context.user_data["awaiting_bahasa"] = True

# Handler untuk menerima bahasa
async def handle_bahasa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_bahasa"):
        bahasa = update.message.text.lower()
        if bahasa not in ["id", "su"]:
            await update.message.reply_text("Bahasa yang kamu pilih tidak tersedia. Pilih antara: id (Bahasa Indonesia) atau su (Bahasa Sunda).")
        else:
            user_id = update.message.from_user.id
            save_bahasa(user_id, bahasa)
            context.user_data["awaiting_bahasa"] = False
            await update.message.reply_text(f"Bahasa yang kamu pilih sekarang adalah {bahasa}.")

# Handler untuk chat bucin
async def chatbucin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    
    # Mengambil tipe chat dan mood user
    tipe_chat = user_data["tipe_chat"]
    mood = user_data["mood"]
    bahasa = get_bahasa(user_id)
    
    # Respons sesuai dengan bahasa
    if bahasa == "id":
        if mood == "baik":
            response = "Aku senang banget bisa ngobrol sama kamu! 💕 Apa kabar?"
        elif mood == "buruk":
            response = "Aku bisa bantu buat kamu merasa lebih baik, gimana kalau ngobrolin sesuatu yang menyenangkan?"
        else:
            response = "Apa kabar? Aku siap menemanimu 😊"
        
        if tipe_chat == "manja":
            response += " 💖 Aku rindu banget sama kamu~"
        elif tipe_chat == "serius":
            response += " Kita harus punya rencana untuk masa depan."
        elif tipe_chat == "humoris":
            response += " Hahaha, aku punya banyak cerita lucu untuk kamu! 😂"
        elif tipe_chat == "cuek tapi perhatian":
            response += " Aku cuma pengen tahu kamu baik-baik aja, nggak lebih."
        elif tipe_chat == "penyayang":
            response += " Aku selalu sayang sama kamu, jangan ragu buat cerita yaa~"
    
    elif bahasa == "su":
        if mood == "baik":
            response = "Senang pisan bisa ngobrol sareng anjeun! 💕 Kumaha kabarna?"
        elif mood == "buruk":
            response = "Kuring tiasa ngabantosan supados anjeun ngarasa langkung saé, kumaha upami ngobrolkeun hal anu pikabungaheun?"
        else:
            response = "Kumaha kabarna? Kuring siap ngiringan anjeun 😊"
        
        if tipe_chat == "manja":
            response += " 💖 Kuring sono pisan ka anjeun~"
        elif tipe_chat == "serius":
            response += " Urang kedah gaduh rencana pikeun masa depan."
        elif tipe_chat == "humoris":
            response += " Hahaha, kuring gaduh seueur carita lucu pikeun anjeun! 😂"
        elif tipe_chat == "cuek tapi perhatian":
            response += " Kuring ngan ukur hoyong terang yén anjeun saé, henteu langkung."
        elif tipe_chat == "penyayang":
            response += " Kuring sok bogoh ka anjeun, ulah ragu pikeun carita yaa~"
    
    await update.message.reply_text(response)

# Main bot
async def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("chatbucin", chatbucin))
    app.add_handler(CommandHandler("setbahasa", setbahasa))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bahasa))

    print("Bot berjalan...")

    await app.run_polling()

if __name__ == "__main__":
  import nest_asyncio
import asyncio

# Terapkan nest_asyncio untuk menghindari error event loop
nest_asyncio.apply()

# Jika kamu menggunakan loop langsung
loop = asyncio.get_event_loop()

# Menjalankan aplikasi tanpa menutup loop
loop.run_until_complete(main())

