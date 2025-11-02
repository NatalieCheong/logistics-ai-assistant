# backend/app/utils/auth.py
"""
Authentication utilities (alternative import location)
"""

from app.routers.auth import (
    get_current_user,
    get_current_active_user,
    create_access_token,
    verify_password,
    get_password_hash
)

__all__ = [
    'get_current_user',
    'get_current_active_user',
    'create_access_token',
    'verify_password',
    'get_password_hash'
]
