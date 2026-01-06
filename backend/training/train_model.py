"""Train fraud detection model."""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
import joblib
import json
from pathlib import Path
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_synthetic_data(n_samples: int = 10000, fraud_rate: float = 0.05) -> pd.DataFrame:
    """
    Generate synthetic transaction data for training.
    
    In production, this would load from your actual data source.
    """
    np.random.seed(42)
    
    n_fraud = int(n_samples * fraud_rate)
    n_normal = n_samples - n_fraud
    
    data = []
    
    # Normal transactions
    for _ in range(n_normal):
        data.append({
            'amount': np.random.lognormal(3, 1),
            'hour': np.random.randint(0, 24),
            'day_of_week': np.random.randint(0, 7),
            'is_weekend': np.random.choice([0, 1], p=[0.7, 0.3]),
            'is_night': np.random.choice([0, 1], p=[0.8, 0.2]),
            'merchant_category_encoded': np.random.random(),
            'transaction_type_encoded': np.random.random(),
            'location_country_encoded': np.random.random(),
            'transactions_24h': np.random.poisson(2),
            'transactions_7d': np.random.poisson(10),
            'avg_amount_7d': np.random.lognormal(3, 0.5),
            'amount_ratio_7d_avg': np.random.lognormal(0, 0.3),
            'location_change': np.random.choice([0, 1], p=[0.9, 0.1]),
            'unusual_merchant': np.random.choice([0, 1], p=[0.8, 0.2]),
            'avg_time_between_transactions': np.random.uniform(2, 48),
            'has_device_id': 1,
            'has_ip_address': 1,
            'is_fraud': 0
        })
    
    # Fraud transactions (different patterns)
    for _ in range(n_fraud):
        data.append({
            'amount': np.random.lognormal(4, 1.5),  # Higher amounts
            'hour': np.random.choice([22, 23, 0, 1, 2, 3], p=[0.15, 0.15, 0.15, 0.15, 0.2, 0.2]),  # More at night
            'day_of_week': np.random.randint(0, 7),
            'is_weekend': np.random.choice([0, 1], p=[0.5, 0.5]),
            'is_night': np.random.choice([0, 1], p=[0.3, 0.7]),  # More at night
            'merchant_category_encoded': np.random.random(),
            'transaction_type_encoded': np.random.random(),
            'location_country_encoded': np.random.random(),
            'transactions_24h': np.random.poisson(5),  # Higher velocity
            'transactions_7d': np.random.poisson(20),
            'avg_amount_7d': np.random.lognormal(2.5, 0.5),
            'amount_ratio_7d_avg': np.random.lognormal(1, 0.8),  # Higher ratio
            'location_change': np.random.choice([0, 1], p=[0.3, 0.7]),  # More location changes
            'unusual_merchant': np.random.choice([0, 1], p=[0.4, 0.6]),  # More unusual merchants
            'avg_time_between_transactions': np.random.uniform(0.5, 4),  # Faster transactions
            'has_device_id': np.random.choice([0, 1], p=[0.3, 0.7]),  # Sometimes missing
            'has_ip_address': np.random.choice([0, 1], p=[0.2, 0.8]),
            'is_fraud': 1
        })
    
    df = pd.DataFrame(data)
    df['amount_log'] = np.log1p(df['amount'])
    
    return df


def train_model():
    """Train fraud detection model."""
    logger.info("Generating synthetic training data...")
    df = generate_synthetic_data(n_samples=20000, fraud_rate=0.05)
    
    # Feature columns
    feature_cols = [
        'amount', 'amount_log', 'hour', 'day_of_week', 'is_weekend', 'is_night',
        'merchant_category_encoded', 'transaction_type_encoded', 'location_country_encoded',
        'transactions_24h', 'transactions_7d', 'avg_amount_7d', 'amount_ratio_7d_avg',
        'location_change', 'unusual_merchant', 'avg_time_between_transactions',
        'has_device_id', 'has_ip_address'
    ]
    
    X = df[feature_cols]
    y = df['is_fraud']
    
    logger.info(f"Training data shape: {X.shape}")
    logger.info(f"Fraud rate: {y.mean():.2%}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train XGBoost model (best for fraud detection)
    logger.info("Training XGBoost model...")
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss',
        scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=20,
        verbose=False
    )
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    logger.info("\nClassification Report:")
    logger.info(classification_report(y_test, y_pred))
    
    logger.info("\nConfusion Matrix:")
    logger.info(confusion_matrix(y_test, y_pred))
    
    auc_score = roc_auc_score(y_test, y_pred_proba)
    logger.info(f"\nROC-AUC Score: {auc_score:.4f}")
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "fraud_detector.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Save feature metadata
    feature_metadata = {
        "feature_names": feature_cols,
        "model_type": "XGBoost",
        "n_features": len(feature_cols),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "auc_score": float(auc_score),
        "fraud_rate": float(y.mean())
    }
    
    metadata_path = model_dir / "feature_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(feature_metadata, f, indent=2)
    logger.info(f"Feature metadata saved to {metadata_path}")
    
    return model, feature_metadata


if __name__ == "__main__":
    train_model()

