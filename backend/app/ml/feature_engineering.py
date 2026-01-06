"""Feature engineering for fraud detection."""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import json


class FeatureEngineer:
    """Engineers features from transaction data for fraud detection."""
    
    def __init__(self, feature_metadata_path: Optional[str] = None):
        """Initialize feature engineer with optional metadata."""
        self.feature_metadata = {}
        if feature_metadata_path:
            try:
                with open(feature_metadata_path, 'r') as f:
                    self.feature_metadata = json.load(f)
            except FileNotFoundError:
                pass
    
    def extract_features(self, transaction: Dict[str, Any], user_history: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Extract features from a transaction.
        
        Args:
            transaction: Transaction data dictionary
            user_history: Optional DataFrame of user's historical transactions
            
        Returns:
            Dictionary of feature names and values
        """
        features = {}
        
        features['amount'] = float(transaction.get('amount', 0))
        features['amount_log'] = np.log1p(features['amount'])
        
        timestamp = transaction.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif timestamp is None:
            timestamp = datetime.now()
        
        features['hour'] = timestamp.hour
        features['day_of_week'] = timestamp.weekday()
        features['is_weekend'] = 1.0 if timestamp.weekday() >= 5 else 0.0
        features['is_night'] = 1.0 if 22 <= timestamp.hour or timestamp.hour < 6 else 0.0
        
        features['merchant_category_encoded'] = self._encode_category(transaction.get('merchant_category', 'unknown'))
        features['transaction_type_encoded'] = self._encode_category(transaction.get('transaction_type', 'unknown'))
        features['location_country_encoded'] = self._encode_category(transaction.get('location_country', 'unknown'))
        
        if user_history is not None and len(user_history) > 0:
            user_history = user_history.sort_values('timestamp')
            
            recent_24h = user_history[user_history['timestamp'] >= timestamp - pd.Timedelta(hours=24)]
            recent_7d = user_history[user_history['timestamp'] >= timestamp - pd.Timedelta(days=7)]
            
            features['transactions_24h'] = len(recent_24h)
            features['transactions_7d'] = len(recent_7d)
            features['avg_amount_7d'] = recent_7d['amount'].mean() if len(recent_7d) > 0 else 0.0
            features['amount_ratio_7d_avg'] = features['amount'] / (features['avg_amount_7d'] + 1e-6)
            
            recent_locations = recent_7d['location_country'].value_counts()
            features['location_change'] = 1.0 if transaction.get('location_country') not in recent_locations.index[:3] else 0.0
            
            recent_merchants = recent_7d['merchant_category'].value_counts()
            features['unusual_merchant'] = 1.0 if transaction.get('merchant_category') not in recent_merchants.index[:5] else 0.0
            
            if len(recent_24h) > 0:
                time_diffs = recent_24h['timestamp'].diff().dt.total_seconds() / 3600
                features['avg_time_between_transactions'] = time_diffs.mean() if len(time_diffs) > 1 else 24.0
            else:
                features['avg_time_between_transactions'] = 24.0
        else:
            features['transactions_24h'] = 0.0
            features['transactions_7d'] = 0.0
            features['avg_amount_7d'] = 0.0
            features['amount_ratio_7d_avg'] = 1.0
            features['location_change'] = 0.0
            features['unusual_merchant'] = 0.0
            features['avg_time_between_transactions'] = 24.0
        
        features['has_device_id'] = 1.0 if transaction.get('device_id') else 0.0
        features['has_ip_address'] = 1.0 if transaction.get('ip_address') else 0.0
        
        return features
    
    def _encode_category(self, category: str) -> float:
        """Simple hash-based encoding for categories."""
        return float(hash(category) % 1000) / 1000.0
    
    def get_feature_names(self) -> list:
        """Get list of feature names in order."""
        return [
            'amount', 'amount_log', 'hour', 'day_of_week', 'is_weekend', 'is_night',
            'merchant_category_encoded', 'transaction_type_encoded', 'location_country_encoded',
            'transactions_24h', 'transactions_7d', 'avg_amount_7d', 'amount_ratio_7d_avg',
            'location_change', 'unusual_merchant', 'avg_time_between_transactions',
            'has_device_id', 'has_ip_address'
        ]

