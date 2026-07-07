# Historiografi Digital Nusantara
**Platform Analisis & Katalogisasi Otomatis Dokumen Sejarah Aceh Abad Pertengahan**

## 📜 Tentang Proyek
Historiografi Digital Nusantara adalah sebuah platform kerja (workspace) yang dirancang untuk membaca, memproses, dan menganalisis kumpulan dokumen sejarah Aceh abad pertengahan (Naskah Jawi, Hikayat, Salasilah, Surat Sultan, dll). 

Mengingat volume dokumen yang sangat melimpah dan keterbatasan waktu untuk penyeliaan manual, proyek ini mengadopsi pendekatan **Digital Humanities** yang digerakkan oleh otomasi dan AI. Platform ini dibangun untuk mengubah tumpukan scan dokumen mentah menjadi database historis yang terstruktur, dapat ditelusuri, dan siap dianalisis.

## 🎯 Tujuan Utama
1. **Otomasi Transkripsi:** Mengubah scan dokumen Aksara Jawi/Melayu Klasik menjadi teks digital (OCR & Transliterasi).
2. **Ekstraksi Entitas Otomatis:** Mengidentifikasi tokoh, tempat, tahun (Hijriah/Masehi), dan peristiwa secara otomatis menggunakan NLP.
3. **Pemetaan Jaringan:** Membangun graf relasi antar-tokoh, silsilah, dan jaringan perdagangan/diplomasi Aceh.
4. **Efisiensi Riset:** Menyediakan antarmuka katalog digital sehingga peneliti hanya perlu menyelia (review) hasil, bukan mengerjakan dari nol.

## 📂 Struktur Direktori Singkat
- `01_Dokumen_Sumber/` : Gudang penyimpanan file mentah (PDF, JPG, TIFF) dan metadata dasar.
- `02_Analisis_Dokumen/` : Workspace hasil OCR, transliterasi, dan analisis kontekstual.
- `03_Katalog_Digital/` : Database (SQLite/CSV) untuk indeks tokoh, tempat, dan relasi dokumen.
- `04_Tools_Dan_Scripts/` : Script Python untuk OCR, NLP, dan visualisasi data.
- `05_Output_Dan_Publikasi/` : Draft paper, visualisasi timeline, dan materi publikasi.
- `06_Dokumentasi_Proyek/` : SOP, panduan tagging, dan log aktivitas.
- `07_Backup_Dan_Arsip/` : Sistem keamanan dan versioning data.
- `08_Kolaborasi/` : Ruang kerja untuk review dan catatan kolaborator.

## ⚙️ Alur Kerja (Workflow) Sistem
1. **Ingest:** Dokumen fisik dipindai dan dimasukkan ke `01_Dokumen_Sumber`.
2. **Process:** Script di `04_Tools_Dan_Scripts` menjalankan OCR (Khusus Aksara Jawi) dan transliterasi.
3. **Analyze:** AI/NLP mengekstrak Named Entities (Tokoh, Tempat, Peristiwa) dan menyimpannya ke `03_Katalog_Digital`.
4. **Review:** Peneliti (Anda) menyelia hasil ekstraksi di folder `02_Analisis_Dokumen`.
5. **Publish:** Data disintesis menjadi visualisasi dan laporan di `05_Output_Dan_Publikasi`.

## 🚀 Cara Memulai
1. Pastikan Python 3.9+ terinstal.
2. Install dependencies: `pip install -r requirements.txt` (akan dibuat di `04_Tools_Dan_Scripts`).
3. Mulai dengan menaruh sampel dokumen ke `01_Dokumen_Sumber/1.1_Naskah_Asal/Aceh_Sultanate/`.
4. Jalankan skrip inisialisasi database: `python 04_Tools_Dan_Scripts/4.3_Data_Management/import_documents.py`.

## 🤝 Peran & Kolaborasi
- **Principal Investigator (Anda):** Menentukan arah riset, menyelia (review) hasil AI, dan menulis sintesis historiografi.
- **System Architect & AI (Qwen):** Membangun pipeline, menjalankan script OCR/NLP, membersihkan data, dan membuat visualisasi.

---
*Dikelola sebagai bagian dari inisiatif pelestarian dan digitalisasi warisan intelektual Nusantara.*
