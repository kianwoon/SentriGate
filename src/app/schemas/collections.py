"""Schemas for collection endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CollectionInfo(BaseModel):
    """Schema for collection information.
    
    Attributes:
        name: Name of the collection
        vectors_count: Number of vectors in the collection
        points_count: Number of points in the collection
        status: Status of the collection
        vector_size: Size of vectors in the collection
        vector_distance: Distance function used for vectors
    """
    
    name: str = Field(..., description="Name of the collection")
    vectors_count: int = Field(..., description="Number of vectors in the collection")
    points_count: int = Field(..., description="Number of points in the collection")
    status: str = Field(..., description="Status of the collection")
    vector_size: int = Field(..., description="Size of vectors in the collection")
    vector_distance: str = Field(..., description="Distance function used for vectors")


class CollectionsList(BaseModel):
    """Schema for list of collections.
    
    Attributes:
        collections: List of collection names
    """
    
    collections: List[str] = Field(..., description="List of collection names")