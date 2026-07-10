#!/bin/bash

# ==========================================
# PIPELINE HISTORIOGRAFI DIGITAL NUSANTARA
# Menjalankan semua proses secara otomatis
# ==========================================

# --- AKTIVASI VIRTUAL ENVIRONMENT ---
MYENV_PATH="/home/sena/python/myenv"

if [ -d "$MYENV_PATH" ]; then
    source "$MYENV_PATH/bin/activate"
    echo "✅ Virtual environment berhasil diaktifkan dari: $MYENV_PATH"
else
    echo "❌ Virtual environment tidak ditemukan di: $MYENV_PATH"
    echo "   Silakan periksa lokasi myenv Anda."
    exit 1
fi
echo ""

echo "=========================================="
echo "🚀 MEMULAI PIPELINE ANALISIS"
echo "=========================================="
echo ""

# Warna output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fungsi cek error
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ GAGAL pada: $1${NC}"
        echo "Pipeline dihentikan. Perbaiki error di atas."
        exit 1
    fi
}

# --- LANGKAH 1: PREPROCESSING ---
echo -e "${BLUE}[1/5] Preprocessing & Deteksi Duplikat...${NC}"
python3 -m src.preprocessing.reader
check_error "Preprocessing"
echo -e "${GREEN}✅ Preprocessing selesai${NC}"
echo ""

# --- LANGKAH 2: NER ---
echo -e "${BLUE}[2/5] Named Entity Recognition (NER)...${NC}"
python3 -m src.nlp.extractor_fallback
check_error "NER"
echo -e "${GREEN}✅ NER selesai${NC}"
echo ""

# --- LANGKAH 3: TOPIC MODELING ---
echo -e "${BLUE}[3/5] Topic Modeling (LDA)...${NC}"
python3 -m src.nlp.topic_modeling
check_error "Topic Modeling"
echo -e "${GREEN}✅ Topic Modeling selesai${NC}"
echo ""

# --- LANGKAH 4: NETWORK GRAPH ---
echo -e "${BLUE}[4/5] Visualisasi Jaringan...${NC}"
python3 -m src.visualization.network_graph
check_error "Network Graph"
echo -e "${GREEN}✅ Network Graph selesai${NC}"
echo ""

# --- LANGKAH 5: SEARCH ENGINE INDEX ---
echo -e "${BLUE}[5/5] Re-index Database Pencarian...${NC}"
python3 -m src.search_engine index
check_error "Search Engine Index"
echo -e "${GREEN}✅ Indexing selesai${NC}"
echo ""

# --- SELESAI ---
echo "=========================================="
echo -e "${GREEN}✅ SEMUA PROSES BERHASIL!${NC}"
echo "=========================================="
echo ""
echo "📊 Dashboard siap dijalankan:"
echo -e "${YELLOW}   streamlit run app.py${NC}"
echo ""
