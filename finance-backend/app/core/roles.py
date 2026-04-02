from enum import Enum


class UserRole(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# Map each role to the set of actions it is allowed to perform.
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.VIEWER: {
        "read:records",
        "read:dashboard",
    },
    UserRole.ANALYST: {
        "read:records",
        "read:dashboard",
        "read:insights",
    },
    UserRole.ADMIN: {
        "read:records",
        "read:dashboard",
        "read:insights",
        "create:records",
        "update:records",
        "delete:records",
        "manage:users",
    },
}


def has_permission(role: UserRole, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
