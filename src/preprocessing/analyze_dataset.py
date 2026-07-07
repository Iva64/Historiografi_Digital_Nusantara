"""Analisis statistik dataset naskah yang sudah diproses."""

import os
import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt


def analyze_processed_dataset(processed_dir: str = "data/processed"):
    """Analisis statistik file yang sudah diproses."""
    processed_path = Path(processed_dir)
    
    if not processed_path.exists():
        print(f"Folder tidak ditemukan: {processed_path}")
        return
    
    files = list(processed_path.glob("*.txt"))
    print(f"Total file terproses: {len(files)}")
    
    # Analisis panjang file
    lengths = []
    for f in files:
        size = f.stat().st_size
        lengths.append(size)
    
    print(f"\n=== Statistik Ukuran File ===")
    print(f"Rata-rata: {sum(lengths)/len(lengths):.0f} bytes")
    print(f"Min: {min(lengths)} bytes")
    print(f"Max: {max(lengths)} bytes")
    print(f"Median: {sorted(lengths)[len(lengths)//2]} bytes")
    
    # Distribusi ukuran
    size_buckets = Counter()
    for size in lengths:
        if size < 1000:
            size_buckets['< 1 KB'] += 1
        elif size < 10000:
            size_buckets['1-10 KB'] += 1
        elif size < 100000:
            size_buckets['10-100 KB'] += 1
        elif size < 1000000:
            size_buckets['100 KB - 1 MB'] += 1
        else:
            size_buckets['> 1 MB'] += 1
    
    print(f"\n=== Distribusi Ukuran ===")
    for bucket, count in sorted(size_buckets.items()):
        print(f"  {bucket}: {count} file ({count/len(files)*100:.1f}%)")
    
    # Visualisasi
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram ukuran
    axes[0].hist(lengths, bins=50, color='steelblue', edgecolor='black')
    axes[0].set_xlabel('Ukuran File (bytes)')
    axes[0].set_ylabel('Frekuensi')
    axes[0].set_title('Distribusi Ukuran File Naskah')
    axes[0].set_xscale('log')
    
    # Pie chart bucket
    labels = list(size_buckets.keys())
    sizes = list(size_buckets.values())
    axes[1].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    axes[1].set_title('Proporsi Ukuran File')
    
    plt.tight_layout()
    plt.savefig('reports/figures/dataset_statistics.png', dpi=150, bbox_inches='tight')
    print(f"\n📊 Visualisasi disimpan: reports/figures/dataset_statistics.png")
    plt.show()


if __name__ == "__main__":
    analyze_processed_dataset()
