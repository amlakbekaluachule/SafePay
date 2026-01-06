"""Transaction database model."""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, JSON, Index
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Transaction(Base):
    """Transaction model for storing credit card transactions."""
    
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    card_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    merchant_id = Column(String, nullable=False, index=True)
    merchant_category = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)  # purchase, withdrawal, etc.
    location_country = Column(String, nullable=False)
    location_city = Column(String)
    ip_address = Column(String)
    device_id = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Raw features stored for audit
    raw_features = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_card_timestamp', 'card_id', 'timestamp'),
    )

