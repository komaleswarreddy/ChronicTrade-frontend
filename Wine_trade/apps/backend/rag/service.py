"""
RAG Service - Main service orchestrating ingestion and retrieval
"""

import logging
import time
import os
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from .ingestion import DocumentIngester
from .retriever import RAGRetriever
from .schemas import (
    Document, Chunk, QueryRequest, QueryResponse, 
    IngestRequest, IngestResponse, Citation
)

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service for document ingestion and retrieval"""
    
    def __init__(self, conn=None):
        self.conn = conn
        self.ingester = DocumentIngester(conn=conn)
        self.retriever = RAGRetriever(conn=conn)
    
    def ingest_document(
        self,
        document_id: str,
        title: str,
        source_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        conn=None
    ) -> IngestResponse:
        """
        Ingest a document into the RAG system.
        
        Args:
            document_id: Unique document identifier
            title: Document title
            source_type: Type of document
            content: Document content
            metadata: Optional metadata
            conn: Database connection
            
        Returns:
            IngestResponse with ingestion results
        """
        if conn is None:
            conn = self.conn
        
        if conn is None:
            raise ValueError("Database connection required")
        
        try:
            result = self.ingester.ingest_document(
                document_id=document_id,
                title=title,
                source_type=source_type,
                content=content,
                metadata=metadata,
                conn=conn
            )
            
            return IngestResponse(
                document_id=document_id,
                chunks_created=result["chunks_created"],
                embeddings_created=result["embeddings_created"],
                success=result["success"]
            )
        except Exception as e:
            logger.error(f"Failed to ingest document: {e}", exc_info=True)
            raise
    
    def query(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        top_k: int = 5,
        min_confidence: float = 0.5,
        conn=None
    ) -> QueryResponse:
        """
        Query the RAG system for relevant documents.
        
        Args:
            query: Query text
            source_types: Optional filter by source types
            top_k: Number of results to return
            min_confidence: Minimum confidence threshold
            conn: Database connection
            
        Returns:
            QueryResponse with citations
        """
        logger.info("[RAG Service] ==" * 40)
        logger.info("[RAG Service] Query method called")
        logger.info(f"[RAG Service]   Query: {query}")
        logger.info(f"[RAG Service]   Source Types: {source_types}")
        logger.info(f"[RAG Service]   Top K: {top_k}")
        logger.info(f"[RAG Service]   Min Confidence: {min_confidence}")
        
        # Validate connection
        if conn is None:
            conn = self.conn
            logger.info("[RAG Service] Using service's connection")
        else:
            logger.info("[RAG Service] Using provided connection")
        
        if conn is None:
            logger.error("[RAG Service] ERROR: No database connection available")
            raise ValueError("Database connection required")
        
        # Verify connection is alive
        try:
            test_cursor = conn.cursor()
            test_cursor.execute("SELECT 1")
            test_cursor.close()
            logger.info("[RAG Service] Database connection verified")
        except Exception as conn_error:
            logger.error(f"[RAG Service] Database connection test failed: {conn_error}")
            raise ValueError(f"Database connection is not valid: {str(conn_error)}")
        
        # Perform database health check (first query only, or periodically)
        try:
            health = self.retriever.check_database_health(conn)
            if health["errors"]:
                logger.warning(f"[RAG Service] Database health check found {len(health['errors'])} issues:")
                for error in health["errors"]:
                    logger.warning(f"[RAG Service]   - {error}")
            else:
                logger.info("[RAG Service] Database health check passed")
        except Exception as health_error:
            logger.warning(f"[RAG Service] Health check failed (non-fatal): {health_error}")
        
        start_time = time.time()
        
        try:
            # Step 1: Check retriever initialization
            logger.info("[RAG Service] Step 1: Checking retriever...")
            if self.retriever is None:
                logger.error("[RAG Service] ERROR: Retriever is None!")
                raise ValueError("RAGRetriever not initialized")
            logger.info("[RAG Service] Retriever is initialized")
            
            if self.retriever.model is None:
                logger.warning("[RAG Service] WARNING: Embedding model is None - queries will fail")
            else:
                logger.info("[RAG Service] Embedding model is loaded")
            
            # Step 2: Call retriever
            logger.info("[RAG Service] Step 2: Calling retriever.retrieve()...")
            retrieve_start = time.time()
            try:
                citations_data = self.retriever.retrieve(
                    query=query,
                    source_types=source_types,
                    top_k=top_k,
                    min_confidence=min_confidence,
                    conn=conn
                )
                retrieve_time = (time.time() - retrieve_start) * 1000
                logger.info(f"[RAG Service] Retriever returned {len(citations_data)} raw citations in {retrieve_time:.2f}ms")
            except Exception as retrieve_error:
                logger.error(f"[RAG Service] Retriever failed: {retrieve_error}", exc_info=True)
                raise
            
            # Step 3: Convert to Citation objects
            logger.info("[RAG Service] Step 3: Converting to Citation objects...")
            citations = []
            conversion_errors = []
            for i, c in enumerate(citations_data):
                try:
                    citation = Citation(
                        document_id=c.get("document_id", "unknown"),
                        title=c.get("title", "Untitled"),
                        source_type=c.get("source_type", "unknown"),
                        chunk_index=c.get("chunk_index", 0),
                        content=c.get("content", ""),
                        confidence=c.get("confidence", 0.0),
                        metadata=c.get("metadata")
                    )
                    citations.append(citation)
                    if i < 3:  # Log first 3
                        logger.info(f"[RAG Service]   Citation {i+1}: {citation.title} (conf: {citation.confidence:.3f})")
                except Exception as conv_error:
                    logger.error(f"[RAG Service] Failed to convert citation {i}: {conv_error}")
                    logger.error(f"[RAG Service]   Raw data: {c}")
                    conversion_errors.append((i, str(conv_error)))
            
            if conversion_errors:
                logger.warning(f"[RAG Service] {len(conversion_errors)} citations failed conversion")
            
            query_time_ms = (time.time() - start_time) * 1000
            
            # Step 4: Build response
            logger.info("[RAG Service] Step 4: Building QueryResponse...")
            try:
                response = QueryResponse(
                    query=query,
                    citations=citations,
                    total_results=len(citations),
                    query_time_ms=query_time_ms
                )
                logger.info(f"[RAG Service] Response built successfully:")
                logger.info(f"[RAG Service]   Total Results: {response.total_results}")
                logger.info(f"[RAG Service]   Query Time: {response.query_time_ms:.2f}ms")
                logger.info(f"[RAG Service]   Citations: {len(response.citations)}")
                logger.info("[RAG Service] ==" * 40)
                return response
            except Exception as response_error:
                logger.error(f"[RAG Service] Failed to build response: {response_error}", exc_info=True)
                raise
            
        except Exception as e:
            query_time_ms = (time.time() - start_time) * 1000
            logger.error(f"[RAG Service] Query failed after {query_time_ms:.2f}ms: {e}", exc_info=True)
            logger.error("[RAG Service] ==" * 40)
            raise
    
    def list_documents(self, source_type: Optional[str] = None, conn=None) -> List[Document]:
        """
        List all documents in the RAG system.
        
        Args:
            source_type: Optional filter by source type
            conn: Database connection
            
        Returns:
            List of Document objects
        """
        if conn is None:
            conn = self.conn
        
        if conn is None:
            raise ValueError("Database connection required")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if source_type:
                cursor.execute(
                    "SELECT * FROM rag_documents WHERE source_type = %s ORDER BY created_at DESC",
                    (source_type,)
                )
            else:
                cursor.execute("SELECT * FROM rag_documents ORDER BY created_at DESC")
            
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = Document(
                    document_id=row['document_id'],
                    title=row['title'],
                    source_type=row['source_type'],
                    content=row['content'],
                    metadata=row.get('metadata'),
                    created_at=row.get('created_at'),
                    updated_at=row.get('updated_at')
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}", exc_info=True)
            raise
        finally:
            cursor.close()
