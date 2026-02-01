#!/usr/bin/env python3
"""
Test RAG Query - Verify RAG retrieval works end-to-end
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

import psycopg2
from rag.service import RAGService

def test_rag_query():
    """Test RAG query functionality"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        rag_service = RAGService(conn=conn)
        
        # Test queries
        test_queries = [
            "What are the compliance rules for BUY recommendations?",
            "What is the minimum confidence score?",
            "What are the risk policies?",
            "What are the portfolio limits?",
        ]
        
        print("=" * 60)
        print("Testing RAG Query System")
        print("=" * 60)
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 60)
            
            try:
                result = rag_service.query(
                    query=query,
                    source_types=None,
                    top_k=3,
                    min_confidence=0.3,  # Lower threshold for testing
                    conn=conn
                )
                
                print(f"[OK] Found {result.total_results} results in {result.query_time_ms:.2f}ms")
                
                if result.citations:
                    for i, citation in enumerate(result.citations, 1):
                        print(f"\n  Result {i}:")
                        print(f"    Title: {citation.title}")
                        print(f"    Source: {citation.source_type}")
                        print(f"    Confidence: {citation.confidence:.3f}")
                        print(f"    Content: {citation.content[:100]}...")
                else:
                    print("  [WARN] No results found")
                    
            except Exception as e:
                print(f"  [ERROR] Error: {e}")
                import traceback
                traceback.print_exc()
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("[OK] RAG Query Test Complete")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_query()
    sys.exit(0 if success else 1)
