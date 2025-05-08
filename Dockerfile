# Gunakan base image Python
FROM python:3.10-slim

# Tentukan direktori kerja dalam container
WORKDIR /app

# Salin requirements dan install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file ke dalam container
COPY . .

# Jalankan aplikasi
CMD ["python", "bot.py"]
