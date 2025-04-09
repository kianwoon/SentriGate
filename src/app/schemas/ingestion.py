"""Schemas for document ingestion."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base schema for document.
    
    Attributes:
        content: The document content
        context: The document context (used for rule filtering)
        metadata: Additional metadata for the document
    """
    
    content: str = Field(..., description="Document content")
    context: str = Field(..., description="Document context (e.g., 'onboard', 'offboard')")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentIngest(DocumentBase):
    """Schema for document ingestion request.
    
    Attributes:
        id: Optional document ID
    """
    
    id: Optional[str] = Field(None, description="Optional document ID")


class BatchIngestRequest(BaseModel):
    """Schema for batch document ingestion request.
    
    Attributes:
        documents: List of documents to ingest
        ids: Optional list of document IDs
    """
    
    documents: List[DocumentBase] = Field(..., description="List of documents to ingest")
    ids: Optional[List[str]] = Field(None, description="Optional list of document IDs")


class IngestionResponse(BaseModel):
    """Schema for ingestion response.
    
    Attributes:
        status: Status of the ingestion operation
        error: Error message if any
        result: Result of the ingestion operation
    """
    
    status: str = Field(..., description="Status of the ingestion operation")
    error: Optional[str] = Field(None, description="Error message if any")
    result: Optional[Dict[str, Any]] = Field(None, description="Result of the ingestion operation")