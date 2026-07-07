"""
Named Entity Recognition berbasis Pattern (tanpa spaCy).
Cocok untuk naskah kuno Nusantara dengan pola tradisional.
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter
import json
import csv


class PatternBasedNER:
    """NER berbasis regex patterns untuk naskah Nusantara."""
    
    def __init__(self):
        self._setup_patterns()
        
        # Storage untuk entitas
        self.all_persons: Set[str] = set()
        self.all_locations: Set[str] = set()
        self.all_organizations: Set[str] = set()
        self.all_dates: Set[str] = set()
    
    def _setup_patterns(self):
        """Setup pola regex untuk entitas naskah kuno."""
        
        # Pola untuk nama tokoh dengan gelar tradisional
        self.person_patterns = [
            r'\b(Sultan|Sunan|Raden|Pangeran|Datuk|Tuanku|Syahbandar|Laksamana|Bendahara|Prabu|Sri|Dewi|Ratu|Kyai|Haji|Hj\.|Raja|Adipati|Senapati)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
            r'\b([A-Z][a-z]+\s+(?:bin|binti|ibn|putra|putri)\s+[A-Z][a-z]+)',
            r'\b(Jan|Johan|Pieter|Cornelis|Willem|Hendrik|Abraham|Isaac|Frans|Coen|VOC)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',  # Nama Belanda/Eropa
        ]
        
        # Pola untuk tempat
        self.location_patterns = [
            r'\b(?:negeri|kerajaan|kota|pelabuhan|tanah|pulau|sungai|gunung|laut)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b(?:di|ke|dari|menuju)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b(Batavia|Malaka|Pasai|Aceh|Demak|Mataram|Majapahit|Srivijaya|Tarumanagara|Pajajaran|Gowa|Ternate|Tidore|Banten|Jepara|Surabaya|Banjarmasin|Palembang|Jambi|Riau|Lampung|Bali|Lombok|Sumbawa|Flores|Timor|Sulawesi|Kalimantan|Sumatra|Java|Borneo|Celebes|Maluku|Nusantara)\b',
        ]
        
        # Pola untuk organisasi/lembaga
        self.org_patterns = [
            r'\b(VOC|Kompeni|Hindia Belanda|Pemerintah|Keraton|Kraton|Istana|Masjid|Surau|Dayah|Pesantren|Syarikat)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Company|Society|Association|Vereniging)',
        ]
        
        # Pola untuk tanggal/tahun
        self.date_patterns = [
            r'\b(tahun|pada|tanggal)\s+(\d{1,4})',
            r'\b(\d{1,2})\s+(?:Januari|Februari|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+(\d{4})',
            r'\b(\d{4})\s*(?:M|Masehi|H|Hijriyah)',
            r'\b(tahun)\s+(\d{4})\s*(?:M|Masehi|H|Hijriyah)',
        ]
    
    def _extract_with_patterns(self, text: str, patterns: List[str]) -> Set[str]:
        """Ekstrak entitas menggunakan regex patterns."""
        results = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                for i in range(1, match.lastindex + 1 if match.lastindex else 1):
                    try:
                        extracted = match.group(i)
                        if extracted and len(extracted) > 2:
                            results.add(extracted.strip())
                    except IndexError:
                        continue
        
        return results
    
    def extract_entities(self, text: str, doc_id: str = "") -> Dict:
        """Ekstrak semua entitas dari teks."""
        persons = self._extract_with_patterns(text, self.person_patterns)
        locations = self._extract_with_patterns(text, self.location_patterns)
        organizations = self._extract_with_patterns(text, self.org_patterns)
        dates = self._extract_with_patterns(text, self.date_patterns)
        
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
    
    def process_file(self, filepath: Path) -> Dict:
        """Proses satu file naskah."""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return self.extract_entities(text, doc_id=filepath.stem)
    
    def process_directory(self, input_dir: str, output_dir: str = "data/ner_results"):
        """Proses semua file dalam direktori."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = list(input_path.glob("*.txt"))
        print(f"\n📚 Memproses {len(files)} file naskah untuk NER (Pattern-Based)...")
        
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
        
        # Simpan hasil JSON
        json_path = output_path / "ner_results_pattern.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        entities_summary = {
            'method': 'pattern-based (no spaCy)',
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
        
        summary_path = output_path / "entities_summary_pattern.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(entities_summary, f, ensure_ascii=False, indent=2)
        
        # Simpan CSV
        csv_path = output_path / "all_entities_pattern.csv"
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
        
        print(f"\n✅ NER Pattern-Based selesai!")
        print(f"  📄 Hasil per file: {json_path}")
        print(f"  📊 Ringkasan: {summary_path}")
        print(f"   CSV: {csv_path}")
        print(f"\n Statistik:")
        print(f"  - Total PERSON: {entities_summary['statistics']['total_persons_mentioned']} ({entities_summary['statistics']['unique_persons']} unik)")
        print(f"  - Total LOCATION: {entities_summary['statistics']['total_locations_mentioned']} ({entities_summary['statistics']['unique_locations']} unik)")
        print(f"  - Total ORGANIZATION: {entities_summary['statistics']['total_organizations_mentioned']} ({entities_summary['statistics']['unique_organizations']} unik)")
        print(f"  - Total DATE: {entities_summary['statistics']['total_dates_mentioned']} ({entities_summary['statistics']['unique_dates']} unik)")
        
        return entities_summary


def main():
    """Fungsi utama."""
    extractor = PatternBasedNER()
    
    summary = extractor.process_directory(
        input_dir="data/processed",
        output_dir="data/ner_results"
    )
    
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
