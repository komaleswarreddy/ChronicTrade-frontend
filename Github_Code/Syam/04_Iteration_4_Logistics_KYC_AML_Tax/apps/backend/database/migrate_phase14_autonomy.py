"""
Phase 14 Database Migration - Guarded Autonomous Execution
Creates tables for autonomy policies and execution logging.
Includes kill switch mechanism and strict limits.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_phase14_autonomy():
    """Create Phase 14 autonomy and policy tables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        print("Starting Phase 14 migration for guarded autonomy...")
        
        # 1. autonomy_policies table - Define what AI is allowed to execute
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autonomy_policies (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                policy_name TEXT NOT NULL UNIQUE,
                max_trade_value REAL DEFAULT 0 CHECK (max_trade_value >= 0),
                max_daily_trades INTEGER DEFAULT 0 CHECK (max_daily_trades >= 0),
                allowed_assets JSONB DEFAULT '[]'::jsonb,
                allowed_regions JSONB DEFAULT '[]'::jsonb,
                confidence_threshold REAL DEFAULT 1.0 CHECK (confidence_threshold >= 0 AND confidence_threshold <= 1),
                risk_threshold REAL DEFAULT 1.0 CHECK (risk_threshold >= 0 AND risk_threshold <= 1),
                enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Indexes for autonomy_policies
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_policies_enabled ON autonomy_policies(enabled) WHERE enabled = TRUE;")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_policies_name ON autonomy_policies(policy_name);")
        
        # 2. autonomy_execution_log table - Log all autonomous executions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autonomy_execution_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                simulation_id UUID REFERENCES simulated_orders(id),
                policy_id UUID REFERENCES autonomy_policies(id),
                execution_type TEXT NOT NULL CHECK (execution_type IN ('AUTONOMOUS', 'MANUAL_OVERRIDE')),
                trade_value REAL,
                confidence_score REAL,
                risk_score REAL,
                policy_checks_passed JSONB,
                execution_result TEXT,
                error_message TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
        """)
        
        # Indexes for autonomy_execution_log
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_log_user_id ON autonomy_execution_log(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_log_simulation_id ON autonomy_execution_log(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_log_policy_id ON autonomy_execution_log(policy_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_log_executed_at ON autonomy_execution_log(executed_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autonomy_log_type ON autonomy_execution_log(execution_type);")
        
        # 3. autonomy_kill_switch table - Global kill switch state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autonomy_kill_switch (
                id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
                enabled BOOLEAN DEFAULT FALSE,
                reason TEXT,
                disabled_at TIMESTAMP,
                disabled_by TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Initialize kill switch as DISABLED (safe default)
        cursor.execute("""
            INSERT INTO autonomy_kill_switch (id, enabled, last_updated)
            VALUES (1, FALSE, CURRENT_TIMESTAMP)
            ON CONFLICT (id) DO NOTHING
        """)
        
        # 4. autonomy_daily_limits table - Track daily execution limits
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autonomy_daily_limits (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                date DATE NOT NULL DEFAULT CURRENT_DATE,
                trades_executed INTEGER DEFAULT 0,
                total_value_executed REAL DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            );
        """)
        
        # Indexes for autonomy_daily_limits
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON autonomy_daily_limits(user_id, date DESC);")
        
        conn.commit()
        print("✓ Phase 14 autonomy tables created successfully")
        print("  - autonomy_policies")
        print("  - autonomy_execution_log")
        print("  - autonomy_kill_switch (initialized as DISABLED)")
        print("  - autonomy_daily_limits")
        print("  Note: Kill switch is DISABLED by default (safe)")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error during Phase 14 migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    migrate_phase14_autonomy()
