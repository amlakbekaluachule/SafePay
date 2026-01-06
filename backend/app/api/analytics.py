"""Analytics endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.transaction_service import TransactionService
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.get("/stats")
async def get_stats(
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get transaction statistics for the last N hours."""
    stats = TransactionService.get_transaction_stats(db, hours=hours)
    return stats


@router.get("/model-metrics")
async def get_model_metrics(
    model_version: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get model performance metrics."""
    metrics = PredictionService.get_model_metrics(db, model_version=model_version)
    return metrics


@router.get("/fraud-trends")
async def get_fraud_trends(
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get fraud trends over time."""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from app.models.transaction import Transaction
    from app.models.prediction import Prediction
    
    cutoff = datetime.now() - timedelta(hours=hours)
    
    hourly_fraud = db.query(
        func.date_trunc('hour', Transaction.timestamp).label('hour'),
        func.count(Transaction.id).label('total'),
        func.sum(func.cast(Prediction.is_fraud, db.Integer)).label('fraud_count')
    ).join(
        Prediction, Transaction.id == Prediction.transaction_id
    ).filter(
        Transaction.timestamp >= cutoff
    ).group_by(
        func.date_trunc('hour', Transaction.timestamp)
    ).order_by('hour').all()
    
    return [
        {
            "hour": hour.isoformat(),
            "total_transactions": total,
            "fraud_transactions": fraud_count,
            "fraud_rate": fraud_count / total if total > 0 else 0.0
        }
        for hour, total, fraud_count in hourly_fraud
    ]

