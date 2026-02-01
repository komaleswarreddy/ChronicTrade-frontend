"""
Autonomy Service - Phase 14
Handles guarded autonomous execution with strict limits and kill switch.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime, date

logger = logging.getLogger(__name__)


def check_kill_switch(conn=None) -> bool:
    """
    Check if kill switch is active.
    
    Returns:
        bool: True if kill switch is active (autonomy disabled), False otherwise
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
        # Check environment variable first (fastest)
        env_kill_switch = os.getenv("AUTONOMY_KILL_SWITCH", "FALSE").upper()
        if env_kill_switch == "TRUE":
            logger.warning("Kill switch ACTIVE via environment variable")
            return True
        
        # Check database kill switch
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'autonomy_kill_switch'
            )
        """)
        if not cursor.fetchone()['exists']:
            # Table doesn't exist, default to safe (kill switch active)
            logger.warning("autonomy_kill_switch table does not exist - defaulting to SAFE (disabled)")
            return True
        
        cursor.execute("SELECT enabled FROM autonomy_kill_switch WHERE id = 1")
        result = cursor.fetchone()
        
        if result:
            kill_switch_active = not result['enabled']  # enabled=False means kill switch is ON
            if kill_switch_active:
                logger.warning("Kill switch ACTIVE via database")
            return kill_switch_active
        
        # No record found, default to safe (kill switch active)
        logger.warning("No kill switch record found - defaulting to SAFE (disabled)")
        return True
        
    except Exception as e:
        logger.error(f"Error checking kill switch: {e}", exc_info=True)
        # On error, default to safe (kill switch active)
        return True
    finally:
        cursor.close()
        if should_close:
            conn.close()


def get_autonomy_status(user_id: str, conn=None) -> Dict:
    """
    Get current autonomy status and limits.
    
    Args:
        user_id: User ID
        conn: Optional database connection
        
    Returns:
        dict: Autonomy status with limits and current usage
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
        kill_switch_active = check_kill_switch(conn)
        
        # Get active policies
        cursor.execute("""
            SELECT * FROM autonomy_policies
            WHERE enabled = TRUE
            ORDER BY created_at DESC
        """)
        policies = cursor.fetchall()
        
        # Get daily limits for user
        today = date.today()
        cursor.execute("""
            SELECT trades_executed, total_value_executed
            FROM autonomy_daily_limits
            WHERE user_id = %s AND date = %s
        """, (user_id, today))
        
        daily_limit = cursor.fetchone()
        trades_today = daily_limit['trades_executed'] if daily_limit else 0
        value_today = float(daily_limit['total_value_executed']) if daily_limit and daily_limit['total_value_executed'] else 0.0
        
        return {
            'autonomy_enabled': not kill_switch_active and len(policies) > 0,
            'kill_switch_active': kill_switch_active,
            'active_policies': [dict(p) for p in policies],
            'daily_limits': {
                'trades_today': trades_today,
                'value_today': value_today
            },
            'total_trades_today': trades_today,
            'total_value_today': value_today
        }
        
    except Exception as e:
        logger.error(f"Error getting autonomy status: {e}", exc_info=True)
        return {
            'autonomy_enabled': False,
            'kill_switch_active': True,
            'active_policies': [],
            'daily_limits': {},
            'total_trades_today': 0,
            'total_value_today': 0.0
        }
    finally:
        cursor.close()
        if should_close:
            conn.close()


def check_autonomy_policy(
    user_id: str,
    simulation_id: str,
    confidence_score: float,
    risk_score: float,
    trade_value: float,
    conn=None
) -> Dict:
    """
    Check if a simulation can be executed autonomously based on policy.
    
    Args:
        user_id: User ID
        simulation_id: Simulation ID
        confidence_score: Confidence score (0-1)
        risk_score: Risk score (0-1)
        trade_value: Trade value
        conn: Optional database connection
        
    Returns:
        dict: Policy check result with allowed flag and reasons
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
        # 1. Check kill switch FIRST
        if check_kill_switch(conn):
            return {
                'allowed': False,
                'reason': 'Kill switch is active',
                'checks_passed': {}
            }
        
        # 2. Get active policy
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
                'reason': 'No active autonomy policy',
                'checks_passed': {}
            }
        
        policy_dict = dict(policy)
        checks_passed = {}
        
        # 3. Check confidence threshold (HARD LIMIT: >= 0.85)
        min_confidence = max(0.85, policy_dict.get('confidence_threshold', 0.85))
        if confidence_score < min_confidence:
            return {
                'allowed': False,
                'reason': f'Confidence {confidence_score:.2f} below threshold {min_confidence:.2f}',
                'checks_passed': {'confidence': False}
            }
        checks_passed['confidence'] = True
        
        # 4. Check risk threshold (HARD LIMIT: <= 0.30)
        max_risk = min(0.30, policy_dict.get('risk_threshold', 0.30))
        if risk_score > max_risk:
            return {
                'allowed': False,
                'reason': f'Risk {risk_score:.2f} above threshold {max_risk:.2f}',
                'checks_passed': {'risk': False}
            }
        checks_passed['risk'] = True
        
        # 5. Check daily trade limit (HARD LIMIT: max 1 per day)
        today = date.today()
        cursor.execute("""
            SELECT trades_executed
            FROM autonomy_daily_limits
            WHERE user_id = %s AND date = %s
        """, (user_id, today))
        
        daily_limit = cursor.fetchone()
        trades_today = daily_limit['trades_executed'] if daily_limit else 0
        
        max_daily = min(1, policy_dict.get('max_daily_trades', 1))  # Hard limit: 1
        if trades_today >= max_daily:
            return {
                'allowed': False,
                'reason': f'Daily trade limit reached ({trades_today}/{max_daily})',
                'checks_passed': checks_passed
            }
        checks_passed['daily_limit'] = True
        
        # 6. Check trade value limit
        max_value = policy_dict.get('max_trade_value', 0)
        if max_value > 0 and trade_value > max_value:
            return {
                'allowed': False,
                'reason': f'Trade value {trade_value:.2f} exceeds limit {max_value:.2f}',
                'checks_passed': checks_passed
            }
        checks_passed['value_limit'] = True
        
        # 7. Check allowed assets/regions if specified
        allowed_assets = policy_dict.get('allowed_assets', [])
        allowed_regions = policy_dict.get('allowed_regions', [])
        
        # Get simulation details
        cursor.execute("""
            SELECT asset_id, buy_region, sell_region
            FROM simulated_orders
            WHERE id = %s
        """, (simulation_id,))
        sim = cursor.fetchone()
        
        if sim:
            if allowed_assets and sim['asset_id'] not in allowed_assets:
                return {
                    'allowed': False,
                    'reason': f'Asset {sim["asset_id"]} not in allowed list',
                    'checks_passed': checks_passed
                }
            checks_passed['asset_allowed'] = True
            
            if allowed_regions:
                region = sim.get('buy_region') or sim.get('sell_region')
                if region and region not in allowed_regions:
                    return {
                        'allowed': False,
                        'reason': f'Region {region} not in allowed list',
                        'checks_passed': checks_passed
                    }
            checks_passed['region_allowed'] = True
        
        return {
            'allowed': True,
            'reason': 'All policy checks passed',
            'checks_passed': checks_passed,
            'policy_id': str(policy_dict['id'])
        }
        
    except Exception as e:
        logger.error(f"Error checking autonomy policy: {e}", exc_info=True)
        return {
            'allowed': False,
            'reason': f'Policy check error: {str(e)}',
            'checks_passed': {}
        }
    finally:
        cursor.close()
        if should_close:
            conn.close()


def execute_autonomous_simulation(
    user_id: str,
    simulation_id: str,
    conn=None
) -> Dict:
    """
    Execute a simulation autonomously if policy allows.
    
    STRICT LIMITS ENFORCED:
    - Max 1 trade per day
    - Confidence >= 0.85 required
    - Risk <= 0.30 required
    - Kill switch checked
    
    Args:
        user_id: User ID
        simulation_id: Simulation ID
        conn: Optional database connection
        
    Returns:
        dict: Execution result
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
        # 1. Check kill switch
        if check_kill_switch(conn):
            raise ValueError("Autonomy disabled: Kill switch is active")
        
        # 2. Get simulation details
        cursor.execute("""
            SELECT so.*, ap.confidence_score, ap.risk_score
            FROM simulated_orders so
            LEFT JOIN agent_proposals ap ON so.proposal_id = ap.proposal_id
            WHERE so.id = %s AND so.user_id = %s AND so.status = 'APPROVED'
        """, (simulation_id, user_id))
        
        simulation = cursor.fetchone()
        if not simulation:
            raise ValueError(f"Simulation {simulation_id} not found or not approved")
        
        sim_dict = dict(simulation)
        confidence = sim_dict.get('confidence', 0.0) or sim_dict.get('confidence_score', 0.0) or 0.0
        risk = sim_dict.get('risk_score', 1.0) or 1.0
        
        # Estimate trade value (simplified)
        trade_value = (sim_dict.get('expected_roi', 0) / 100) * 1000  # Placeholder calculation
        
        # 3. Check policy
        policy_check = check_autonomy_policy(
            user_id=user_id,
            simulation_id=simulation_id,
            confidence_score=confidence,
            risk_score=risk,
            trade_value=trade_value,
            conn=conn
        )
        
        if not policy_check['allowed']:
            # Log failed attempt
            log_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO autonomy_execution_log (
                    id, user_id, simulation_id, execution_type,
                    confidence_score, risk_score, policy_checks_passed,
                    execution_result, error_message, executed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                log_id, user_id, simulation_id, 'AUTONOMOUS',
                confidence, risk, json.dumps(policy_check['checks_passed']),
                'REJECTED', policy_check['reason'], datetime.now()
            ))
            conn.commit()
            
            raise ValueError(f"Policy check failed: {policy_check['reason']}")
        
        # 4. Update daily limits
        today = date.today()
        cursor.execute("""
            INSERT INTO autonomy_daily_limits (
                id, user_id, date, trades_executed, total_value_executed, last_reset
            ) VALUES (
                %s, %s, %s, 1, %s, %s
            )
            ON CONFLICT (user_id, date) 
            DO UPDATE SET 
                trades_executed = autonomy_daily_limits.trades_executed + 1,
                total_value_executed = autonomy_daily_limits.total_value_executed + %s,
                last_reset = %s
        """, (
            str(uuid.uuid4()), user_id, today, trade_value, datetime.now(),
            trade_value, datetime.now()
        ))
        
        # 5. Mark simulation as executed
        cursor.execute("""
            UPDATE simulated_orders
            SET status = 'EXECUTED', executed_at = %s
            WHERE id = %s
        """, (datetime.now(), simulation_id))
        
        # 6. Log execution
        log_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO autonomy_execution_log (
                id, user_id, simulation_id, policy_id, execution_type,
                trade_value, confidence_score, risk_score,
                policy_checks_passed, execution_result, executed_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            log_id, user_id, simulation_id, policy_check.get('policy_id'),
            'AUTONOMOUS', trade_value, confidence, risk,
            json.dumps(policy_check['checks_passed']), 'SUCCESS', datetime.now()
        ))
        
        conn.commit()
        logger.info(f"Autonomous execution completed for simulation {simulation_id}")
        
        return {
            'success': True,
            'simulation_id': simulation_id,
            'execution_log_id': log_id,
            'policy_checks': policy_check['checks_passed']
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Autonomous execution failed: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        if should_close:
            conn.close()


def toggle_kill_switch(enabled: bool, reason: Optional[str] = None, disabled_by: Optional[str] = None, conn=None):
    """
    Toggle the global kill switch.
    
    Args:
        enabled: True to enable autonomy, False to disable (activate kill switch)
        reason: Optional reason for change
        disabled_by: Optional user/admin who made the change
        conn: Optional database connection
    """
    should_close = False
    if conn is None:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not set")
        conn = psycopg2.connect(DATABASE_URL)
        should_close = True
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE autonomy_kill_switch
            SET enabled = %s,
                reason = %s,
                disabled_at = CASE WHEN %s = FALSE THEN CURRENT_TIMESTAMP ELSE NULL END,
                disabled_by = %s,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (enabled, reason, enabled, disabled_by))
        
        if cursor.rowcount == 0:
            # Insert if doesn't exist
            cursor.execute("""
                INSERT INTO autonomy_kill_switch (id, enabled, reason, disabled_by, last_updated)
                VALUES (1, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (enabled, reason, disabled_by))
        
        conn.commit()
        logger.info(f"Kill switch toggled: enabled={enabled}, reason={reason}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error toggling kill switch: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        if should_close:
            conn.close()
