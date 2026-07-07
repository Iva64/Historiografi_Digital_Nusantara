"""
Named Entity Recognition untuk Naskah Nusantara.
Ekstrak: PERSON (nama tokoh), LOCATION (tempat), ORGANIZATION, DATE.
"""

import spacy
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter
import json


class NusantaraNER:
    """NER khusus untuk naskah Nusantara dengan custom patterns."""
    
    def __init__(self, model_name: str = "id_core_news_sm"):
        """Inisialisasi model spaCy dan custom patterns."""
        try:
            self.nlp = spacy.load(model_name)
            print(f"✅ Model spaCy '{model_name}' berhasil dimuat")
        except OSError:
            print(f"⚠️ Model '{model_name}' tidak ditemukan. Jalankan: python -m spacy download {model_name}")
            raise
        
        # Custom patterns untuk naskah klasik
        self._setup_custom_patterns()
        
        # Storage untuk entitas
        self.all_persons: Set[str] = set()
        self.all_locations: Set[str] = set()
        self.all_organizations: Set[str] = set()
        self.all_dates: Set[str] = set()
    
    def _setup_custom_patterns(self):
        """Setup pola custom untuk entitas naskah kuno."""
        
        # Pola untuk gelar dan sebutan tradisional
        self.gelar_patterns = [
            r'\b(Sultan|Sunan|Raden|Pangeran|Datuk|Tuanku|Syahbandar|Laksamana|Bendahara)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
            r'\b(Prabu|Sri|Dewi|Ratu|Kyai|Haji|Hj\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
        ]
        
        # Pola untuk tempat tradisional
        self.location_patterns = [
            r'\b(negeri|kerajaan|kota|pelabuhan|tanah)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b(di|ke|dari|ke)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
        ]
        
        # Pola untuk tahun/tanggal
        self.date_patterns = [
            r'\b(tahun|pada|tanggal)\s+(\d{1,4})',
            r'\b(\d{1,2})\s+(Januari|Februari|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+(\d{4})',
            r'\b( Hijriyah|H|Masehi|M)\s+(\d{4})',
        ]
    
    def extract_entities(self, text: str, doc_id: str = "") -> Dict:
        """
        Ekstrak semua entitas dari teks.
        
        Returns:
            Dictionary dengan keys: persons, locations, organizations, dates
        """
        # Proses dengan spaCy
        doc = self.nlp(text)
        
        # Ekstrak entitas dari spaCy
        persons = set()
        locations = set()
        organizations = set()
        dates = set()
        
        # Entitas dari spaCy model
        for ent in doc.ents:
            if ent.label_ == "PER" or ent.label_ == "PERSON":
                persons.add(ent.text.strip())
            elif ent.label_ in ["LOC", "LOCATION", "GPE"]:
                locations.add(ent.text.strip())
            elif ent.label_ in ["ORG", "ORGANIZATION"]:
                organizations.add(ent.text.strip())
            elif ent.label_ in ["DATE", "TIME"]:
                dates.add(ent.text.strip())
        
        # Ekstrak dengan custom patterns
        custom_persons = self._extract_with_patterns(text, self.gelar_patterns, group=2)
        custom_locations = self._extract_with_patterns(text, self.location_patterns, group=2)
        custom_dates = self._extract_with_patterns(text, self.date_patterns, groups=[2, 3])
        
        # Gabungkan hasil
        persons.update(custom_persons)
        locations.update(custom_locations)
        dates.update(custom_dates)
        
        # Simpan ke storage global
        self.all_persons.update(persons)
        self.all_locations.update(locations)
        self.all_organizations.update(organizations)
        self.all_dates.update(dates)
        
        return {
            'doc_id': doc_id,
            'persons': list(persons),
            'locations': list(locations),
            'organizations': list(organizations),
            'dates': list(dates),
            'counts': {
                'persons': len(persons),
                'locations': len(locations),
                'organizations': len(organizations),
                'dates': len(dates)
            }
        }
    
    def _extract_with_patterns(self, text: str, patterns: List[str], group: int = 1, groups: List[int] = None) -> Set[str]:
        """Ekstrak entitas menggunakan regex patterns."""
        results = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    if groups:
                        # Ambil multiple groups
                        extracted = [match.group(g) for g in groups if match.lastindex and g <= match.lastindex]
                        results.update([e.strip() for e in extracted if e])
                    else:
                        extracted = match.group(group)
                        if extracted:
                            results.add(extracted.strip())
                except IndexError:
                    continue
        
        return results
    
    def process_file(self, filepath: Path) -> Dict:
        """Proses satu file naskah."""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return self.extract_entities(text, doc_id=filepath.stem)
    
    def process_directory(self, input_dir: str, output_dir: str = "data/ner_results"):
        """
        Proses semua file dalam direktori.
        
        Returns:
            Dictionary dengan statistik keseluruhan
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = list(input_path.glob("*.txt"))
        print(f"\n📚 Memproses {len(files)} file naskah untuk NER...")
        
        results = []
        total_entities = {
            'persons': Counter(),
            'locations': Counter(),
            'organizations': Counter(),
            'dates': Counter()
        }
        
        for i, filepath in enumerate(files):
            if (i + 1) % 1000 == 0:
                print(f"  Progress: {i+1}/{len(files)} ({(i+1)/len(files)*100:.1f}%)")
            
            try:
                result = self.process_file(filepath)
                results.append(result)
                
                # Update counters
                for person in result['persons']:
                    total_entities['persons'][person] += 1
                for loc in result['locations']:
                    total_entities['locations'][loc] += 1
                for org in result['organizations']:
                    total_entities['organizations'][org] += 1
                for date in result['dates']:
                    total_entities['dates'][date] += 1
                    
            except Exception as e:
                print(f"  ⚠️ Error memproses {filepath.name}: {e}")
        
        # Simpan hasil per file
        json_path = output_path / "ner_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Simpan entitas unik
        entities_summary = {
            'total_files_processed': len(results),
            'unique_entities': {
                'persons': sorted(list(self.all_persons)),
                'locations': sorted(list(self.all_locations)),
                'organizations': sorted(list(self.all_organizations)),
                'dates': sorted(list(self.all_dates))
            },
            'top_entities': {
                'persons': total_entities['persons'].most_common(50),
                'locations': total_entities['locations'].most_common(50),
                'organizations': total_entities['organizations'].most_common(50),
                'dates': total_entities['dates'].most_common(50)
            },
            'statistics': {
                'total_persons_mentioned': sum(total_entities['persons'].values()),
                'total_locations_mentioned': sum(total_entities['locations'].values()),
                'total_organizations_mentioned': sum(total_entities['organizations'].values()),
                'total_dates_mentioned': sum(total_entities['dates'].values()),
                'unique_persons': len(self.all_persons),
                'unique_locations': len(self.all_locations),
                'unique_organizations': len(self.all_organizations),
                'unique_dates': len(self.all_dates)
            }
        }
        
        summary_path = output_path / "entities_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(entities_summary, f, ensure_ascii=False, indent=2)
        
        # Simpan dalam format CSV untuk analisis
        self._save_to_csv(results, output_path)
        
        print(f"\n✅ NER selesai!")
        print(f"  📄 Hasil per file: {json_path}")
        print(f"  📊 Ringkasan entitas: {summary_path}")
        print(f"  📈 Statistik:")
        print(f"     - Total entitas PERSON: {entities_summary['statistics']['total_persons_mentioned']}")
        print(f"     - Total entitas LOCATION: {entities_summary['statistics']['total_locations_mentioned']}")
        print(f"     - Total entitas ORGANIZATION: {entities_summary['statistics']['total_organizations_mentioned']}")
        print(f"     - Total entitas DATE: {entities_summary['statistics']['total_dates_mentioned']}")
        
        return entities_summary
    
    def _save_to_csv(self, results: List[Dict], output_path: Path):
        """Simpan hasil dalam format CSV."""
        import csv
        
        # CSV untuk semua entitas
        csv_path = output_path / "all_entities.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['doc_id', 'entity_type', 'entity_text'])
            
            for result in results:
                for person in result['persons']:
                    writer.writerow([result['doc_id'], 'PERSON', person])
                for loc in result['locations']:
                    writer.writerow([result['doc_id'], 'LOCATION', loc])
                for org in result['organizations']:
                    writer.writerow([result['doc_id'], 'ORGANIZATION', org])
                for date in result['dates']:
                    writer.writerow([result['doc_id'], 'DATE', date])
        
        print(f"  📋 CSV entities: {csv_path}")


def main():
    """Fungsi utama untuk testing NER."""
    extractor = NusantaraNER()
    
    # Proses semua naskah yang sudah diproses
    summary = extractor.process_directory(
        input_dir="data/processed",
        output_dir="data/ner_results"
    )
    
    # Tampilkan top 10 entities
    print("\n" + "="*70)
    print("TOP 10 ENTITIES")
    print("="*70)
    
    print("\n👤 Tokoh (PERSON):")
    for person, count in summary['top_entities']['persons'][:10]:
        print(f"  {person}: {count} kali")
    
    print("\n📍 Tempat (LOCATION):")
    for loc, count in summary['top_entities']['locations'][:10]:
        print(f"  {loc}: {count} kali")
    
    print("\n🏢 Organisasi (ORGANIZATION):")
    for org, count in summary['top_entities']['organizations'][:10]:
        print(f"  {org}: {count} kali")
    
    print("\n📅 Tanggal (DATE):")
    for date, count in summary['top_entities']['dates'][:10]:
        print(f"  {date}: {count} kali")


if __name__ == "__main__":
    main()
