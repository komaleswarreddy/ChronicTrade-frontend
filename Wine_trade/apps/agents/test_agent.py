"""
Test Script for Agent Service

Fetches user IDs and data from backend database to test the agent.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to load from backend .env if exists
backend_env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    print("Please set DATABASE_URL in your .env file")
    print("Example: DATABASE_URL=postgresql://user:password@localhost:5432/winedb")
    sys.exit(1)


def fetch_users():
    """Fetch all users from the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get users from portfolio table
        cursor.execute("""
            SELECT DISTINCT user_id 
            FROM portfolio 
            ORDER BY user_id
        """)
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [row["user_id"] for row in users]
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def fetch_user_holdings(user_id: str):
    """Fetch holdings for a specific user"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                h.id,
                h.asset_id,
                a.name as asset_name,
                h.quantity,
                h.status
            FROM holdings h
            JOIN assets a ON h.asset_id = a.asset_id
            WHERE h.user_id = %s
            AND h.status IN ('OPEN', 'PARTIALLY_SOLD')
            LIMIT 10
        """, (user_id,))
        
        holdings = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return holdings
    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return []


def fetch_sample_assets():
    """Fetch sample assets from database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT asset_id, name, region, vintage
            FROM assets
            LIMIT 10
        """)
        
        assets = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return assets
    except Exception as e:
        print(f"Error fetching assets: {e}")
        return []


def main():
    print("=" * 60)
    print("ChronoShift Agent Test - Data Fetcher")
    print("=" * 60)
    print()
    
    # Test database connection
    print("1. Testing database connection...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        print("   [OK] Database connection successful!")
    except Exception as e:
        print(f"   [ERROR] Database connection failed: {e}")
        sys.exit(1)
    
    print()
    
    # Fetch users
    print("2. Fetching users from database...")
    users = fetch_users()
    
    if not users:
        print("   [WARNING] No users found in database")
        print("   You may need to initialize the database first:")
        print("   cd apps/backend")
        print("   python database/init_db.py")
        print()
    else:
        print(f"   [OK] Found {len(users)} user(s):")
        for i, user_id in enumerate(users[:5], 1):  # Show first 5
            print(f"      {i}. {user_id}")
        if len(users) > 5:
            print(f"      ... and {len(users) - 5} more")
        print()
    
    # Fetch sample assets
    print("3. Fetching sample assets...")
    assets = fetch_sample_assets()
    
    if assets:
        print(f"   [OK] Found {len(assets)} sample asset(s):")
        for i, asset in enumerate(assets[:3], 1):  # Show first 3
            print(f"      {i}. {asset['asset_id']} - {asset['name']} ({asset['region']})")
        print()
    
    # Show user holdings if available
    if users:
        test_user = users[0]
        print(f"4. Fetching holdings for user: {test_user}")
        holdings = fetch_user_holdings(test_user)
        
        if holdings:
            print(f"   [OK] Found {len(holdings)} holding(s):")
            for i, holding in enumerate(holdings[:3], 1):
                print(f"      {i}. {holding['asset_name']} (ID: {holding['asset_id']}, Qty: {holding['quantity']})")
        else:
            print("   [WARNING] No active holdings found for this user")
        print()
    
    # Generate test commands
    print("=" * 60)
    print("READY TO TEST AGENT")
    print("=" * 60)
    print()
    
    if users:
        test_user = users[0]
        print(f"To test the agent, run:")
        print(f"  cd apps/agents")
        print(f"  python main.py {test_user}")
        print()
        
        # Check if user has holdings
        holdings = fetch_user_holdings(test_user)
        if holdings:
            test_asset = holdings[0]['asset_id']
            print(f"To test with a specific asset:")
            print(f"  python main.py {test_user} {test_asset}")
            print()
    else:
        print("No users found. Please initialize the database first:")
        print("  cd apps/backend")
        print("  python database/init_db.py")
        print()
    
    print("=" * 60)


if __name__ == "__main__":
    main()
