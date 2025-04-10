"""Database models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

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

    id = Column(Integer, primary_key=True, autoincrement=True)
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


class AuditLog(Base):
    """Audit log model for tracking queries and responses.
    
    Attributes:
        id: Primary key integer (auto-incrementing)
        token_id: Foreign key to the API token used
        collection_name: Name of the collection queried
        query_text: The actual query text
        filter_data: The filters applied to the query
        result_count: Number of results returned
        response_data: The full response data returned
        execution_time_ms: Query execution time in milliseconds
        created_at: When the query was executed
    """
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    collection_name = Column(String(255), nullable=False)
    query_text = Column(Text, nullable=False)
    filter_data = Column(JSONB, nullable=True)
    result_count = Column(Integer, default=0)
    response_data = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to Token
    token = relationship("Token", back_populates="audit_logs")


# Add relationship to Token class
Token.audit_logs = relationship("AuditLog", back_populates="token")