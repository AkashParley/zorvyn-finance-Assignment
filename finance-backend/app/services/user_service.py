from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.roles import UserStatus
from app.core.exceptions import (
    conflict_exception, not_found_exception, bad_request_exception
)


class UserService:

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise not_found_exception("User")
        return user

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.scalar(select(User).where(User.username == username))

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.scalar(select(User).where(User.email == email))

    @staticmethod
    def list_users(db: Session, page: int = 1, page_size: int = 20) -> tuple[int, list[User]]:
        offset = (page - 1) * page_size
        total = db.scalar(select(func.count()).select_from(User))
        users = db.scalars(select(User).offset(offset).limit(page_size)).all()
        return total, list(users)

    @staticmethod
    def create(db: Session, data: UserCreate) -> User:
        if UserService.get_by_username(db, data.username):
            raise conflict_exception(f"Username '{data.username}' is already taken.")
        if UserService.get_by_email(db, data.email):
            raise conflict_exception(f"Email '{data.email}' is already registered.")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            role=data.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user_id: int, data: UserUpdate) -> User:
        user = UserService.get_by_id(db, user_id)
        # Pydantic v1: .dict()  |  v2: .model_dump()
        update_data = (
            data.model_dump(exclude_unset=True)
            if hasattr(data, "model_dump")
            else data.dict(exclude_unset=True)
        )

        if "username" in update_data:
            existing = UserService.get_by_username(db, update_data["username"])
            if existing and existing.id != user_id:
                raise conflict_exception("Username is already taken.")

        if "email" in update_data:
            existing = UserService.get_by_email(db, update_data["email"])
            if existing and existing.id != user_id:
                raise conflict_exception("Email is already registered.")

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise bad_request_exception("Current password is incorrect.")
        user.hashed_password = get_password_hash(new_password)
        db.commit()

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        user = UserService.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def deactivate(db: Session, user_id: int) -> User:
        user = UserService.get_by_id(db, user_id)
        user.status = UserStatus.INACTIVE
        db.commit()
        db.refresh(user)
        return user
