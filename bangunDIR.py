"""
SETUP PROJECT - Historiografi Digital Nusantara
Script otomatis untuk membangun struktur direktori dan inisialisasi database
"""

import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
def print_header(text):
    """Print header dengan format yang rapi"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")
def print_success(text):
    """Print pesan sukses"""
    print(f"✓ {text}")
def print_info(text):
    """Print pesan informasi"""
    print(f"  {text}")
def create_directory_structure(base_path):
    """Membuat seluruh struktur direktori proyek"""
    print_header("MEMBANGUN STRUKTUR DIREKTORI")
