#!/usr/bin/env python3
"""
Initialize RAG Documents

This script ingests the initial knowledge documents into the RAG system.
Run this after setting up the database and RAG tables.
"""

import os
import sys
import psycopg2
from pathlib import Path

# Fix Windows console encoding for emoji characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Optional dotenv support so the script can load from .env file
try:
    from dotenv import load_dotenv  # type: ignore
    # Load .env from the backend directory (parent of scripts)
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return None

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.service import RAGService

def init_rag_documents():
    """Initialize RAG documents from markdown files"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        rag_service = RAGService(conn=conn)
        
        # Document definitions
        documents_dir = Path(__file__).parent.parent / "rag" / "documents"
        documents = [
            {
                "document_id": "compliance_rules",
                "title": "Compliance Rules for Wine Trading",
                "source_type": "compliance_rule",
                "filepath": documents_dir / "compliance_rules.md"
            },
            {
                "document_id": "risk_policies",
                "title": "Risk Management Policies",
                "source_type": "risk_policy",
                "filepath": documents_dir / "risk_policies.md"
            },
            {
                "document_id": "strategy_docs",
                "title": "Trading Strategy Documentation",
                "source_type": "strategy_doc",
                "filepath": documents_dir / "strategy_documentation.md"
            },
            {
                "document_id": "execution_constraints",
                "title": "Execution Constraints and Limits",
                "source_type": "execution_constraint",
                "filepath": documents_dir / "execution_constraints.md"
            },
        ]
        
        print("Ingesting RAG documents...")
        for doc in documents:
            if not doc["filepath"].exists():
                print(f"WARNING: File not found: {doc['filepath']}")
                continue
            
            with open(doc["filepath"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                result = rag_service.ingest_document(
                    document_id=doc["document_id"],
                    title=doc["title"],
                    source_type=doc["source_type"],
                    content=content,
                    metadata={"source_file": str(doc["filepath"])},
                    conn=conn
                )
                print(f"✅ Ingested: {doc['title']} ({result.chunks_created} chunks, {result.embeddings_created} embeddings)")
            except Exception as e:
                print(f"❌ Failed to ingest {doc['title']}: {e}")
        
        conn.close()
        print("\n✅ RAG document initialization complete!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_rag_documents()
    sys.exit(0 if success else 1)
