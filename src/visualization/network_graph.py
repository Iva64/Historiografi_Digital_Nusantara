"""
Visualisasi Jaringan Ko-kemunculan Entitas (Tokoh dan Tempat) dari Naskah Nusantara.
Versi 2.0: Dioptimasi untuk browser dengan membatasi Top Nodes.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from pyvis.network import Network


class NusantaraNetwork:
    """Kelas untuk membangun dan memvisualisasikan jaringan entitas."""
    
    def __init__(self, ner_results_path: str = "data/ner_results/ner_results_pattern.json"):
        self.ner_path = Path(ner_results_path)
        
        if not self.ner_path.exists():
            raise FileNotFoundError(f"File hasil NER tidak ditemukan: {self.ner_path}")
            
        with open(self.ner_path, 'r', encoding='utf-8') as f:
            self.ner_data = json.load(f)
            
        print(f"✅ Berhasil memuat {len(self.ner_data)} hasil NER dari {self.ner_path}")
        
        self.edges = Counter()
        self.node_attributes = {}

    def build_cooccurrence_network(self, min_cooccurrence: int = 5, max_nodes: int = 150):
        """
        Membangun jaringan berdasarkan ko-kemunculan.
        max_nodes: Membatasi hanya menampilkan N node paling terhubung (agar browser tidak lemot).
        """
        print(f"\n️ Membangun jaringan ko-kemunculan...")
        
        for doc in self.ner_data:
            persons = set(doc.get('persons', []))
            locations = set(doc.get('locations', []))
            all_entities = persons.union(locations)
            
            for p in persons: self.node_attributes[p] = 'person'
            for l in locations: self.node_attributes[l] = 'location'
                
            entities_list = list(all_entities)
            for i in range(len(entities_list)):
                for j in range(i + 1, len(entities_list)):
                    edge = tuple(sorted([entities_list[i], entities_list[j]]))
                    self.edges[edge] += 1
                    
        # Filter edge yang muncul terlalu sedikit
        self.edges = Counter({k: v for k, v in self.edges.items() if v >= min_cooccurrence})
        
        # === OPTIMASI: BATASI JUMLAH NODE ===
        # Hitung seberapa penting setiap node (berdasarkan total bobot koneksi)
        node_importance = Counter()
        for (node1, node2), weight in self.edges.items():
            node_importance[node1] += weight
            node_importance[node2] += weight
            
        # Ambil hanya Top N node terpenting
        top_nodes = set([node for node, score in node_importance.most_common(max_nodes)])
        
        # Buang edge dan node yang tidak masuk Top N
        self.edges = Counter({k: v for k, v in self.edges.items() if k[0] in top_nodes and k[1] in top_nodes})
        self.node_attributes = {k: v for k, v in self.node_attributes.items() if k in top_nodes}
        
        print(f"✅ Jaringan terbentuk: {len(self.node_attributes)} node, {len(self.edges)} edge")
        print(f"   (Difilter: min ko-kemunculan={min_cooccurrence}, max node={max_nodes})")

    def visualize_interactive(self, output_dir: str = "reports/figures", output_file: str = "network_nusantara.html"):
        """Membuat visualisasi jaringan interaktif menggunakan Pyvis."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n Membuat visualisasi interaktif...")
        
        net = Network(
            height="800px", 
            width="100%", 
            bgcolor="#1a1a1a", 
            font_color="white",
            directed=False,
            notebook=False
        )
        
        # Konfigurasi fisika yang lebih stabil dan cepat
        net.barnes_hut(
            gravity=-80000,
            central_gravity=0.3,
            spring_length=200,
            spring_strength=0.01,
            damping=0.09,
            overlap=0
        )
        
        # Tambahkan Node
        for node, attr in self.node_attributes.items():
            degree = sum(1 for edge in self.edges if node in edge)
            
            if attr == 'person':
                color = '#ff4757' # Merah untuk Tokoh
                shape = 'dot'
            else:
                color = '#2ed573' # Hijau untuk Tempat
                shape = 'diamond'
                
            size = min(15 + (degree * 4), 60) 
            
            net.add_node(
                node, 
                label=node, 
                color=color, 
                size=size, 
                shape=shape,
                title=f"<b>{attr.upper()}</b><br>{node}<br>Koneksi: {degree}"
            )
            
        # Tambahkan Edge
        for (node1, node2), weight in self.edges.items():
            width = min(1 + (weight * 0.5), 8)
            # Warna garis semi-transparan agar tidak terlalu ramai
            net.add_edge(node1, node2, width=width, color="rgba(255, 255, 255, 0.3)", title=f"Muncul bersama {weight} kali")

        # Simpan HTML
        html_path = output_path / output_file
        net.write_html(str(html_path))
        
        print(f"✅ Visualisasi berhasil disimpan!")
        print(f"    Buka di browser: firefox {html_path.absolute()} &")
        return html_path


def main():
    network = NusantaraNetwork()
    
    # PENTING: Naikkan min_cooccurrence dan batasi max_nodes agar browser tidak lemot!
    network.build_cooccurrence_network(min_cooccurrence=5, max_nodes=100)
    
    network.visualize_interactive()


if __name__ == "__main__":
    main()
