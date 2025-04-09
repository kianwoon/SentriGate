"""Schemas for search results."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """Schema for a single search result item.
    
    Attributes:
        score: The similarity score
        payload: The document payload containing content and metadata
        vector: The vector representation (optional)
    """
    
    score: float = Field(..., description="Similarity score of the result")
    payload: Dict[str, Any] = Field(..., description="Document payload containing content and metadata")
    vector: Optional[List[float]] = Field(None, description="Vector representation of the document")


class SearchResults(BaseModel):
    """Schema for collection of search result items.
    
    Attributes:
        items: List of search result items
        total: Total number of results returned
    """
    
    items: List[SearchResultItem] = Field(..., description="List of search result items")
    total: int = Field(..., description="Total number of results returned")
