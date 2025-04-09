"""Query service for vector search."""

from typing import Any, Dict

from app.db.models import Token
from app.qdrant.client import QdrantSearchEngine
from app.qdrant.embedding import EmbeddingService
from app.schemas.query import QueryRequest, QueryResponse, ResponseItem
import logging  # Import logging

logger = logging.getLogger(__name__)  # Initialize logger


class QueryService:
    """Service for handling vector search queries."""

    def __init__(self):
        """Initialize the query service."""
        self.embedding_service = EmbeddingService()
        self.search_engine = QdrantSearchEngine()

    async def process_query(self, collection_name: str, query_request: QueryRequest, api_key: Token) -> QueryResponse:
        """Process a vector search query.
        
        Args:
            collection_name: Name of the collection to search in.
            query_request: The query request.
            
        Returns:
            QueryResponse: The query response.
        """

        #check collection name exist in qdrant first
        if not await self.search_engine.collection_exists(collection_name):
            logger.error(f"Collection {collection_name} does not exist.")
            return QueryResponse(response=[])

        # Embed the query


        embedded_query = self.embedding_service.embed_query(query_request.query)
        
        logger.debug(f"Embedded query: {query_request.query} -> {embedded_query}")

        # Build filter based on context
        filter_ = self._build_filter(query_request, api_key)
        
        # Search Qdrant with error handling
        try:
            search_results = await self.search_engine.search(
                collection_name=collection_name,
                vector=embedded_query,
                filter_=filter_,
                limit=query_request.top_k,
            )
            
            # Format the results with the correct schema
            response_items = [
                ResponseItem(
                    score=result["score"],
                    type="text",
                    text=f'{{"pageContent":"{result["payload"].get("content", "")}"}}'
                )
                for result in search_results
            ]
            logger.info(f"Search results: {response_items}")
        except Exception as e:
            logger.error(f"Error searching collection {collection_name}: {str(e)}")
            # Return a friendly error message
            response_items = [ 
            ]
        
        return QueryResponse(response=response_items)

    def _build_filter(self, query_request: QueryRequest, api_key: Token) -> Dict[str, Any]:
        """Build a filter for Qdrant search based on the query request and API key rules.
        
        Args:
            query_request: The query request.
            api_key: The API key object with allow/deny rules.
            
        Returns:
            Dict[str, Any]: The filter dictionary.
        """
        filter_ = {}
        must_conditions = []

        # Apply sensitivity filter - correct the path to match the actual data structure
        must_conditions.append({"key": "metadata.sensitivity", "match": {"value": api_key.sensitivity}})

        # Apply metadata filter
        # # Apply allow rules
        # if api_key.allow_rules:
        #     allow_values = []
        #     for rule in api_key.allow_rules:
        #         if rule["field"] == "context":
        #             allow_values.extend(rule["values"])
        #     if allow_values:
        #         must_conditions.append({"key": "context", "match": {"value": query_request.context}})

        # # Apply deny rules
        # if api_key.deny_rules:
        #     must_not_conditions = []
        #     for rule in api_key.deny_rules:
        #         if rule["field"] == "context":
        #             for value in rule["values"]:
        #                 must_not_conditions.append({"key": "context", "match": {"value": value}})
        #     if must_not_conditions:
        #         filter_["must_not"] = must_not_conditions

        if must_conditions:
            filter_["must"] = must_conditions
        
        # Add additional filters if provided
        if query_request.filter:
            if "must" in query_request.filter:
                if "must" in filter_:
                    filter_["must"].extend(query_request.filter["must"])
                else:
                    filter_["must"] = query_request.filter["must"]
            
            for key in ["should", "must_not"]:
                if key in query_request.filter:
                    filter_[key] = query_request.filter[key]
        
        return filter_