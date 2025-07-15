# Gunakan gambar dasar Python dalam versi 3.8
FROM python:3.8-slim-buster

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
COPY requirements.txt .

# Instal paket yang ditentukan dalam requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari direktori lokal saat ini (techtrends) ke direktori kerja di kontainer (/app)
COPY . .

# Pastikan database diinisialisasi dengan postingan yang telah ditentukan sebelumnya
RUN python init_db.py

# Paparkan port aplikasi 3111
EXPOSE 3111

# Aplikasi harus dijalankan pada awal kontainer
CMD ["python", "app.py"]