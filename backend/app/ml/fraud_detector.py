"""Fraud detection model and inference."""
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import json
import time
from pathlib import Path
import logging

from app.ml.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class FraudDetector:
    """Fraud detection model with explainability."""
    
    def __init__(self, model_path: str, feature_metadata_path: Optional[str] = None):
        """
        Initialize fraud detector.
        
        Args:
            model_path: Path to trained model file
            feature_metadata_path: Path to feature metadata JSON
        """
        self.model_path = model_path
        self.model = None
        self.feature_engineer = FeatureEngineer(feature_metadata_path)
        self.feature_names = self.feature_engineer.get_feature_names()
        self.model_version = "1.0.0"
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk."""
        try:
            model_file = Path(self.model_path)
            if model_file.exists():
                self.model = joblib.load(model_file)
                logger.info(f"Model loaded from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using dummy model.")
                self._create_dummy_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}. Using dummy model.")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a dummy model for development/testing."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        
        X, y = make_classification(n_samples=1000, n_features=len(self.feature_names), 
                                  n_informative=10, random_state=42)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        logger.info("Dummy model created for development")
    
    def predict(
        self, 
        transaction: Dict[str, Any], 
        user_history: Optional[pd.DataFrame] = None,
        threshold: float = 0.5,
        include_explainability: bool = True
    ) -> Dict[str, Any]:
        """
        Predict fraud probability for a transaction.
        
        Args:
            transaction: Transaction data dictionary
            user_history: Optional DataFrame of user's historical transactions
            threshold: Fraud detection threshold
            include_explainability: Whether to compute SHAP values
            
        Returns:
            Dictionary with prediction results and explainability
        """
        start_time = time.time()
        
        features_dict = self.feature_engineer.extract_features(transaction, user_history)
        feature_vector = np.array([features_dict.get(name, 0.0) for name in self.feature_names]).reshape(1, -1)
        
        fraud_probability = float(self.model.predict_proba(feature_vector)[0, 1])
        is_fraud = fraud_probability >= threshold
        
        inference_time_ms = (time.time() - start_time) * 1000
        
        result = {
            'fraud_probability': fraud_probability,
            'is_fraud': is_fraud,
            'threshold': threshold,
            'model_version': self.model_version,
            'inference_time_ms': inference_time_ms,
            'features': features_dict,
        }
        
        if include_explainability:
            try:
                shap_values, feature_contributions = self._compute_explainability(
                    feature_vector, features_dict
                )
                result['shap_values'] = shap_values
                result['feature_contributions'] = feature_contributions
            except Exception as e:
                logger.warning(f"Error computing explainability: {e}")
                result['shap_values'] = {}
                result['feature_contributions'] = {}
        
        return result
    
    def _compute_explainability(
        self, 
        feature_vector: np.ndarray, 
        features_dict: Dict[str, float]
    ) -> Tuple[Dict[str, float], Dict[str, Dict[str, Any]]]:
        """
        Compute SHAP values for model explainability.
        
        Args:
            feature_vector: Feature vector for the transaction
            features_dict: Dictionary of feature names and values
            
        Returns:
            Tuple of (shap_values_dict, feature_contributions_dict)
        """
        try:
            import shap
            
            if hasattr(self.model, 'estimators_'):
                explainer = shap.TreeExplainer(self.model)
                shap_values = explainer.shap_values(feature_vector)
                
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]
                
                shap_dict = {
                    name: float(val) 
                    for name, val in zip(self.feature_names, shap_values[0])
                }
            else:
                # Fallback: use feature importance
                if hasattr(self.model, 'feature_importances_'):
                    importances = self.model.feature_importances_
                    shap_dict = {
                        name: float(imp) 
                        for name, imp in zip(self.feature_names, importances)
                    }
                else:
                    shap_dict = {name: 0.0 for name in self.feature_names}
            
            feature_contributions = {}
            sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            
            for feature_name, shap_value in sorted_features[:10]:
                feature_value = features_dict.get(feature_name, 0.0)
                feature_contributions[feature_name] = {
                    'shap_value': shap_value,
                    'feature_value': feature_value,
                    'contribution': 'increases' if shap_value > 0 else 'decreases',
                    'impact': abs(shap_value)
                }
            
            return shap_dict, feature_contributions
            
        except ImportError:
            logger.warning("SHAP not available, using feature importance")
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                shap_dict = {
                    name: float(imp) 
                    for name, imp in zip(self.feature_names, importances)
                }
            else:
                shap_dict = {name: 0.0 for name in self.feature_names}
            
            feature_contributions = {
                name: {
                    'shap_value': val,
                    'feature_value': features_dict.get(name, 0.0),
                    'contribution': 'increases' if val > 0 else 'decreases',
                    'impact': abs(val)
                }
                for name, val in list(shap_dict.items())[:10]
            }
            
            return shap_dict, feature_contributions

