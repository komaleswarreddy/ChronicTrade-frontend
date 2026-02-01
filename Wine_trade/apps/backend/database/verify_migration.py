"""
Verify that users and refresh_tokens tables were created successfully
"""

import psycopg2
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check users table
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"[OK] Users table exists. Current user count: {user_count}")
    
    # Check refresh_tokens table
    cursor.execute("SELECT COUNT(*) FROM refresh_tokens")
    token_count = cursor.fetchone()[0]
    print(f"[OK] Refresh tokens table exists. Current token count: {token_count}")
    
    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """)
    print("\nUsers table columns:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    cursor.close()
    conn.close()
    
    print("\n[OK] Migration verification successful!")
    
except Exception as e:
    print(f"[ERROR] Error verifying migration: {e}")
    raise
