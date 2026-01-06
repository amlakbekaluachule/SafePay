"""Prediction service for managing fraud predictions."""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.models.prediction import Prediction
from app.models.transaction import Transaction


class PredictionService:
    """Service for prediction operations."""
    
    @staticmethod
    def create_prediction(
        db: Session,
        transaction_id: str,
        prediction_result: Dict[str, Any]
    ) -> Prediction:
        """Create a new prediction record."""
        prediction = Prediction(
            transaction_id=transaction_id,
            fraud_probability=prediction_result['fraud_probability'],
            is_fraud=prediction_result['is_fraud'],
            threshold=prediction_result.get('threshold', 0.5),
            shap_values=prediction_result.get('shap_values', {}),
            feature_contributions=prediction_result.get('feature_contributions', {}),
            model_version=prediction_result.get('model_version', '1.0.0'),
            inference_time_ms=prediction_result.get('inference_time_ms', 0.0)
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction
    
    @staticmethod
    def get_prediction(db: Session, transaction_id: str) -> Optional[Prediction]:
        """Get prediction for a transaction."""
        return db.query(Prediction).filter(
            Prediction.transaction_id == transaction_id
        ).first()
    
    @staticmethod
    def update_ground_truth(
        db: Session,
        transaction_id: str,
        actual_label: bool
    ) -> Optional[Prediction]:
        """Update prediction with ground truth label."""
        prediction = db.query(Prediction).filter(
            Prediction.transaction_id == transaction_id
        ).first()
        
        if prediction:
            prediction.actual_label = actual_label
            db.commit()
            db.refresh(prediction)
        
        return prediction
    
    @staticmethod
    def get_model_metrics(db: Session, model_version: Optional[str] = None) -> Dict[str, Any]:
        """Get model performance metrics."""
        query = db.query(Prediction)
        
        if model_version:
            query = query.filter(Prediction.model_version == model_version)
        
        total = query.count()
        
        if total == 0:
            return {
                'total_predictions': 0,
                'fraud_predictions': 0,
                'avg_fraud_probability': 0.0,
                'avg_inference_time_ms': 0.0
            }
        
        fraud_count = query.filter(Prediction.is_fraud == True).count()
        
        avg_prob = query.with_entities(
            db.func.avg(Prediction.fraud_probability)
        ).scalar() or 0.0
        
        avg_inference_time = query.with_entities(
            db.func.avg(Prediction.inference_time_ms)
        ).scalar() or 0.0
        
        with_truth = query.filter(Prediction.actual_label.isnot(None))
        accuracy = None
        if with_truth.count() > 0:
            correct = with_truth.filter(
                Prediction.is_fraud == Prediction.actual_label
            ).count()
            accuracy = correct / with_truth.count()
        
        return {
            'total_predictions': total,
            'fraud_predictions': fraud_count,
            'fraud_rate': fraud_count / total if total > 0 else 0.0,
            'avg_fraud_probability': float(avg_prob),
            'avg_inference_time_ms': float(avg_inference_time),
            'accuracy': float(accuracy) if accuracy is not None else None
        }

