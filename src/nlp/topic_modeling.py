"""
Topic Modeling untuk Naskah Nusantara menggunakan LDA.
Versi 2.0: Pembersihan HTML, Multi-bahasa Stopwords, dan Visualisasi Matplotlib.
"""

import os
import re
from pathlib import Path
from collections import Counter

import gensim
from gensim import corpora
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import matplotlib.pyplot as plt
import json


class NusantaraTopicModeler:
    """Kelas untuk melakukan Topic Modeling pada kumpulan naskah."""
    
    def __init__(self, num_topics: int = 10, passes: int = 15):
        self.num_topics = num_topics
        self.passes = passes
        
        # Inisialisasi Sastrawi
        factory_stopword = StopWordRemoverFactory()
        self.stopword_remover = factory_stopword.create_stop_word_remover()
        
        factory_stemmer = StemmerFactory()
        self.stemmer = factory_stemmer.create_stemmer()
        
        # Stopwords Custom untuk Naskah Kuno
        self.custom_stopwords = {
            'yang', 'dan', 'di', 'ke', 'dari', 'pada', 'dengan', 'untuk', 'dalam',
            'maka', 'tersebutlah', 'alkisah', 'syahdan', 'hatta', 'kalakian', 'bermula',
            'telah', 'akan', 'ia', 'itu', 'ini', 'jua', 'pun', 'lah', 'tah', 'nya',
            'hamba', 'beta', 'baginda', 'titah', 'kata', 'ujar', 'sabda', 'orang',
            'art', 'line', 'font', 'par', 'block', 'text', 'page', 'span', 'rem', 'fon', 'height'
        }
        
        # Stopwords Bahasa Asing (Belanda, Inggris, Jerman) yang sering muncul di dokumen kolonial
        self.foreign_stopwords = {
            # Belanda
            'de', 'het', 'een', 'van', 'en', 'in', 'is', 'dat', 'die', 'dit', 'voor', 'met',
            'bij', 'tot', 'over', 'door', 'aan', 'als', 'ook', 'niet', 'maar', 'om', 'uit',
            'vergadering', 'vennootschap', 'wordt', 'algemeene', 'part', 'aandeelhouders',
            'naamlooze', 'aandeelen', 'deze', 'dito', 'bijv', 'vgl', 'zal', 'licht', 'zou',
            'ons', 'hem', 'onder', 'meer', 'onze', 'zeer', 'kunnen', 'geb', 'welke', 'andere',
            'waar', 'hier', 'ind', 'des', 'ein', 'werden', 'das', 'dem',
            # Inggris
            'the', 'and', 'that', 'with', 'for', 'this', 'not', 'from', 'which', 'are', 'have',
            'has', 'was', 'were', 'been', 'will', 'can', 'may', 'shall', 'must', 'should',
            # Jerman
            'und', 'von', 'mit', 'des', 'ind', 'ein', 'werden', 'das', 'indi', 'dem', 'der',
            'die', 'ist', 'sich', 'auf', 'für', 'ist', 'es', 'im', 'den', 'zum', 'zur', 'aus'
        }

        # Gabungkan semua stopwords
        standard_stopwords = set(factory_stopword.get_stop_words())
        self.all_stopwords = standard_stopwords.union(self.custom_stopwords).union(self.foreign_stopwords)
        
        self.dictionary = None
        self.corpus = None
        self.model = None
        self.processed_docs = []
        self.doc_paths = []

    def preprocess_text(self, text: str) -> list:
        """Preprocessing teks: Hapus HTML, lower case, hapus stopwords."""
        # 1. Hapus tag HTML/XML (sangat penting untuk hasil OCR/PDF)
        text = re.sub(r'<[^>]+>', '', text)
        
        # 2. Hapus karakter khusus, angka, dan tanda baca
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # 3. Lowercase
        text = text.lower()
        
        # 4. Hapus Stopwords (Sastrawi + Custom + Asing)
        text = self.stopword_remover.remove(text)
        
        # 5. Tokenisasi
        tokens = text.split()
        
        # 6. Buang kata terlalu pendek (< 3 huruf)
        tokens = [word for word in tokens if len(word) > 3 and word not in self.all_stopwords]
        
        return tokens

    def load_and_process(self, input_dir: str = "data/processed"):
        """Memuat dan memproses semua dokumen."""
        input_path = Path(input_dir)
        files = list(input_path.glob("*.txt"))
        
        print(f"📚 Memuat dan memproses {len(files)} naskah...")
        
        for i, filepath in enumerate(files):
            if (i + 1) % 200 == 0:
                print(f"  Progress: {i+1}/{len(files)}")
                
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
            tokens = self.preprocess_text(text)
            # Hanya simpan dokumen yang memiliki minimal 10 kata setelah dibersihkan
            if len(tokens) >= 10:
                self.processed_docs.append(tokens)
                self.doc_paths.append(filepath.name)
            
        print(f"✅ Selesai memproses {len(self.processed_docs)} naskah yang valid.")

    def train_model(self):
        """Melatih model LDA."""
        print(f"\n🧠 Melatih model LDA dengan {self.num_topics} topik...")
        
        self.dictionary = corpora.Dictionary(self.processed_docs)
        # Filter kata yang muncul di < 5 dokumen atau > 50% dokumen
        self.dictionary.filter_extremes(no_below=5, no_above=0.5)
        
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.processed_docs]
        
        self.model = gensim.models.LdaMulticore(
            self.corpus,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            passes=self.passes,
            random_state=42,
            workers=2
        )
        print("✅ Model LDA berhasil dilatih!")

    def display_and_save_topics(self, output_dir: str = "data/topic_results"):
        """Menampilkan dan menyimpan hasil topik."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*60)
        print(f"📜 TOP {self.num_topics} TOPIK DALAM NASKAH NUSANTARA")
        print("="*60)
        
        topics_data = []
        for idx, topic in self.model.print_topics(-1):
            # Parse kata-kata dari format string gensim
            words = []
            for item in topic.split(' + '):
                weight, word = item.split('*')
                words.append(word.strip().strip('"'))
            
            topic_name = f"Topik {idx+1}: {', '.join(words[:4])}"
            print(f"\n{topic_name}")
            
            topics_data.append({
                'topic_id': idx,
                'name': topic_name,
                'top_words': words
            })
            
        json_path = output_path / "topics_summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(topics_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Ringkasan topik disimpan di: {json_path}")
        
        return topics_data

    def plot_topics(self, topics_data, output_dir: str = "data/topic_results"):
        """Membuat visualisasi bar chart untuk setiap topik (Pengganti pyLDAvis)."""
        output_path = Path(output_dir)
        
        print("\n📊 Membuat visualisasi topik...")
        
        fig, axes = plt.subplots(2, 5, figsize=(20, 10))
        fig.suptitle('Top 10 Topik dalam Naskah Nusantara', fontsize=16, fontweight='bold')
        
        for idx, topic in enumerate(topics_data):
            ax = axes[idx // 5, idx % 5]
            words = topic['top_words'][:8] # Ambil 8 kata teratas
            # Kita tidak punya bobot pasti dari string, jadi kita plot frekuensi kata saja
            ax.barh(range(len(words)), range(len(words), 0, -1), color='steelblue', alpha=0.7)
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words, fontsize=9)
            ax.set_title(f"Topik {idx+1}", fontsize=10, fontweight='bold')
            ax.invert_yaxis()
            ax.set_xlabel('Ranking')
            
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        
        img_path = output_path / "topics_visualization.png"
        plt.savefig(img_path, dpi=150, bbox_inches='tight')
        print(f"✅ Visualisasi berhasil disimpan!")
        print(f"   🖼️ Buka file ini: {img_path}")
        plt.close()


def main():
    Path("data/topic_results").mkdir(parents=True, exist_ok=True)
    
    # Coba 8 topik agar lebih fokus
    modeler = NusantaraTopicModeler(num_topics=8, passes=20)
    
    modeler.load_and_process("data/processed")
    modeler.train_model()
    topics_data = modeler.display_and_save_topics()
    modeler.plot_topics(topics_data)


if __name__ == "__main__":
    main()
