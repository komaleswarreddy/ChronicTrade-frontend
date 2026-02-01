"""
User Service - Handle user initialization and portfolio setup

This module ensures new users start with empty portfolios and handles
user-specific data initialization, user CRUD operations, and password verification.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict
from auth.password_auth import hash_password, verify_password, validate_password_strength, validate_email
import logging
import os

logger = logging.getLogger("chronoshift.user_service")


def ensure_user_portfolio_initialized(conn, user_id: str) -> bool:
    """
    Ensure a user has an initialized (empty) portfolio entry.
    This is called when a user first accesses their portfolio.
    
    Args:
        conn: PostgreSQL database connection
        user_id: Authenticated user ID
        
    Returns:
        bool: True if portfolio was initialized, False if it already existed
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if portfolio entry exists
    cursor.execute("SELECT user_id FROM portfolio WHERE user_id = %s", (user_id,))
    exists = cursor.fetchone()
    
    if exists:
        cursor.close()
        return False  # Already initialized
    
    # Create empty portfolio entry
    cursor.execute("""
        INSERT INTO portfolio (user_id, total_value, today_change, change_percent, bottles, regions, avg_roi)
        VALUES (%s, 0, 0, 0, 0, '', 0)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id,))
    
    conn.commit()
    cursor.close()
    return True  # Newly initialized


def get_user_holdings_count(conn, user_id: str) -> int:
    """
    Get the count of holdings for a user.
    
    Args:
        conn: PostgreSQL database connection
        user_id: Authenticated user ID
        
    Returns:
        int: Number of holdings
    """
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM holdings WHERE user_id = %s", (user_id,))
    count = cursor.fetchone()[0]
    
    cursor.close()
    return count


def create_user(email: str, password: str, full_name: Optional[str] = None) -> Optional[Dict]:
    """
    Create a new user account.
    
    Args:
        email: User email address
        password: Plain text password
        full_name: Optional full name
        
    Returns:
        Dict with user info (id, email, full_name) if successful, None otherwise
    """
    # Validate email
    if not validate_email(email):
        logger.warning(f"Invalid email format: {email}")
        return None
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        logger.warning(f"Password validation failed: {error_msg}")
        return None
    
    # Hash password
    password_hash = hash_password(password)
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set")
        return None
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email.lower(),))
        existing = cursor.fetchone()
        
        if existing:
            logger.warning(f"User with email {email} already exists")
            cursor.close()
            conn.close()
            return None
        
        # Create user
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name)
            VALUES (%s, %s, %s)
            RETURNING id, email, full_name, created_at
        """, (email.lower(), password_hash, full_name))
        
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"User created successfully: {email}")
        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "created_at": user['created_at']
        }
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None


def verify_user_password(email: str, password: str) -> Optional[Dict]:
    """
    Verify user password and return user info if valid.
    
    Args:
        email: User email address
        password: Plain text password
        
    Returns:
        Dict with user info (id, email, full_name) if valid, None otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set")
        return None
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user by email
        cursor.execute("""
            SELECT id, email, password_hash, full_name
            FROM users
            WHERE email = %s
        """, (email.lower(),))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        logger.info(f"Password verified for user: {email}")
        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name']
        }
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        if conn:
            conn.close()
        return None


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Get user by email address.
    
    Args:
        email: User email address
        
    Returns:
        Dict with user info (id, email, full_name) if found, None otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return None
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, email, full_name, email_verified, created_at, last_login
            FROM users
            WHERE email = %s
        """, (email.lower(),))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return None
        
        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "email_verified": user['email_verified'],
            "created_at": user['created_at'],
            "last_login": user['last_login']
        }
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        if conn:
            conn.close()
        return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with user info (id, email, full_name) if found, None otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return None
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, email, full_name, email_verified, created_at, last_login
            FROM users
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return None
        
        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "email_verified": user['email_verified'],
            "created_at": user['created_at'],
            "last_login": user['last_login']
        }
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        if conn:
            conn.close()
        return None


def update_last_login(user_id: int) -> bool:
    """
    Update user's last login timestamp.
    
    Args:
        user_id: User ID
        
    Returns:
        True if updated successfully, False otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        from datetime import datetime
        cursor.execute("""
            UPDATE users
            SET last_login = %s
            WHERE id = %s
        """, (datetime.utcnow(), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to update last login: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

