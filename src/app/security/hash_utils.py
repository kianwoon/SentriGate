"""Utilities for hashing and verifying API keys."""

import logging
from typing import Tuple
import secrets
import string

logger = logging.getLogger(__name__)

# Attempt to import bcrypt with a fallback
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    logger.error("bcrypt package is not installed. Hashing will not work properly.")
    logger.error("Please install bcrypt using: pip install bcrypt")
    BCRYPT_AVAILABLE = False
    
    # Mock bcrypt for development environments without crashing the application
    class MockBcrypt:
        @staticmethod
        def gensalt():
            return b'mock_salt'
        
        @staticmethod
        def hashpw(password, salt):
            return f"mock_hash_{password.decode()}".encode()
        
        @staticmethod
        def checkpw(password, hashed):
            # Always return False in mock mode
            return False
    
    bcrypt = MockBcrypt()


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt.

    Args:
        api_key: The API key to hash.

    Returns:
        str: The hashed API key.
    """
    if not BCRYPT_AVAILABLE:
        logger.warning("Using mock bcrypt - hash_api_key will not produce secure hashes!")
        
    # Convert string to bytes
    api_key_bytes = api_key.encode("utf-8")
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(api_key_bytes, salt)
    
    # Convert bytes back to string for storage
    return hashed_bytes.decode("utf-8")


def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key against a hashed API key.

    Args:
        api_key: The API key to verify.
        hashed_api_key: The hashed API key to verify against.

    Returns:
        bool: True if the API key matches the hash, False otherwise.
    """
    if not BCRYPT_AVAILABLE:
        logger.warning("Using mock bcrypt - verify_api_key will always return False!")
        return False
        
    # Convert strings to bytes
    api_key_bytes = api_key.encode("utf-8")
    hashed_bytes = hashed_api_key.encode("utf-8")
    
    # Check if the password matches the hash
    try:
        return bcrypt.checkpw(api_key_bytes, hashed_bytes)
    except Exception:
        return False


def generate_api_key(length: int = 32) -> Tuple[str, str]:
    """Generate a new API key and its hash.

    Args:
        length: The length of the API key to generate.

    Returns:
        Tuple[str, str]: The API key and its hash.
    """
    # Generate a random API key
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Hash the API key
    hashed_api_key = hash_api_key(api_key)
    
    return api_key, hashed_api_key