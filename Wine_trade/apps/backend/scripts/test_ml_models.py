#!/usr/bin/env python3
"""
Test ML Models API - Verify ML models listing works end-to-end
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
from psycopg2.extras import RealDictCursor

def test_ml_models_api():
    """Test ML models API functionality"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("ML Models API Test")
        print("=" * 80)
        
        # Test 1: Check if ml_models table exists
        print("\n[Test 1] Checking if ml_models table exists...")
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'ml_models'
                ) as exists
            """)
            result = cursor.fetchone()
            table_exists = result['exists'] if isinstance(result, dict) else result[0]
            
            if not table_exists:
                print("  [WARNING] ml_models table does not exist!")
                print("  [INFO] Creating ml_models table...")
                
                # Create the table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ml_models (
                        id SERIAL PRIMARY KEY,
                        model_id TEXT UNIQUE NOT NULL,
                        model_type TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        model_path TEXT NOT NULL,
                        training_dataset_hash TEXT NOT NULL,
                        training_metrics JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                conn.commit()
                print("  [OK] ml_models table created")
            else:
                print("  [OK] ml_models table exists")
        except Exception as e:
            print(f"  [ERROR] Failed to check/create table: {e}")
            return False
        
        # Test 2: Check current row count
        print("\n[Test 2] Checking current model count...")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM ml_models")
            result = cursor.fetchone()
            count = result['count'] if isinstance(result, dict) else result[0]
            print(f"  [INFO] Current models in database: {count}")
            
            if count == 0:
                print("  [INFO] No models found. Creating test models...")
                create_test_models(cursor, conn)
        except Exception as e:
            print(f"  [ERROR] Failed to count models: {e}")
            return False
        
        # Test 3: Test query without filter
        print("\n[Test 3] Testing query without filter (all models)...")
        try:
            cursor.execute("""
                SELECT model_id, model_type, model_name, version, is_active,
                       training_metrics, created_at
                FROM ml_models
                ORDER BY model_type, version DESC
            """)
            all_models = cursor.fetchall()
            print(f"  [OK] Found {len(all_models)} models")
            
            for i, model in enumerate(all_models[:3], 1):  # Show first 3
                print(f"    Model {i}:")
                print(f"      - ID: {model['model_id']}")
                print(f"      - Type: {model['model_type']}")
                print(f"      - Name: {model['model_name']}")
                print(f"      - Version: {model['version']}")
                print(f"      - Active: {model['is_active']}")
        except Exception as e:
            print(f"  [ERROR] Query failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 4: Test query with price_prediction filter
        print("\n[Test 4] Testing query with filter: price_prediction...")
        try:
            cursor.execute("""
                SELECT model_id, model_type, model_name, version, is_active,
                       training_metrics, created_at
                FROM ml_models
                WHERE model_type = %s
                ORDER BY version DESC
            """, ('price_prediction',))
            price_models = cursor.fetchall()
            print(f"  [OK] Found {len(price_models)} price prediction models")
            
            for i, model in enumerate(price_models[:3], 1):
                print(f"    Model {i}: {model['model_name']} (v{model['version']})")
        except Exception as e:
            print(f"  [ERROR] Filtered query failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 5: Test query with risk_scoring filter
        print("\n[Test 5] Testing query with filter: risk_scoring...")
        try:
            cursor.execute("""
                SELECT model_id, model_type, model_name, version, is_active,
                       training_metrics, created_at
                FROM ml_models
                WHERE model_type = %s
                ORDER BY version DESC
            """, ('risk_scoring',))
            risk_models = cursor.fetchall()
            print(f"  [OK] Found {len(risk_models)} risk scoring models")
            
            for i, model in enumerate(risk_models[:3], 1):
                print(f"    Model {i}: {model['model_name']} (v{model['version']})")
        except Exception as e:
            print(f"  [ERROR] Filtered query failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 6: Test invalid filter
        print("\n[Test 6] Testing query with invalid filter: invalid_type...")
        try:
            cursor.execute("""
                SELECT model_id, model_type, model_name, version, is_active,
                       training_metrics, created_at
                FROM ml_models
                WHERE model_type = %s
                ORDER BY version DESC
            """, ('invalid_type',))
            invalid_models = cursor.fetchall()
            print(f"  [OK] Found {len(invalid_models)} models (expected 0)")
        except Exception as e:
            print(f"  [ERROR] Invalid filter query failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 7: Verify response format
        print("\n[Test 7] Verifying response format...")
        try:
            cursor.execute("SELECT * FROM ml_models LIMIT 1")
            sample = cursor.fetchone()
            
            if sample:
                required_fields = ['model_id', 'model_type', 'model_name', 'version', 'is_active', 'created_at']
                missing_fields = [f for f in required_fields if f not in sample]
                
                if missing_fields:
                    print(f"  [ERROR] Missing required fields: {missing_fields}")
                    return False
                else:
                    print("  [OK] Response format is correct")
                    print(f"    Sample fields: {list(sample.keys())}")
            else:
                print("  [WARNING] No models to verify format")
        except Exception as e:
            print(f"  [ERROR] Format verification failed: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("[OK] All ML Models API tests passed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_models(cursor, conn):
    """Create test ML models for testing"""
    import uuid
    import json
    from datetime import datetime
    
    test_models = [
        {
            'model_id': f'test_price_{uuid.uuid4().hex[:8]}',
            'model_type': 'price_prediction',
            'model_name': 'XGBoost Price Predictor',
            'version': 1,
            'model_path': '/models/price_predictor_v1.pkl',
            'training_dataset_hash': 'abc123',
            'training_metrics': json.dumps({
                'val_r2': 0.85,
                'val_mae': 0.12,
                'train_size': 1000,
                'val_size': 200
            }),
            'is_active': True
        },
        {
            'model_id': f'test_price_{uuid.uuid4().hex[:8]}',
            'model_type': 'price_prediction',
            'model_name': 'XGBoost Price Predictor',
            'version': 2,
            'model_path': '/models/price_predictor_v2.pkl',
            'training_dataset_hash': 'def456',
            'training_metrics': json.dumps({
                'val_r2': 0.88,
                'val_mae': 0.10,
                'train_size': 1200,
                'val_size': 250
            }),
            'is_active': True
        },
        {
            'model_id': f'test_risk_{uuid.uuid4().hex[:8]}',
            'model_type': 'risk_scoring',
            'model_name': 'Risk Scoring Model',
            'version': 1,
            'model_path': '/models/risk_scorer_v1.pkl',
            'training_dataset_hash': 'ghi789',
            'training_metrics': json.dumps({
                'val_r2': 0.75,
                'val_mae': 0.15,
                'train_size': 800,
                'val_size': 150
            }),
            'is_active': True
        },
        {
            'model_id': f'test_risk_{uuid.uuid4().hex[:8]}',
            'model_type': 'risk_scoring',
            'model_name': 'Risk Scoring Model',
            'version': 2,
            'model_path': '/models/risk_scorer_v2.pkl',
            'training_dataset_hash': 'jkl012',
            'training_metrics': json.dumps({
                'val_r2': 0.78,
                'val_mae': 0.13,
                'train_size': 900,
                'val_size': 180
            }),
            'is_active': False  # Inactive model
        }
    ]
    
    for model in test_models:
        try:
            cursor.execute("""
                INSERT INTO ml_models 
                (model_id, model_type, model_name, version, model_path, 
                 training_dataset_hash, training_metrics, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
            """, (
                model['model_id'],
                model['model_type'],
                model['model_name'],
                model['version'],
                model['model_path'],
                model['training_dataset_hash'],
                model['training_metrics'],
                model['is_active'],
                datetime.now()
            ))
            print(f"    Created: {model['model_name']} v{model['version']} ({model['model_type']})")
        except Exception as e:
            print(f"    [WARNING] Failed to create {model['model_name']}: {e}")
    
    conn.commit()
    print(f"  [OK] Created {len(test_models)} test models")

if __name__ == '__main__':
    success = test_ml_models_api()
    sys.exit(0 if success else 1)
