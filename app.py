"""
Dashboard Web Historiografi Digital Nusantara - Versi Final (Fixed)
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
import streamlit.components.v1 as components

# Konfigurasi Halaman
st.set_page_config(
    page_title="Historiografi Digital Nusantara",
    page_icon="📜",
    layout="wide"
)

# --- FUNGSI BANTU ---

@st.cache_resource
def get_db_connection():
    """Koneksi ke database SQLite."""
    db_path = Path("data/nusantara_search.db")
    if not db_path.exists():
        return None
    # FIX 1: Tambahkan check_same_thread=False agar tidak error di Streamlit
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_ner_data():
    """Memuat data JSON hasil NER."""
    ner_path = Path("data/ner_results/entities_summary_pattern.json")
    if not ner_path.exists():
        return None
    with open(ner_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def load_topic_data():
    """Memuat data JSON hasil Topic Modeling."""
    topic_path = Path("data/topic_results/topics_summary.json")
    if not topic_path.exists():
        return None
    with open(topic_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- SIDEBAR ---

st.sidebar.title("📜 Historiografi Digital")
page = st.sidebar.radio(
    "Menu:",
    ("🏠 Beranda", "🔍 Pencarian", "🏷️ Statistik NER", "📚 Topik", "🕸️ Jaringan")
)

# --- HALAMAN 1: BERANDA ---
if page == "🏠 Beranda":
    st.title("🏠 Historiografi Digital Nusantara")
    st.markdown("Dashboard analisis digital untuk naskah sejarah Nusantara.")
    
    ner_data = load_ner_data()
    if ner_data:
        stats = ner_data['statistics']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Naskah", stats.get('total_files_processed', 1074))
        col2.metric("Tokoh Unik", stats.get('unique_persons', 0))
        col3.metric("Tempat Unik", stats.get('unique_locations', 0))
        col4.metric("Tanggal", stats.get('unique_dates', 0))
# -----------------------------------------------------
# --- HALAMAN 2: PENCARIAN (WITH DEBUG) ---
elif page == "🔍 Pencarian":
    st.title("🔍 Pencarian Naskah")
    
    conn = get_db_connection()
    if conn:
        query = st.text_input("Kata kunci:")
        
        if st.button("Cari"):
            if query:
                try:
                    # DEBUG: Tampilkan query dan parameter
                    st.write(f"**Debug Info:**")
                    st.write(f"- Query: `{query}`")
                    st.write(f"- Parameter: `{(query, 10)}`")
                    
                    sql = '''
                        SELECT filename, snippet(naskah_fts, 1, '<b>', '</b>', '...', 64) as snippet
                        FROM naskah_fts
                        WHERE naskah_fts MATCH ?
                        ORDER BY rank
                        LIMIT ?
                    '''
                    
                    # DEBUG: Tampilkan SQL
                    st.write(f"- SQL: `{sql}`")
                    
                    df = pd.read_sql_query(sql, conn, params=(query, 10))
                    
                    # DEBUG: Tampilkan hasil DataFrame
                    st.write(f"- Hasil query: {len(df)} baris")
                    if not df.empty:
                        st.write(df.head())
                    
                    if df.empty:
                        st.info("Tidak ada hasil.")
                    else:
                        st.success(f"Ditemukan {len(df)} hasil")
                        for _, row in df.iterrows():
                            st.markdown(f"**{row['filename']}**")
                            st.markdown(row['snippet'], unsafe_allow_html=True)
                            st.divider()
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
# --------------------------------------------------
# --- HALAMAN 3: STATISTIK NER ---
elif page == "🏷️ Statistik NER":
    st.title("🏷️ Statistik Entitas")
    
    ner_data = load_ner_data()
    if ner_data:
        # Top Tokoh
        st.subheader("👤 Top 20 Tokoh")
        top_persons = pd.DataFrame(ner_data['top_entities']['persons'][:20], columns=['Nama', 'Frekuensi'])
        fig1 = px.bar(top_persons, x='Frekuensi', y='Nama', orientation='h')
        st.plotly_chart(fig1, use_container_width=True)
        
        st.divider()
        
        # Top Tempat
        st.subheader("📍 Top 20 Tempat")
        top_locs = pd.DataFrame(ner_data['top_entities']['locations'][:20], columns=['Nama', 'Frekuensi'])
        fig2 = px.bar(top_locs, x='Frekuensi', y='Nama', orientation='h')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.divider()
        
        # Top Organisasi
        st.subheader("🏢 Top 20 Organisasi")
        top_orgs = pd.DataFrame(ner_data['top_entities']['organizations'][:20], columns=['Nama', 'Frekuensi'])
        fig3 = px.bar(top_orgs, x='Frekuensi', y='Nama', orientation='h')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Data NER tidak ditemukan.")
# -----------------------------------------------
# --- HALAMAN 4: TOPIK ---
elif page == "📚 Topik":
    st.title("📚 Topik Naskah")
    
    topic_data = load_topic_data()
    if topic_data:
        for topic in topic_data:
            st.subheader(f"📌 {topic['name']}")
            
            # FIX 2: Gunakan key 'top_words' (sudah berupa list, tidak perlu di-split lagi)
            words = topic.get('top_words', [])
            
            if words:
                st.write("**Kata kunci:** " + ", ".join(words[:10]))
            else:
                st.write("Tidak ada kata kunci yang tersedia.")
            st.divider()
    else:
        st.warning("Data topik tidak ditemukan.")

# --- HALAMAN 5: JARINGAN ---
elif page == "🕸️ Jaringan":
    st.title("🕸️ Jaringan Tokoh & Tempat")
    
    html_path = Path("reports/figures/network_nusantara.html")
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            html_string = f.read()
        components.html(html_string, height=800, scrolling=True)
    else:
        st.error("File jaringan tidak ditemukan.")
