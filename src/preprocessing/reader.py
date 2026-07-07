"""
Modul untuk membaca, membersihkan, dan mendeteksi duplikat naskah kuno Nusantara.
Versi 3.0 - Dengan fitur laporan duplikat (JSON & CSV) untuk audit trail.
"""

import os
import re
import json
import csv
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class ManuscriptReader:
    """Kelas untuk membaca, memproses, dan mendeteksi duplikat naskah kuno."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.csv', '.html', '.xml'}
    
    def __init__(
        self, 
        source_dir: str = "01_Dokumen_Sumber/1.1_Naskah_Asal",
        duplicate_dir: str = "01_Dokumen_Sumber/1.2_Duplikat",
        processed_dir: str = "data/processed",
        report_dir: str = "reports/duplicate_reports"
    ):
        self.source_dir = Path(source_dir).resolve()
        self.duplicate_dir = Path(duplicate_dir).resolve()
        self.processed_dir = Path(processed_dir).resolve()
        self.report_dir = Path(report_dir).resolve()
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Folder sumber tidak ditemukan: {self.source_dir}")
        
        self.duplicate_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Source: {self.source_dir}")
        print(f"Duplicate: {self.duplicate_dir}")
        print(f"Processed: {self.processed_dir}")
        print(f"Reports: {self.report_dir}")
    
    def _read_file_content(self, filepath: Path) -> Optional[str]:
        """Membaca konten file berdasarkan ekstensi."""
        ext = filepath.suffix.lower()
        
        try:
            if ext in self.SUPPORTED_EXTENSIONS:
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        with open(filepath, 'r', encoding=encoding) as f:
                            return f.read()
                    except UnicodeDecodeError:
                        continue
            elif ext == '.pdf':
                try:
                    import PyPDF2
                    with open(filepath, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() or ""
                        return text
                except ImportError:
                    print(f"PyPDF2 belum terinstal. Jalankan: pip install PyPDF2")
                    return None
            elif ext == '.docx':
                try:
                    import docx
                    doc = docx.Document(str(filepath))
                    return "\n".join([p.text for p in doc.paragraphs])
                except ImportError:
                    print(f"python-docx belum terinstal. Jalankan: pip install python-docx")
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"Error membaca {filepath.name}: {e}")
            return None
    
    def calculate_content_hash(self, filepath: Path) -> Optional[str]:
        """Menghitung hash dari KONTEN TEKS untuk deteksi duplikat."""
        text = self._read_file_content(filepath)
        if text is None:
            return None
        
        normalized = self.normalize_text(text)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def read_file(self, filepath: Path) -> str:
        """Membaca satu file naskah."""
        if not filepath.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {filepath}")
        
        content = self._read_file_content(filepath)
        if content is None:
            raise ValueError(f"Tidak bisa membaca konten: {filepath}")
        return content
    
    def clean_ocr_noise(self, text: str) -> str:
        """Membersihkan noise khas OCR dari teks."""
        text = re.sub(r'\b([A-Z])\s+(?=[A-Z]\s+[A-Z])', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    def normalize_text(self, text: str) -> str:
        """Normalisasi teks untuk perbandingan."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Ekstraksi entitas sederhana."""
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        names = re.findall(name_pattern, text)
        
        place_pattern = r'(?:negeri|kraton|tanah|kota)\s+([A-Z][a-z]+)'
        places = re.findall(place_pattern, text)
        
        return {
            'possible_names': list(set(names)),
            'possible_places': list(set(places))
        }
    
    def _scan_files(self, recursive: bool = True) -> List[Path]:
        """Scan semua file yang didukung di folder sumber."""
        all_files = []
        
        if recursive:
            files = list(self.source_dir.rglob('*'))
        else:
            files = list(self.source_dir.glob('*'))
        
        for f in files:
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                all_files.append(f)
        
        return all_files
    
    def detect_duplicates(self, scan_recursive: bool = True) -> Dict[str, List[Path]]:
        """Mendeteksi file duplikat berdasarkan KONTEN TEKS."""
        file_hashes = defaultdict(list)
        files = self._scan_files(scan_recursive)
        
        print(f"\nMemindai {len(files)} file untuk mendeteksi duplikat...")
        
        skipped = 0
        for filepath in files:
            try:
                content_hash = self.calculate_content_hash(filepath)
                if content_hash:
                    file_hashes[content_hash].append(filepath)
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error memproses {filepath.name}: {e}")
                skipped += 1
        
        if skipped > 0:
            print(f"{skipped} file dilewati (format tidak didukung atau error)")
        
        duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
        
        total_dup_files = sum(len(files) - 1 for files in duplicates.values())
        print(f"Ditemukan {len(duplicates)} grup duplikat ({total_dup_files} file duplikat)")
        
        return duplicates
    
    def separate_duplicates(
        self, 
        duplicates: Dict[str, List[Path]],
        move_files: bool = True
    ) -> Dict[str, Dict]:
        """Memisahkan file duplikat ke folder terpisah."""
        results = {}
        
        for file_hash, filepaths in duplicates.items():
            original = filepaths[0]
            duplicates_list = filepaths[1:]
            
            result = {
                'hash': file_hash,
                'original': str(original.relative_to(self.source_dir)),
                'original_full_path': str(original),
                'duplicates': [str(f.relative_to(self.source_dir)) for f in duplicates_list],
                'duplicates_full_paths': [str(f) for f in duplicates_list],
                'moved_paths': [],
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"\nGrup duplikat (hash: {file_hash[:8]}...):")
            print(f"   Original: {result['original']}")
            
            if move_files:
                for dup_file in duplicates_list:
                    try:
                        relative_path = dup_file.relative_to(self.source_dir)
                        dest_path = self.duplicate_dir / relative_path
                        
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        if dest_path.exists():
                            stem = dest_path.stem
                            suffix = dest_path.suffix
                            counter = 1
                            while dest_path.exists():
                                dest_path = dest_path.parent / f"{stem}_{counter}{suffix}"
                                counter += 1
                        
                        shutil.move(str(dup_file), str(dest_path))
                        result['moved_paths'].append(str(dest_path.relative_to(self.duplicate_dir)))
                        print(f"   Dipindahkan: {dup_file.name} -> {dest_path.relative_to(self.duplicate_dir)}")
                    except Exception as e:
                        print(f"   Gagal memindahkan {dup_file.name}: {e}")
            else:
                for dup_file in duplicates_list:
                    print(f"   [DRY-RUN] Seharusnya dipindahkan: {dup_file.relative_to(self.source_dir)}")
            
            results[file_hash] = result
        
        return results
    
    def save_duplicate_report(
        self, 
        duplicate_report: Dict[str, Dict],
        total_files_scanned: int,
        total_files_processed: int
    ) -> Tuple[Path, Path]:
        """Menyimpan laporan duplikat dalam format JSON dan CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        json_report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'source_directory': str(self.source_dir),
                'duplicate_directory': str(self.duplicate_dir),
                'total_files_scanned': total_files_scanned,
                'total_files_processed': total_files_processed,
                'total_duplicate_groups': len(duplicate_report),
                'total_duplicate_files': sum(len(info['duplicates']) for info in duplicate_report.values())
            },
            'duplicate_groups': list(duplicate_report.values())
        }
        
        json_path = self.report_dir / f"duplicate_report_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        
        csv_path = self.report_dir / f"duplicate_report_{timestamp}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow([
                'Group_Hash',
                'Original_File',
                'Duplicate_File',
                'Moved_To',
                'Timestamp'
            ])
            
            for hash_val, info in duplicate_report.items():
                for i, dup_file in enumerate(info['duplicates']):
                    moved_to = info['moved_paths'][i] if i < len(info['moved_paths']) else 'N/A'
                    writer.writerow([
                        hash_val,
                        info['original'],
                        dup_file,
                        moved_to,
                        info['timestamp']
                    ])
        
        print(f"\nLaporan disimpan:")
        print(f"   JSON: {json_path}")
        print(f"   CSV: {csv_path}")
        
        return json_path, csv_path
    
    def process_manuscript(self, filepath: Path) -> Dict:
        """Proses lengkap satu naskah."""
        raw_text = self.read_file(filepath)
        cleaned_text = self.clean_ocr_noise(raw_text)
        entities = self.extract_entities(cleaned_text)
        
        return {
            'filename': filepath.name,
            'filepath': str(filepath),
            'raw_length': len(raw_text),
            'cleaned_length': len(cleaned_text),
            'cleaned_text': cleaned_text,
            'entities': entities
        }
    
    def process_all_manuscripts(
        self,
        scan_recursive: bool = True,
        separate_duplicates: bool = True,
        move_duplicates: bool = True,
        save_report: bool = True
    ) -> Tuple[List[Dict], Dict, Optional[Tuple[Path, Path]]]:
        """Proses semua naskah dengan laporan duplikat."""
        files = self._scan_files(scan_recursive)
        total_files_scanned = len(files)
        
        duplicates = self.detect_duplicates(scan_recursive)
        
        duplicate_report = {}
        if separate_duplicates and duplicates:
            print(f"\nMemisahkan {len(duplicates)} grup duplikat...")
            duplicate_report = self.separate_duplicates(duplicates, move_duplicates)
        elif not duplicates:
            print("\nTidak ada duplikat yang ditemukan.")
        
        processed_manuscripts = []
        remaining_files = self._scan_files(scan_recursive)
        total_files_processed = len(remaining_files)
        
        print(f"\nMemproses {total_files_processed} file naskah...")
        
        for filepath in remaining_files:
            try:
                result = self.process_manuscript(filepath)
                processed_manuscripts.append(result)
                
                output_file = self.processed_dir / f"{filepath.stem}_processed.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['cleaned_text'])
                    
            except Exception as e:
                print(f"Error memproses {filepath.name}: {e}")
        
        report_paths = None
        if save_report and duplicate_report:
            report_paths = self.save_duplicate_report(
                duplicate_report,
                total_files_scanned,
                total_files_processed
            )
        
        return processed_manuscripts, duplicate_report, report_paths


def main():
    """Fungsi utama untuk testing."""
    reader = ManuscriptReader()
    
    print("\n" + "="*70)
    print("ANALISIS NASKAH NUSANTARA - DENGAN LAPORAN DUPLIKAT")
    print("="*70)
    
    processed, duplicates, report_paths = reader.process_all_manuscripts(
        scan_recursive=True,
        separate_duplicates=True,
        move_duplicates=True,
        save_report=True
    )
    
    print("\n" + "="*70)
    print("RINGKASAN AKHIR")
    print("="*70)
    print(f"Naskah yang diproses: {len(processed)}")
    print(f"Grup duplikat: {len(duplicates)}")
    
    if report_paths:
        json_path, csv_path = report_paths
        print(f"\nLaporan tersedia di:")
        print(f"   JSON: {json_path.name}")
        print(f"   CSV: {csv_path.name}")
        print(f"   Lokasi: {json_path.parent}")
    
    if duplicates:
        print("\nDetail duplikat:")
        for hash_val, info in duplicates.items():
            print(f"\n   Original: {info['original']}")
            print(f"   Duplikat ({len(info['duplicates'])} file):")
            for dup in info['duplicates']:
                print(f"      -> {dup}")


if __name__ == "__main__":
    main()
