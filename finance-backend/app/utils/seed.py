from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.roles import UserRole
from app.core.config import settings


def seed_admin(db: Session) -> None:
    """Create the initial admin user if one does not already exist."""
    existing = UserService.get_by_email(db, settings.FIRST_ADMIN_EMAIL)
    if existing:
        return

    UserService.create(
        db,
        UserCreate(
            username=settings.FIRST_ADMIN_USERNAME,
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
            role=UserRole.ADMIN,
        ),
    )
    print(f"[seed] Admin user '{settings.FIRST_ADMIN_USERNAME}' created.")
