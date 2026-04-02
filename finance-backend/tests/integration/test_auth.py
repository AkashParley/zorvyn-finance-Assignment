import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "NewUser@123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["role"] == "viewer"
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client):
        payload = {"username": "dupuser", "email": "dup1@test.com", "password": "Dup@12345"}
        client.post("/api/v1/auth/register", json=payload)
        payload["email"] = "dup2@test.com"
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_weak_password(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "weakpass",
            "email": "weak@test.com",
            "password": "alllower",
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "Valid@123",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "admin", "password": "Admin@123"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "admin", "password": "WrongPassword1"
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "ghost", "password": "Ghost@123"
        })
        assert resp.status_code == 401


class TestMe:
    def test_get_me_authenticated(self, client, admin_headers):
        resp = client.get("/api/v1/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "admin"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 403
