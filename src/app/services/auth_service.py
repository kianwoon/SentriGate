"""Authentication and authorization service."""

from datetime import datetime
from typing import Dict, Optional, Tuple, Any

import bcrypt
from fastapi import Depends, HTTPException, status, Header  # Added Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging  # Import logging

from app.core.config import settings
from app.db.models import Token
from app.db.session import get_db
from app.rules.rule_checker import RuleChecker

logger = logging.getLogger(__name__)  # Initialize logger


class AuthService:
    """Service for API key authentication and authorization."""

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

        # Hash the API key
        # hashed_value = bcrypt.hashpw(api_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # hashed_api_key = f"$2b$12$A.Enz7z/SGPtUufTM7uTV.0RsJX2Z/5fDIiXb9jxXD413qnqRS9F2" #pi_key = f"$2b$12$YzXa9rxIU8KCVulRfkqLfObyBkEZEthw6/9H/qbfSOej1zJQmjSPG" # hash_api_key(api_key)
        # logger.debug(f"Hashed API key: {hashed_api_key}")

        # Query the database for the API key
        try:
            query = select(Token).where(Token.is_active, Token.expiry >= datetime.now())   
            result = await self.db.execute(query)
            all_tokens = result.scalars().all()
 
            for token in all_tokens:
                # Ensure hashed_token is bytes if bcrypt expects bytes
                hashed_token_bytes = token.hashed_token.encode('utf-8') if isinstance(token.hashed_token, str) else token.hashed_token
                if bcrypt.checkpw(api_key.encode('utf-8'), hashed_token_bytes):                    
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