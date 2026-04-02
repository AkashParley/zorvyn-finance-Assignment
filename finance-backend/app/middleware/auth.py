from typing import Callable, Iterable, Set, Union

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.exceptions import credentials_exception, inactive_user_exception, forbidden_exception
from app.core.roles import UserRole, has_permission
from app.models.user import User
from app.core.roles import UserStatus

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception()

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception()
    return user


def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise inactive_user_exception()
    return current_user


def require_permission(permission: str):
    """Factory: returns a dependency that enforces a specific permission."""
    def _check(current_user: User = Depends(get_active_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise forbidden_exception(f"perform action '{permission}'")
        return current_user
    return _check


def require_admin(current_user: User = Depends(get_active_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise forbidden_exception("access admin resources")
    return current_user


def require_role(allowed_roles: Iterable[Union[UserRole, str]]) -> Callable[..., User]:
    """
    Enforce that the current user has one of the given roles (viewer / analyst / admin).
    Example: Depends(require_role(["admin"]))  |  Depends(require_role(["admin", "analyst"]))
    """
    allowed: Set[UserRole] = set()
    for r in allowed_roles:
        allowed.add(r if isinstance(r, UserRole) else UserRole(r))

    def _check(current_user: User = Depends(get_active_user)) -> User:
        if current_user.role not in allowed:
            names = ", ".join(sorted(x.value for x in allowed))
            raise forbidden_exception(f"This action requires one of these roles: {names}")
        return current_user

    return _check
