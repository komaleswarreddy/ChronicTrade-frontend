"""
Phase C5: KYC/AML/Tax Automation
Creates KYC, AML, and tax_obligations tables for pre-execution gating.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment")

def migrate():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        print("Phase C5: Creating KYC/AML/Tax tables...")
        
        # Create kyc_status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kyc_status (
                user_id TEXT PRIMARY KEY,
                kyc_level TEXT NOT NULL CHECK (kyc_level IN ('NONE', 'BASIC', 'ENHANCED', 'VERIFIED')),
                verification_status TEXT NOT NULL CHECK (verification_status IN ('PENDING', 'VERIFIED', 'REJECTED', 'EXPIRED')),
                verified_at TIMESTAMP,
                expires_at TIMESTAMP,
                verification_documents TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create aml_risk_flags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aml_risk_flags (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                counterparty_id TEXT,
                risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
                risk_reason TEXT,
                flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                active BOOLEAN DEFAULT true
            )
        """)
        
        # Create tax_obligations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tax_obligations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                simulation_id UUID NOT NULL REFERENCES simulated_orders(id) ON DELETE CASCADE,
                source_country TEXT NOT NULL,
                destination_country TEXT NOT NULL,
                tax_type TEXT NOT NULL CHECK (tax_type IN ('IMPORT_DUTY', 'VAT', 'EXCISE', 'CUSTOMS', 'OTHER')),
                tax_rate FLOAT NOT NULL,
                tax_amount FLOAT,
                obligation_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (obligation_status IN ('PENDING', 'CALCULATED', 'PAID', 'EXEMPT')),
                calculated_at TIMESTAMP,
                paid_at TIMESTAMP,
                exemption_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create execution_gates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_gates (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                simulation_id UUID NOT NULL REFERENCES simulated_orders(id) ON DELETE CASCADE,
                gate_type TEXT NOT NULL CHECK (gate_type IN ('KYC', 'AML', 'TAX', 'COMPLIANCE')),
                gate_status TEXT NOT NULL CHECK (gate_status IN ('PENDING', 'PASSED', 'BLOCKED')),
                block_reason TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(simulation_id, gate_type)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aml_risk_user ON aml_risk_flags(user_id, active);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tax_obligations_simulation ON tax_obligations(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_gates_simulation ON execution_gates(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_gates_status ON execution_gates(gate_status);")
        
        conn.commit()
        print("  [OK] Created kyc_status table")
        print("  [OK] Created aml_risk_flags table")
        print("  [OK] Created tax_obligations table")
        print("  [OK] Created execution_gates table")
        print("  [OK] Created indexes")
        print("Phase C5 migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
