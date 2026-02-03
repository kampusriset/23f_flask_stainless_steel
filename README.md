# BIMANTARA STAINLESS STEEL - Aplikasi E-Commerce

Aplikasi web e-commerce untuk penjualan produk stainless steel seperti dandang (panci) menggunakan framework Flask.

# Perkenalan Tim
- Fandy Dwi Putra ( 2313010522 )
- Ilyas Nur Rokhim ( 2313010512 )

## Fitur Utama

- **Manajemen Produk**: Tambah, edit, dan hapus produk stainless steel
- **Sistem User**: Registrasi, login, dan manajemen profil pengguna
- **Keranjang Belanja**: Tambah produk ke keranjang dan checkout
- **Sistem Pesanan**: Pembuatan pesanan, pembayaran, dan invoice
- **Dashboard Admin**: Manajemen pesanan, laporan penjualan, dan statistik
- **Laporan PDF**: Download laporan penjualan dalam format PDF

## Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Authentication**: bcrypt untuk hashing password
- **PDF Generation**: FPDF untuk laporan
- **Frontend**: HTML, CSS, JavaScript (templates Jinja2)

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- MySQL Server
- pip (Python package manager)

## Instalasi dan Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd 23f_flask_stainless_steel
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database MySQL

1. Pastikan MySQL Server sudah terinstall dan berjalan
2. Buat database baru:

```sql
CREATE DATABASE bimantara_db;
```

### 4. Konfigurasi Environment Variables

Buat file `.env` di root directory atau set environment variables:

```bash
# Database Configuration
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_mysql_password
export DB_NAME=bimantara_db

# Flask Configuration
export SECRET_KEY=your_secret_key_here
export FLASK_SECRET=your_flask_secret_here
export FLASK_ENV=development
```

**Catatan**: Ganti `your_mysql_password`, `your_secret_key_here`, dan `your_flask_secret_here` dengan nilai yang sesuai.

### 5. Jalankan Aplikasi

```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## Akun Default

Setelah menjalankan aplikasi, akun admin default akan dibuat otomatis:

- **Email**: admin@bimantara.com
- **Password**: admin123

## Struktur Database

Aplikasi ini menggunakan 3 tabel utama:

1. **products**: Menyimpan data produk (nama, slug, harga)
2. **users**: Menyimpan data pengguna (nama, email, password, role)
3. **orders**: Menyimpan data pesanan (kode order, produk, jumlah, pelanggan, dll)

Database akan dibuat otomatis saat aplikasi pertama kali dijalankan.

## Cara Penggunaan

### Untuk Pembeli:
1. **Registrasi/Login**: Daftar akun baru atau login dengan akun existing
2. **Lihat Produk**: Kunjungi halaman produk untuk melihat katalog
3. **Tambah ke Keranjang**: Klik tombol "Tambah ke Keranjang" pada produk
4. **Checkout**: Isi form checkout dengan data pengiriman
5. **Pembayaran**: Pilih metode pembayaran
6. **Invoice**: Lihat detail pesanan dan invoice

### Untuk Admin:
1. **Login**: Gunakan akun admin untuk masuk ke dashboard
2. **Manajemen Produk**: Tambah, edit, atau hapus produk
3. **Manajemen Pesanan**: Update status pesanan (pending, processing, completed, cancelled)
4. **Manajemen User**: Update role pengguna
5. **Laporan**: Lihat statistik penjualan dan download laporan PDF

## API Endpoints Utama

- `GET /` - Halaman utama
- `GET/POST /login` - Login pengguna
- `GET/POST /register` - Registrasi pengguna
- `GET /product` - Halaman produk
- `GET /checkout/<produk>` - Checkout produk individual
- `GET /dashboard` - Dashboard admin (hanya admin)
- `GET /profile` - Profil pengguna
- Dan lainnya...

## Troubleshooting

### Error Koneksi Database
- Pastikan MySQL Server berjalan
- Periksa konfigurasi environment variables
- Pastikan database `bimantara_db` sudah dibuat

### Error Import Module
- Pastikan semua dependencies sudah terinstall: `pip install -r requirements.txt`
- Gunakan virtual environment jika diperlukan

### Port Sudah Digunakan
- Ubah port di `app.py`: `app.run(debug=True, port=5001)`

## Kontribusi

1. Fork repository
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request


## Kontak

Untuk pertanyaan atau dukungan, silakan hubungi tim development.
