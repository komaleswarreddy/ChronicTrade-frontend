#!/usr/bin/env python3
"""
Install pgvector extension and verify RAG tables
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set")
        sys.exit(1)
    
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Install pgvector extension
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("[OK] pgvector extension installed")
    except Exception as e:
        print(f"[WARN] Could not install pgvector: {e}")
        print("   Note: RAG embeddings will not work without pgvector")
    
    # Check RAG tables
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE 'rag_%'
        ORDER BY table_name
    """)
    rag_tables = [row[0] for row in cursor.fetchall()]
    
    if rag_tables:
        print(f"[OK] RAG tables found: {', '.join(rag_tables)}")
    else:
        print("[WARN] RAG tables not found - they should be in schema.sql")
        print("   Run the main schema.sql to create RAG tables")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
