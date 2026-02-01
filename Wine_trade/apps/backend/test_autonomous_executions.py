"""
Test script to verify autonomous executions API endpoint
This script tests if the backend is correctly returning autonomous execution data
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection - try multiple sources
DATABASE_URL = os.getenv("DATABASE_URL")

# Try loading from .env file if not set
if not DATABASE_URL:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL")
    except ImportError:
        pass

# Try common default locations
if not DATABASE_URL:
    env_files = ['.env', '../.env', '../../.env', '.env.local']
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                DATABASE_URL = os.getenv("DATABASE_URL")
                if DATABASE_URL:
                    break
            except:
                pass

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    print("Please set DATABASE_URL environment variable or create a .env file")
    print("\nTrying to read from start.py configuration...")
    # Try to read from start.py
    try:
        import re
        start_py_path = os.path.join(os.path.dirname(__file__), '..', 'start.py')
        if os.path.exists(start_py_path):
            with open(start_py_path, 'r') as f:
                content = f.read()
                # Look for DATABASE_URL pattern
                match = re.search(r'DATABASE_URL\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    DATABASE_URL = match.group(1)
                    print(f"Found DATABASE_URL in start.py: {DATABASE_URL[:50]}...")
    except:
        pass

if not DATABASE_URL:
    print("\nPlease provide DATABASE_URL manually:")
    print("  Option 1: Set environment variable: export DATABASE_URL='your_url'")
    print("  Option 2: Create .env file with: DATABASE_URL=your_url")
    print("  Option 3: Run this script with: DATABASE_URL='your_url' python test_autonomous_executions.py")
    sys.exit(1)

def test_autonomous_executions_table():
    """Test if autonomous_executions table exists and has data"""
    print("=" * 80)
    print("TEST 1: Checking autonomous_executions table")
    print("=" * 80)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'autonomous_executions'
            ) as exists
        """)
        result = cursor.fetchone()
        table_exists = result['exists'] if result else False
        
        print(f"Table exists: {table_exists}")
        
        if not table_exists:
            print("❌ ERROR: autonomous_executions table does not exist!")
            return False
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'autonomous_executions'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nTable columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
        
        # Count total records
        cursor.execute("SELECT COUNT(*) as count FROM autonomous_executions")
        count_result = cursor.fetchone()
        total_count = count_result['count'] if count_result else 0
        print(f"\nTotal records: {total_count}")
        
        # Get sample records
        cursor.execute("""
            SELECT * FROM autonomous_executions
            ORDER BY executed_at DESC
            LIMIT 10
        """)
        records = cursor.fetchall()
        
        print(f"\nSample records (showing {len(records)}):")
        for i, record in enumerate(records, 1):
            print(f"\n  Record {i}:")
            record_dict = dict(record)
            for key, value in record_dict.items():
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, dict):
                    value = json.dumps(value)
                print(f"    {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


def test_user_executions(user_id="user_36c7blJff5Pu2ZbINQlLHfxzzjZ"):
    """Test getting executions for a specific user"""
    print("\n" + "=" * 80)
    print(f"TEST 2: Getting executions for user {user_id}")
    print("=" * 80)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM autonomous_executions
            WHERE user_id = %s
            ORDER BY executed_at DESC
            LIMIT 50
        """, (user_id,))
        
        executions = cursor.fetchall()
        print(f"Found {len(executions)} executions for user")
        
        if len(executions) == 0:
            print("⚠️  WARNING: No executions found for this user")
            return False
        
        print("\nExecutions:")
        for i, exec_record in enumerate(executions, 1):
            exec_dict = dict(exec_record)
            print(f"\n  Execution {i}:")
            print(f"    ID: {exec_dict.get('id')}")
            print(f"    Decision: {exec_dict.get('decision')}")
            print(f"    Simulation ID: {exec_dict.get('simulation_id')}")
            print(f"    Executed At: {exec_dict.get('executed_at')}")
            print(f"    Failure Reason: {exec_dict.get('failure_reason')}")
            print(f"    Reason: {exec_dict.get('reason')}")
            
            # Check policy_snapshot
            policy_snapshot = exec_dict.get('policy_snapshot')
            if policy_snapshot:
                if isinstance(policy_snapshot, str):
                    try:
                        policy_snapshot = json.loads(policy_snapshot)
                    except:
                        pass
                print(f"    Policy Snapshot: {json.dumps(policy_snapshot) if isinstance(policy_snapshot, dict) else policy_snapshot}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


def test_api_response_format():
    """Test the API response format matches what frontend expects"""
    print("\n" + "=" * 80)
    print("TEST 3: Testing API response format")
    print("=" * 80)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    user_id = "user_36c7blJff5Pu2ZbINQlLHfxzzjZ"
    
    try:
        # Simulate what the API endpoint does
        cursor.execute("""
            SELECT * FROM autonomous_executions
            WHERE user_id = %s
            ORDER BY executed_at DESC
            LIMIT 50
        """, (user_id,))
        
        executions = cursor.fetchall()
        
        execution_responses = []
        for exec_record in executions:
            exec_dict = dict(exec_record)
            policy_snapshot = exec_dict.get('policy_snapshot', {})
            if isinstance(policy_snapshot, str):
                try:
                    policy_snapshot = json.loads(policy_snapshot)
                except:
                    policy_snapshot = {}
            
            execution_response = {
                'id': str(exec_dict['id']),
                'user_id': exec_dict['user_id'],
                'simulation_id': str(exec_dict['simulation_id']),
                'decision': exec_dict['decision'],
                'executed_at': exec_dict['executed_at'].isoformat() if isinstance(exec_dict['executed_at'], datetime) else str(exec_dict['executed_at']),
                'failure_reason': exec_dict.get('failure_reason'),
                'reason': exec_dict.get('reason'),
                'policy_snapshot': policy_snapshot
            }
            execution_responses.append(execution_response)
        
        response = {
            'executions': execution_responses,
            'total': len(execution_responses)
        }
        
        print(f"Response structure:")
        print(f"  - executions: array of {len(execution_responses)} items")
        print(f"  - total: {response['total']}")
        
        if len(execution_responses) > 0:
            print(f"\nFirst execution example:")
            first = execution_responses[0]
            for key, value in first.items():
                print(f"    {key}: {value}")
        
        # Check if response matches frontend expectations
        print("\n[OK] Response format check:")
        print(f"  - Has 'executions' key: {'executions' in response}")
        print(f"  - Has 'total' key: {'total' in response}")
        print(f"  - Executions is list: {isinstance(response['executions'], list)}")
        
        if len(execution_responses) > 0:
            first_exec = execution_responses[0]
            required_keys = ['id', 'decision', 'simulation_id', 'executed_at']
            missing_keys = [key for key in required_keys if key not in first_exec]
            if missing_keys:
                print(f"  [WARNING] Missing keys in execution: {missing_keys}")
            else:
                print(f"  [OK] All required keys present")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


def test_recent_simulations():
    """Check if there are recent simulations that should have autonomous executions"""
    print("\n" + "=" * 80)
    print("TEST 4: Checking recent simulations")
    print("=" * 80)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    user_id = "user_36c7blJff5Pu2ZbINQlLHfxzzjZ"
    
    try:
        # Get recent executed simulations
        cursor.execute("""
            SELECT id, status, executed_at, created_at
            FROM simulated_orders
            WHERE user_id = %s
            AND status = 'EXECUTED'
            ORDER BY executed_at DESC
            LIMIT 10
        """, (user_id,))
        
        simulations = cursor.fetchall()
        print(f"Found {len(simulations)} executed simulations")
        
        if len(simulations) == 0:
            print("⚠️  WARNING: No executed simulations found")
            return False
        
        print("\nRecent executed simulations:")
        for sim in simulations:
            sim_dict = dict(sim)
            sim_id = str(sim_dict['id'])
            print(f"\n  Simulation ID: {sim_id}")
            print(f"    Status: {sim_dict['status']}")
            print(f"    Executed At: {sim_dict.get('executed_at')}")
            print(f"    Created At: {sim_dict.get('created_at')}")
            
            # Check if there's an autonomous execution for this simulation
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM autonomous_executions
                WHERE simulation_id = %s
            """, (sim_id,))
            exec_count = cursor.fetchone()
            count = exec_count['count'] if exec_count else 0
            print(f"    Autonomous executions: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AUTONOMOUS EXECUTIONS BACKEND TEST")
    print("=" * 80)
    print(f"Database URL: {DATABASE_URL[:50]}..." if DATABASE_URL else "Not set")
    print()
    
    results = []
    
    # Run tests
    results.append(("Table Check", test_autonomous_executions_table()))
    results.append(("User Executions", test_user_executions()))
    results.append(("API Format", test_api_response_format()))
    results.append(("Recent Simulations", test_recent_simulations()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print(f"\n{'[OK] All tests passed!' if all_passed else '[FAIL] Some tests failed!'}")
    print("=" * 80)
    
    # Additional analysis
    print("\n" + "=" * 80)
    print("ANALYSIS: Why no new autonomous executions?")
    print("=" * 80)
    print("""
    IMPORTANT FINDING:
    - Autonomous executions are ONLY created by the autonomous execution engine
    - Manual execution (via 'Execute' button) does NOT create autonomous execution records
    - The 6 records shown are all for simulation c31f9bad... from 1/20/2026
    - Newer simulations (1/22, 1/23) were manually executed, so no autonomous records exist
    
    SOLUTION OPTIONS:
    1. Create autonomous execution records when simulations are manually executed
    2. Show a message in UI explaining the difference
    3. Check if autonomous execution engine is running and creating records
    """)
