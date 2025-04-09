"""General vector search endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Token
from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.auth_service import get_current_api_key
from app.services.query_service import QueryService


router = APIRouter(prefix="/search", tags=["Vector Search"])


@router.post("", response_model=QueryResponse)
async def search_collection(
    query_request: QueryRequest,
    api_key: Token = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db), 
) -> QueryResponse:
    """Search a collection based on context and query.
    
    Args:
        query_request: The query request containing context and search query.
        api_key: The authenticated API key.
        db: Database session.
        
    Returns:
        QueryResponse: The search results.
        
    Raises:
        HTTPException: If the API key is not authorized for the requested context.
    """
    # Check if the API key is authorized for the requested context
    # auth_service = AuthService(db)
    
    
    # Construct the collection name
    full_collection_name = api_key.get_collection_name()

    # Process the query
    query_service = QueryService()
    
    return await query_service.process_query(full_collection_name, query_request, api_key)
    