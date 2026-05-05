# Arithmetic Coding Demo

Tugas Pertemuan 6 — Teori Informasi

## Cara Menjalankan

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Atau langsung:
   ```bash
   pip install streamlit pandas plotly
   ```

2. **Jalankan aplikasi:**
   ```bash
   streamlit run app.py
   ```

3. Browser akan otomatis terbuka di `http://localhost:8501`. Kalau tidak, buka manual.

## Fitur

- **Input validasi** — hanya huruf kecil dan spasi
- **Tabel probabilitas** — frekuensi, P(c), cumulative range (Fraction & decimal)
- **Visualisasi penyempitan interval** — chart log-scale lebar interval per step
- **Slider step-by-step** — geser untuk lihat penyempitan tiap langkah secara visual
- **Tabel lengkap encoding** — semua step dengan low, high, lebar
- **Hasil akhir** — interval [low, high) dan bilangan output (titik tengah)
- **Analisis entropi** — perbandingan H(X) × N teoretis vs −log₂(lebar) aktual
- **Verifikasi decoding** — decode bilangan output kembali ke string asli

## Catatan Teknis

Program ini menggunakan `fractions.Fraction` (bukan `float`) untuk presisi eksak.
Setelah ~15 karakter, `float` 64-bit kehilangan presisi dan hasil encoding tidak
unik lagi. `Fraction` menyimpan pembilang/penyebut sebagai bilangan bulat besar,
jadi presisi tetap eksak berapapun panjang inputnya.

## Struktur Kode

- **Algoritma inti** (atas file `app.py`):
  - `validate_input(s)` — validasi karakter
  - `build_model(s)` — bangun tabel frekuensi + cumulative range
  - `encode(s, ranges)` — arithmetic encoding utama
  - `decode(value, length, ranges)` — decode untuk verifikasi
  - `compute_entropy(freq, n)` — hitung H(X) Shannon

- **UI Streamlit** (bawah file): tampilan dengan section yang jelas
  untuk demo video.
