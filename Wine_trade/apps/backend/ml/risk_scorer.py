"""
Risk Scorer - Logistic regression/tree-based risk model
"""

import logging
import os
import pickle
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import scikit-learn
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Using simple risk scoring.")


class RiskScorer:
    """Risk scoring model using logistic regression or random forest"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.feature_names = [
            "volatility", "liquidity_risk", "market_dispersion",
            "mean_predicted_change", "num_arbitrage_opportunities"
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained model from file"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Loaded risk scoring model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    def save_model(self, model_path: str):
        """Save trained model to file"""
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Saved risk scoring model to {model_path}")
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
        Train the risk scoring model.
        
        Args:
            X: Feature matrix
            y: Target risk scores (0-1)
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
        
        if SKLEARN_AVAILABLE:
            # Use Random Forest for risk scoring
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
            # Convert risk scores to classes (low/medium/high)
            y_train_classes = np.digitize(y_train, bins=[0.33, 0.67])
            y_val_classes = np.digitize(y_val, bins=[0.33, 0.67])
            self.model.fit(X_train, y_train_classes)
        else:
            # Fallback: simple weighted average
            self.model = None
        
        # Evaluate
        if self.model:
            y_train_pred = self.model.predict_proba(X_train)[:, 1] if hasattr(self.model, 'predict_proba') else self.model.predict(X_train)
            y_val_pred = self.model.predict_proba(X_val)[:, 1] if hasattr(self.model, 'predict_proba') else self.model.predict(X_val)
        else:
            # Fallback evaluation
            y_train_pred = np.mean(X_train, axis=1)
            y_val_pred = np.mean(X_val, axis=1)
        
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
        Predict risk score.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Risk score dict with risk_score, components, confidence
        """
        # Extract components
        volatility = features.get("volatility", 0.0)
        liquidity_risk = features.get("liquidity_risk", 0.0)
        market_dispersion = features.get("market_dispersion", 0.0)
        
        if self.model:
            # Use trained model
            X = np.array([[features.get(name, 0) for name in self.feature_names]])
            try:
                if hasattr(self.model, 'predict_proba'):
                    risk_score = float(self.model.predict_proba(X)[0][1])
                else:
                    risk_score = float(self.model.predict(X)[0])
                risk_score = max(0.0, min(1.0, risk_score))
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                risk_score = self._fallback_risk_score(features)
        else:
            # Fallback: weighted formula
            risk_score = self._fallback_risk_score(features)
        
        # Confidence based on feature availability
        num_features = sum(1 for k in self.feature_names if features.get(k) is not None)
        confidence = min(0.95, max(0.5, 0.5 + (num_features / len(self.feature_names)) * 0.45))
        
        return {
            "risk_score": risk_score,
            "volatility": volatility,
            "liquidity_risk": liquidity_risk,
            "market_dispersion": market_dispersion,
            "confidence": confidence
        }
    
    def _fallback_risk_score(self, features: Dict[str, float]) -> float:
        """Fallback risk score calculation using formula"""
        w1, w2, w3 = 0.4, 0.3, 0.3
        volatility = features.get("volatility", 0.0)
        liquidity_risk = features.get("liquidity_risk", 0.0)
        market_dispersion = features.get("market_dispersion", 0.0)
        
        risk_score = w1 * volatility + w2 * liquidity_risk + w3 * market_dispersion
        return max(0.0, min(1.0, risk_score))
