try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from pydantic import BaseSettings  # type: ignore
    SettingsConfigDict = None  # type: ignore

class Settings(BaseSettings):
    APP_NAME: str = "Finance Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/finance_db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # First admin seeded on startup
    FIRST_ADMIN_EMAIL: str = "admin@finance.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@123"
    FIRST_ADMIN_USERNAME: str = "admin"

    # pydantic-settings v2 configuration (when available)
    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    else:
        class Config:
            env_file = ".env"
            case_sensitive = True


settings = Settings()
