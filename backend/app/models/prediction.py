"""Prediction database model."""
from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Prediction(Base):
    """Prediction model for storing fraud detection predictions."""
    
    __tablename__ = "predictions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False, unique=True, index=True)
    fraud_probability = Column(Float, nullable=False, index=True)
    is_fraud = Column(Boolean, nullable=False, index=True)
    threshold = Column(Float, default=0.5)
    
    # Model explainability
    shap_values = Column(JSON)  # Feature importance scores
    feature_contributions = Column(JSON)  # Human-readable feature contributions
    
    # Model metadata
    model_version = Column(String, nullable=False)
    inference_time_ms = Column(Float)
    
    # Ground truth (if available later)
    actual_label = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    transaction = relationship("Transaction", backref="prediction")
    
    __table_args__ = (
        Index('idx_fraud_timestamp', 'is_fraud', 'created_at'),
        Index('idx_model_version', 'model_version'),
    )

