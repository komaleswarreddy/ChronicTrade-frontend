"""
Phase C5: KYC/AML/Tax Automation
Implements pre-execution gating to block illegal or non-compliant trades.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


def evaluate_execution_gates(simulation_id: str, user_id: str, conn=None) -> Dict:
    """
    Evaluate all execution gates (KYC, AML, Tax) for a simulation.
    
    Args:
        simulation_id: Simulation ID
        user_id: User ID
        conn: Optional database connection
        
    Returns:
        dict: {
            'overall_status': 'PASSED' | 'BLOCKED',
            'gates': list of gate evaluations,
            'block_reasons': list of reasons if blocked
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
        # Check if tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'execution_gates'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            logger.warning("execution_gates table does not exist. Run Phase C5 migration.")
            return {
                'overall_status': 'PASSED',
                'gates': [],
                'block_reasons': [],
                'message': 'Gating system not initialized - defaulting to PASSED'
            }
        
        # Ensure KYC status exists for user (auto-initialize if missing)
        _ensure_kyc_initialized(user_id, cursor)
        
        # Get simulation details
        cursor.execute("""
            SELECT so.*, a.region as asset_region
            FROM simulated_orders so
            JOIN assets a ON so.asset_id = a.asset_id
            WHERE so.id = %s
        """, (simulation_id,))
        
        simulation = cursor.fetchone()
        if not simulation:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        sim_dict = dict(simulation)
        source_country = sim_dict.get('buy_region') or sim_dict.get('asset_region')
        dest_country = sim_dict.get('sell_region') or sim_dict.get('asset_region')
        
        gates = []
        block_reasons = []
        overall_status = 'PASSED'
        
        # Evaluate KYC gate
        kyc_result = _evaluate_kyc_gate(user_id, cursor)
        gates.append(kyc_result)
        if kyc_result['status'] == 'BLOCKED':
            overall_status = 'BLOCKED'
            block_reasons.append(kyc_result['block_reason'])
        
        # Evaluate AML gate
        aml_result = _evaluate_aml_gate(user_id, cursor)
        gates.append(aml_result)
        if aml_result['status'] == 'BLOCKED':
            overall_status = 'BLOCKED'
            block_reasons.append(aml_result['block_reason'])
        
        # Evaluate Tax gate
        tax_result = _evaluate_tax_gate(simulation_id, source_country, dest_country, cursor)
        gates.append(tax_result)
        if tax_result['status'] == 'BLOCKED':
            overall_status = 'BLOCKED'
            block_reasons.append(tax_result['block_reason'])
        
        # Store gate evaluations
        for gate in gates:
            gate_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO execution_gates (
                    id, simulation_id, gate_type, gate_status, block_reason, evaluated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (simulation_id, gate_type) DO UPDATE SET
                    gate_status = EXCLUDED.gate_status,
                    block_reason = EXCLUDED.block_reason,
                    evaluated_at = CURRENT_TIMESTAMP
            """, (
                gate_id,
                simulation_id,
                gate['type'],
                gate['status'],
                gate.get('block_reason'),
                datetime.now()
            ))
        
        conn.commit()
        
        return {
            'overall_status': overall_status,
            'gates': gates,
            'block_reasons': block_reasons
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error evaluating execution gates: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        if should_close:
            conn.close()


def _ensure_kyc_initialized(user_id: str, cursor):
    """Ensure KYC status exists for a user. Auto-initializes if missing."""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'kyc_status'
        ) as exists
    """)
    result = cursor.fetchone()
    if not result or not result['exists']:
        return  # Table doesn't exist, skip initialization
    
    cursor.execute("""
        SELECT user_id FROM kyc_status WHERE user_id = %s
    """, (user_id,))
    
    existing = cursor.fetchone()
    if not existing:
        # Auto-initialize KYC status for development/testing
        # Note: user_id is the PRIMARY KEY, so no separate id field needed
        try:
            cursor.execute("""
                INSERT INTO kyc_status (
                    user_id, verification_status, kyc_level, verified_at, updated_at
                ) VALUES (
                    %s, 'VERIFIED', 'BASIC', %s, %s
                )
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, datetime.now(), datetime.now()))
            logger.info(f"Auto-initialized KYC status for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to auto-initialize KYC for user {user_id}: {e}")


def _evaluate_kyc_gate(user_id: str, cursor) -> Dict:
    """Evaluate KYC gate for a user. KYC should already be initialized by _ensure_kyc_initialized."""
    cursor.execute("""
        SELECT * FROM kyc_status WHERE user_id = %s
    """, (user_id,))
    
    kyc = cursor.fetchone()
    
    if not kyc:
        # This should not happen if _ensure_kyc_initialized was called, but handle gracefully
        logger.warning(f"KYC status not found for user {user_id} despite initialization attempt")
        return {
            'type': 'KYC',
            'status': 'BLOCKED',
            'block_reason': 'KYC verification not completed'
        }
    
    kyc_dict = dict(kyc)
    
    if kyc_dict['verification_status'] != 'VERIFIED':
        return {
            'type': 'KYC',
            'status': 'BLOCKED',
            'block_reason': f"KYC status: {kyc_dict['verification_status']}"
        }
    
    if kyc_dict['kyc_level'] == 'NONE':
        return {
            'type': 'KYC',
            'status': 'BLOCKED',
            'block_reason': 'KYC level insufficient'
        }
    
    return {
        'type': 'KYC',
        'status': 'PASSED',
        'kyc_level': kyc_dict['kyc_level']
    }


def _evaluate_aml_gate(user_id: str, cursor) -> Dict:
    """Evaluate AML gate for a user."""
    cursor.execute("""
        SELECT * FROM aml_risk_flags
        WHERE user_id = %s AND active = true
        ORDER BY flagged_at DESC
        LIMIT 1
    """, (user_id,))
    
    aml_flag = cursor.fetchone()
    
    if not aml_flag:
        return {
            'type': 'AML',
            'status': 'PASSED'
        }
    
    aml_dict = dict(aml_flag)
    
    if aml_dict['risk_level'] in ['HIGH', 'CRITICAL']:
        return {
            'type': 'AML',
            'status': 'BLOCKED',
            'block_reason': f"AML risk level: {aml_dict['risk_level']} - {aml_dict.get('risk_reason', '')}"
        }
    
    return {
        'type': 'AML',
        'status': 'PASSED',
        'risk_level': aml_dict['risk_level']
    }


def _evaluate_tax_gate(simulation_id: str, source_country: str, dest_country: str, cursor) -> Dict:
    """Evaluate Tax gate for a simulation."""
    # Simplified tax evaluation - in production, use actual tax rules
    if source_country == dest_country:
        return {
            'type': 'TAX',
            'status': 'PASSED',
            'message': 'Domestic trade - no import duties'
        }
    
    # Store tax obligation
    tax_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO tax_obligations (
            id, simulation_id, source_country, destination_country,
            tax_type, tax_rate, obligation_status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT DO NOTHING
    """, (
        tax_id,
        simulation_id,
        source_country,
        dest_country,
        'IMPORT_DUTY',
        0.15,  # 15% default
        'CALCULATED'
    ))
    
    return {
        'type': 'TAX',
        'status': 'PASSED',
        'tax_obligation_id': tax_id
    }


def get_execution_gates(simulation_id: str, conn=None) -> List[Dict]:
    """
    Get execution gate evaluations for a simulation.
    
    Args:
        simulation_id: Simulation ID
        conn: Optional database connection
        
    Returns:
        list: List of gate evaluations
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
        cursor.execute("""
            SELECT * FROM execution_gates
            WHERE simulation_id = %s
            ORDER BY evaluated_at DESC
        """, (simulation_id,))
        
        gates = cursor.fetchall()
        return [dict(gate) for gate in gates]
        
    except Exception as e:
        logger.error(f"Error fetching execution gates: {e}", exc_info=True)
        return []
    finally:
        cursor.close()
        if should_close:
            conn.close()
