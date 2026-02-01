"""
Migration Script: Add users and refresh_tokens tables

This script creates the users table for email/password authentication
and the refresh_tokens table for JWT refresh token management.
"""

import psycopg2
import os
import sys
from datetime import datetime

# Optional dotenv support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


def migrate():
    """Create users and refresh_tokens tables"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        print("Creating users table...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Create index on email
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        
        print("[OK] Users table created")
        
        # Create refresh_tokens table
        print("Creating refresh_tokens table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                revoked BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at)
        """)
        
        print("[OK] Refresh tokens table created")
        
        conn.commit()
        print("\n[OK] Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("Starting users table migration...")
    try:
        migrate()
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
