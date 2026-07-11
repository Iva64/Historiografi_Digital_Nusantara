#!/bin/bash

# ==========================================
# PIPELINE CRON JOB - Versi Tahan Banting
# Untuk dijalankan otomatis oleh cron
# ==========================================

# --- KONFIGURASI PATH (WAJIB ABSOLUT) ---
PROJECT_DIR="/home/sena/python/Historiografi_Digital_Nusantara"
MYENV_PATH="/home/sena/python/myenv/bin/activate"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/pipeline_$(date +\%Y\%m\%d_\%H\%M\%S).log"

# --- PASTIKAN FOLDER LOG ADA ---
mkdir -p "$LOG_DIR"

# --- LOG HEADER ---
echo "==========================================" >> "$LOG_FILE"
echo "🚀 PIPELINE DIMULAI: $(date)" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

# --- PINDAH KE FOLDER PROYEK ---
cd "$PROJECT_DIR" || exit 1

# --- AKTIVASI VIRTUAL ENVIRONMENT ---
if [ -f "$MYENV_PATH" ]; then
    source "$MYENV_PATH"
    echo "✅ Virtual environment diaktifkan" >> "$LOG_FILE"
else
    echo "❌ Virtual environment tidak ditemukan: $MYENV_PATH" >> "$LOG_FILE"
    exit 1
fi

# --- LANGKAH 1: PREPROCESSING ---
echo "" >> "$LOG_FILE"
echo "[1/5] Preprocessing..." >> "$LOG_FILE"
python3 -m src.preprocessing.reader >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ GAGAL: Preprocessing" >> "$LOG_FILE"
    exit 1
fi
echo "✅ Preprocessing selesai" >> "$LOG_FILE"

# --- LANGKAH 2: NER ---
echo "" >> "$LOG_FILE"
echo "[2/5] NER..." >> "$LOG_FILE"
python3 -m src.nlp.extractor_fallback >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ GAGAL: NER" >> "$LOG_FILE"
    exit 1
fi
echo "✅ NER selesai" >> "$LOG_FILE"

# --- LANGKAH 3: TOPIC MODELING ---
echo "" >> "$LOG_FILE"
echo "[3/5] Topic Modeling..." >> "$LOG_FILE"
python3 -m src.nlp.topic_modeling >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ GAGAL: Topic Modeling" >> "$LOG_FILE"
    exit 1
fi
echo "✅ Topic Modeling selesai" >> "$LOG_FILE"

# --- LANGKAH 4: NETWORK GRAPH ---
echo "" >> "$LOG_FILE"
echo "[4/5] Network Graph..." >> "$LOG_FILE"
python3 -m src.visualization.network_graph >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ GAGAL: Network Graph" >> "$LOG_FILE"
    exit 1
fi
echo "✅ Network Graph selesai" >> "$LOG_FILE"

# --- LANGKAH 5: SEARCH ENGINE INDEX ---
echo "" >> "$LOG_FILE"
echo "[5/5] Re-index Database..." >> "$LOG_FILE"
python3 -m src.search_engine index >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ GAGAL: Search Engine Index" >> "$LOG_FILE"
    exit 1
fi
echo "✅ Indexing selesai" >> "$LOG_FILE"

# --- SELESAI ---
echo "" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"
echo "✅ SEMUA PROSES BERHASIL: $(date)" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

# --- BERSIHKAN LOG LAMA (Simpan 30 hari terakhir) ---
find "$LOG_DIR" -name "pipeline_*.log" -mtime +30 -delete

exit 0
