"""
RAG Schemas - Pydantic models for documents, chunks, queries
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Document(BaseModel):
    """Document model for RAG"""
    document_id: str
    title: str
    source_type: str  # 'compliance_rule', 'risk_policy', 'strategy_doc', 'execution_constraint'
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Chunk(BaseModel):
    """Chunk model for RAG"""
    chunk_id: Optional[int] = None
    document_id: str
    chunk_index: int
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class Citation(BaseModel):
    """Citation from RAG retrieval"""
    document_id: str
    title: str
    source_type: str
    chunk_index: int
    content: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    """Request for RAG query"""
    query: str = Field(..., description="Query text to search for")
    source_types: Optional[List[str]] = Field(None, description="Filter by source types")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    min_confidence: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")


class QueryResponse(BaseModel):
    """Response from RAG query"""
    query: str
    citations: List[Citation]
    total_results: int
    query_time_ms: float


class IngestRequest(BaseModel):
    """Request to ingest a document"""
    document_id: str
    title: str
    source_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class IngestResponse(BaseModel):
    """Response from document ingestion"""
    document_id: str
    chunks_created: int
    embeddings_created: int
    success: bool
