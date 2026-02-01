"""
Email-based Authentication Module for FastAPI

Simple email-based authentication that extracts email from Authorization header
and uses it directly as user_id.
"""

import re
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger("chronoshift.auth")

# Security scheme
security = HTTPBearer(auto_error=False)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    FastAPI dependency that extracts email from Authorization header.
    
    This function:
    1. Extracts the email from Authorization header (Bearer email@example.com)
    2. Validates the email format
    3. Returns the email as user_id
    
    Args:
        credentials: HTTPBearer credentials from Authorization header
        
    Returns:
        str: The authenticated user's email (used as user_id)
        
    Raises:
        HTTPException: 401 if email is missing, invalid, or not authorized
    """
    if not credentials:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization email missing"
        )
    
    email = credentials.credentials
    
    if not email or not email.strip():
        logger.warning("Empty or missing email")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization email missing"
        )
    
    # Validate email format
    if not validate_email(email):
        logger.warning(f"Invalid email format: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email format"
        )
    
    # For now, only allow the specific email
    # In the future, this could check against a database of authorized emails
    allowed_email = "komaleswarreddy@gmail.com"
    if email.lower() != allowed_email.lower():
        logger.warning(f"Unauthorized email attempt: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized email address"
        )
    
    logger.info(f"Authentication successful for email: {email}")
    return email
