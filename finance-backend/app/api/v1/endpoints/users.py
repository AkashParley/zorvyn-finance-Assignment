from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate, UserListResponse, PasswordChange
from app.services.user_service import UserService
from app.middleware.auth import require_role, get_active_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse, dependencies=[Depends(require_role(["admin"]))])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """[Admin] List all users with pagination."""
    total, users = UserService.list_users(db, page=page, page_size=page_size)
    return UserListResponse(total=total, users=users)


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_role(["admin"]))])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """[Admin] Get a specific user by ID."""
    return UserService.get_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_role(["admin"]))])
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    """[Admin] Update a user's role, status, email, or username."""
    return UserService.update(db, user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(["admin"]))])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """[Admin] Deactivate a user (soft disable — does not delete)."""
    UserService.deactivate(db, user_id)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db),
):
    """Change the current user's own password."""
    UserService.change_password(db, current_user, data.current_password, data.new_password)
