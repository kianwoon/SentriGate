"""Client for interacting with Qdrant vector database."""

from typing import Any, Dict, List, Optional

from fastapi import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import settings


class QdrantSearchEngine:
    """Client for searching Qdrant vector database.
    
    This class provides an abstraction over the Qdrant client to perform
    vector searches with embedded queries.
    """
    
    def __init__(self):
        """Initialize the Qdrant client."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )
    
    async def search(
        self,
        collection_name: str,
        vector: List[float],
        filter_: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        with_vector: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for vectors in Qdrant.
        
        Args:
            collection_name: Name of the collection to search in.
            vector: Embedded query vector.
            filter_: Optional filter to apply to the search.
            limit: Maximum number of results to return.
            with_vector: Whether to include vectors in the response.
            
        Returns:
            List[Dict[str, Any]]: List of search results.
        """
        # Convert filter to Qdrant filter format if provided
        qdrant_filter = None
        if filter_:
            qdrant_filter = self._build_filter(filter_)
        
        # Perform the search
        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            query_filter=qdrant_filter,
            limit=limit,
            with_vectors=with_vector
        )
        
        # Format the results as plain dictionaries
        return [
            {
                "score": hit.score,
                "payload": hit.payload,
                "vector": hit.vector if with_vector else None,
            }
            for hit in search_result
        ]
         
    
    async def list_collections(self) -> List[str]:
        """List all collections in Qdrant.
        
        Returns:
            List[str]: List of collection names.
        """
        collections = self.client.get_collections()
        return [collection.name for collection in collections.collections]
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection.
        
        Args:
            collection_name: Name of the collection.
            
        Returns:
            Dict[str, Any]: Collection information.
        """
        try:
            collection_info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_info.name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": str(collection_info.status),
                "vector_size": collection_info.config.params.vectors.size,
                "vector_distance": str(collection_info.config.params.vectors.distance),
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in Qdrant.
        
        Args:
            collection_name: Name of the collection to check.
            
        Returns:
            bool: True if the collection exists, False otherwise.
        """
        try:
            collections = await self.list_collections()
            return collection_name in collections
        except Exception as e:
            logger.error(f"Error checking if collection {collection_name} exists: {str(e)}")
            return False
    
    def _build_filter(self, filter_: Dict[str, Any]) -> models.Filter:
        """Build a Qdrant filter from a dictionary.
        
        Args:
            filter_: Dictionary representation of the filter.
            
        Returns:
            models.Filter: Qdrant filter object.
        """
        # Handle 'must' conditions (AND)
        must_conditions = []
        if "must" in filter_:
            for condition in filter_["must"]:
                if "match" in condition:
                    must_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            match=models.MatchValue(value=condition["match"]["value"]),
                        )
                    )
                elif "range" in condition:
                    must_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            range=models.Range(
                                gt=condition["range"].get("gt"),
                                gte=condition["range"].get("gte"),
                                lt=condition["range"].get("lt"),
                                lte=condition["range"].get("lte"),
                            ),
                        )
                    )
        
        # Handle 'should' conditions (OR)
        should_conditions = []
        if "should" in filter_:
            for condition in filter_["should"]:
                if "match" in condition:
                    should_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            match=models.MatchValue(value=condition["match"]["value"]),
                        )
                    )
                elif "range" in condition:
                    should_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            range=models.Range(
                                gt=condition["range"].get("gt"),
                                gte=condition["range"].get("gte"),
                                lt=condition["range"].get("lt"),
                                lte=condition["range"].get("lte"),
                            ),
                        )
                    )
        
        # Handle 'must_not' conditions (NOT)
        must_not_conditions = []
        if "must_not" in filter_:
            for condition in filter_["must_not"]:
                if "match" in condition:
                    must_not_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            match=models.MatchValue(value=condition["match"]["value"]),
                        )
                    )
                elif "range" in condition:
                    must_not_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            range=models.Range(
                                gt=condition["range"].get("gt"),
                                gte=condition["range"].get("gte"),
                                lt=condition["range"].get("lt"),
                                lte=condition["range"].get("lte"),
                            ),
                        )
                    )
        
        # Combine all conditions into a filter
        return models.Filter(
            must=must_conditions if must_conditions else None,
            should=should_conditions if should_conditions else None,
            must_not=must_not_conditions if must_not_conditions else None,
        )