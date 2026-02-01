"""
JWT Authentication Utilities

Handles JWT token generation, validation, and refresh token management.
Uses PyJWT for token operations.
"""

import jwt
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("chronoshift.auth")

# Security scheme
security = HTTPBearer(auto_error=False)

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))

if not JWT_SECRET:
    logger.warning("JWT_SECRET not set in environment variables. Generating temporary secret.")
    JWT_SECRET = secrets.token_urlsafe(32)


def create_access_token(user_id: int, email: str) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID from database
        email: User email address
        
    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[Dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            logger.warning("Token is not an access token")
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def create_refresh_token(user_id: int) -> str:
    """
    Create a secure random refresh token.
    
    Args:
        user_id: User ID from database
        
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)


def store_refresh_token(user_id: int, token: str, expires_at: datetime) -> bool:
    """
    Store refresh token in database.
    
    Args:
        user_id: User ID
        token: Refresh token string
        expires_at: Expiration timestamp
        
    Returns:
        True if stored successfully, False otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        """, (user_id, token, expires_at))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to store refresh token: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def validate_refresh_token(token: str) -> Optional[Dict]:
    """
    Validate refresh token and return user info.
    
    Args:
        token: Refresh token string
        
    Returns:
        Dict with user_id and email if valid, None otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return None
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if token exists and is valid
        cursor.execute("""
            SELECT rt.user_id, rt.expires_at, rt.revoked, u.email
            FROM refresh_tokens rt
            JOIN users u ON rt.user_id = u.id
            WHERE rt.token = %s
        """, (token,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            logger.warning("Refresh token not found")
            return None
        
        if result['revoked']:
            logger.warning("Refresh token has been revoked")
            return None
        
        if result['expires_at'] < datetime.utcnow():
            logger.warning("Refresh token has expired")
            return None
        
        return {
            "user_id": result['user_id'],
            "email": result['email']
        }
    except Exception as e:
        logger.error(f"Error validating refresh token: {e}")
        if conn:
            conn.close()
        return None


def revoke_refresh_token(token: str) -> bool:
    """
    Revoke a refresh token.
    
    Args:
        token: Refresh token string
        
    Returns:
        True if revoked successfully, False otherwise
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE refresh_tokens
            SET revoked = TRUE
            WHERE token = %s
        """, (token,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to revoke refresh token: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """
    FastAPI dependency that validates JWT token and returns user info.
    
    Args:
        credentials: HTTPBearer credentials from Authorization header
        
    Returns:
        Dict with user_id and email
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not credentials:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing"
        )
    
    token = credentials.credentials
    
    if not token or not token.strip():
        logger.warning("Empty or missing token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing"
        )
    
    # Decode and validate token
    payload = decode_access_token(token)
    
    if not payload:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id")
    email = payload.get("email")
    
    if not user_id or not email:
        logger.warning("Token missing user_id or email")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    logger.info(f"Authentication successful for user: {email}")
    return {
        "user_id": user_id,
        "email": email
    }
