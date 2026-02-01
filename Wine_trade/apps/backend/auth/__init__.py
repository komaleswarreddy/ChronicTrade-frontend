"""Authentication package - exports the main authentication function"""

from auth.jwt_auth import get_current_user

# Use JWT-based authentication
get_authenticated_user = get_current_user

__all__ = ['get_authenticated_user', 'get_current_user']
