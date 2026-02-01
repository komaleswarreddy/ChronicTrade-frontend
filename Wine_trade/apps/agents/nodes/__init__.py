"""
Agent Nodes

Individual nodes for the LangGraph advisor workflow.
Each node performs a specific task and updates the shared state.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.fetch_data import fetch_data_node
from nodes.predict_price import predict_price_node
from nodes.arbitrage_analysis import arbitrage_analysis_node
from nodes.signal_calculation import signal_calculation_node
from nodes.risk_evaluation import risk_evaluation_node
from nodes.recommend_action import recommend_action_node
from nodes.compliance_check import compliance_check_node
from nodes.explanation_builder import explanation_builder_node

__all__ = [
    "fetch_data_node",
    "predict_price_node",
    "arbitrage_analysis_node",
    "signal_calculation_node",
    "risk_evaluation_node",
    "recommend_action_node",
    "compliance_check_node",
    "explanation_builder_node",
]
