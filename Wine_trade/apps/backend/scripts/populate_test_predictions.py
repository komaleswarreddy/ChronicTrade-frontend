#!/usr/bin/env python3
"""
Populate test predictions for ML models
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

import psycopg2
from psycopg2.extras import RealDictCursor

def populate_test_predictions():
    """Populate test predictions for existing models"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("Populating test predictions...")
        print("=" * 80)
        
        # Get all models
        cursor.execute("""
            SELECT model_id, model_type, model_name, version
            FROM ml_models
            ORDER BY model_type, version DESC
        """)
        models = cursor.fetchall()
        
        if not models:
            print("[ERROR] No models found. Please create models first.")
            return False
        
        print(f"Found {len(models)} models")
        
        # Check if ml_predictions table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'ml_predictions'
            ) as exists
        """)
        result = cursor.fetchone()
        table_exists = result['exists'] if isinstance(result, dict) else result[0]
        
        if not table_exists:
            print("[INFO] ml_predictions table does not exist. Creating it...")
            create_cursor = conn.cursor()
            create_cursor.execute("""
                CREATE TABLE ml_predictions (
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
            create_cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ml_predictions_model_id 
                ON ml_predictions(model_id, created_at DESC)
            """)
            conn.commit()
            create_cursor.close()
            print("[OK] Table created")
        
        # Generate test predictions for each model
        total_predictions = 0
        
        for model in models:
            model_id = model['model_id']
            model_type = model['model_type']
            model_name = model['model_name']
            
            print(f"\n[INFO] Generating predictions for: {model_name} ({model_type})")
            
            # Check existing predictions count
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM ml_predictions
                WHERE model_id = %s
            """, (model_id,))
            existing_count = cursor.fetchone()['count']
            
            if existing_count > 0:
                print(f"  [WARNING] Already has {existing_count} predictions. Skipping...")
                continue
            
            # Generate 10-15 test predictions
            num_predictions = random.randint(10, 15)
            insert_cursor = conn.cursor()
            
            for i in range(num_predictions):
                # Generate prediction based on model type
                if model_type == 'price_prediction':
                    # Price predictions: $50-$200 range
                    base_price = random.uniform(50, 200)
                    prediction_value = base_price + random.uniform(-10, 10)
                    confidence = random.uniform(0.75, 0.95)
                    
                    input_features = {
                        'current_price': round(base_price, 2),
                        'volume_24h': random.randint(1000, 10000),
                        'price_change_7d': random.uniform(-0.1, 0.1),
                        'market_cap': random.randint(1000000, 10000000),
                        'liquidity_score': random.uniform(0.5, 1.0)
                    }
                else:  # risk_scoring
                    # Risk scores: 0-1 range
                    prediction_value = random.uniform(0.3, 0.8)
                    confidence = random.uniform(0.70, 0.92)
                    
                    input_features = {
                        'volatility': random.uniform(0.1, 0.5),
                        'correlation': random.uniform(-0.5, 0.5),
                        'liquidity_risk': random.uniform(0.1, 0.7),
                        'market_conditions': random.choice(['bull', 'bear', 'neutral']),
                        'historical_drawdown': random.uniform(0.05, 0.25)
                    }
                
                # Create prediction key (hash of input features)
                prediction_key = f"test_{model_id}_{i}_{int(datetime.now().timestamp())}"
                
                # Random timestamp within last 30 days
                days_ago = random.randint(0, 30)
                created_at = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                
                try:
                    insert_cursor.execute("""
                        INSERT INTO ml_predictions 
                        (model_id, prediction_key, prediction_value, confidence_score, 
                         input_features, created_at)
                        VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                        ON CONFLICT (model_id, prediction_key) DO NOTHING
                    """, (
                        model_id,
                        prediction_key,
                        round(prediction_value, 4),
                        round(confidence, 4),
                        json.dumps(input_features),
                        created_at
                    ))
                    total_predictions += 1
                except Exception as e:
                    print(f"  [WARNING] Error inserting prediction {i}: {e}")
            
            conn.commit()
            insert_cursor.close()
            print(f"  [OK] Generated {num_predictions} predictions")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print(f"[OK] Successfully populated {total_predictions} test predictions!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = populate_test_predictions()
    sys.exit(0 if success else 1)
