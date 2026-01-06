"""Audit log database model."""
from sqlalchemy import Column, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.database import Base
import uuid


class AuditLog(Base):
    """Audit log for tracking all system actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String, nullable=False, index=True)  # predict, train_model, update_threshold, etc.
    entity_type = Column(String, nullable=False)  # transaction, prediction, model, etc.
    entity_id = Column(String, nullable=True, index=True)
    user_id = Column(String, nullable=True)
    details = Column(JSON)  # Additional context
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_entity', 'entity_type', 'entity_id'),
    )

