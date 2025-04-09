"""Service for ingesting documents into Qdrant."""

from typing import Any, Dict, List, Optional, Union

from app.qdrant.client import QdrantSearchEngine
from app.qdrant.embedding import EmbeddingService


class IngestionService:
    """Service for ingesting documents into Qdrant."""

    def __init__(self):
        """Initialize the ingestion service."""
        self.embedding_service = EmbeddingService()
        self.search_engine = QdrantSearchEngine()

    async def ingest_document(
        self,
        collection_name: str,
        document: Dict[str, Any],
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ingest a document into Qdrant.
        
        Args:
            collection_name: Name of the collection to ingest into.
            document: Document to ingest. Must contain 'content' and 'context' fields.
            id: Optional ID for the document. If not provided, one will be generated.
            
        Returns:
            Dict[str, Any]: Result of the ingestion operation.
        """
        # Validate document
        if "content" not in document:
            return {"error": "Document must contain 'content' field"}
        
        if "context" not in document:
            return {"error": "Document must contain 'context' field"}
        
        # Embed the document content
        embedded_content = self.embedding_service.embed_query(document["content"])
        
        # Prepare the point for Qdrant
        point = {
            "id": id,  # Will be auto-generated if None
            "vector": embedded_content,
            "payload": document,
        }
        
        # Upsert the point into Qdrant
        try:
            result = await self.search_engine.client.upsert(
                collection_name=collection_name,
                points=[point],
            )
            return {"status": "success", "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def batch_ingest_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Ingest multiple documents into Qdrant in a batch.
        
        Args:
            collection_name: Name of the collection to ingest into.
            documents: List of documents to ingest. Each must contain 'content' and 'context' fields.
            ids: Optional list of IDs for the documents. If not provided, they will be generated.
            
        Returns:
            Dict[str, Any]: Result of the batch ingestion operation.
        """
        # Validate documents
        for i, doc in enumerate(documents):
            if "content" not in doc:
                return {"error": f"Document at index {i} must contain 'content' field"}
            
            if "context" not in doc:
                return {"error": f"Document at index {i} must contain 'context' field"}
        
        # Embed all document contents
        contents = [doc["content"] for doc in documents]
        embedded_contents = self.embedding_service.embed_batch(contents)
        
        # Prepare points for Qdrant
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embedded_contents)):
            point_id = ids[i] if ids and i < len(ids) else None
            points.append({
                "id": point_id,  # Will be auto-generated if None
                "vector": embedding,
                "payload": doc,
            })
        
        # Upsert the points into Qdrant
        try:
            result = await self.search_engine.client.upsert(
                collection_name=collection_name,
                points=points,
            )
            return {"status": "success", "result": result}
        except Exception as e:
            return {"error": str(e)}