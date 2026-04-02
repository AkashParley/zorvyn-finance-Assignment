from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.common import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.core.exceptions import credentials_exception, inactive_user_exception
from app.core.roles import UserStatus
from app.middleware.auth import get_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. Default role is **viewer**.
    Only an admin can later promote the user to analyst or admin.
    """
    user = UserService.create(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username + password and receive a JWT bearer token."""
    user = UserService.authenticate(db, data.username, data.password)
    if not user:
        raise credentials_exception()
    if user.status != UserStatus.ACTIVE:
        raise inactive_user_exception()
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_active_user)):
    """Return the currently authenticated user's profile."""
    return current_user
