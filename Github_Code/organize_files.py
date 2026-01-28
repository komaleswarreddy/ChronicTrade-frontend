"""
Script to organize files into GitHubPush structure by team member and iteration.
This script ONLY copies files - it never modifies originals.
"""

import os
import shutil
from pathlib import Path

# Workspace root
WORKSPACE_ROOT = Path(r"C:\Users\KomaleswarReddy\Desktop\PROJECT-M\Wine_trade")
GITHUB_PUSH_ROOT = WORKSPACE_ROOT / "GitHubPush"

# Team member folders
TEAM_MEMBERS = ["Komal", "Manikanta", "Yuvraj", "Syam"]
ITERATIONS = [
    "00_Core_Foundation_Completed",
    "01_Iteration_1_Foundation_And_Contracts",
    "02_Iteration_2_Execution_Engine_And_UI",
    "03_Iteration_3_Compliance_And_Counterfactuals",
    "04_Iteration_4_Logistics_KYC_AML_Tax"
]

def ensure_dir(path):
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)

def copy_file(source_rel, dest_rel):
    """Copy file from source to destination (relative to workspace root)"""
    source = WORKSPACE_ROOT / source_rel
    dest = GITHUB_PUSH_ROOT / dest_rel
    
    if not source.exists():
        print(f"WARNING: Source not found: {source_rel}")
        return False
    
    ensure_dir(dest.parent)
    
    if source.is_file():
        shutil.copy2(source, dest)
    elif source.is_dir():
        shutil.copytree(source, dest, dirs_exist_ok=True)
    
    print(f"Copied: {source_rel} -> {dest_rel}")
    return True

def main():
    print("=" * 60)
    print("Organizing files into GitHubPush structure")
    print("=" * 60)
    
    # ========== CORE FOUNDATION (00) ==========
    print("\n[00] Core Foundation Files...")
    
    # Komal - Frontend Core
    copy_file("apps/frontend/pages/index.js", "Komal/00_Core_Foundation_Completed/apps/frontend/pages/index.js")
    copy_file("apps/frontend/pages/sign-in", "Komal/00_Core_Foundation_Completed/apps/frontend/pages/sign-in")
    copy_file("apps/frontend/pages/register", "Komal/00_Core_Foundation_Completed/apps/frontend/pages/register")
    copy_file("apps/frontend/pages/_app.js", "Komal/00_Core_Foundation_Completed/apps/frontend/pages/_app.js")
    copy_file("apps/frontend/pages/dashboard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/pages/dashboard.js")
    copy_file("apps/frontend/components/NavBar.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/NavBar.js")
    copy_file("apps/frontend/components/PortfolioCard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/PortfolioCard.js")
    copy_file("apps/frontend/components/HoldingsTable.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/HoldingsTable.js")
    copy_file("apps/frontend/components/SoldHoldingsTable.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/SoldHoldingsTable.js")
    copy_file("apps/frontend/components/MarketPulseCard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/MarketPulseCard.js")
    copy_file("apps/frontend/components/ArbitrageCard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/ArbitrageCard.js")
    copy_file("apps/frontend/components/AlertCard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/AlertCard.js")
    copy_file("apps/frontend/components/WatchlistCard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/WatchlistCard.js")
    copy_file("apps/frontend/components/PortfolioChart.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/PortfolioChart.js")
    copy_file("apps/frontend/components/PortfolioTrendChart.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/PortfolioTrendChart.js")
    
    # Manikanta - Backend Core
    copy_file("apps/backend/auth", "Manikanta/00_Core_Foundation_Completed/apps/backend/auth")
    copy_file("apps/backend/main.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/main.py")
    copy_file("apps/backend/models/schemas.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/models/schemas.py")
    copy_file("apps/backend/services/portfolio_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/portfolio_service.py")
    copy_file("apps/backend/services/holdings_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/holdings_service.py")
    copy_file("apps/backend/services/alert_engine.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/alert_engine.py")
    copy_file("apps/backend/services/watchlist_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/watchlist_service.py")
    
    # Yuvraj - Agents Core
    copy_file("apps/agents/main.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/main.py")
    copy_file("apps/agents/config.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/config.py")
    copy_file("apps/agents/schemas.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/schemas.py")
    copy_file("apps/agents/graphs/advisor_graph.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/graphs/advisor_graph.py")
    copy_file("apps/agents/nodes/fetch_data.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/nodes/fetch_data.py")
    copy_file("apps/agents/nodes/arbitrage_analysis.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/nodes/arbitrage_analysis.py")
    copy_file("apps/agents/nodes/risk_evaluation.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/nodes/risk_evaluation.py")
    copy_file("apps/agents/nodes/signal_calculation.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/nodes/signal_calculation.py")
    copy_file("apps/agents/nodes/predict_price.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/nodes/predict_price.py")
    copy_file("apps/agents/nodes/recommend_action.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/nodes/recommend_action.py")
    copy_file("apps/agents/tools/backend_api.py", "Yuvraj/00_Core_Foundation_Completed/apps/agents/tools/backend_api.py")
    
    # Syam - Database Core
    copy_file("db/schema.sql", "Syam/00_Core_Foundation_Completed/db/schema.sql")
    copy_file("apps/backend/database/init_db.py", "Syam/00_Core_Foundation_Completed/apps/backend/database/init_db.py")
    copy_file("apps/backend/database/migrate_demo_user.py", "Syam/00_Core_Foundation_Completed/apps/backend/database/migrate_demo_user.py")
    copy_file("apps/backend/database/migrate_holdings_phase8.py", "Syam/00_Core_Foundation_Completed/apps/backend/database/migrate_holdings_phase8.py")
    copy_file("apps/backend/database/migrate_phase8_tables.py", "Syam/00_Core_Foundation_Completed/apps/backend/database/migrate_phase8_tables.py")
    copy_file("apps/backend/database/migrate_phase9_agent_tables.py", "Syam/00_Core_Foundation_Completed/apps/backend/database/migrate_phase9_agent_tables.py")
    
    # ========== ITERATION 1: FOUNDATION AND CONTRACTS ==========
    print("\n[01] Iteration 1: Foundation and Contracts...")
    
    # Models and schemas only
    copy_file("apps/backend/models/schemas.py", "Manikanta/01_Iteration_1_Foundation_And_Contracts/apps/backend/models/schemas.py")
    copy_file("apps/agents/schemas.py", "Yuvraj/01_Iteration_1_Foundation_And_Contracts/apps/agents/schemas.py")
    
    # Syam - Foundational Database Schema (the "contracts" - data model definitions)
    copy_file("db/schema.sql", "Syam/01_Iteration_1_Foundation_And_Contracts/db/schema.sql")
    copy_file("apps/backend/database/schema.sql", "Syam/01_Iteration_1_Foundation_And_Contracts/apps/backend/database/schema.sql")
    
    # Komal - Frontend Data Contracts (components that define data structures and API response handling)
    # These files establish the "contracts" for how frontend handles data, even if not explicit types
    copy_file("apps/frontend/components/PortfolioCard.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/components/PortfolioCard.js")
    copy_file("apps/frontend/components/HoldingsTable.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/components/HoldingsTable.js")
    copy_file("apps/frontend/components/ArbitrageCard.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/components/ArbitrageCard.js")
    copy_file("apps/frontend/components/AlertCard.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/components/AlertCard.js")
    copy_file("apps/frontend/components/WatchlistCard.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/components/WatchlistCard.js")
    copy_file("apps/frontend/components/AdvisorCard.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/components/AdvisorCard.js")
    copy_file("apps/frontend/pages/dashboard.js", "Komal/01_Iteration_1_Foundation_And_Contracts/apps/frontend/pages/dashboard.js")
    
    # ========== ITERATION 2: EXECUTION ENGINE AND UI ==========
    print("\n[02] Iteration 2: Execution Engine and UI...")
    
    # Manikanta - Execution Engine
    copy_file("apps/backend/services/execution_engine_c1.py", "Manikanta/02_Iteration_2_Execution_Engine_And_UI/apps/backend/services/execution_engine_c1.py")
    copy_file("apps/backend/services/execution_engine.py", "Manikanta/02_Iteration_2_Execution_Engine_And_UI/apps/backend/services/execution_engine.py")
    copy_file("apps/backend/services/simulation_service.py", "Manikanta/02_Iteration_2_Execution_Engine_And_UI/apps/backend/services/simulation_service.py")
    
    # Komal - Execution UI
    copy_file("apps/frontend/components/ExecutionTimeline.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/ExecutionTimeline.js")
    copy_file("apps/frontend/components/ExecutionStepsPanel.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/ExecutionStepsPanel.js")
    copy_file("apps/frontend/components/ExecutionHistoryTable.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/ExecutionHistoryTable.js")
    copy_file("apps/frontend/components/SimulationModal.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/SimulationModal.js")
    copy_file("apps/frontend/components/SimulationDetailModal.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/SimulationDetailModal.js")
    copy_file("apps/frontend/components/SimulationHistoryTable.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/SimulationHistoryTable.js")
    copy_file("apps/frontend/components/ApprovalDialog.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/ApprovalDialog.js")
    
    # Syam - Execution Database
    copy_file("apps/backend/database/migrate_phase_c1_execution_engine.py", "Syam/02_Iteration_2_Execution_Engine_And_UI/apps/backend/database/migrate_phase_c1_execution_engine.py")
    copy_file("apps/backend/database/migrate_phase11_simulated_execution.py", "Syam/02_Iteration_2_Execution_Engine_And_UI/apps/backend/database/migrate_phase11_simulated_execution.py")
    
    # ========== ITERATION 3: COMPLIANCE AND COUNTERFACTUALS ==========
    print("\n[03] Iteration 3: Compliance and Counterfactuals...")
    
    # Manikanta - Compliance Services
    copy_file("apps/backend/services/compliance_reasoning_c2.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/compliance_reasoning_c2.py")
    copy_file("apps/backend/services/counterfactual_c3.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/counterfactual_c3.py")
    copy_file("apps/backend/services/explainability_service.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/explainability_service.py")
    
    # Komal - Compliance UI
    copy_file("apps/frontend/components/ComplianceEvaluationPanel.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/ComplianceEvaluationPanel.js")
    copy_file("apps/frontend/components/CounterfactualPanel.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/CounterfactualPanel.js")
    copy_file("apps/frontend/components/DecisionReplayPanel.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/DecisionReplayPanel.js")
    copy_file("apps/frontend/components/DecisionTimeline.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/DecisionTimeline.js")
    copy_file("apps/frontend/components/WhatChangedPanel.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/WhatChangedPanel.js")
    
    # Yuvraj - Compliance Nodes
    copy_file("apps/agents/nodes/compliance_check.py", "Yuvraj/03_Iteration_3_Compliance_And_Counterfactuals/apps/agents/nodes/compliance_check.py")
    copy_file("apps/agents/nodes/explain_decision.py", "Yuvraj/03_Iteration_3_Compliance_And_Counterfactuals/apps/agents/nodes/explain_decision.py")
    copy_file("apps/agents/nodes/explanation_builder.py", "Yuvraj/03_Iteration_3_Compliance_And_Counterfactuals/apps/agents/nodes/explanation_builder.py")
    
    # Syam - Compliance Database
    copy_file("apps/backend/database/migrate_phase_c2_compliance_reasoning.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase_c2_compliance_reasoning.py")
    copy_file("apps/backend/database/migrate_phase_c3_counterfactual.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase_c3_counterfactual.py")
    copy_file("apps/backend/database/migrate_phase10_structured_explanation.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase10_structured_explanation.py")
    
    # ========== ITERATION 4: LOGISTICS KYC AML TAX ==========
    print("\n[04] Iteration 4: Logistics, KYC, AML, Tax...")
    
    # Manikanta - Logistics and Gating Services
    copy_file("apps/backend/services/logistics_tracking_c4.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/logistics_tracking_c4.py")
    copy_file("apps/backend/services/execution_gating_c5.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/execution_gating_c5.py")
    copy_file("apps/backend/services/execution_guard.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/execution_guard.py")
    
    # Komal - Logistics UI
    copy_file("apps/frontend/components/LogisticsTimelinePanel.js", "Komal/04_Iteration_4_Logistics_KYC_AML_Tax/apps/frontend/components/LogisticsTimelinePanel.js")
    copy_file("apps/frontend/components/ExecutionGatesPanel.js", "Komal/04_Iteration_4_Logistics_KYC_AML_Tax/apps/frontend/components/ExecutionGatesPanel.js")
    
    # Syam - Logistics Database
    copy_file("apps/backend/database/migrate_phase_c4_logistics.py", "Syam/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/database/migrate_phase_c4_logistics.py")
    copy_file("apps/backend/database/migrate_phase_c5_kyc_aml_tax.py", "Syam/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/database/migrate_phase_c5_kyc_aml_tax.py")
    
    # Yuvraj - Agent files that interact with logistics/KYC/AML services via backend API
    copy_file("apps/agents/tools/backend_api.py", "Yuvraj/04_Iteration_4_Logistics_KYC_AML_Tax/apps/agents/tools/backend_api.py")
    copy_file("apps/agents/schemas.py", "Yuvraj/04_Iteration_4_Logistics_KYC_AML_Tax/apps/agents/schemas.py")
    copy_file("apps/agents/nodes/compliance_check.py", "Yuvraj/04_Iteration_4_Logistics_KYC_AML_Tax/apps/agents/nodes/compliance_check.py")
    copy_file("apps/agents/config.py", "Yuvraj/04_Iteration_4_Logistics_KYC_AML_Tax/apps/agents/config.py")
    
    # ========== ADDITIONAL FILES - Core Foundation ==========
    print("\n[Additional] Adding remaining Core Foundation files...")
    
    # Komal - Additional Core UI Components and Config
    copy_file("apps/frontend/components/AdvisorCard.js", "Komal/00_Core_Foundation_Completed/apps/frontend/components/AdvisorCard.js")
    copy_file("apps/frontend/package.json", "Komal/00_Core_Foundation_Completed/apps/frontend/package.json")
    copy_file("apps/frontend/next.config.js", "Komal/00_Core_Foundation_Completed/apps/frontend/next.config.js")
    copy_file("apps/frontend/tailwind.config.js", "Komal/00_Core_Foundation_Completed/apps/frontend/tailwind.config.js")
    copy_file("apps/frontend/postcss.config.js", "Komal/00_Core_Foundation_Completed/apps/frontend/postcss.config.js")
    copy_file("apps/frontend/styles/globals.css", "Komal/00_Core_Foundation_Completed/apps/frontend/styles/globals.css")
    copy_file("apps/frontend/middleware.ts", "Komal/00_Core_Foundation_Completed/apps/frontend/middleware.ts")
    
    # Manikanta - Additional Core Services, Middleware, and Config
    copy_file("apps/backend/services/agent_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/agent_service.py")
    copy_file("apps/backend/services/user_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/user_service.py")
    copy_file("apps/backend/services/sold_holdings_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/sold_holdings_service.py")
    copy_file("apps/backend/services/alert_rules_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/alert_rules_service.py")
    copy_file("apps/backend/services/holdings_state_service.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/holdings_state_service.py")
    copy_file("apps/backend/services/update_holdings_prices.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/services/update_holdings_prices.py")
    copy_file("apps/backend/middleware", "Manikanta/00_Core_Foundation_Completed/apps/backend/middleware")
    copy_file("apps/backend/requirements.txt", "Manikanta/00_Core_Foundation_Completed/apps/backend/requirements.txt")
    copy_file("apps/backend/start.py", "Manikanta/00_Core_Foundation_Completed/apps/backend/start.py")
    copy_file("apps/backend/env.example", "Manikanta/00_Core_Foundation_Completed/apps/backend/env.example")
    
    # Yuvraj - Additional Config
    copy_file("apps/agents/requirements.txt", "Yuvraj/00_Core_Foundation_Completed/apps/agents/requirements.txt")
    copy_file("apps/agents/README.md", "Yuvraj/00_Core_Foundation_Completed/apps/agents/README.md")
    
    # Syam - Additional Database Files
    copy_file("apps/backend/database/verify_schema.py", "Syam/00_Core_Foundation_Completed/apps/backend/database/verify_schema.py")
    copy_file("apps/backend/database/schema.sql", "Syam/00_Core_Foundation_Completed/apps/backend/database/schema.sql")
    
    # ========== ADDITIONAL FILES - Iteration 2 (Outcome Tracking) ==========
    print("\n[Additional] Adding outcome tracking files to Iteration 2...")
    
    # Manikanta - Outcome Services (related to execution)
    copy_file("apps/backend/services/outcome_service.py", "Manikanta/02_Iteration_2_Execution_Engine_And_UI/apps/backend/services/outcome_service.py")
    copy_file("apps/backend/services/outcome_realization_service.py", "Manikanta/02_Iteration_2_Execution_Engine_And_UI/apps/backend/services/outcome_realization_service.py")
    
    # Komal - Outcome UI
    copy_file("apps/frontend/components/OutcomeHistoryTable.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/OutcomeHistoryTable.js")
    copy_file("apps/frontend/components/PerformanceMetricsPanel.js", "Komal/02_Iteration_2_Execution_Engine_And_UI/apps/frontend/components/PerformanceMetricsPanel.js")
    
    # Yuvraj - Outcome Nodes
    copy_file("apps/agents/nodes/outcome_evaluator.py", "Yuvraj/02_Iteration_2_Execution_Engine_And_UI/apps/agents/nodes/outcome_evaluator.py")
    
    # Syam - Outcome Database
    copy_file("apps/backend/database/migrate_phase12_outcome_tracking.py", "Syam/02_Iteration_2_Execution_Engine_And_UI/apps/backend/database/migrate_phase12_outcome_tracking.py")
    copy_file("apps/backend/database/migrate_phase17_outcome_realization.py", "Syam/02_Iteration_2_Execution_Engine_And_UI/apps/backend/database/migrate_phase17_outcome_realization.py")
    
    # ========== ADDITIONAL FILES - Iteration 3 (Learning & Strategy) ==========
    print("\n[Additional] Adding learning and strategy files to Iteration 3...")
    
    # Manikanta - Learning Services
    copy_file("apps/backend/services/learning_service.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/learning_service.py")
    copy_file("apps/backend/services/strategy_service.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/strategy_service.py")
    copy_file("apps/backend/services/feedback_signal_service.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/feedback_signal_service.py")
    copy_file("apps/backend/services/portfolio_capital_service.py", "Manikanta/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/services/portfolio_capital_service.py")
    
    # Komal - Learning UI
    copy_file("apps/frontend/components/LearningInsightsPanel.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/LearningInsightsPanel.js")
    copy_file("apps/frontend/components/StrategyPerformancePanel.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/StrategyPerformancePanel.js")
    copy_file("apps/frontend/components/StrategyReliabilityBadge.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/StrategyReliabilityBadge.js")
    copy_file("apps/frontend/components/ConfidenceStabilityIndicator.js", "Komal/03_Iteration_3_Compliance_And_Counterfactuals/apps/frontend/components/ConfidenceStabilityIndicator.js")
    
    # Yuvraj - Learning Nodes
    copy_file("apps/agents/nodes/learning_evaluator.py", "Yuvraj/03_Iteration_3_Compliance_And_Counterfactuals/apps/agents/nodes/learning_evaluator.py")
    
    # Syam - Learning Database
    copy_file("apps/backend/database/migrate_phase13_learning.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase13_learning.py")
    copy_file("apps/backend/database/migrate_phase18_learning_metrics_cache.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase18_learning_metrics_cache.py")
    copy_file("apps/backend/database/migrate_phase19_feedback_signals.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase19_feedback_signals.py")
    copy_file("apps/backend/database/migrate_phase20_portfolio_capital.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase20_portfolio_capital.py")
    copy_file("apps/backend/database/migrate_phase21_strategy_layer.py", "Syam/03_Iteration_3_Compliance_And_Counterfactuals/apps/backend/database/migrate_phase21_strategy_layer.py")
    
    # ========== ADDITIONAL FILES - Iteration 4 (Autonomy & Advanced Features) ==========
    print("\n[Additional] Adding autonomy and advanced features to Iteration 4...")
    
    # Manikanta - Autonomy Services
    copy_file("apps/backend/services/autonomy_service.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/autonomy_service.py")
    copy_file("apps/backend/services/autonomy_policy_service.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/autonomy_policy_service.py")
    copy_file("apps/backend/services/execution_audit.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/execution_audit.py")
    copy_file("apps/backend/services/audit_service.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/audit_service.py")
    copy_file("apps/backend/services/snapshot_service.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/snapshot_service.py")
    copy_file("apps/backend/services/snapshot_initialization.py", "Manikanta/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/services/snapshot_initialization.py")
    
    # Komal - Autonomy UI
    copy_file("apps/frontend/components/AutonomousExecutionPanel.js", "Komal/04_Iteration_4_Logistics_KYC_AML_Tax/apps/frontend/components/AutonomousExecutionPanel.js")
    copy_file("apps/frontend/components/AutonomyControlPanel.js", "Komal/04_Iteration_4_Logistics_KYC_AML_Tax/apps/frontend/components/AutonomyControlPanel.js")
    copy_file("apps/frontend/components/CapitalSummaryPanel.js", "Komal/04_Iteration_4_Logistics_KYC_AML_Tax/apps/frontend/components/CapitalSummaryPanel.js")
    
    # Syam - Autonomy Database
    copy_file("apps/backend/database/migrate_phase14_autonomy.py", "Syam/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/database/migrate_phase14_autonomy.py")
    copy_file("apps/backend/database/migrate_phase16_autonomous_execution.py", "Syam/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/database/migrate_phase16_autonomous_execution.py")
    copy_file("apps/backend/database/migrate_phase23_governance_audit.py", "Syam/04_Iteration_4_Logistics_KYC_AML_Tax/apps/backend/database/migrate_phase23_governance_audit.py")
    
    print("\n" + "=" * 60)
    print("File organization complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
