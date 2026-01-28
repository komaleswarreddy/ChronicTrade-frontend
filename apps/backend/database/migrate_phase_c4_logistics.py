"""
Phase C4: Logistics & Condition Tracking
Creates shipment and condition_snapshots tables.
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
        print("Phase C4: Creating logistics tracking tables...")
        
        # Create shipments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                simulation_id UUID NOT NULL REFERENCES simulated_orders(id) ON DELETE CASCADE,
                tracking_number TEXT UNIQUE,
                origin_location TEXT NOT NULL,
                destination_location TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'IN_TRANSIT', 'DELIVERED', 'DELAYED', 'LOST')),
                estimated_delivery_date TIMESTAMP,
                actual_delivery_date TIMESTAMP,
                carrier TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create condition_snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS condition_snapshots (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                shipment_id UUID NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
                temperature_celsius FLOAT,
                humidity_percent FLOAT,
                shock_events INTEGER DEFAULT 0,
                condition_score FLOAT CHECK (condition_score >= 0 AND condition_score <= 100),
                risk_level TEXT CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
                snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Create storage_facilities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage_facilities (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                facility_name TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity_bottles INTEGER,
                temperature_controlled BOOLEAN DEFAULT true,
                humidity_controlled BOOLEAN DEFAULT true,
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipments_simulation ON shipments(simulation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_condition_snapshots_shipment ON condition_snapshots(shipment_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_condition_snapshots_timestamp ON condition_snapshots(snapshot_timestamp DESC);")
        
        conn.commit()
        print("  [OK] Created shipments table")
        print("  [OK] Created condition_snapshots table")
        print("  [OK] Created storage_facilities table")
        print("  [OK] Created indexes")
        print("Phase C4 migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
