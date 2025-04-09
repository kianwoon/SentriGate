"""Text embedding service for vector search using OpenAI."""

from typing import List
import logging

from openai import OpenAI

from app.core.config import settings

class EmbeddingService:
    """Service for embedding text queries using OpenAI.
    
    This class provides functionality to convert text queries into
    vector embeddings using OpenAI's embedding models.
    """
    
    def __init__(self, model_name: str = None):
        """Initialize the embedding service.
        
        Args:
            model_name: Name of the OpenAI embedding model to use.
                        Defaults to the model specified in settings.
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        logging.info(f"Initialized EmbeddingService with model: {self.model_name}")
        logging.info(f"Initialized EmbeddingService with model: {settings.OPENAI_API_KEY}")
    
    def embed_query(self, query: str) -> List[float]:
        """Embed a text query into a vector using OpenAI.
        
        Args:
            query: The text query to embed.
            
        Returns:
            List[float]: The embedded vector.
        """
        try:
            response = self.client.embeddings.create(
                input=query,
                model=self.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error embedding query: {e}")
            # Return a zero vector as fallback (dimension depends on the model)
            # text-embedding-3-small has 1536 dimensions
            return [0.0] * 1536
    
    def embed_batch(self, queries: List[str]) -> List[List[float]]:
        """Embed multiple text queries into vectors using OpenAI.
        
        Args:
            queries: List of text queries to embed.
            
        Returns:
            List[List[float]]: List of embedded vectors.
        """
        if not queries:
            return []
            
        try:
            response = self.client.embeddings.create(
                input=queries,
                model=self.model_name
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logging.error(f"Error embedding batch: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 1536 for _ in queries]