"""
RAG Ingestion - Document ingestion, chunking, embedding generation
"""

import logging
import hashlib
import os
import json
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, fallback to None if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. RAG embeddings will not work.")


class DocumentIngester:
    """Handles document ingestion, chunking, and embedding generation"""
    
    def __init__(self, conn=None):
        self.conn = conn
        self.model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model: {e}")
                self.model = None
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap  # Overlap for context
        
        return chunks
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for text using sentence-transformers.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if model not available
        """
        if not self.model:
            logger.warning("Embedding model not available")
            return None
        
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def ingest_document(
        self,
        document_id: str,
        title: str,
        source_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        conn=None
    ) -> Dict[str, Any]:
        """
        Ingest a document: store document, chunk it, generate embeddings.
        
        Args:
            document_id: Unique document identifier
            title: Document title
            source_type: Type of document (compliance_rule, risk_policy, etc.)
            content: Document content
            metadata: Optional metadata
            conn: Database connection
            
        Returns:
            Dict with chunks_created and embeddings_created counts
        """
        if conn is None:
            conn = self.conn
        
        if conn is None:
            raise ValueError("Database connection required")
        
        cursor = conn.cursor()
        
        try:
            # Check if document already exists
            cursor.execute(
                "SELECT id FROM rag_documents WHERE document_id = %s",
                (document_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing document
                cursor.execute(
                    """UPDATE rag_documents 
                       SET title = %s, source_type = %s, content = %s, 
                           metadata = %s, updated_at = CURRENT_TIMESTAMP
                       WHERE document_id = %s""",
                    (title, source_type, content, 
                     Json(metadata or {}), document_id)
                )
                # Delete old chunks and embeddings
                cursor.execute(
                    """DELETE FROM rag_chunks WHERE document_id = %s""",
                    (document_id,)
                )
            else:
                # Insert new document
                cursor.execute(
                    """INSERT INTO rag_documents (document_id, title, source_type, content, metadata)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (document_id, title, source_type, content,
                     Json(metadata or {}))
                )
            
            # Chunk the content
            chunks = self.chunk_text(content)
            chunks_created = 0
            embeddings_created = 0
            
            for idx, chunk_content in enumerate(chunks):
                # Insert chunk
                cursor.execute(
                    """INSERT INTO rag_chunks (document_id, chunk_index, content, metadata)
                       VALUES (%s, %s, %s, %s)
                       RETURNING id""",
                    (document_id, idx, chunk_content,
                     Json({"chunk_size": len(chunk_content)}))
                )
                chunk_row = cursor.fetchone()
                chunk_id = chunk_row[0]
                chunks_created += 1
                
                # Generate embedding
                embedding = self.generate_embedding(chunk_content)
                if embedding is not None:
                    # Convert numpy array to list for PostgreSQL
                    embedding_list = embedding.tolist()
                    cursor.execute(
                        """INSERT INTO rag_embeddings (chunk_id, embedding, model_name)
                           VALUES (%s, %s, %s)""",
                        (chunk_id, str(embedding_list), 'sentence-transformers/all-MiniLM-L6-v2')
                    )
                    embeddings_created += 1
                else:
                    logger.warning(f"Could not generate embedding for chunk {idx} of document {document_id}")
            
            conn.commit()
            
            return {
                "chunks_created": chunks_created,
                "embeddings_created": embeddings_created,
                "success": True
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to ingest document {document_id}: {e}", exc_info=True)
            raise
        finally:
            cursor.close()
