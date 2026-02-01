"""
Price Predictor - XGBoost/LightGBM price prediction model
"""

import logging
import os
import pickle
import hashlib
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Try to import XGBoost, fallback to simple model if not available
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not available. Using simple linear model for price prediction.")


class PricePredictor:
    """Price prediction model using XGBoost or fallback"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.feature_names = [
            "current_price", "price_mean", "price_std", 
            "price_trend", "price_volatility", "days_of_data"
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained model from file"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Loaded price prediction model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    def save_model(self, model_path: str):
        """Save trained model to file"""
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Saved price prediction model to {model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train the price prediction model.
        
        Args:
            X: Feature matrix
            y: Target prices
            validation_split: Fraction of data for validation
            
        Returns:
            Training metrics
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        if XGBOOST_AVAILABLE:
            # Train XGBoost model
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.model.fit(X_train, y_train)
        else:
            # Fallback to simple linear model
            from sklearn.linear_model import LinearRegression
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
        
        # Evaluate
        y_train_pred = self.model.predict(X_train)
        y_val_pred = self.model.predict(X_val)
        
        metrics = {
            "train_mae": float(mean_absolute_error(y_train, y_train_pred)),
            "train_rmse": float(np.sqrt(mean_squared_error(y_train, y_train_pred))),
            "train_r2": float(r2_score(y_train, y_train_pred)),
            "val_mae": float(mean_absolute_error(y_val, y_val_pred)),
            "val_rmse": float(np.sqrt(mean_squared_error(y_val, y_val_pred))),
            "val_r2": float(r2_score(y_val, y_val_pred)),
            "train_size": len(X_train),
            "val_size": len(X_val)
        }
        
        return metrics
    
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict price change.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Prediction dict with predicted_price, predicted_change_percent, confidence
        """
        if self.model is None:
            # Fallback prediction
            current_price = features.get("current_price", 0)
            trend = features.get("price_trend", 0)
            predicted_change = trend * 0.5  # Conservative estimate
            return {
                "predicted_price": current_price * (1 + predicted_change),
                "predicted_change_percent": predicted_change * 100,
                "confidence": 0.6  # Lower confidence for fallback
            }
        
        # Prepare features
        X = np.array([[features.get(name, 0) for name in self.feature_names]])
        
        try:
            predicted_price = float(self.model.predict(X)[0])
            current_price = features.get("current_price", predicted_price)
            predicted_change = (predicted_price - current_price) / current_price if current_price > 0 else 0
            
            # Confidence based on feature quality
            days_of_data = features.get("days_of_data", 0)
            confidence = min(0.95, max(0.5, 0.5 + (days_of_data / 30.0) * 0.45))
            
            return {
                "predicted_price": predicted_price,
                "predicted_change_percent": predicted_change * 100,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            # Fallback
            current_price = features.get("current_price", 0)
            return {
                "predicted_price": current_price,
                "predicted_change_percent": 0.0,
                "confidence": 0.5
            }
