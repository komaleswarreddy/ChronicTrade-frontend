#!/usr/bin/env python3
"""
Test ML Models API Endpoint - Simulate actual API calls
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
import json

def test_api_response_format():
    """Test that API response format matches what frontend expects"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("ML Models API Response Format Test")
        print("=" * 80)
        
        # Test 1: Test without filter
        print("\n[Test 1] Testing API response format (no filter)...")
        cursor.execute("""
            SELECT model_id, model_type, model_name, version, is_active,
                   training_metrics, created_at
            FROM ml_models
            ORDER BY model_type, version DESC
        """)
        models = cursor.fetchall()
        
        models_list = []
        for model in models:
            model_dict = dict(model)
            
            # Handle JSONB field
            if 'training_metrics' in model_dict and model_dict['training_metrics']:
                if hasattr(model_dict['training_metrics'], 'dict'):
                    model_dict['training_metrics'] = model_dict['training_metrics'].dict()
                elif isinstance(model_dict['training_metrics'], str):
                    try:
                        model_dict['training_metrics'] = json.loads(model_dict['training_metrics'])
                    except:
                        pass
            
            # Convert datetime to ISO format string for JSON serialization
            if 'created_at' in model_dict and model_dict['created_at']:
                if hasattr(model_dict['created_at'], 'isoformat'):
                    model_dict['created_at'] = model_dict['created_at'].isoformat()
            
            models_list.append(model_dict)
        
        print(f"  [OK] Response contains {len(models_list)} models")
        
        # Verify structure
        if models_list:
            sample = models_list[0]
            required = ['model_id', 'model_type', 'model_name', 'version', 'is_active', 'created_at']
            missing = [f for f in required if f not in sample]
            
            if missing:
                print(f"  [ERROR] Missing fields: {missing}")
                return False
            
            print("  [OK] Response structure is correct")
            print(f"    Sample model keys: {list(sample.keys())}")
            
            # Test JSON serialization (as API would do)
            try:
                json_str = json.dumps(models_list)
                print("  [OK] Response is JSON serializable")
            except Exception as e:
                print(f"  [ERROR] JSON serialization failed: {e}")
                return False
        
        # Test 2: Test with filter
        print("\n[Test 2] Testing API response format (with filter: price_prediction)...")
        cursor.execute("""
            SELECT model_id, model_type, model_name, version, is_active,
                   training_metrics, created_at
            FROM ml_models
            WHERE model_type = %s
            ORDER BY version DESC
        """, ('price_prediction',))
        
        filtered_models = cursor.fetchall()
        filtered_list = []
        
        for model in filtered_models:
            model_dict = dict(model)
            if 'training_metrics' in model_dict and model_dict['training_metrics']:
                if hasattr(model_dict['training_metrics'], 'dict'):
                    model_dict['training_metrics'] = model_dict['training_metrics'].dict()
                elif isinstance(model_dict['training_metrics'], str):
                    try:
                        model_dict['training_metrics'] = json.loads(model_dict['training_metrics'])
                    except:
                        pass
            
            # Convert datetime to ISO format string
            if 'created_at' in model_dict and model_dict['created_at']:
                if hasattr(model_dict['created_at'], 'isoformat'):
                    model_dict['created_at'] = model_dict['created_at'].isoformat()
            
            filtered_list.append(model_dict)
        
        print(f"  [OK] Filtered response contains {len(filtered_list)} models")
        
        # Verify all are price_prediction
        all_price = all(m['model_type'] == 'price_prediction' for m in filtered_list)
        if not all_price:
            print("  [ERROR] Filter not working correctly")
            return False
        
        print("  [OK] Filter working correctly")
        
        # Test 3: Verify training_metrics structure
        print("\n[Test 3] Verifying training_metrics structure...")
        models_with_metrics = [m for m in models_list if m.get('training_metrics')]
        
        if models_with_metrics:
            sample_metrics = models_with_metrics[0]['training_metrics']
            print(f"  [INFO] Sample metrics type: {type(sample_metrics)}")
            
            if isinstance(sample_metrics, dict):
                print("  [OK] training_metrics is a dictionary")
                print(f"    Keys: {list(sample_metrics.keys())}")
            elif isinstance(sample_metrics, str):
                print("  [WARNING] training_metrics is a string, attempting to parse...")
                try:
                    parsed = json.loads(sample_metrics)
                    print("  [OK] Successfully parsed training_metrics")
                except:
                    print("  [ERROR] Failed to parse training_metrics")
            else:
                print(f"  [WARNING] training_metrics is {type(sample_metrics)}")
        else:
            print("  [INFO] No models with training_metrics found")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("[OK] All API response format tests passed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_api_response_format()
    sys.exit(0 if success else 1)
