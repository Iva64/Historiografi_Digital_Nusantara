"""
Mesin Pencari Full-Text (Search Engine) untuk Naskah Nusantara.
Menggunakan SQLite FTS5 untuk pencarian cepat dan snippet highlighting.
"""

import sqlite3
import json
from pathlib import Path
import argparse
import sys


class NusantaraSearchEngine:
    """Kelas untuk indexing dan pencarian naskah."""
    
    def __init__(self, db_path: str = "data/nusantara_search.db"):
        self.db_path = Path(db_path)
        # Pastikan folder database ada
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Koneksi ke SQLite
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        self._create_tables()

    def _create_tables(self):
        """Membuat tabel FTS5 untuk indexing."""
        # Tabel virtual FTS5
        # Kolom: 0=filename, 1=content, 2=persons, 3=locations, 4=dates
        self.cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS naskah_fts USING fts5(
                filename,
                content,
                persons,
                locations,
                dates
            )
        ''')
        self.conn.commit()

    def index_data(self, processed_dir: str, ner_json_path: str):
        """Melakukan indexing pada semua naskah dan metadata NER."""
        processed_path = Path(processed_dir)
        ner_path = Path(ner_json_path)
        
        if not processed_path.exists():
            print(f"❌ Folder processed tidak ditemukan: {processed_path}")
            return
            
        if not ner_path.exists():
            print(f"⚠️ File NER tidak ditemukan: {ner_path}. Indexing tanpa metadata NER.")
            ner_data_map = {}
        else:
            # Load hasil NER dan mapping berdasarkan filename
            with open(ner_path, 'r', encoding='utf-8') as f:
                ner_list = json.load(f)
            ner_data_map = {item['doc_id']: item for item in ner_list}
            print(f"✅ Memuat metadata NER untuk {len(ner_data_map)} dokumen.")

        files = list(processed_path.glob("*.txt"))
        print(f"\n📚 Memulai indexing {len(files)} naskah ke SQLite FTS5...")
        
        count = 0
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ambil metadata NER jika ada
                ner = ner_data_map.get(filepath.stem, {})
                persons = " ".join(ner.get('persons', []))
                locations = " ".join(ner.get('locations', []))
                dates = " ".join(ner.get('dates', []))
                
                # Insert ke FTS5
                self.cursor.execute('''
                    INSERT INTO naskah_fts(filename, content, persons, locations, dates)
                    VALUES (?, ?, ?, ?, ?)
                ''', (filepath.name, content, persons, locations, dates))
                count += 1
                
            except Exception as e:
                print(f"  ⚠️ Gagal mengindex {filepath.name}: {e}")
                
        self.conn.commit()
        print(f"✅ Indexing selesai! {count} naskah berhasil diindex di {self.db_path}")

    def search(self, query: str, limit: int = 10):
        """
        Mencari naskah berdasarkan query.
        Mendukung sintaks FTS5: 'kata1 kata2', '"frasa tepat"', 'persons:Raden'
        """
        # Menggunakan fungsi snippet untuk highlight hasil
        # snippet(table, column_index, open_tag, close_tag, ellipsis, max_tokens)
        # content ada di index 1
        sql = '''
            SELECT 
                filename,
                snippet(naskah_fts, 1, '<b>', '</b>', '...', 64) as snippet
            FROM naskah_fts
            WHERE naskah_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        '''
        
        self.cursor.execute(sql, (query, limit))
        results = self.cursor.fetchall()
        
        return results

    def close(self):
        """Menutup koneksi database."""
        self.conn.close()


def main():
    """CLI untuk Search Engine."""
    parser = argparse.ArgumentParser(description="Mesin Pencari Naskah Nusantara")
    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia")
    
    # Perintah Index
    parser_index = subparsers.add_parser("index", help="Index semua naskah ke database")
    parser_index.add_argument("--processed", default="data/processed", help="Folder naskah terproses")
    parser_index.add_argument("--ner", default="data/ner_results/ner_results_pattern.json", help="File JSON hasil NER")
    
    # Perintah Search
    parser_search = subparsers.add_parser("search", help="Cari naskah")
    parser_search.add_argument("query", help="Kata kunci pencarian (contoh: 'Laksamana Malaka', 'persons:Sultan')")
    parser_search.add_argument("--limit", type=int, default=10, help="Jumlah hasil maksimal")
    
    args = parser.parse_args()
    
    engine = NusantaraSearchEngine()
    
    if args.command == "index":
        engine.index_data(args.processed, args.ner)
    elif args.command == "search":
        print(f"\n🔍 Mencari: '{args.query}'\n" + "="*60)
        results = engine.search(args.query, args.limit)
        
        if not results:
            print("❌ Tidak ada hasil yang ditemukan.")
        else:
            for i, row in enumerate(results, 1):
                print(f"\n[{i}] 📄 {row['filename']}")
                print(f"    Snippet: {row['snippet']}")
            print(f"\n✅ Ditemukan {len(results)} hasil.")
    else:
        parser.print_help()
        
    engine.close()


if __name__ == "__main__":
    main()
