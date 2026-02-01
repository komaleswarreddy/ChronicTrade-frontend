"""
ML Schemas - Pydantic models for ML predictions and training
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PricePredictionRequest(BaseModel):
    """Request for price prediction"""
    asset_id: str
    region: str
    current_price: float
    price_history: Optional[List[Dict[str, Any]]] = None
    market_pulse: Optional[Dict[str, float]] = None
    days_ahead: int = Field(30, ge=1, le=90, description="Days ahead to predict")


class PricePredictionResponse(BaseModel):
    """Response from price prediction"""
    asset_id: str
    region: str
    current_price: float
    predicted_price: float
    predicted_change_percent: float
    confidence: float
    model_id: str
    model_version: int


class RiskScoringRequest(BaseModel):
    """Request for risk scoring"""
    asset_id: Optional[str] = None
    price_predictions: Optional[List[Dict[str, Any]]] = None
    arbitrage_analysis: Optional[List[Dict[str, Any]]] = None
    market_pulse: Optional[Dict[str, float]] = None
    portfolio_context: Optional[Dict[str, Any]] = None


class RiskScoringResponse(BaseModel):
    """Response from risk scoring"""
    risk_score: float
    volatility: Optional[float] = None
    liquidity_risk: Optional[float] = None
    market_dispersion: Optional[float] = None
    confidence: float
    model_id: str
    model_version: int


class TrainingRequest(BaseModel):
    """Request to train ML models"""
    model_type: str = Field(..., description="'price_prediction' or 'risk_scoring'")
    training_data_limit: Optional[int] = Field(None, description="Limit training data size")


class TrainingResponse(BaseModel):
    """Response from training"""
    model_id: str
    model_type: str
    version: int
    training_metrics: Dict[str, Any]
    training_duration_seconds: float
    success: bool
