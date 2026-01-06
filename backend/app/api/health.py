"""Health check endpoints."""
from fastapi import APIRouter
from typing import Dict, Any
from app.ml.fraud_detector import FraudDetector
from app.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check."""
    return {"status": "healthy", "service": "safepay-api"}


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check including model availability."""
    try:
        detector = FraudDetector(settings.MODEL_PATH, settings.FEATURE_METADATA_PATH)
        model_loaded = detector.model is not None
        return {
            "status": "ready" if model_loaded else "not_ready",
            "model_loaded": model_loaded,
            "model_version": detector.model_version
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "model_loaded": False,
            "error": str(e)
        }

