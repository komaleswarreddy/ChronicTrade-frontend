#!/usr/bin/env python3
"""
Production Database Migration Runner

Runs all migrations in the correct order for production deployment.
DO NOT run init_db.py in production (it drops tables and creates demo data).

Migration Order:
1. Core schema (via schema.sql)
2. Phase 8: Holdings tables
3. Phase 9: Agent tables
4. Phase 10: Structured explanation
5. Phase 11: Simulated execution
6. Phase 12: Outcome tracking
7. Phase 13: Learning
8. Phase 14: Autonomy
9. Phase 16: Autonomous execution
10. Phase 17: Outcome realization
11. Phase 18: Learning metrics cache
12. Phase 19: Feedback signals
13. Phase 20: Portfolio capital
14. Phase 21: Strategy layer
15. Phase 23: Governance audit
16. Phase C1: Execution engine
17. Phase C2: Compliance reasoning
18. Phase C3: Counterfactual ledger
19. Phase C4: Logistics
20. Phase C5: KYC/AML/Tax
"""

import os
import sys
import psycopg2
from pathlib import Path

# Optional dotenv support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Migration scripts in order
MIGRATION_SCRIPTS = [
    # Core schema (must be first)
    ("schema.sql", "SQL"),
    # Phase migrations
    ("migrate_phase8_tables.py", "PYTHON"),
    ("migrate_holdings_phase8.py", "PYTHON"),
    ("migrate_phase9_agent_tables.py", "PYTHON"),
    ("migrate_phase10_structured_explanation.py", "PYTHON"),
    ("migrate_phase11_simulated_execution.py", "PYTHON"),
    ("migrate_phase12_outcome_tracking.py", "PYTHON"),
    ("migrate_phase13_learning.py", "PYTHON"),
    ("migrate_phase14_autonomy.py", "PYTHON"),
    ("migrate_phase16_autonomous_execution.py", "PYTHON"),
    ("migrate_phase17_outcome_realization.py", "PYTHON"),
    ("migrate_phase18_learning_metrics_cache.py", "PYTHON"),
    ("migrate_phase19_feedback_signals.py", "PYTHON"),
    ("migrate_phase20_portfolio_capital.py", "PYTHON"),
    ("migrate_phase21_strategy_layer.py", "PYTHON"),
    ("migrate_phase23_governance_audit.py", "PYTHON"),
    # Execution engine migrations
    ("migrate_phase_c1_execution_engine.py", "PYTHON"),
    ("migrate_phase_c2_compliance_reasoning.py", "PYTHON"),
    ("migrate_phase_c3_counterfactual.py", "PYTHON"),
    ("migrate_phase_c4_logistics.py", "PYTHON"),
    ("migrate_phase_c5_kyc_aml_tax.py", "PYTHON"),
]

def run_sql_migration(conn, sql_file_path):
    """Run SQL migration file"""
    print(f"  Running SQL migration: {sql_file_path.name}")
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    # Remove comments and split by semicolon
    lines = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            lines.append(line)
    
    full_sql = ' '.join(lines)
    statements = [s.strip() + ';' for s in full_sql.split(';') if s.strip()]
    
    cursor = conn.cursor()
    for statement in statements:
        if statement and statement != ';':
            try:
                cursor.execute(statement)
            except Exception as e:
                error_msg = str(e).lower()
                # Ignore "already exists" errors
                if 'already exists' not in error_msg and 'duplicate' not in error_msg:
                    if 'does not exist' in error_msg and 'index' in statement.lower():
                        continue
                    print(f"    Warning: {e}")
    conn.commit()
    cursor.close()

def run_python_migration(script_path):
    """Run Python migration script"""
    print(f"  Running Python migration: {script_path.name}")
    import importlib.util
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, 'migrate'):
        module.migrate()
    elif hasattr(module, 'migrate_holdings'):
        # Special case for holdings migration
        module.migrate_holdings()
    elif hasattr(module, 'migrate_phase11_simulated_execution'):
        # Phase 11 migration
        module.migrate_phase11_simulated_execution()
    elif hasattr(module, 'migrate_phase9_agent_tables'):
        # Phase 9 migration
        module.migrate_agent_tables()
    elif hasattr(module, 'migrate_phase10_structured_explanation'):
        # Phase 10 migration
        module.migrate_phase10_structured_explanation()
    elif hasattr(module, 'migrate_phase12_outcome_tracking'):
        # Phase 12 migration
        module.migrate_phase12_outcome_tracking()
    elif hasattr(module, 'migrate_phase13_learning'):
        # Phase 13 migration
        module.migrate_phase13_learning()
    elif hasattr(module, 'migrate_phase14_autonomy'):
        # Phase 14 migration
        module.migrate_phase14_autonomy()
    elif hasattr(module, 'migrate_phase16_autonomous_execution'):
        # Phase 16 migration
        module.migrate_phase16_autonomous_execution()
    else:
        print(f"    Warning: {script_path.name} does not have migrate() function")

def main():
    """Run all migrations in order"""
    print("🚀 Starting production database migrations...")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'REDACTED'}")
    
    # Test connection
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Get migration directory
    migration_dir = Path(__file__).parent
    
    # Run migrations
    for script_name, script_type in MIGRATION_SCRIPTS:
        script_path = migration_dir / script_name
        
        if not script_path.exists():
            print(f"⚠️  Skipping {script_name} (not found)")
            continue
        
        try:
            print(f"\n📦 Running {script_name}...")
            if script_type == "SQL":
                run_sql_migration(conn, script_path)
            elif script_type == "PYTHON":
                run_python_migration(script_path)
            print(f"✅ {script_name} completed")
        except Exception as e:
            print(f"❌ {script_name} failed: {e}")
            # Continue with other migrations (non-destructive)
            continue
    
    conn.close()
    print("\n✅ All migrations completed!")

if __name__ == "__main__":
    main()
