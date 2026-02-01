#!/usr/bin/env python3
"""
Create ml_predictions table if it doesn't exist
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

import psycopg2

def create_ml_predictions_table():
    """Create ml_predictions table if it doesn't exist"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("Creating ml_predictions table...")
        print("=" * 80)
        
        # Create ml_predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id SERIAL PRIMARY KEY,
                model_id TEXT NOT NULL REFERENCES ml_models(model_id),
                prediction_key TEXT NOT NULL,
                prediction_value REAL NOT NULL,
                confidence_score REAL,
                input_features JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(model_id, prediction_key)
            )
        """)
        
        # Create index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ml_predictions_expires 
            ON ml_predictions(expires_at)
        """)
        
        # Create index for model_id lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ml_predictions_model_id 
            ON ml_predictions(model_id, created_at DESC)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[OK] ml_predictions table created successfully!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error creating table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_ml_predictions_table()
    sys.exit(0 if success else 1)
