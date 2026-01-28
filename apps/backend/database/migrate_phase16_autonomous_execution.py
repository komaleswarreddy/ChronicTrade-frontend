"""
Phase 16 Database Migration - Controlled Autonomous Execution Engine
Creates tables for autonomous execution tracking and extends audit logging.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_phase16_autonomous_execution():
    """Create Phase 16 autonomous execution tables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        print("Starting Phase 16 migration for autonomous execution engine...")
        
        # 1. autonomous_executions table - Track all autonomous execution decisions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autonomous_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                simulation_id UUID NOT NULL REFERENCES simulated_orders(id),
                user_id TEXT NOT NULL,
                decision TEXT NOT NULL CHECK (decision IN ('EXECUTED', 'SKIPPED', 'BLOCKED')),
                policy_snapshot JSONB NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failure_reason TEXT,
                execution_result JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Indexes for autonomous_executions
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomous_executions_simulation_id ON autonomous_executions(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomous_executions_user_id ON autonomous_executions(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomous_executions_decision ON autonomous_executions(decision);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomous_executions_executed_at ON autonomous_executions(executed_at DESC);")
        
        # 2. Extend execution_audit_log if needed (check if event_type column exists)
        # Note: execution_audit_log was created in Phase 11, but we need to ensure it has event_type
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'execution_audit_log' AND column_name = 'event_type'
        """)
        if not cursor.fetchone():
            # Add event_type column if it doesn't exist
            cursor.execute("""
                ALTER TABLE execution_audit_log 
                ADD COLUMN IF NOT EXISTS event_type TEXT;
            """)
            print("Added event_type column to execution_audit_log")
        
        # Ensure execution_audit_log has all needed columns for Phase 16
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'execution_audit_log' AND column_name = 'details'
        """)
        if not cursor.fetchone():
            # Add details column if it doesn't exist (as JSONB for flexibility)
            cursor.execute("""
                ALTER TABLE execution_audit_log 
                ADD COLUMN IF NOT EXISTS details JSONB;
            """)
            print("Added details column to execution_audit_log")
        
        conn.commit()
        print("Phase 16 migration completed successfully!")
        print("Created tables:")
        print("  - autonomous_executions")
        print("  - Extended execution_audit_log with event_type and details columns")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during Phase 16 migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_phase16_autonomous_execution()
