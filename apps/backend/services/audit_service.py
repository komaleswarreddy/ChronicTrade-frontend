"""
Audit Service - Phase 23
Manages decision lineage and policy evaluations for governance.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


def record_decision_lineage(
    user_id: str,
    simulation_id: str,
    model_version: Optional[str] = None,
    policy_version: Optional[str] = None,
    input_snapshot: Optional[Dict] = None,
    decision_reasoning: Optional[str] = None,
    conn=None
) -> Dict:
    """
    Record decision lineage for a simulation (IMMUTABLE).
    
    Args:
        user_id: User ID
        simulation_id: Simulation ID
        model_version: Model version used
        policy_version: Policy version used
        input_snapshot: Snapshot of inputs at decision time
        decision_reasoning: Human-readable reasoning
        conn: Optional database connection
        
    Returns:
        dict: Lineage record
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
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'decision_lineage'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            logger.warning("decision_lineage table does not exist. Run Phase 23 migration.")
            return {}
        
        lineage_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO decision_lineage (
                id, user_id, simulation_id, model_version, policy_version,
                input_snapshot, decision_reasoning, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """, (
            lineage_id,
            user_id,
            simulation_id,
            model_version or 'v1.0',
            policy_version or 'v1.0',
            json.dumps(input_snapshot) if input_snapshot else None,
            decision_reasoning,
            datetime.now()
        ))
        
        lineage = cursor.fetchone()
        conn.commit()
        
        logger.info(f"Recorded decision lineage {lineage_id} for simulation {simulation_id}")
        return dict(lineage) if lineage else {}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error recording decision lineage: {e}", exc_info=True)
        return {}
    finally:
        cursor.close()
        if should_close:
            conn.close()


def record_policy_evaluation(
    simulation_id: str,
    policy_name: str,
    result: str,
    failure_reason: Optional[str] = None,
    conn=None
) -> Dict:
    """
    Record policy evaluation result (IMMUTABLE).
    
    Args:
        simulation_id: Simulation ID
        policy_name: Name of policy evaluated
        result: 'PASS' or 'FAIL'
        failure_reason: Reason if failed
        conn: Optional database connection
        
    Returns:
        dict: Policy evaluation record
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
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'policy_evaluations'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            logger.warning("policy_evaluations table does not exist. Run Phase 23 migration.")
            return {}
        
        eval_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO policy_evaluations (
                id, simulation_id, policy_name, result, failure_reason, evaluated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """, (
            eval_id,
            simulation_id,
            policy_name,
            result,
            failure_reason,
            datetime.now()
        ))
        
        evaluation = cursor.fetchone()
        conn.commit()
        
        logger.info(f"Recorded policy evaluation {eval_id}: {policy_name} = {result} for simulation {simulation_id}")
        return dict(evaluation) if evaluation else {}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error recording policy evaluation: {e}", exc_info=True)
        return {}
    finally:
        cursor.close()
        if should_close:
            conn.close()


def get_decision_lineage(user_id: str, simulation_id: Optional[str] = None, conn=None) -> List[Dict]:
    """
    Get decision lineage records for a user.
    
    Args:
        user_id: User ID
        simulation_id: Optional simulation ID filter
        conn: Optional database connection
        
    Returns:
        list: List of lineage records
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
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'decision_lineage'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            return []
        
        query = """
            SELECT * FROM decision_lineage
            WHERE user_id = %s
        """
        params = [user_id]
        
        if simulation_id:
            query += " AND simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        lineage = cursor.fetchall()
        
        # Parse JSONB fields
        result = []
        for record in lineage:
            rec_dict = dict(record)
            if rec_dict.get('input_snapshot'):
                try:
                    if isinstance(rec_dict['input_snapshot'], str):
                        rec_dict['input_snapshot'] = json.loads(rec_dict['input_snapshot'])
                except:
                    pass
            result.append(rec_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching decision lineage: {e}", exc_info=True)
        return []
    finally:
        cursor.close()
        if should_close:
            conn.close()


def get_policy_evaluations(simulation_id: str, conn=None) -> List[Dict]:
    """
    Get policy evaluations for a simulation.
    
    Args:
        simulation_id: Simulation ID
        conn: Optional database connection
        
    Returns:
        list: List of policy evaluation records
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
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'policy_evaluations'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            return []
        
        cursor.execute("""
            SELECT * FROM policy_evaluations
            WHERE simulation_id = %s
            ORDER BY evaluated_at DESC
        """, (simulation_id,))
        
        evaluations = cursor.fetchall()
        return [dict(eval) for eval in evaluations]
        
    except Exception as e:
        logger.error(f"Error fetching policy evaluations: {e}", exc_info=True)
        return []
    finally:
        cursor.close()
        if should_close:
            conn.close()
