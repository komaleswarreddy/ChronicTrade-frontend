#!/usr/bin/env python3
"""
Verify RAG + ML Setup

Checks database schema and Python package installation.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check database tables
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set")
        sys.exit(1)
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Check for RAG tables
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND (table_name LIKE 'rag_%' OR table_name LIKE 'ml_%' OR table_name LIKE 'learning_%')
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print("Database Tables:")
    if tables:
        for table in tables:
            print(f"  [OK] {table}")
    else:
        print("  [WARN] No RAG/ML tables found")
    
    # Check for pgvector extension
    cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
    has_vector = cursor.fetchone()[0]
    if has_vector:
        print("  [OK] pgvector extension installed")
    else:
        print("  [WARN] pgvector extension not installed")
    
    cursor.close()
    conn.close()
    
    # Check Python packages
    print("\nPython Packages:")
    packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'sentence_transformers': 'sentence-transformers',
        'pytest': 'pytest'
    }
    
    installed = []
    missing = []
    
    for module, package_name in packages.items():
        try:
            __import__(module)
            installed.append(package_name)
            print(f"  [OK] {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"  [WARN] {package_name} (not installed)")
    
    print(f"\nSetup Summary:")
    print(f"  - Database tables: {len(tables)} found")
    print(f"  - Python packages: {len(installed)}/{len(packages)} installed")
    
    if missing:
        print(f"\n[WARN] Missing packages: {', '.join(missing)}")
        print("   Note: RAG and ML features will use fallback implementations")
    
    if len(tables) >= 5:
        print("\n[OK] Database schema is ready!")
    else:
        print("\n[WARN] Some database tables may be missing")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
