"""
Execution Audit Service - Phase 16
Comprehensive audit logging for autonomous executions.
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


def log_execution_event(
    user_id: str,
    event_type: str,
    entity_id: str,
    details: Optional[Dict] = None,
    conn=None
) -> str:
    """
    Log an execution audit event.
    
    Args:
        user_id: User ID
        event_type: Type of event (e.g., 'AUTONOMOUS_EXECUTION', 'POLICY_EVALUATION', 'KILL_SWITCH_ACTIVATED')
        entity_id: Entity ID (simulation_id, execution_id, etc.)
        details: Optional details dictionary
        conn: Optional database connection
        
    Returns:
        str: Audit log entry ID
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
        audit_id = str(uuid.uuid4())
        
        # Use execution_audit_log table (from Phase 11, extended in Phase 16)
        # Check if event_type and details columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'execution_audit_log' AND column_name IN ('event_type', 'details')
        """)
        columns = {row[0] for row in cursor.fetchall()}
        
        has_event_type = 'event_type' in columns
        has_details = 'details' in columns
        
        if has_event_type and has_details:
            # Phase 16 extended table
            cursor.execute("""
                INSERT INTO execution_audit_log (
                    id, user_id, entity_type, entity_id, action,
                    metadata, event_type, details, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                audit_id,
                user_id,
                'EXECUTION',  # entity_type
                entity_id,
                event_type,  # action
                json.dumps(details) if details else None,  # metadata (for backward compatibility)
                event_type,  # event_type (Phase 16 addition)
                json.dumps(details) if details else None,  # details (Phase 16 addition)
                datetime.now()
            ))
        else:
            # Phase 11 table structure (backward compatibility)
            cursor.execute("""
                INSERT INTO execution_audit_log (
                    id, user_id, entity_type, entity_id, action,
                    metadata, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                audit_id,
                user_id,
                'EXECUTION',  # entity_type
                entity_id,
                event_type,  # action
                json.dumps(details) if details else None,  # metadata
                datetime.now()
            ))
        
        if should_close:
            conn.commit()
        
        logger.debug(f"Logged execution audit event: {event_type} for {entity_id}")
        return audit_id
        
    except Exception as e:
        if should_close:
            conn.rollback()
        logger.error(f"Failed to log execution audit event: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        if should_close:
            conn.close()


def get_execution_audit_log(
    user_id: str,
    event_type: Optional[str] = None,
    limit: int = 50,
    conn=None
) -> List[Dict]:
    """
    Get execution audit log entries for a user.
    
    Args:
        user_id: User ID
        event_type: Optional event type filter
        limit: Maximum number of entries to return
        conn: Optional database connection
        
    Returns:
        list: List of audit log entries
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
        if event_type:
            cursor.execute("""
                SELECT * FROM execution_audit_log
                WHERE user_id = %s AND event_type = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, event_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM execution_audit_log
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
        
        entries = cursor.fetchall()
        return [dict(entry) for entry in entries]
        
    except Exception as e:
        logger.error(f"Error fetching execution audit log: {e}", exc_info=True)
        return []
    finally:
        cursor.close()
        if should_close:
            conn.close()
