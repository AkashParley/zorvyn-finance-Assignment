# Finance Dashboard Backend

A production-quality REST API for a finance dashboard system, built with **Python + FastAPI**, **PostgreSQL**, and **JWT authentication**. Implements role-based access control, financial records management, dashboard analytics, and full-text search.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Running Tests](#running-tests)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Role & Permission Model](#role--permission-model)
- [Design Decisions & Assumptions](#design-decisions--assumptions)
- [Tradeoffs](#tradeoffs)

---

## Tech Stack

| Layer         | Choice                              |
|---------------|-------------------------------------|
| Framework     | FastAPI 0.111                       |
| Database      | PostgreSQL (via SQLAlchemy 2.0)     |
| Migrations    | Alembic                             |
| Auth          | JWT (python-jose) + bcrypt          |
| Validation    | Pydantic v2                         |
| Testing       | pytest + httpx (SQLite in-memory)   |
| Server        | Uvicorn                             |

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py                  # App factory, lifespan, global error handlers
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Aggregates all endpoint routers
│   │       └── endpoints/
│   │           ├── auth.py      # /auth — register, login, me
│   │           ├── users.py     # /users — admin user management
│   │           ├── transactions.py  # /transactions — CRUD + filters
│   │           └── dashboard.py     # /dashboard — summary analytics
│   ├── core/
│   │   ├── config.py            # Settings from environment variables
│   │   ├── security.py          # JWT encode/decode, password hashing
│   │   ├── roles.py             # Role enum, permission map, has_permission()
│   │   └── exceptions.py        # Typed HTTP exception helpers
│   ├── db/
│   │   └── session.py           # SQLAlchemy engine, SessionLocal, get_db()
│   ├── models/
│   │   ├── user.py              # User ORM model
│   │   └── transaction.py       # Transaction ORM model (with soft-delete)
│   ├── schemas/
│   │   ├── user.py              # UserCreate, UserUpdate, UserResponse
│   │   ├── transaction.py       # TransactionCreate, TransactionFilter, etc.
│   │   └── common.py            # LoginRequest, TokenResponse, DashboardSummary
│   ├── services/
│   │   ├── user_service.py      # All user business logic
│   │   └── transaction_service.py  # CRUD + dashboard aggregation queries
│   ├── middleware/
│   │   └── auth.py              # get_current_user, require_permission(), require_admin()
│   └── utils/
│       └── seed.py              # Seeds first admin on startup
├── tests/
│   ├── conftest.py              # Fixtures: DB, TestClient, tokens
│   ├── unit/
│   │   ├── test_security.py     # Password hashing and JWT unit tests
│   │   └── test_roles.py        # Permission logic unit tests
│   └── integration/
│       ├── test_auth.py         # Register, login, /me tests
│       ├── test_transactions.py # CRUD, filters, search, access control tests
│       └── test_dashboard.py    # Dashboard summary tests
├── alembic/
│   ├── env.py                   # Alembic migration environment
│   └── versions/                # Auto-generated migration files go here
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd finance-backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set your DATABASE_URL and a strong SECRET_KEY
```

### 4. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE finance_db;"
```

### 5. Run migrations

```bash
alembic upgrade head
```

> **Note:** On first startup the app also calls `Base.metadata.create_all()` as a safety net, but Alembic is the recommended path for schema management.

---

## Environment Variables

| Variable                    | Default                  | Description                              |
|-----------------------------|--------------------------|------------------------------------------|
| `DATABASE_URL`              | *(required)*             | PostgreSQL connection string             |
| `SECRET_KEY`                | *(required)*             | JWT signing key — use a long random string |
| `ALGORITHM`                 | `HS256`                  | JWT algorithm                            |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                   | Token lifetime in minutes                |
| `FIRST_ADMIN_EMAIL`         | `admin@finance.com`      | Auto-seeded admin email                  |
| `FIRST_ADMIN_PASSWORD`      | `Admin@123`              | Auto-seeded admin password               |
| `FIRST_ADMIN_USERNAME`      | `admin`                  | Auto-seeded admin username               |

---

## Running the App

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

---

## Running Tests

Tests use an **in-memory SQLite database** — no PostgreSQL required for testing.

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## Database Migrations

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint             | Auth     | Description                        |
|--------|----------------------|----------|------------------------------------|
| POST   | `/auth/register`     | None     | Register a new user (role: viewer) |
| POST   | `/auth/login`        | None     | Login and receive JWT token        |
| GET    | `/auth/me`           | Any role | Get current user profile           |

**Login example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin@123"}'
```

---

### Users *(Admin only)*

| Method | Endpoint                   | Description                          |
|--------|----------------------------|--------------------------------------|
| GET    | `/users`                   | List all users (paginated)           |
| GET    | `/users/{id}`              | Get user by ID                       |
| PATCH  | `/users/{id}`              | Update role, status, email, username |
| DELETE | `/users/{id}`              | Deactivate user (soft disable)       |
| POST   | `/users/me/change-password`| Change own password                  |

---

### Transactions

| Method | Endpoint                    | Min Role | Description                       |
|--------|-----------------------------|----------|-----------------------------------|
| GET    | `/transactions`             | Viewer   | List with filters + search        |
| GET    | `/transactions/{id}`        | Viewer   | Get single transaction            |
| POST   | `/transactions`             | Admin    | Create a new record               |
| PATCH  | `/transactions/{id}`        | Admin    | Update a record                   |
| DELETE | `/transactions/{id}`        | Admin    | Soft-delete a record              |

**Query parameters for `GET /transactions`:**

| Param       | Type   | Description                                          |
|-------------|--------|------------------------------------------------------|
| `type`      | string | `income` or `expense`                                |
| `category`  | string | Partial match on category name                       |
| `date_from` | date   | Start of date range (YYYY-MM-DD)                     |
| `date_to`   | date   | End of date range (YYYY-MM-DD)                       |
| `search`    | string | Full-text search across category and description     |
| `page`      | int    | Page number (default: 1)                             |
| `page_size` | int    | Results per page, max 100 (default: 20)              |

---

### Dashboard

| Method | Endpoint              | Min Role | Description                          |
|--------|-----------------------|----------|--------------------------------------|
| GET    | `/dashboard/summary`  | Viewer   | Full aggregated dashboard summary    |

**Response includes:**
- `total_income`, `total_expenses`, `net_balance`
- `income_by_category` — ranked list of income totals per category
- `expense_by_category` — ranked list of expense totals per category
- `monthly_trends` — income, expense, and net per month
- `recent_transactions` — 10 most recent records

---

## Role & Permission Model

| Permission        | Viewer | Analyst | Admin |
|-------------------|--------|---------|-------|
| `read:records`    | ✅     | ✅      | ✅    |
| `read:dashboard`  | ✅     | ✅      | ✅    |
| `read:insights`   | ❌     | ✅      | ✅    |
| `create:records`  | ❌     | ❌      | ✅    |
| `update:records`  | ❌     | ❌      | ✅    |
| `delete:records`  | ❌     | ❌      | ✅    |
| `manage:users`    | ❌     | ❌      | ✅    |

Permissions are enforced at the route level via the `require_permission(permission)` dependency factory in `app/middleware/auth.py`. Each role holds a set of permission strings; the system checks membership, not a hierarchy integer, making it easy to adjust roles without cascading changes.

---

## Design Decisions & Assumptions

### Soft Deletes
Transactions are never permanently deleted. A `is_deleted` boolean flag hides records from all queries while preserving the audit trail. This is a common requirement in financial systems.

### Service Layer Pattern
Business logic lives in `app/services/`, not in route handlers. Routes are thin — they validate input, call a service method, and return the result. This makes logic easy to test in isolation and reuse across endpoints.

### Permission-String Model
Rather than a simple role integer comparison (`role >= ANALYST`), each role maps to an explicit set of permission strings (e.g. `"create:records"`). This makes intent clear at the call site (`require_permission("create:records")`) and makes future role adjustments surgical rather than global.

### Schema Separation (Request vs Response)
`UserCreate` / `TransactionCreate` are separate from `UserResponse` / `TransactionResponse`. This ensures `hashed_password` and `is_deleted` never leak into API responses, regardless of how the ORM model evolves.

### Test Database
Tests run against SQLite (in-memory) via a session-scoped fixture. Each test function gets a rolled-back transaction, so tests are fully isolated without needing to truncate tables. This means tests run fast with zero external dependencies.

### First Admin Seeding
The first admin is auto-created on startup via `seed.py` if the email doesn't exist. Credentials are controlled via `.env`. This avoids a chicken-and-egg problem where no admin exists to create the first admin.

### Assumption: Single Currency
All amounts are stored as `NUMERIC(15, 2)` — two decimal places, single implicit currency. Multi-currency support would require a `currency` field and an exchange-rate service.

### Assumption: No Multi-Tenancy
All users share the same transaction pool. An admin sees all records. A multi-tenant design would scope queries by `organization_id`.

---

## Tradeoffs

| Decision | Alternative | Reason for choice |
|----------|-------------|-------------------|
| SQLite for tests | Spin up test Postgres | Faster CI, no external service needed |
| `Base.metadata.create_all` on startup | Alembic only | Easier local dev; Alembic still available for production |
| Soft delete via flag | Separate archive table | Simpler queries; flag is standard for financial records |
| Bcrypt for passwords | Argon2 | bcrypt is well-proven and passlib supports it out of the box |
| `NUMERIC(15,2)` for amounts | `FLOAT` | Avoids floating-point rounding errors in financial data |
