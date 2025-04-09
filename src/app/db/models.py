"""Database models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.session import Base
from app.core.config import settings


class Token(Base):
    """API key model.

    Attributes:
        id: Primary key UUID
        name: API key name
        description: Explanation of the API key's purpose
        hashed_token: Bcrypt hashed API key
        sensitivity: Security level (e.g., public, internal, confidential)
        is_active: Whether the key is active
        owner_email: Email of the key owner
        expiry: Expiration timestamp
        allow_rules: Rules to allow (e.g., context match)
        deny_rules: Rules to deny (takes precedence over allow_rules)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    hashed_token = Column(String(255), nullable=False)
    sensitivity = Column(String(50), nullable=False, default="internal")
    is_active = Column(Boolean, nullable=False, default=True)
    owner_email = Column(String(255), nullable=False)
    expiry = Column(DateTime, nullable=True)
    allow_rules = Column(JSONB, nullable=True)
    deny_rules = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_collection_name(self) -> str:
        """Get the collection name for this token.

        Returns:
            str: The collection name formatted as owner_email with @ and . replaced by _.
        """
        return f"{self.owner_email.replace('@', '_').replace('.', '_')}{settings.COLLECTION_NAME_SUFFIX}"

    def is_expired(self) -> bool:
        """Check if the API key is expired.

        Returns:
            bool: True if expired, False otherwise.
        """
        if self.expiry is None:
            return False
        # Make the comparison timezone-aware
        now_utc = datetime.utcnow()
        if self.expiry.tzinfo is None:
            # If self.expiry is naive, assume UTC
            return now_utc > self.expiry
        else:
            # If self.expiry is aware, convert now_utc to aware as well
            import pytz
            utc_timezone = pytz.utc
            now_utc_aware = utc_timezone.localize(now_utc)
            return now_utc_aware > self.expiry

    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired).

        Returns:
            bool: True if valid, False otherwise.
        """
        return self.is_active and not self.is_expired()