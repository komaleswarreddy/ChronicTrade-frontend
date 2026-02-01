"""
RAG (Retrieval-Augmented Generation) Module

Provides knowledge grounding for agent decisions through document retrieval.
"""

from .service import RAGService
from .schemas import Document, Chunk, QueryRequest, QueryResponse, IngestRequest

__all__ = ['RAGService', 'Document', 'Chunk', 'QueryRequest', 'QueryResponse', 'IngestRequest']
