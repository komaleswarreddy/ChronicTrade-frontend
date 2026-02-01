#!/usr/bin/env python3
"""
Apply RAG schema from schema.sql
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
    
    # Read schema.sql
    schema_file = Path(__file__).parent.parent / "database" / "schema.sql"
    if not schema_file.exists():
        print(f"[ERROR] Schema file not found: {schema_file}")
        sys.exit(1)
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Extract only RAG-related SQL (from -- Enable pgvector onwards)
    rag_sql = []
    in_rag_section = False
    for line in schema_sql.split('\n'):
        if '-- Enable pgvector' in line or 'CREATE TABLE IF NOT EXISTS rag_' in line:
            in_rag_section = True
        if in_rag_section:
            rag_sql.append(line)
        if in_rag_section and line.strip() and not line.strip().startswith('--') and 'CREATE' not in line and 'INDEX' not in line and 'EXTENSION' not in line and not line.strip().endswith(';'):
            # End of RAG section
            break
    
    rag_sql_text = '\n'.join(rag_sql)
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Execute RAG schema
    try:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in rag_sql_text.split(';') if s.strip() and not s.strip().startswith('--')]
        for stmt in statements:
            if stmt:
                try:
                    cursor.execute(stmt)
                except psycopg2.errors.DuplicateTable:
                    pass  # Table already exists
                except psycopg2.errors.DuplicateObject:
                    pass  # Extension/index already exists
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"[WARN] {e}")
        
        conn.commit()
        print("[OK] RAG schema applied")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'rag_%'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        if tables:
            print(f"[OK] RAG tables created: {', '.join(tables)}")
        else:
            print("[WARN] No RAG tables found after applying schema")
            
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to apply schema: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
