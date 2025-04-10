"""Authentication and authorization service."""

from datetime import datetime
from typing import Dict, Optional, Tuple, Any, ClassVar

import bcrypt
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time

from app.core.config import settings
from app.db.models import Token
from app.db.session import get_db
from app.rules.rule_checker import RuleChecker

logger = logging.getLogger(__name__)


class AuthService:
    """Service for API key authentication and authorization."""
    
    # Simple class-level cache with token expiration
    _api_key_cache: ClassVar[Dict[str, Tuple[float, Tuple[bool, Optional[Token]]]]] = {}
    _cache_ttl: ClassVar[int] = 10  # Cache TTL in seconds
    
    def __init__(self, db: AsyncSession):
        """Initialize the auth service.
        
        Args:
            db: Database session.
        """
        self.db = db

    async def authenticate_api_key(self, api_key: str) -> Tuple[bool, Optional[Token]]:
        """Authenticate an API key."""
        logger.debug("Authenticating API key")

        if not api_key:
            logger.debug("API key is empty.")
            return False, None
        
        # Check cache first
        current_time = time.time()
        if api_key in self.__class__._api_key_cache:
            timestamp, result = self.__class__._api_key_cache[api_key]
            if current_time - timestamp < self.__class__._cache_ttl:
                logger.debug("Using cached API key result")
                return result
            else:
                # Remove expired cache entry
                del self.__class__._api_key_cache[api_key]

        # Query the database for the API key
        try:
            # Use only columns that definitely exist in the database
            columns = [
                Token.id, Token.name, Token.description, Token.hashed_token,
                Token.sensitivity, Token.is_active, Token.owner_email,
                Token.expiry, Token.allow_rules, Token.deny_rules,
                Token.created_at
            ]
            
            query = select(*columns).where(Token.is_active, Token.expiry >= datetime.now())
            logger.debug(f"Executing query: {query}")
            result = await self.db.execute(query)
            
            # Need to use all() instead of scalars().all() when selecting specific columns
            rows = result.all()
 
            for row in rows:
                # Create a Token object with the values from the row
                token = Token(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    hashed_token=row.hashed_token,
                    sensitivity=row.sensitivity,
                    is_active=row.is_active,
                    owner_email=row.owner_email,
                    expiry=row.expiry,
                    allow_rules=row.allow_rules,
                    deny_rules=row.deny_rules,
                    created_at=row.created_at
                )
                
                # Check if this token matches the API key
                hashed_token_bytes = token.hashed_token.encode('utf-8') if isinstance(token.hashed_token, str) else token.hashed_token
                
                # Use constant-time comparison to prevent timing attacks
                start_time = time.time()
                if bcrypt.checkpw(api_key.encode('utf-8'), hashed_token_bytes):
                    verification_time = time.time() - start_time
                    logger.debug(f"bcrypt verification took {verification_time:.4f} seconds")
                    
                    # Cache successful result
                    self.__class__._api_key_cache[api_key] = (current_time, (True, token))
                    logger.debug(f"Retrieved API key from database, name: {token.owner_email}")
                    return True, token
                
        except Exception as e:
            logger.error(f"Error querying API key: {e}")
            return False, None

        return False, None

    async def authorize_context(self, api_key: Token, context: Dict[str, Any]) -> bool:
        """Authorize a context based on API key rules.
        
        Args:
            api_key: The API key to check rules against.
            context: The context to authorize.
            
        Returns:
            bool: True if authorized, False otherwise.
        """
        return RuleChecker.check_rules(
            context=context,
            allow_rules=api_key.allow_rules,
            deny_rules=api_key.deny_rules,
        )


async def get_current_api_key(
    db: AsyncSession = Depends(get_db),  # db first
    x_api_key: str = Header(None, alias=settings.API_KEY_HEADER_NAME),  # then header
) -> Token:
    """Dependency for getting the current API key.
    
    Args:
        db: Database session.
        x_api_key: The API key from the request header.
        
    Returns:
        Token: The authenticated API key.
        
    Raises:
        HTTPException: If the API key is invalid or unauthorized.
    """
    auth_service = AuthService(db)
    
    # Check if API key is provided
    if not x_api_key:  # check x_api_key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": f"Bearer realm=\"API key\" header=\"{settings.API_KEY_HEADER_NAME}\""},
        )
    
    # Authenticate the API key
    is_authenticated, db_api_key = await auth_service.authenticate_api_key(x_api_key)  # use x_api_key
    
    if not is_authenticated or not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": f"Bearer realm=\"API key\" header=\"{settings.API_KEY_HEADER_NAME}\""},
        )
    
    return db_api_key