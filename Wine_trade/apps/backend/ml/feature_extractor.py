"""
Feature Extractor - Extract features from price_history, holdings, etc.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features for ML models"""
    
    @staticmethod
    def extract_price_features(
        price_history: List[Dict[str, Any]],
        current_price: float,
        days: int = 30
    ) -> Dict[str, float]:
        """
        Extract features from price history for price prediction.
        
        Args:
            price_history: List of price history records
            current_price: Current price
            days: Number of days to look back
            
        Returns:
            Dict of feature values
        """
        if not price_history:
            return {
                "current_price": current_price,
                "price_mean": current_price,
                "price_std": 0.0,
                "price_trend": 0.0,
                "price_volatility": 0.0,
                "days_of_data": 0
            }
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(price_history)
        if 'price' not in df.columns:
            df['price'] = df.get('current_value', current_price)
        
        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date')
        
        # Take last N days
        df = df.tail(days)
        
        prices = df['price'].values
        
        features = {
            "current_price": current_price,
            "price_mean": float(np.mean(prices)),
            "price_std": float(np.std(prices)) if len(prices) > 1 else 0.0,
            "price_trend": float((prices[-1] - prices[0]) / prices[0]) if len(prices) > 1 and prices[0] > 0 else 0.0,
            "price_volatility": float(np.std(prices) / np.mean(prices)) if np.mean(prices) > 0 else 0.0,
            "days_of_data": len(prices)
        }
        
        return features
    
    @staticmethod
    def extract_risk_features(
        price_predictions: Optional[List[Dict[str, Any]]] = None,
        arbitrage_analysis: Optional[List[Dict[str, Any]]] = None,
        market_pulse: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Extract features for risk scoring.
        
        Args:
            price_predictions: List of price predictions
            arbitrage_analysis: List of arbitrage opportunities
            market_pulse: Market pulse by region
            
        Returns:
            Dict of feature values
        """
        features = {}
        
        # Volatility from price predictions
        if price_predictions:
            predicted_changes = [
                pred.get("predicted_change_percent", 0) / 100.0
                for pred in price_predictions
                if pred.get("predicted_change_percent") is not None
            ]
            if predicted_changes:
                features["volatility"] = float(np.std(predicted_changes))
                features["mean_predicted_change"] = float(np.mean(predicted_changes))
            else:
                features["volatility"] = 0.0
                features["mean_predicted_change"] = 0.0
        else:
            features["volatility"] = 0.0
            features["mean_predicted_change"] = 0.0
        
        # Liquidity risk from arbitrage
        if arbitrage_analysis:
            num_opportunities = len(arbitrage_analysis)
            avg_confidence = np.mean([
                arb.get("confidence", 0)
                for arb in arbitrage_analysis
            ]) if num_opportunities > 0 else 0.0
            features["liquidity_risk"] = float(max(0.0, min(1.0, 1.0 - (num_opportunities / 10.0) * avg_confidence)))
            features["num_arbitrage_opportunities"] = float(num_opportunities)
        else:
            features["liquidity_risk"] = 1.0
            features["num_arbitrage_opportunities"] = 0.0
        
        # Market dispersion from market pulse
        if market_pulse and len(market_pulse) > 1:
            values = list(market_pulse.values())
            mean = np.mean(values)
            dispersion = np.mean([abs(x - mean) for x in values])
            features["market_dispersion"] = float(min(1.0, max(0.0, dispersion / 5.0)))
        else:
            features["market_dispersion"] = 0.0
        
        return features
