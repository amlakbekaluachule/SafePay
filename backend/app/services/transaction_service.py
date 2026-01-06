"""Transaction service for managing transactions."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from app.models.transaction import Transaction
from app.models.prediction import Prediction


class TransactionService:
    """Service for transaction operations."""
    
    @staticmethod
    def create_transaction(db: Session, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(**transaction_data)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def get_transaction(db: Session, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    @staticmethod
    def get_user_history(
        db: Session, 
        user_id: str, 
        days: int = 30,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get user's transaction history as DataFrame for feature engineering.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days of history to retrieve
            limit: Maximum number of transactions
            
        Returns:
            DataFrame with transaction history
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.timestamp >= cutoff_date
        ).order_by(desc(Transaction.timestamp)).limit(limit).all()
        
        if not transactions:
            return pd.DataFrame()
        
        data = []
        for txn in transactions:
            data.append({
                'id': txn.id,
                'amount': txn.amount,
                'merchant_category': txn.merchant_category,
                'location_country': txn.location_country,
                'timestamp': txn.timestamp,
            })
        
        df = pd.DataFrame(data)
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    @staticmethod
    def get_recent_transactions(
        db: Session,
        limit: int = 100,
        user_id: Optional[str] = None,
        is_fraud: Optional[bool] = None
    ) -> List[Transaction]:
        """Get recent transactions with optional filters."""
        query = db.query(Transaction)
        
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        if is_fraud is not None:
            query = query.join(Prediction).filter(Prediction.is_fraud == is_fraud)
        
        return query.order_by(desc(Transaction.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_transaction_stats(db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get transaction statistics for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        total = db.query(Transaction).filter(Transaction.timestamp >= cutoff).count()
        
        fraud_count = db.query(Transaction).join(Prediction).filter(
            Transaction.timestamp >= cutoff,
            Prediction.is_fraud == True
        ).count()
        
        total_amount = db.query(Transaction).filter(
            Transaction.timestamp >= cutoff
        ).with_entities(
            db.func.sum(Transaction.amount)
        ).scalar() or 0.0
        
        fraud_amount = db.query(Transaction).join(Prediction).filter(
            Transaction.timestamp >= cutoff,
            Prediction.is_fraud == True
        ).with_entities(
            db.func.sum(Transaction.amount)
        ).scalar() or 0.0
        
        return {
            'total_transactions': total,
            'fraud_transactions': fraud_count,
            'fraud_rate': fraud_count / total if total > 0 else 0.0,
            'total_amount': float(total_amount),
            'fraud_amount': float(fraud_amount),
            'time_window_hours': hours
        }

