"""
Phase 23 Migration: Governance & Audit
Creates decision_lineage and policy_evaluations tables.
"""

import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def migrate():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        print("Phase 23: Creating governance and audit tables...")
        
        # 1. decision_lineage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_lineage (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                simulation_id UUID REFERENCES simulated_orders(id),
                model_version TEXT,
                policy_version TEXT,
                input_snapshot JSONB,
                decision_reasoning TEXT,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. policy_evaluations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS policy_evaluations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                simulation_id UUID NOT NULL REFERENCES simulated_orders(id),
                policy_name TEXT NOT NULL,
                result TEXT NOT NULL CHECK (result IN ('PASS', 'FAIL')),
                failure_reason TEXT,
                evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decision_lineage_user_id ON decision_lineage(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decision_lineage_simulation_id ON decision_lineage(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decision_lineage_timestamp ON decision_lineage(timestamp DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_evaluations_simulation_id ON policy_evaluations(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_evaluations_policy_name ON policy_evaluations(policy_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_evaluations_result ON policy_evaluations(result);")
        
        conn.commit()
        print("Phase 23 migration completed successfully")
        print("  - Created decision_lineage table")
        print("  - Created policy_evaluations table")
        print("  - Created indexes")
        print("  Note: All records are immutable - enforce in application code")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
