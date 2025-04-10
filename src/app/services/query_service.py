"""Query service for vector search."""

from typing import Any, Dict
import time


from app.db.models import Token, AuditLog
from app.db.session import async_session_factory
from app.qdrant.client import QdrantSearchEngine
from app.qdrant.embedding import EmbeddingService
from app.schemas.query import QueryRequest, QueryResponse, ResponseItem
import logging  # Import logging

logger = logging.getLogger(__name__)  # Initialize logger

async def log_query_audit(token: Token, collection_name: str, query_request: QueryRequest, 
                    response: QueryResponse, execution_time_ms: int) -> None:
    """Log query execution to the audit log table.
    
    Args:
        token: The API token used for the query
        collection_name: Name of the collection queried
        query_request: The original query request
        response: The query response object
        execution_time_ms: Query execution time in milliseconds
    """
    try:
        # Create a new audit log entry
        audit_log = AuditLog(
            token_id=token.id,
            collection_name=collection_name,
            query_text=query_request.query,
            filter_data="allow_rules:" + str(token.allow_rules) + ", deny_rules:" + str(token.deny_rules),
            result_count=len(response.response),
            response_data=response.model_dump_json(),
            execution_time_ms=execution_time_ms,
        )
        
        # Create a new session for audit logging
        async with async_session_factory() as session:
            session.add(audit_log)
            await session.commit()
            
        logger.debug(f"Audit log created for query in collection {collection_name}")
    except Exception as e:
        # Don't let audit logging failures affect the main application flow
        logger.error(f"Failed to save audit log: {str(e)}")


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
        # Start timing the execution
        start_time = time.time()
        response_items = []

        # Check collection name exist in qdrant first
        if not await self.search_engine.collection_exists(collection_name):
            logger.error(f"Collection {collection_name} does not exist.")
            response = QueryResponse(response=response_items)
            
            # Log the query even when collection doesn't exist
            execution_time_ms = int((time.time() - start_time) * 1000)
            await log_query_audit(api_key, collection_name, query_request, response, execution_time_ms)
            
            return response

        # Embed the query
        embedded_query = self.embedding_service.embed_query(query_request.query)
        
        logger.debug(f"Embedded query: {query_request.query} -> {embedded_query}")

              

        # Build filter based on context
        filter_ = self._build_filter(query_request, api_key)
        
        # Search Qdrant with error handling
        try:
            # Make sure we're getting raw dictionaries, not SearchResultItem objects
            search_results = await self.search_engine.search(
                collection_name=collection_name,
                vector=embedded_query,
                filter_=filter_,  # Changed from filter_ to query_filter to match QdrantSearchEngine.search() parameter name
                limit=query_request.top_k,
                with_vector=True  # Make sure vectors are included for similarity checks
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
            # Response_items remains empty
        
        # Create the response object
        response = QueryResponse(response=response_items)
        
        # Calculate execution time and log the audit entry
        execution_time_ms = int((time.time() - start_time) * 1000)
        await log_query_audit(api_key, collection_name, query_request, response, execution_time_ms)
        
        return response

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
        must_not_conditions = []

        # Apply sensitivity filter - correct the path to match the actual data structure
        must_conditions.append({"key": "metadata.sensitivity", "match": {"value": api_key.sensitivity}})

        if api_key.allow_rules:
            for allow_rule in api_key.allow_rules:
                must_conditions.append({"key": "metadata.tags", "match": {"value": allow_rule}})
            logger.info(f"Allow rules: {api_key.allow_rules}")

        if api_key.deny_rules:
            for deny_rule in api_key.deny_rules:
                must_not_conditions.append({"key": "metadata.tags", "match": {"value": deny_rule}})
            logger.info(f"Deny rules: {api_key.deny_rules}")
 
 
        if must_conditions:
            filter_["must"] = must_conditions

        if must_not_conditions:
            filter_["must_not"] = must_not_conditions
        

        return filter_
