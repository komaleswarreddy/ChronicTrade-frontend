#!/usr/bin/env python3
"""
Create RAG tables directly
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
    cursor = conn.cursor()
    
    # Check if pgvector extension is available
    try:
        cursor.execute("SELECT 1 FROM pg_type WHERE typname = 'vector'")
        has_pgvector = cursor.fetchone() is not None
    except:
        has_pgvector = False
    
    # Determine embedding column type
    if has_pgvector:
        embedding_type = "vector(384)"
    else:
        embedding_type = "TEXT"  # Store as text representation of array
    
    # Create tables first
    tables_sql = [
        """CREATE TABLE IF NOT EXISTS rag_documents (
            id SERIAL PRIMARY KEY,
            document_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS rag_chunks (
            id SERIAL PRIMARY KEY,
            document_id TEXT NOT NULL REFERENCES rag_documents(document_id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(document_id, chunk_index)
        )""",
        f"""CREATE TABLE IF NOT EXISTS rag_embeddings (
            id SERIAL PRIMARY KEY,
            chunk_id INTEGER NOT NULL REFERENCES rag_chunks(id) ON DELETE CASCADE,
            embedding {embedding_type},
            model_name TEXT NOT NULL DEFAULT 'sentence-transformers/all-MiniLM-L6-v2',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_rag_documents_source ON rag_documents(source_type)"
    ]
    
    # Only add vector index if pgvector is available
    if has_pgvector:
        indexes_sql.append("CREATE INDEX IF NOT EXISTS idx_rag_embeddings_vector ON rag_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")
    
    # Create tables
    for stmt in tables_sql:
    
        try:
            cursor.execute(stmt)
            conn.commit()
            table_name = stmt.split('rag_')[1].split()[0] if 'rag_' in stmt else 'table'
            print(f"[OK] Created table: {table_name}")
        except psycopg2.errors.DuplicateTable:
            conn.rollback()
            print(f"[SKIP] Table already exists")
        except Exception as e:
            conn.rollback()
            if 'already exists' not in str(e).lower():
                print(f"[WARN] {e}")
    
    # Create indexes
    for stmt in indexes_sql:
        try:
            cursor.execute(stmt)
            conn.commit()
            print(f"[OK] Created index")
        except psycopg2.errors.DuplicateObject:
            conn.rollback()
            print(f"[SKIP] Index already exists")
        except psycopg2.errors.UndefinedObject as e:
            conn.rollback()
            if 'vector' in str(e):
                print(f"[WARN] pgvector not available - skipping vector index")
            else:
                print(f"[WARN] {e}")
        except psycopg2.errors.OperationalError as e:
            conn.rollback()
            if 'extension' in str(e).lower() and 'vector' in str(e).lower():
                print(f"[WARN] pgvector extension not installed - skipping vector index")
            else:
                print(f"[WARN] {e}")
        except Exception as e:
            conn.rollback()
            if 'already exists' not in str(e).lower():
                print(f"[WARN] {e}")
    
    # Verify
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE 'rag_%'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    if tables:
        print(f"\n[OK] RAG tables created: {', '.join(tables)}")
    else:
        print("\n[WARN] No RAG tables found")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
