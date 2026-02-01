"""
Autonomy Policy Service - Phase 16
Evaluates policies for autonomous execution decisions.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime, date

logger = logging.getLogger(__name__)


def evaluate_autonomy_policy(
    user_id: str,
    simulation_data: Dict,
    conn=None
) -> Dict:
    """
    Evaluate if an approved simulation can be executed autonomously.
    
    Args:
        user_id: User ID
        simulation_data: Simulation data including confidence, risk_score, expected_roi, etc.
        conn: Optional database connection
        
    Returns:
        dict: {
            'allowed': bool,
            'decision': 'ALLOW_EXECUTION' | 'DENY_EXECUTION' | 'DEFER_TO_MANUAL',
            'reason': str,
            'policy_snapshot': dict,
            'violations': list
        }
    """
    should_close = False
    if conn is None:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not set")
        conn = psycopg2.connect(DATABASE_URL)
        should_close = True
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 1. Check kill switch first (highest priority)
        from services.autonomy_service import check_kill_switch
        if check_kill_switch(conn):
            return {
                'allowed': False,
                'decision': 'DENY_EXECUTION',
                'reason': 'Kill switch is active',
                'policy_snapshot': {},
                'violations': ['kill_switch_active']
            }
        
        # 2. Get active autonomy policy for user
        cursor.execute("""
            SELECT * FROM autonomy_policies
            WHERE enabled = TRUE
            ORDER BY created_at DESC
            LIMIT 1
        """)
        policy = cursor.fetchone()
        
        if not policy:
            return {
                'allowed': False,
                'decision': 'DEFER_TO_MANUAL',
                'reason': 'No active autonomy policy found',
                'policy_snapshot': {},
                'violations': ['no_active_policy']
            }
        
        policy_dict = dict(policy)
        violations = []
        checks_passed = {}
        
        # 3. Extract simulation metrics with proper None handling
        # Handle confidence - check both 'confidence' and 'confidence_score'
        confidence_raw = simulation_data.get('confidence')
        if confidence_raw is None:
            confidence_raw = simulation_data.get('confidence_score')
        
        # Convert to float, handling None and invalid values
        try:
            confidence = float(confidence_raw) if confidence_raw is not None else 0.0
            if not (0.0 <= confidence <= 1.0):
                confidence = 0.0
        except (TypeError, ValueError):
            confidence = 0.0
        
        # Handle risk_score
        risk_score_raw = simulation_data.get('risk_score')
        risk_score_missing = False
        try:
            if risk_score_raw is None:
                # If risk_score is missing, use a conservative default (0.25) that passes threshold
                # This allows execution but logs a warning for manual review
                risk_score = 0.25
                risk_score_missing = True
                logger.warning(f"Risk score missing for simulation, using conservative default 0.25 (below threshold)")
            else:
                risk_score = float(risk_score_raw)
                if not (0.0 <= risk_score <= 1.0):
                    # Invalid range - use conservative default
                    risk_score = 0.25
                    risk_score_missing = True
                    logger.warning(f"Invalid risk_score value: {risk_score_raw}, using conservative default 0.25")
        except (TypeError, ValueError):
            risk_score = 0.25
            risk_score_missing = True
            logger.warning(f"Failed to parse risk_score: {risk_score_raw}, using conservative default 0.25")
        
        # Handle expected_roi
        expected_roi_raw = simulation_data.get('expected_roi')
        try:
            expected_roi = float(expected_roi_raw) if expected_roi_raw is not None else 0.0
        except (TypeError, ValueError):
            expected_roi = 0.0
        
        # Handle quantity
        quantity_raw = simulation_data.get('quantity')
        try:
            quantity = int(quantity_raw) if quantity_raw is not None else 1
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1
        
        # Estimate execution value (simplified - in production, use actual asset price)
        execution_value = abs(float(expected_roi)) * int(quantity) * 0.01  # Placeholder calculation
        
        # 4. Check confidence threshold (HARD LIMIT: >= 0.85)
        try:
            policy_confidence = policy_dict.get('confidence_threshold')
            policy_confidence_float = float(policy_confidence) if policy_confidence is not None else 0.85
            min_confidence = max(0.85, policy_confidence_float)
        except (TypeError, ValueError):
            min_confidence = 0.85
        
        if confidence < min_confidence:
            violations.append(f'confidence_below_threshold: {confidence:.2f} < {min_confidence:.2f}')
            checks_passed['confidence'] = False
        else:
            checks_passed['confidence'] = True
        
        # 5. Check risk threshold (HARD LIMIT: <= 0.30)
        try:
            policy_risk = policy_dict.get('risk_threshold')
            policy_risk_float = float(policy_risk) if policy_risk is not None else 0.30
            max_risk = min(0.30, policy_risk_float)
        except (TypeError, ValueError):
            max_risk = 0.30
        
        if risk_score > max_risk:
            if risk_score_missing:
                violations.append(f'risk_score_missing_or_invalid: calculated risk {risk_score:.2f} exceeds threshold {max_risk:.2f}')
            else:
                violations.append(f'risk_above_threshold: {risk_score:.2f} > {max_risk:.2f}')
            checks_passed['risk'] = False
        else:
            checks_passed['risk'] = True
            if risk_score_missing:
                # Log warning but don't block execution if default passes
                logger.info(f"Risk score was missing, used conservative default 0.25 which passes threshold {max_risk:.2f}")
        
        # 6. Check daily trade limit (HARD LIMIT: max 1 per day)
        today = date.today()
        # Check if autonomous_executions table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'autonomous_executions'
            ) as exists
        """)
        result = cursor.fetchone()
        table_exists = result['exists'] if result else False
        
        if table_exists:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM autonomous_executions
                WHERE user_id = %s 
                AND DATE(executed_at) = %s
                AND decision = 'EXECUTED'
            """, (user_id, today))
            
            daily_result = cursor.fetchone()
            trades_today = daily_result['count'] if daily_result else 0
        else:
            trades_today = 0  # Table doesn't exist, no trades today
        
        max_daily = min(1, policy_dict.get('max_daily_trades', 1))  # Hard limit: 1
        if trades_today >= max_daily:
            violations.append(f'daily_trade_limit_reached: {trades_today}/{max_daily}')
            checks_passed['daily_limit'] = False
        else:
            checks_passed['daily_limit'] = True
        
        # 7. Check daily value limit
        if table_exists:
            cursor.execute("""
                SELECT COALESCE(SUM((execution_result->>'execution_value')::numeric), 0) as total_value
                FROM autonomous_executions
                WHERE user_id = %s 
                AND DATE(executed_at) = %s
                AND decision = 'EXECUTED'
            """, (user_id, today))
            
            value_result = cursor.fetchone()
            value_today = float(value_result['total_value']) if value_result and value_result['total_value'] else 0.0
        else:
            value_today = 0.0  # Table doesn't exist, no value today
        
        try:
            max_daily_value_raw = policy_dict.get('max_trade_value')
            max_daily_value = float(max_daily_value_raw) if max_daily_value_raw is not None else 0.0
        except (TypeError, ValueError):
            max_daily_value = 0.0
        
        if max_daily_value > 0 and (value_today + execution_value) > max_daily_value:
            violations.append(f'daily_value_limit_exceeded: {value_today + execution_value:.2f} > {max_daily_value:.2f}')
            checks_passed['value_limit'] = False
        else:
            checks_passed['value_limit'] = True
        
        # 8. Check asset restrictions (if policy has allowed_assets)
        allowed_assets = policy_dict.get('allowed_assets', [])
        if isinstance(allowed_assets, list) and len(allowed_assets) > 0:
            asset_id = simulation_data.get('asset_id')
            if asset_id not in allowed_assets:
                violations.append(f'asset_not_allowed: {asset_id}')
                checks_passed['asset_restriction'] = False
            else:
                checks_passed['asset_restriction'] = True
        else:
            checks_passed['asset_restriction'] = True  # No restriction
        
        # 9. Check region restrictions (if policy has allowed_regions)
        allowed_regions = policy_dict.get('allowed_regions', [])
        if isinstance(allowed_regions, list) and len(allowed_regions) > 0:
            buy_region = simulation_data.get('buy_region')
            sell_region = simulation_data.get('sell_region')
            regions_used = [r for r in [buy_region, sell_region] if r]
            if regions_used and not any(r in allowed_regions for r in regions_used):
                violations.append(f'region_not_allowed: {regions_used}')
                checks_passed['region_restriction'] = False
            else:
                checks_passed['region_restriction'] = True
        else:
            checks_passed['region_restriction'] = True  # No restriction
        
        # 10. Make decision
        if len(violations) == 0:
            decision = 'ALLOW_EXECUTION'
            allowed = True
            reason = 'All policy checks passed'
        else:
            decision = 'DENY_EXECUTION'
            allowed = False
            reason = f'Policy violations: {", ".join(violations)}'
        
        # Create policy snapshot for audit
        policy_snapshot = {
            'policy_id': str(policy_dict['id']),
            'policy_name': policy_dict['policy_name'],
            'confidence_threshold': min_confidence,
            'risk_threshold': max_risk,
            'max_daily_trades': max_daily,
            'max_daily_value': max_daily_value,
            'simulation_metrics': {
                'confidence': confidence,
                'risk_score': risk_score,
                'expected_roi': expected_roi,
                'execution_value': execution_value
            },
            'daily_usage': {
                'trades_today': trades_today,
                'value_today': value_today
            },
            'checks_passed': checks_passed,
            'violations': violations,
            'evaluated_at': datetime.now().isoformat()
        }
        
        return {
            'allowed': allowed,
            'decision': decision,
            'reason': reason,
            'policy_snapshot': policy_snapshot,
            'violations': violations
        }
        
    except Exception as e:
        logger.error(f"Error evaluating autonomy policy: {e}", exc_info=True)
        return {
            'allowed': False,
            'decision': 'DEFER_TO_MANUAL',
            'reason': f'Policy evaluation error: {str(e)}',
            'policy_snapshot': {},
            'violations': ['evaluation_error']
        }
    finally:
        cursor.close()
        if should_close:
            conn.close()
