from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine, SessionLocal
from app.db.session import Base

# Import models so Alembic / Base.metadata can see them
from app.models import user, transaction  # noqa: F401
from app.utils.seed import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    # Create tables + seed (safe in dev; use Alembic migrations in production).
    # If the database isn't reachable (wrong creds / Postgres not running),
    # we still want the API to start so `/health` and docs work.
    try:
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            try:
                seed_admin(db)
            except Exception as e:
                # Seeding is best-effort in dev; don't block API startup.
                print(f"[startup] Seed skipped due to error: {e}")
        finally:
            db.close()
    except SQLAlchemyError as e:
        # Startup will continue; endpoints that need DB will error later.
        print(f"[startup] Database init skipped due to error: {e}")

    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    # Nothing to clean up for now


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Finance Dashboard Backend — role-based access control, "
            "financial records management, and dashboard analytics."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global exception handlers ────────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error.", "errors": errors},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occurred. Please try again."},
        )

    # ── Routes ───────────────────────────────────────────────────────────────
    app.include_router(api_router)

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
