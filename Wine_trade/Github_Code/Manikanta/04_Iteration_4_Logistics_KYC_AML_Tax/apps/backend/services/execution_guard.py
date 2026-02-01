"""
Execution Guard - Phase 16
Safety checks and kill switch enforcement for autonomous execution.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def check_execution_safety(
    user_id: str,
    simulation_id: str,
    conn=None
) -> Dict:
    """
    Perform safety checks before allowing autonomous execution.
    
    Args:
        user_id: User ID
        simulation_id: Simulation ID to check
        conn: Optional database connection
        
    Returns:
        dict: {
            'safe': bool,
            'reason': str,
            'checks': dict
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
        checks = {}
        
        # 1. Check global kill switch
        from services.autonomy_service import check_kill_switch
        kill_switch_active = check_kill_switch(conn)
        checks['kill_switch'] = not kill_switch_active
        if kill_switch_active:
            return {
                'safe': False,
                'reason': 'Global kill switch is active',
                'checks': checks
            }
        
        # 2. Verify simulation exists and is APPROVED
        cursor.execute("""
            SELECT * FROM simulated_orders
            WHERE id = %s AND user_id = %s
        """, (simulation_id, user_id))
        
        simulation = cursor.fetchone()
        if not simulation:
            checks['simulation_exists'] = False
            return {
                'safe': False,
                'reason': 'Simulation not found',
                'checks': checks
            }
        
        sim_dict = dict(simulation)
        checks['simulation_exists'] = True
        
        if sim_dict['status'] != 'APPROVED':
            checks['simulation_approved'] = False
            return {
                'safe': False,
                'reason': f"Simulation status is {sim_dict['status']}, must be APPROVED",
                'checks': checks
            }
        checks['simulation_approved'] = True
        
        # 3. Check if simulation was already executed
        if sim_dict['status'] == 'EXECUTED':
            checks['not_already_executed'] = False
            return {
                'safe': False,
                'reason': 'Simulation already executed',
                'checks': checks
            }
        checks['not_already_executed'] = True
        
        # 4. Check if there's already an autonomous execution record
        # First check if table exists
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
                SELECT * FROM autonomous_executions
                WHERE simulation_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (simulation_id,))
            
            existing_execution = cursor.fetchone()
            if existing_execution:
                exec_dict = dict(existing_execution)
                if exec_dict['decision'] == 'EXECUTED':
                    checks['no_duplicate_execution'] = False
                    return {
                        'safe': False,
                        'reason': 'Autonomous execution already recorded',
                        'checks': checks
                    }
        checks['no_duplicate_execution'] = True
        
        # 5. Check user autonomy status
        cursor.execute("""
            SELECT * FROM autonomy_policies
            WHERE enabled = TRUE
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        policy = cursor.fetchone()
        if not policy:
            checks['autonomy_enabled'] = False
            return {
                'safe': False,
                'reason': 'No active autonomy policy',
                'checks': checks
            }
        checks['autonomy_enabled'] = True
        
        # All checks passed
        return {
            'safe': True,
            'reason': 'All safety checks passed',
            'checks': checks
        }
        
    except Exception as e:
        logger.error(f"Error checking execution safety: {e}", exc_info=True)
        return {
            'safe': False,
            'reason': f'Safety check error: {str(e)}',
            'checks': {}
        }
    finally:
        cursor.close()
        if should_close:
            conn.close()


def enforce_kill_switch(conn=None) -> bool:
    """
    Check and enforce kill switch - returns True if execution should be blocked.
    
    Args:
        conn: Optional database connection
        
    Returns:
        bool: True if kill switch is active (block execution), False otherwise
    """
    try:
        from services.autonomy_service import check_kill_switch
        return check_kill_switch(conn)
    except Exception as e:
        logger.error(f"Error checking kill switch: {e}", exc_info=True)
        # On error, default to blocking execution (safe default)
        return True
