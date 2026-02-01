"""
RAG Retriever - Vector similarity search using pgvector with TEXT fallback
"""

import logging
import os
import ast
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. RAG retrieval will not work.")


class RAGRetriever:
    """Handles vector similarity search for RAG"""
    
    def __init__(self, conn=None):
        self.conn = conn
        self.model = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence-transformers model for retrieval")
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model: {e}")
                self.model = None
    
    def generate_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Generate embedding for query text"""
        if not self.model:
            logger.warning("Embedding model not available")
            return None
        
        try:
            embedding = self.model.encode(query, normalize_embeddings=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return None
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two normalized vectors"""
        try:
            # Both vectors should already be normalized, so dot product = cosine similarity
            similarity = float(np.dot(vec1, vec2))
            # Clamp to [-1, 1] range to handle floating point errors
            return max(-1.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Error computing cosine similarity: {e}")
            return 0.0
    
    def parse_embedding_text(self, embedding_text: str) -> Optional[np.ndarray]:
        """Parse embedding from TEXT column (stored as string representation of list)"""
        if not embedding_text:
            return None
        
        try:
            # Try to parse as Python list literal
            embedding_list = ast.literal_eval(embedding_text)
            if isinstance(embedding_list, list):
                embedding_array = np.array(embedding_list, dtype=np.float32)
                # Normalize the embedding
                norm = np.linalg.norm(embedding_array)
                if norm > 0:
                    embedding_array = embedding_array / norm
                return embedding_array
            return None
        except (ValueError, SyntaxError, TypeError) as e:
            logger.warning(f"Failed to parse embedding text: {e}")
            return None
    
    def check_embedding_column_type(self, conn) -> str:
        """Check if embedding column is TEXT or vector type"""
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'rag_embeddings' 
                AND column_name = 'embedding'
            """)
            result = cursor.fetchone()
            if result:
                return result[0].lower()
            return 'unknown'
        except Exception as e:
            logger.warning(f"Could not check column type: {e}")
            return 'unknown'
        finally:
            cursor.close()
    
    def check_database_health(self, conn) -> Dict[str, Any]:
        """Perform comprehensive database health check"""
        health = {
            "tables_exist": False,
            "table_counts": {},
            "embeddings_exist": False,
            "embedding_count": 0,
            "column_type": "unknown",
            "sample_embedding_valid": False,
            "errors": []
        }
        
        cursor = conn.cursor()
        try:
            # Check if tables exist
            logger.info("[RAG Health] Checking if RAG tables exist...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('rag_documents', 'rag_chunks', 'rag_embeddings')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['rag_documents', 'rag_chunks', 'rag_embeddings']
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                health["errors"].append(f"Missing tables: {missing_tables}")
                logger.error(f"[RAG Health] Missing tables: {missing_tables}")
            else:
                health["tables_exist"] = True
                logger.info(f"[RAG Health] All required tables exist: {existing_tables}")
            
            # Get row counts
            logger.info("[RAG Health] Counting rows in tables...")
            for table in required_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    health["table_counts"][table] = count
                    logger.info(f"[RAG Health]   {table}: {count} rows")
                except Exception as count_error:
                    health["errors"].append(f"Failed to count {table}: {str(count_error)}")
                    logger.error(f"[RAG Health] Failed to count {table}: {count_error}")
            
            # Check embeddings
            logger.info("[RAG Health] Checking embeddings...")
            try:
                cursor.execute("SELECT COUNT(*) FROM rag_embeddings WHERE embedding IS NOT NULL")
                embedding_count = cursor.fetchone()[0]
                health["embedding_count"] = embedding_count
                health["embeddings_exist"] = embedding_count > 0
                logger.info(f"[RAG Health] Embeddings found: {embedding_count}")
            except Exception as embed_error:
                health["errors"].append(f"Failed to count embeddings: {str(embed_error)}")
                logger.error(f"[RAG Health] Failed to count embeddings: {embed_error}")
            
            # Check column type
            logger.info("[RAG Health] Checking embedding column type...")
            try:
                column_type = self.check_embedding_column_type(conn)
                health["column_type"] = column_type
                logger.info(f"[RAG Health] Embedding column type: {column_type}")
            except Exception as type_error:
                health["errors"].append(f"Failed to check column type: {str(type_error)}")
                logger.error(f"[RAG Health] Failed to check column type: {type_error}")
            
            # Validate sample embedding
            logger.info("[RAG Health] Validating sample embedding...")
            try:
                cursor.execute("SELECT embedding FROM rag_embeddings WHERE embedding IS NOT NULL LIMIT 1")
                sample_row = cursor.fetchone()
                if sample_row:
                    sample_embedding = sample_row[0]
                    if health["column_type"] in ('text', 'character varying', 'varchar'):
                        parsed = self.parse_embedding_text(sample_embedding)
                        health["sample_embedding_valid"] = parsed is not None
                        if parsed is not None:
                            logger.info(f"[RAG Health] Sample embedding valid (shape: {parsed.shape})")
                        else:
                            logger.warning("[RAG Health] Sample embedding failed to parse")
                            health["errors"].append("Sample embedding failed to parse")
                    else:
                        health["sample_embedding_valid"] = True
                        logger.info("[RAG Health] Sample embedding exists (vector type)")
                else:
                    logger.warning("[RAG Health] No embeddings found to validate")
                    health["errors"].append("No embeddings found in database")
            except Exception as sample_error:
                health["errors"].append(f"Failed to validate sample: {str(sample_error)}")
                logger.error(f"[RAG Health] Failed to validate sample: {sample_error}")
            
            # Summary
            logger.info("[RAG Health] Health check summary:")
            logger.info(f"[RAG Health]   Tables exist: {health['tables_exist']}")
            logger.info(f"[RAG Health]   Embeddings exist: {health['embeddings_exist']}")
            logger.info(f"[RAG Health]   Embedding count: {health['embedding_count']}")
            logger.info(f"[RAG Health]   Column type: {health['column_type']}")
            logger.info(f"[RAG Health]   Sample valid: {health['sample_embedding_valid']}")
            logger.info(f"[RAG Health]   Errors: {len(health['errors'])}")
            
        except Exception as e:
            health["errors"].append(f"Health check failed: {str(e)}")
            logger.error(f"[RAG Health] Health check exception: {e}", exc_info=True)
        finally:
            cursor.close()
        
        return health
    
    def retrieve_with_text_embeddings(
        self,
        query_embedding: np.ndarray,
        source_types: Optional[List[str]] = None,
        top_k: int = 5,
        min_confidence: float = 0.5,
        conn=None
    ) -> List[Dict[str, Any]]:
        """Retrieve using TEXT embeddings (fallback when pgvector not available)"""
        import time
        text_start = time.time()
        
        logger.info("[RAG Retriever TEXT] " + "-" * 60)
        logger.info("[RAG Retriever TEXT] Starting TEXT embedding retrieval")
        logger.info(f"[RAG Retriever TEXT]   Query embedding shape: {query_embedding.shape}")
        logger.info(f"[RAG Retriever TEXT]   Source types: {source_types}")
        logger.info(f"[RAG Retriever TEXT]   Top K: {top_k}")
        logger.info(f"[RAG Retriever TEXT]   Min Confidence: {min_confidence}")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Step 1: Build and execute query
            logger.info("[RAG Retriever TEXT] Step 1: Building SQL query...")
            base_query = """
                SELECT 
                    c.id as chunk_id,
                    c.document_id,
                    c.chunk_index,
                    c.content,
                    c.metadata as chunk_metadata,
                    d.title,
                    d.source_type,
                    d.metadata as doc_metadata,
                    e.embedding as embedding_text
                FROM rag_embeddings e
                JOIN rag_chunks c ON e.chunk_id = c.id
                JOIN rag_documents d ON c.document_id = d.document_id
                WHERE e.embedding IS NOT NULL
            """
            
            params = []
            
            if source_types:
                placeholders = ','.join(['%s'] * len(source_types))
                base_query += f" AND d.source_type IN ({placeholders})"
                params.extend(source_types)
                logger.info(f"[RAG Retriever TEXT] Added source type filter: {source_types}")
            
            logger.info("[RAG Retriever TEXT] Step 2: Executing SQL query...")
            try:
                cursor.execute(base_query, params)
                logger.info("[RAG Retriever TEXT] SQL query executed")
            except Exception as sql_error:
                logger.error(f"[RAG Retriever TEXT] SQL execution failed: {sql_error}", exc_info=True)
                raise
            
            # Step 3: Fetch all results
            logger.info("[RAG Retriever TEXT] Step 3: Fetching all embeddings...")
            try:
                all_results = cursor.fetchall()
                logger.info(f"[RAG Retriever TEXT] Fetched {len(all_results)} rows from database")
            except Exception as fetch_error:
                logger.error(f"[RAG Retriever TEXT] Failed to fetch: {fetch_error}", exc_info=True)
                raise
            
            if len(all_results) == 0:
                logger.warning("[RAG Retriever TEXT] WARNING: No embeddings found in database!")
                return []
            
            # Step 4: Parse embeddings and compute similarities
            logger.info("[RAG Retriever TEXT] Step 4: Parsing embeddings and computing similarities...")
            similarities = []
            parsed_count = 0
            parse_errors = 0
            
            for i, row in enumerate(all_results):
                try:
                    embedding_text = row.get('embedding_text')
                    if not embedding_text:
                        parse_errors += 1
                        if parse_errors <= 3:
                            logger.warning(f"[RAG Retriever TEXT] Row {i}: embedding_text is None or empty")
                        continue
                    
                    stored_embedding = self.parse_embedding_text(embedding_text)
                    if stored_embedding is None:
                        parse_errors += 1
                        if parse_errors <= 3:
                            logger.warning(f"[RAG Retriever TEXT] Row {i}: Failed to parse embedding")
                        continue
                    
                    parsed_count += 1
                    similarity = self.cosine_similarity(query_embedding, stored_embedding)
                    
                    if similarity >= min_confidence:
                        similarities.append((similarity, row))
                        if len(similarities) <= 3:
                            logger.info(f"[RAG Retriever TEXT]   Match {len(similarities)}: {row.get('title', 'unknown')} (conf: {similarity:.3f})")
                    
                except Exception as row_error:
                    parse_errors += 1
                    if parse_errors <= 3:
                        logger.warning(f"[RAG Retriever TEXT] Row {i} processing error: {row_error}")
            
            logger.info(f"[RAG Retriever TEXT] Parsing complete:")
            logger.info(f"[RAG Retriever TEXT]   Total rows: {len(all_results)}")
            logger.info(f"[RAG Retriever TEXT]   Successfully parsed: {parsed_count}")
            logger.info(f"[RAG Retriever TEXT]   Parse errors: {parse_errors}")
            logger.info(f"[RAG Retriever TEXT]   Above threshold ({min_confidence}): {len(similarities)}")
            
            # Step 5: Sort and limit
            logger.info("[RAG Retriever TEXT] Step 5: Sorting and limiting results...")
            similarities.sort(key=lambda x: x[0], reverse=True)
            similarities = similarities[:top_k]
            logger.info(f"[RAG Retriever TEXT] Selected top {len(similarities)} results")
            
            # Step 6: Build citations
            logger.info("[RAG Retriever TEXT] Step 6: Building citations...")
            citations = []
            for i, (similarity, row) in enumerate(similarities):
                try:
                    citation = {
                        "document_id": row.get('document_id', 'unknown'),
                        "title": row.get('title', 'Untitled'),
                        "source_type": row.get('source_type', 'unknown'),
                        "chunk_index": row.get('chunk_index', 0),
                        "content": row.get('content', ''),
                        "confidence": similarity,
                        "metadata": {
                            "chunk_metadata": row.get('chunk_metadata'),
                            "doc_metadata": row.get('doc_metadata')
                        }
                    }
                    citations.append(citation)
                    if i < 3:
                        logger.info(f"[RAG Retriever TEXT]   Citation {i+1}: {citation['title']} (conf: {similarity:.3f})")
                except Exception as cite_error:
                    logger.error(f"[RAG Retriever TEXT] Failed to build citation {i}: {cite_error}")
            
            text_time = (time.time() - text_start) * 1000
            logger.info(f"[RAG Retriever TEXT] TEXT retrieval completed: {len(citations)} citations in {text_time:.2f}ms")
            logger.info("[RAG Retriever TEXT] " + "-" * 60)
            return citations
            
        except Exception as e:
            text_time = (time.time() - text_start) * 1000
            logger.error(f"[RAG Retriever TEXT] Failed after {text_time:.2f}ms: {e}", exc_info=True)
            logger.error("[RAG Retriever TEXT] " + "-" * 60)
            return []
        finally:
            try:
                cursor.close()
            except Exception as close_error:
                logger.warning(f"[RAG Retriever TEXT] Error closing cursor: {close_error}")
    
    def retrieve(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        top_k: int = 5,
        min_confidence: float = 0.5,
        conn=None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using vector similarity search.
        
        Args:
            query: Query text
            source_types: Optional filter by source types
            top_k: Number of results to return
            min_confidence: Minimum similarity threshold
            conn: Database connection
            
        Returns:
            List of citation dictionaries
        """
        import time
        retrieve_start = time.time()
        
        logger.info("[RAG Retriever] " + "=" * 70)
        logger.info("[RAG Retriever] Retrieve method called")
        logger.info(f"[RAG Retriever]   Query: {query}")
        logger.info(f"[RAG Retriever]   Source Types: {source_types}")
        logger.info(f"[RAG Retriever]   Top K: {top_k}")
        logger.info(f"[RAG Retriever]   Min Confidence: {min_confidence}")
        
        # Validate connection
        if conn is None:
            conn = self.conn
            logger.info("[RAG Retriever] Using retriever's connection")
        else:
            logger.info("[RAG Retriever] Using provided connection")
        
        if conn is None:
            logger.error("[RAG Retriever] ERROR: No database connection")
            raise ValueError("Database connection required")
        
        # Step 1: Generate query embedding
        logger.info("[RAG Retriever] Step 1: Generating query embedding...")
        query_embedding = None
        try:
            query_embedding = self.generate_query_embedding(query)
            if query_embedding is None:
                logger.error("[RAG Retriever] ERROR: Failed to generate query embedding")
                logger.error("[RAG Retriever] Model status:")
                logger.error(f"[RAG Retriever]   Model is None: {self.model is None}")
                logger.error(f"[RAG Retriever]   SENTENCE_TRANSFORMERS_AVAILABLE: {SENTENCE_TRANSFORMERS_AVAILABLE}")
                return []
            
            embedding_shape = query_embedding.shape if hasattr(query_embedding, 'shape') else 'unknown'
            embedding_dtype = query_embedding.dtype if hasattr(query_embedding, 'dtype') else 'unknown'
            logger.info(f"[RAG Retriever] Query embedding generated successfully")
            logger.info(f"[RAG Retriever]   Shape: {embedding_shape}")
            logger.info(f"[RAG Retriever]   Dtype: {embedding_dtype}")
            logger.info(f"[RAG Retriever]   Norm: {np.linalg.norm(query_embedding):.4f}")
        except Exception as embed_error:
            logger.error(f"[RAG Retriever] Embedding generation failed: {embed_error}", exc_info=True)
            return []
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Step 2: Check column type
            logger.info("[RAG Retriever] Step 2: Checking embedding column type...")
            column_type = None
            try:
                column_type = self.check_embedding_column_type(conn)
                logger.info(f"[RAG Retriever] Column type detected: {column_type}")
            except Exception as col_error:
                logger.error(f"[RAG Retriever] Failed to check column type: {col_error}", exc_info=True)
                raise
            
            # Step 3: Choose retrieval path
            if column_type in ('text', 'character varying', 'varchar'):
                logger.info("[RAG Retriever] Step 3: Using TEXT embedding retrieval path")
                return self.retrieve_with_text_embeddings(
                    query_embedding=query_embedding,
                    source_types=source_types,
                    top_k=top_k,
                    min_confidence=min_confidence,
                    conn=conn
                )
            
            # Step 4: Try pgvector query
            logger.info("[RAG Retriever] Step 3: Using pgvector retrieval path")
            logger.info("[RAG Retriever] Step 3a: Converting embedding to list...")
            try:
                embedding_list = query_embedding.tolist()
                logger.info(f"[RAG Retriever] Embedding converted to list (length: {len(embedding_list)})")
            except Exception as conv_error:
                logger.error(f"[RAG Retriever] Failed to convert embedding: {conv_error}")
                raise
            
            # Step 3b: Build SQL query
            logger.info("[RAG Retriever] Step 3b: Building SQL query...")
            base_query = """
                SELECT 
                    c.id as chunk_id,
                    c.document_id,
                    c.chunk_index,
                    c.content,
                    c.metadata as chunk_metadata,
                    d.title,
                    d.source_type,
                    d.metadata as doc_metadata,
                    1 - (e.embedding <=> %s::vector) as similarity
                FROM rag_embeddings e
                JOIN rag_chunks c ON e.chunk_id = c.id
                JOIN rag_documents d ON c.document_id = d.document_id
                WHERE 1 - (e.embedding <=> %s::vector) >= %s
            """
            
            params = [
                str(embedding_list),
                str(embedding_list),
                min_confidence
            ]
            
            if source_types:
                placeholders = ','.join(['%s'] * len(source_types))
                base_query += f" AND d.source_type IN ({placeholders})"
                params.extend(source_types)
                logger.info(f"[RAG Retriever] Added source type filter: {source_types}")
            
            base_query += """
                ORDER BY e.embedding <=> %s::vector
                LIMIT %s
            """
            params.extend([str(embedding_list), top_k])
            
            logger.info(f"[RAG Retriever] SQL query built (params count: {len(params)})")
            
            # Step 3c: Execute query
            logger.info("[RAG Retriever] Step 3c: Executing SQL query...")
            try:
                cursor.execute(base_query, params)
                logger.info("[RAG Retriever] SQL query executed successfully")
            except Exception as sql_error:
                error_str = str(sql_error).lower()
                logger.error(f"[RAG Retriever] SQL execution failed: {sql_error}", exc_info=True)
                
                # Try fallback if pgvector error
                if "operator does not exist" in error_str or "vector" in error_str or "does not exist" in error_str:
                    logger.warning("[RAG Retriever] pgvector operator failed, trying TEXT fallback")
                    try:
                        return self.retrieve_with_text_embeddings(
                            query_embedding=query_embedding,
                            source_types=source_types,
                            top_k=top_k,
                            min_confidence=min_confidence,
                            conn=conn
                        )
                    except Exception as fallback_error:
                        logger.error(f"[RAG Retriever] TEXT fallback also failed: {fallback_error}", exc_info=True)
                        return []
                raise
            
            # Step 3d: Fetch results
            logger.info("[RAG Retriever] Step 3d: Fetching results...")
            try:
                results = cursor.fetchall()
                logger.info(f"[RAG Retriever] Fetched {len(results)} rows from database")
            except Exception as fetch_error:
                logger.error(f"[RAG Retriever] Failed to fetch results: {fetch_error}", exc_info=True)
                raise
            
            # Step 3e: Build citations
            logger.info("[RAG Retriever] Step 3e: Building citations...")
            citations = []
            for i, row in enumerate(results):
                try:
                    similarity = float(row.get('similarity', 0.0))
                    citation = {
                        "document_id": row.get('document_id', 'unknown'),
                        "title": row.get('title', 'Untitled'),
                        "source_type": row.get('source_type', 'unknown'),
                        "chunk_index": row.get('chunk_index', 0),
                        "content": row.get('content', ''),
                        "confidence": similarity,
                        "metadata": {
                            "chunk_metadata": row.get('chunk_metadata'),
                            "doc_metadata": row.get('doc_metadata')
                        }
                    }
                    citations.append(citation)
                    if i < 3:  # Log first 3
                        logger.info(f"[RAG Retriever]   Citation {i+1}: {citation['title']} (conf: {similarity:.3f})")
                except Exception as cite_error:
                    logger.error(f"[RAG Retriever] Failed to build citation {i}: {cite_error}")
                    logger.error(f"[RAG Retriever]   Row data: {dict(row)}")
            
            retrieve_time = (time.time() - retrieve_start) * 1000
            logger.info(f"[RAG Retriever] pgvector query completed: {len(citations)} citations in {retrieve_time:.2f}ms")
            logger.info("[RAG Retriever] " + "=" * 70)
            return citations
            
        except Exception as e:
            retrieve_time = (time.time() - retrieve_start) * 1000
            logger.error(f"[RAG Retriever] Retrieve failed after {retrieve_time:.2f}ms: {e}", exc_info=True)
            logger.error("[RAG Retriever] " + "=" * 70)
            raise
        finally:
            try:
                cursor.close()
            except Exception as close_error:
                logger.warning(f"[RAG Retriever] Error closing cursor: {close_error}")
