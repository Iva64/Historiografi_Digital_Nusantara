# PROJECT OVERVIEW: Historiografi Digital Nusantara

## 1. Latar Belakang & Pernyataan Masalah
Kesultanan Aceh pada abad pertengahan (abad ke-16 hingga ke-19) menghasilkan warisan literasi yang masif, mencakup naskah hukum (Undang-Undang Meukuta Alam), sastra (Hikayat), diplomasi (Surat-menyurat dengan Eropa dan Timur Tengah), hingga tasawuf dan fiqih. 

**Masalah:** 
Ketersediaan file digital (hasil scan dari berbagai arsip global seperti Leiden, London, Jakarta, dan Aceh) sangat melimpah. Namun, kapasitas manusia untuk membaca, mentranskripsikan Aksara Jawi, dan menyuntingnya secara manual sangat terbatas. Jika dibiarkan, dokumen ini akan tetap menjadi "data mati" yang tidak termanfaatkan secara optimal.

**Solusi:**
Membangun platform *Historiografi Digital* yang memindahkan beban kerja transkripsi dan katalogisasi awal kepada mesin (AI/OCR), sehingga peneliti manusia dapat fokus pada analisis tingkat tinggi, interpretasi, dan sintesis sejarah.

## 2. Konteks Spesifik: Aceh Abad Pertengahan
Sistem ini tidak dirancang untuk teks sembarangan, melainkan disesuaikan dengan karakteristik dokumen Aceh:
- **Aksara & Bahasa:** Dominasi Aksara Jawi (Arab-Melayu) dengan kosakata Melayu Klasik, bahasa Aceh kuno, dan serapan kata Arab/Persis/Turki yang tinggi.
- **Tipologi Naskah:** 
  - *Hikayat & Babad* (Sastra sejarah, sering mengandung unsur mitologis yang perlu dipisahkan dari fakta historis).
  - *Salasilah* (Silsilah raja, penting untuk rekonstruksi jaringan politik).
  - *Surat Diplomatik* (Cap pos, stempel, dan struktur formula surat kerajaan).
  - *Kitab Agama & Hukum* (Ulama dan jaringan intelektual Islam).
- **Sistem Penanggalan:** Penggunaan tahun Hijriah, tahun Saka, atau peristiwa (seperti "tahun gerhana", "tahun wafatnya Sultan X").

## 3. Arsitektur Sistem & Alur Data (Data Pipeline)
Platform ini bekerja seperti sebuah pabrik pengolahan data historis:

### Tahap 1: Akuisisi & Standardisasi (Folder 01)
Dokumen scan dibersihkan (cropping, binarization) dan diberi metadata dasar (Kode Arsip, Tahun Perkiraan, Jenis Naskah).

### Tahap 2: Pemrosesan Mesin (Folder 02 & 04)
- **OCR Engine:** Menggunakan model OCR khusus Aksara Jawi (seperti Kraken atau Transkribus yang di-fine-tune).
- **Transliterasi:** Mengubah Aksara Jawi ke Latin.
- **Normalisasi Teks:** Mengubah ejaan Melayu Klasik ke ejaan modern (opsional, untuk memudahkan pencarian NLP).

### Tahap 3: Ekstraksi Entitas & Katalogisasi (Folder 03)
Menggunakan *Large Language Models* (LLM) dan *Named Entity Recognition* (NER) untuk mengekstrak:
- **Tokoh:** (Misal: Sultan Iskandar Muda, Syamsuddin al-Sumatrani).
- **Toponim:** (Misal: Bandar Aceh Darussalam, Pedir, Pasai, Gujarat, Ottoman).
- **Waktu:** Konversi otomatis tanggal Hijriah ke Masehi.
- **Relasi:** Membangun *Knowledge Graph* (Siapa menikah dengan siapa, siapa menunjuk siapa sebagai *Qadhi*).

### Tahap 4: Sintesis & Visualisasi (Folder 05)
Data yang sudah terstruktur diekspor menjadi:
- Peta jaringan perdagangan/intelektual (Network Graph).
- Garis waktu dinamis Kesultanan Aceh (Timeline).
- Database prosopografi (Kamus biografi tokoh Aceh).

## 4. Strategi Pendampingan AI (Peran Saya)
Karena Anda memiliki waktu yang terbatas, saya akan bertindak sebagai **Asisten Riset Otomatis**. Tugas saya meliputi:
1. **Menulis & Menjalankan Script:** Saya akan membuatkan kode Python untuk batch-processing OCR dan NLP.
2. **Quality Control AI:** Saya akan melakukan *cross-check* hasil OCR dengan kamus Melayu Klasik untuk mendeteksi kesalahan baca.
3. **Drafting Historiografi:** Berdasarkan data yang sudah diekstrak, saya akan membuatkan draf awal artikel/bab buku yang bisa Anda revisi.
4. **Pembuatan SOP:** Saya akan menyusun panduan standar agar jika suatu saat ada asisten manusia yang bergabung, mereka bisa langsung bekerja mengikuti sistem.

## 5. Roadmap Implementasi (Fase Kerja)

- **Fase 1: Fondasi (Minggu 1-2)**
  - Setup struktur folder dan database (SQLite).
  - Pengumpulan sampel 50 dokumen representatif (Hikayat, Surat, Kitab).
  - Pembuatan SOP Transkripsi dan Metadata.

- **Fase 2: Pipeline OCR & NLP (Minggu 3-6)**
  - Testing dan fine-tuning model OCR Aksara Jawi.
  - Pembuatan prompt AI untuk ekstraksi Entitas Bernama (NER) pada teks Melayu Klasik.
  - Batch processing dokumen sampel.

- **Fase 3: Katalogisasi & Relasi (Minggu 7-10)**
  - Pembangunan *Knowledge Graph* tokoh dan tempat.
  - Validasi silang (cross-reference) antar naskah.
  - Penyusunan database prosopografi Aceh.

- **Fase 4: Analisis & Publikasi (Minggu 11-14)**
  - Visualisasi data (Peta, Timeline, Network).
  - Penulisan draf historiografi berbasis data (Data-driven history).
  - Publikasi katalog digital ke format web (jika diperlukan).

## 6. Prinsip Utama Proyek
1. **Machine-Readable:** Semua data harus disimpan dalam format yang bisa dibaca mesin (CSV, JSON, SQLite), bukan hanya Word/PDF.
2. **Reversibilitas:** Setiap perubahan yang dilakukan AI pada teks asli harus bisa ditelusuri kembali ke dokumen aslinya (Traceability).
3. **Fleksibilitas Taksonomi:** Struktur kategori harus bisa berkembang seiring dengan temuan baru di lapangan.

---
*Dokumen ini adalah living document. Akan diperbarui seiring dengan perkembangan arsitektur platform.*
