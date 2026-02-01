"""
ML Service - Main service orchestrating ML predictions and training
"""

import logging
import os
import uuid
import hashlib
import time
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from .price_predictor import PricePredictor
from .risk_scorer import RiskScorer
from .feature_extractor import FeatureExtractor
from .schemas import (
    PricePredictionRequest, PricePredictionResponse,
    RiskScoringRequest, RiskScoringResponse
)

logger = logging.getLogger(__name__)


class MLService:
    """Main ML service for predictions and training"""
    
    def __init__(self, conn=None, models_dir: str = "models"):
        self.conn = conn
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        self.feature_extractor = FeatureExtractor()
        self.price_predictor = None
        self.risk_scorer = None
        self._load_active_models(conn)
    
    def _load_active_models(self, conn=None):
        """Load active models from database"""
        if conn is None:
            conn = self.conn
        if conn is None:
            return
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Load active price prediction model
            cursor.execute("""
                SELECT model_id, model_path, version
                FROM ml_models
                WHERE model_type = 'price_prediction' AND is_active = TRUE
                ORDER BY version DESC
                LIMIT 1
            """)
            price_model = cursor.fetchone()
            if price_model:
                self.price_predictor = PricePredictor(model_path=price_model['model_path'])
                logger.info(f"Loaded price prediction model: {price_model['model_id']} v{price_model['version']}")
            
            # Load active risk scoring model
            cursor.execute("""
                SELECT model_id, model_path, version
                FROM ml_models
                WHERE model_type = 'risk_scoring' AND is_active = TRUE
                ORDER BY version DESC
                LIMIT 1
            """)
            risk_model = cursor.fetchone()
            if risk_model:
                self.risk_scorer = RiskScorer(model_path=risk_model['model_path'])
                logger.info(f"Loaded risk scoring model: {risk_model['model_id']} v{risk_model['version']}")
            
            cursor.close()
        except Exception as e:
            logger.warning(f"Failed to load models from database: {e}")
    
    def _save_prediction(
        self,
        model_id: str,
        prediction_value: float,
        confidence_score: float,
        input_features: Dict[str, Any],
        conn=None
    ):
        """
        Save prediction to ml_predictions table.
        
        Args:
            model_id: Model identifier
            prediction_value: The predicted value
            confidence_score: Confidence score (0-1)
            input_features: Dictionary of input features
            conn: Database connection
        """
        if conn is None:
            conn = self.conn
        
        if not conn:
            logger.warning("No database connection available for saving prediction")
            return
        
        try:
            import json
            from datetime import datetime, timedelta
            
            # Create prediction key from input features hash (for deduplication)
            features_str = json.dumps(input_features, sort_keys=True)
            prediction_key = hashlib.md5(features_str.encode()).hexdigest()
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ml_predictions 
                (model_id, prediction_key, prediction_value, confidence_score, 
                 input_features, created_at, expires_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (model_id, prediction_key) 
                DO UPDATE SET 
                    prediction_value = EXCLUDED.prediction_value,
                    confidence_score = EXCLUDED.confidence_score,
                    created_at = EXCLUDED.created_at,
                    expires_at = EXCLUDED.expires_at
            """, (
                model_id,
                prediction_key,
                prediction_value,
                confidence_score,
                json.dumps(input_features),
                datetime.now(),
                datetime.now() + timedelta(days=30)  # Expire after 30 days
            ))
            conn.commit()
            cursor.close()
            logger.info(f"Saved prediction for model {model_id}: value={prediction_value:.4f}, confidence={confidence_score:.4f}")
        except Exception as e:
            logger.warning(f"Failed to save prediction to database: {e}")
            # Don't raise - prediction was successful, just saving failed
    
    def predict_price(
        self,
        request: PricePredictionRequest,
        conn=None
    ) -> PricePredictionResponse:
        """
        Predict price for an asset.
        
        Args:
            request: Price prediction request
            conn: Database connection
            
        Returns:
            Price prediction response
        """
        if conn is None:
            conn = self.conn
        
        # Extract features
        features = self.feature_extractor.extract_price_features(
            price_history=request.price_history or [],
            current_price=request.current_price,
            days=30
        )
        
        # Initialize predictor if not loaded
        if self.price_predictor is None:
            self.price_predictor = PricePredictor()
        
        # Predict
        prediction = self.price_predictor.predict(features)
        
        # Get model info
        model_id = "default_price_model"
        model_version = 1
        if conn:
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT model_id, version
                    FROM ml_models
                    WHERE model_type = 'price_prediction' AND is_active = TRUE
                    ORDER BY version DESC
                    LIMIT 1
                """)
                model = cursor.fetchone()
                if model:
                    model_id = model['model_id']
                    model_version = model['version']
                cursor.close()
            except Exception as e:
                logger.warning(f"Failed to get model info: {e}")
        
        # Save prediction to database
        if conn:
            try:
                # Combine request data + extracted features for input_features
                # Note: features already contains current_price, so we merge carefully
                input_features_dict = {
                    "asset_id": request.asset_id,
                    "region": request.region,
                    "price_history_length": len(request.price_history or []),
                    # Add all extracted features (includes current_price, price_mean, price_std, etc.)
                    **features
                }
                
                self._save_prediction(
                    model_id=model_id,
                    prediction_value=prediction["predicted_price"],
                    confidence_score=prediction["confidence"],
                    input_features=input_features_dict,
                    conn=conn
                )
            except Exception as e:
                logger.warning(f"Failed to save price prediction: {e}")
        
        return PricePredictionResponse(
            asset_id=request.asset_id,
            region=request.region,
            current_price=request.current_price,
            predicted_price=prediction["predicted_price"],
            predicted_change_percent=prediction["predicted_change_percent"],
            confidence=prediction["confidence"],
            model_id=model_id,
            model_version=model_version
        )
    
    def score_risk(
        self,
        request: RiskScoringRequest,
        conn=None
    ) -> RiskScoringResponse:
        """
        Score risk for a recommendation.
        
        Args:
            request: Risk scoring request
            conn: Database connection
            
        Returns:
            Risk scoring response
        """
        if conn is None:
            conn = self.conn
        
        # Extract features
        features = self.feature_extractor.extract_risk_features(
            price_predictions=request.price_predictions,
            arbitrage_analysis=request.arbitrage_analysis,
            market_pulse=request.market_pulse
        )
        
        # Initialize scorer if not loaded
        if self.risk_scorer is None:
            self.risk_scorer = RiskScorer()
        
        # Predict
        risk_result = self.risk_scorer.predict(features)
        
        # Get model info
        model_id = "default_risk_model"
        model_version = 1
        if conn:
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT model_id, version
                    FROM ml_models
                    WHERE model_type = 'risk_scoring' AND is_active = TRUE
                    ORDER BY version DESC
                    LIMIT 1
                """)
                model = cursor.fetchone()
                if model:
                    model_id = model['model_id']
                    model_version = model['version']
                cursor.close()
            except Exception as e:
                logger.warning(f"Failed to get model info: {e}")
        
        # Save prediction to database
        if conn:
            try:
                # Combine request data + extracted features for input_features
                input_features_dict = {
                    "asset_id": request.asset_id or None,
                    "price_predictions_count": len(request.price_predictions or []),
                    "arbitrage_analysis_count": len(request.arbitrage_analysis or []),
                    "market_pulse_available": bool(request.market_pulse),
                    # Add all extracted features (includes volatility, liquidity_risk, market_dispersion, etc.)
                    **features
                }
                
                self._save_prediction(
                    model_id=model_id,
                    prediction_value=risk_result["risk_score"],
                    confidence_score=risk_result["confidence"],
                    input_features=input_features_dict,
                    conn=conn
                )
            except Exception as e:
                logger.warning(f"Failed to save risk prediction: {e}")
        
        return RiskScoringResponse(
            risk_score=risk_result["risk_score"],
            volatility=risk_result.get("volatility"),
            liquidity_risk=risk_result.get("liquidity_risk"),
            market_dispersion=risk_result.get("market_dispersion"),
            confidence=risk_result["confidence"],
            model_id=model_id,
            model_version=model_version
        )
