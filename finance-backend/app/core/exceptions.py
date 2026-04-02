from fastapi import HTTPException, status


class FinanceException(Exception):
    """Base application exception."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# ── Auth ────────────────────────────────────────────────────────────────────

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(action: str = "perform this action"):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"You do not have permission to {action}.",
    )


def inactive_user_exception():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Your account is inactive. Contact an administrator.",
    )


# ── Resource ────────────────────────────────────────────────────────────────

def not_found_exception(resource: str = "Resource"):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found.",
    )


def conflict_exception(detail: str = "Resource already exists."):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    )


def bad_request_exception(detail: str):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )
