"""Prediction endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.requests import Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.database import get_db
from app.ml.fraud_detector import FraudDetector
from app.config import settings
from app.services.transaction_service import TransactionService
from app.services.prediction_service import PredictionService
from app.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

_fraud_detector: Optional[FraudDetector] = None


def get_fraud_detector() -> FraudDetector:
    """Get or create fraud detector instance."""
    global _fraud_detector
    if _fraud_detector is None:
        _fraud_detector = FraudDetector(
            settings.MODEL_PATH,
            settings.FEATURE_METADATA_PATH
        )
    return _fraud_detector


class TransactionRequest(BaseModel):
    """Transaction prediction request."""
    user_id: str = Field(..., description="User ID")
    card_id: str = Field(..., description="Card ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    merchant_id: str = Field(..., description="Merchant ID")
    merchant_category: str = Field(..., description="Merchant category")
    transaction_type: str = Field(default="purchase", description="Transaction type")
    location_country: str = Field(..., description="Country code")
    location_city: Optional[str] = Field(None, description="City name")
    ip_address: Optional[str] = Field(None, description="IP address")
    device_id: Optional[str] = Field(None, description="Device ID")
    threshold: float = Field(default=0.5, ge=0, le=1, description="Fraud detection threshold")
    include_explainability: bool = Field(default=True, description="Include SHAP explainability")


class PredictionResponse(BaseModel):
    """Prediction response."""
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    threshold: float
    model_version: str
    inference_time_ms: float
    explainability: Optional[Dict[str, Any]] = None


@router.post("/", response_model=PredictionResponse)
async def predict_fraud(
    request: TransactionRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    fraud_detector: FraudDetector = Depends(get_fraud_detector)
):
    """
    Predict fraud for a transaction.
    
    Returns fraud probability, prediction, and explainability.
    """
    try:
        user_history = TransactionService.get_user_history(db, request.user_id, days=30)
        
        transaction_data = request.dict()
        transaction_data['timestamp'] = transaction_data.get('timestamp') or None
        
        transaction = TransactionService.create_transaction(db, transaction_data)
        
        prediction_result = fraud_detector.predict(
            transaction_data,
            user_history=user_history if not user_history.empty else None,
            threshold=request.threshold,
            include_explainability=request.include_explainability
        )
        
        prediction = PredictionService.create_prediction(
            db,
            transaction.id,
            prediction_result
        )
        
        client_ip = http_request.client.host if http_request and http_request.client else None
        AuditService.log_action(
            db,
            action="predict",
            entity_type="transaction",
            entity_id=transaction.id,
            user_id=request.user_id,
            details={
                "fraud_probability": prediction_result['fraud_probability'],
                "is_fraud": prediction_result['is_fraud'],
                "amount": request.amount
            },
            ip_address=client_ip,
            user_agent=http_request.headers.get("user-agent") if http_request else None
        )
        
        return PredictionResponse(
            transaction_id=transaction.id,
            fraud_probability=prediction_result['fraud_probability'],
            is_fraud=prediction_result['is_fraud'],
            threshold=prediction_result['threshold'],
            model_version=prediction_result['model_version'],
            inference_time_ms=prediction_result['inference_time_ms'],
            explainability={
                "shap_values": prediction_result.get('shap_values', {}),
                "feature_contributions": prediction_result.get('feature_contributions', {})
            } if request.include_explainability else None
        )
        
    except Exception as e:
        logger.error(f"Error in fraud prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/{transaction_id}")
async def get_prediction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get prediction for a transaction."""
    prediction = PredictionService.get_prediction(db, transaction_id)
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return {
        "transaction_id": prediction.transaction_id,
        "fraud_probability": prediction.fraud_probability,
        "is_fraud": prediction.is_fraud,
        "threshold": prediction.threshold,
        "model_version": prediction.model_version,
        "inference_time_ms": prediction.inference_time_ms,
        "shap_values": prediction.shap_values,
        "feature_contributions": prediction.feature_contributions,
        "created_at": prediction.created_at.isoformat()
    }

