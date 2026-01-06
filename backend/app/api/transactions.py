"""Transaction endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.transaction_service import TransactionService
from app.models.transaction import Transaction

router = APIRouter()


@router.get("/")
async def get_transactions(
    limit: int = Query(default=100, le=1000),
    user_id: Optional[str] = Query(None),
    is_fraud: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get recent transactions with optional filters."""
    transactions = TransactionService.get_recent_transactions(
        db, limit=limit, user_id=user_id, is_fraud=is_fraud
    )
    
    return [
        {
            "id": txn.id,
            "user_id": txn.user_id,
            "card_id": txn.card_id,
            "amount": txn.amount,
            "currency": txn.currency,
            "merchant_id": txn.merchant_id,
            "merchant_category": txn.merchant_category,
            "transaction_type": txn.transaction_type,
            "location_country": txn.location_country,
            "location_city": txn.location_city,
            "timestamp": txn.timestamp.isoformat(),
            "created_at": txn.created_at.isoformat()
        }
        for txn in transactions
    ]


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific transaction."""
    transaction = TransactionService.get_transaction(db, transaction_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "id": transaction.id,
        "user_id": transaction.user_id,
        "card_id": transaction.card_id,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "merchant_id": transaction.merchant_id,
        "merchant_category": transaction.merchant_category,
        "transaction_type": transaction.transaction_type,
        "location_country": transaction.location_country,
        "location_city": transaction.location_city,
        "ip_address": transaction.ip_address,
        "device_id": transaction.device_id,
        "timestamp": transaction.timestamp.isoformat(),
        "created_at": transaction.created_at.isoformat()
    }

