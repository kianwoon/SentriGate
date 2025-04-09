"""Schemas for query requests and responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Schema for vector search query request.
    
    Attributes:
        query: The search query text to be embedded and searched
        top_k: Number of results to return (default: 5)
        filter: Additional filters to apply to the search
    """
    
    query: str = Field(..., description="Search query text")
    top_k: int = Field(10, description="Number of results to return")
    filter: Optional[Dict[str, Any]] = Field(None, description="Additional filters for the search")


class ResponseItem(BaseModel):
    """Schema for a single response item.
    
    Attributes:
        type: The type of response item (e.g., 'text')
        text: The text content, typically containing JSON with pageContent
        score: The similarity score of the response item
    """
    score: float
    type: str = Field(..., description="Type of the response item")
    text: str = Field(..., description="Text content, usually JSON with pageContent")


class MatchPayload(BaseModel):
    """Schema for a single match payload.
    
    Attributes:
        context: The context of the document
        content: The content of the document
    """
    
    context: str = ""  # Default empty string
    content: str = Field(..., description="Document content")


class Match(BaseModel):
    """Schema for a single vector search match.
    
    Attributes:
        score: The similarity score
        payload: The document payload
    """
    
    score: float
    payload: ResponseItem


class QueryResponse(BaseModel):
    """Schema for vector search query response.
    
    Attributes:
        response: List of response items from the vector search
    """
    
    response: List[ResponseItem] = Field(..., description="List of response items from the vector search")