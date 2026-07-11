"""
Dashboard Web Historiografi Digital Nusantara - Versi Final (Cloud-Ready)
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Historiografi Digital Nusantara", page_icon="📜", layout="wide")

def get_data_path():
    data_path = Path("data")
    sample_path = Path("sample_data")
    if data_path.exists() and any(data_path.iterdir()):
        return data_path
    elif sample_path.exists() and any(sample_path.iterdir()):
        return sample_path
    return None

@st.cache_resource
def get_db_connection():
    data_path = get_data_path()
    if not data_path: return None
    db_path = data_path / "nusantara_search.db"
    if not db_path.exists(): return None
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_ner_data():
    data_path = get_data_path()
    if not data_path: return None
    ner_path = data_path / "ner_results" / "entities_summary_pattern.json"
    if not ner_path.exists(): return None
    with open(ner_path, 'r', encoding='utf-8') as f: return json.load(f)

@st.cache_data
def load_topic_data():
    data_path = get_data_path()
    if not data_path: return None
    topic_path = data_path / "topic_results" / "topics_summary.json"
    if not topic_path.exists(): return None
    with open(topic_path, 'r', encoding='utf-8') as f: return json.load(f)

st.sidebar.title("📜 Historiografi Digital")
data_path = get_data_path()
if data_path:
    mode_label = "🖥️ Mode Lokal" if str(data_path) == "data" else "☁️ Mode Cloud (Data Asli Subset)"
    st.sidebar.info(f"**{mode_label}**\n\nData: `{data_path}`")
else:
    st.sidebar.error("⚠️ Data tidak ditemukan!")

page = st.sidebar.radio("Menu:", ("🏠 Beranda", " Pencarian", "🏷️ Statistik NER", "📚 Topik", "🕸️ Jaringan"))

if page == "🏠 Beranda":
    st.title("🏠 Historiografi Digital Nusantara")
    st.markdown("Dashboard analisis digital untuk naskah sejarah Nusantara.")
    ner_data = load_ner_data()
    if ner_data:
        stats = ner_data.get('statistics', {})
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Naskah", stats.get('total_files_processed', 0))
        col2.metric("Tokoh Unik", stats.get('unique_persons', 0))
        col3.metric("Tempat Unik", stats.get('unique_locations', 0))
        col4.metric("Tanggal Unik", stats.get('unique_dates', 0))
        st.success(f"✅ Dashboard aktif dalam **{mode_label}**")
    else:
        st.warning("⚠️ Data NER tidak ditemukan.")

elif page == "🔍 Pencarian":
    st.title("🔍 Pencarian Naskah")
    conn = get_db_connection()
    if conn:
        query = st.text_input("Kata kunci:", placeholder="Contoh: Sultan, Batavia, 1628")
        if st.button("Cari"):
            if query:
                try:
                    sql = '''SELECT filename, content as snippet FROM naskah_fts WHERE naskah_fts MATCH ? LIMIT ?'''
                    df = pd.read_sql_query(sql, conn, params=(query, 20))
                    if df.empty:
                        st.info("Tidak ada hasil yang cocok.")
                    else:
                        st.success(f"✅ Ditemukan **{len(df)}** hasil")
                        for _, row in df.iterrows():
                            st.markdown(f"** {row['filename']}**")
                            st.markdown(row['snippet'])
                            st.divider()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Database tidak ditemukan.")

elif page == "🏷️ Statistik NER":
    st.title("️ Statistik Entitas")
    ner_data = load_ner_data()
    if ner_data:
        top_entities = ner_data.get('top_entities', {})
        st.subheader("👤 Top 20 Tokoh")
        persons = top_entities.get('persons', [])
        if persons:
            fig1 = px.bar(pd.DataFrame(persons[:20], columns=['Nama', 'Frekuensi']), x='Frekuensi', y='Nama', orientation='h')
            st.plotly_chart(fig1, use_container_width=True)
        st.divider()
        st.subheader(" Top 20 Tempat")
        locations = top_entities.get('locations', [])
        if locations:
            fig2 = px.bar(pd.DataFrame(locations[:20], columns=['Nama', 'Frekuensi']), x='Frekuensi', y='Nama', orientation='h')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("️ Data NER tidak ditemukan.")

elif page == "📚 Topik":
    st.title("📚 Topik Naskah")
    topic_data = load_topic_data()
    if topic_data:
        for i, topic in enumerate(topic_data, 1):
            st.subheader(f"📌 {topic.get('name', f'Topik {i}')}")
            words = topic.get('top_words', [])
            if words: st.write("**Kata kunci:** " + ", ".join(words[:10]))
            st.divider()
    else:
        st.warning("⚠️ Data topik tidak ditemukan.")

elif page == "🕸️ Jaringan":
    st.title("🕸️ Jaringan Tokoh & Tempat")
    html_path = Path("reports/figures/network_nusantara.html") if Path("reports/figures/network_nusantara.html").exists() else Path("sample_reports/figures/network_nusantara.html")
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f: html_string = f.read()
        components.html(html_string, height=800, scrolling=True)
    else:
        st.warning("⚠️ File jaringan tidak ditemukan.")
