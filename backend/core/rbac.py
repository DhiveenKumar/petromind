# =============================================================================
# rbac.py — Role-Based Access Control for PetroMind
#
# Architecture: User → Role → Permission → Module
#
# Three roles:
#   field_engineer      — operational access
#   maintenance_manager — reporting + approval access
#   administrator       — full access + configuration
#
# Why RBAC matters in interviews:
# Shows enterprise thinking — not just "anyone can use everything"
# Real enterprise AI systems have governance and access control
# =============================================================================

from enum import Enum
from typing import List
from fastapi import HTTPException, Header
from backend.core.config import SECRET_KEY


# =============================================================================
# PERMISSIONS — granular access rights
# =============================================================================

class Permission(str, Enum):
    # Knowledge module
    READ_KNOWLEDGE      = "read:knowledge"
    WRITE_KNOWLEDGE     = "write:knowledge"

    # Prediction module
    READ_PREDICTION     = "read:prediction"
    WRITE_SENSOR_UPLOAD = "write:sensor_upload"

    # Vision module
    READ_VISION         = "read:vision"
    WRITE_IMAGE_UPLOAD  = "write:image_upload"

    # Report module
    READ_REPORTS        = "read:reports"
    WRITE_REPORTS       = "write:reports"
    APPROVE_REPORTS     = "write:approve"

    # Admin
    READ_MONITORING     = "read:monitoring"
    WRITE_SETTINGS      = "write:settings"
    CONFIGURE_MODELS    = "write:model_config"
    READ_ALL            = "read:all"
    WRITE_ALL           = "write:all"


# =============================================================================
# ROLES — collections of permissions
# =============================================================================

class Role(str, Enum):
    FIELD_ENGINEER      = "field_engineer"
    MAINTENANCE_MANAGER = "maintenance_manager"
    ADMINISTRATOR       = "administrator"


# Role → Permission mapping
ROLE_PERMISSIONS = {
    Role.FIELD_ENGINEER: [
        Permission.READ_KNOWLEDGE,
        Permission.READ_PREDICTION,
        Permission.READ_VISION,
        Permission.WRITE_SENSOR_UPLOAD,
        Permission.WRITE_IMAGE_UPLOAD,
    ],
    Role.MAINTENANCE_MANAGER: [
        Permission.READ_KNOWLEDGE,
        Permission.READ_PREDICTION,
        Permission.READ_VISION,
        Permission.READ_REPORTS,
        Permission.WRITE_REPORTS,
        Permission.APPROVE_REPORTS,
        Permission.WRITE_SENSOR_UPLOAD,
        Permission.WRITE_IMAGE_UPLOAD,
    ],
    Role.ADMINISTRATOR: [
        Permission.READ_ALL,
        Permission.WRITE_ALL,
        Permission.READ_MONITORING,
        Permission.WRITE_SETTINGS,
        Permission.CONFIGURE_MODELS,
    ],
}


# =============================================================================
# USER — simple user model
# =============================================================================

class User:
    """
    Lightweight user model.
    In production: integrate with GCP Identity Platform or Azure AD.
    For portfolio: simple token-based auth demonstrates the pattern.
    """
    def __init__(self, username: str, role: Role):
        self.username = username
        self.role = role
        self.permissions = ROLE_PERMISSIONS.get(role, [])

    def has_permission(self, permission: Permission) -> bool:
        if Permission.READ_ALL in self.permissions:
            if permission.startswith("read:"):
                return True
        if Permission.WRITE_ALL in self.permissions:
            return True
        return permission in self.permissions

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions]
        }


# =============================================================================
# DEMO USERS — for portfolio demonstration
# =============================================================================

DEMO_USERS = {
    "field_token_123": User(
        username="john.field@petromind.com",
        role=Role.FIELD_ENGINEER
    ),
    "manager_token_456": User(
        username="sarah.manager@petromind.com",
        role=Role.MAINTENANCE_MANAGER
    ),
    "admin_token_789": User(
        username="admin@petromind.com",
        role=Role.ADMINISTRATOR
    ),
}


# =============================================================================
# AUTH FUNCTIONS — used as FastAPI dependencies
# =============================================================================

def get_current_user(
    authorization: str = Header(default="Bearer field_token_123")
) -> User:
    """
    Extracts user from Authorization header.
    Format: Bearer <token>

    In production: validate JWT token against GCP Identity Platform.
    For portfolio: token maps directly to demo user.
    """
    try:
        token = authorization.replace("Bearer ", "").strip()
        user = DEMO_USERS.get(token)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


def require_permission(permission: Permission):
    """
    FastAPI dependency factory.
    Usage: Depends(require_permission(Permission.READ_REPORTS))

    Returns a dependency function that checks the current user
    has the required permission before allowing access.
    """
    def check_permission(
        user: User = Header(default="Bearer field_token_123")
    ) -> User:
        current_user = get_current_user(user)
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission.value} required. "
                       f"Your role ({current_user.role.value}) does not "
                       f"have this permission."
            )
        return current_user
    return check_permission


def get_role_summary() -> dict:
    """
    Returns RBAC summary for admin monitoring page.
    """
    return {
        role.value: {
            "permissions": [p.value for p in perms],
            "permission_count": len(perms)
        }
        for role, perms in ROLE_PERMISSIONS.items()
    }