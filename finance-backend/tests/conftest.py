import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.db.session import Base, get_db
from app.utils.seed import seed_admin

# Use SQLite in-memory for tests (no Postgres required)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    app = create_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    seed_admin(db)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_token(client):
    resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def viewer_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "viewer1", "email": "viewer@test.com", "password": "Viewer@123"},
    )
    resp = client.post("/api/v1/auth/login", json={"username": "viewer1", "password": "Viewer@123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
