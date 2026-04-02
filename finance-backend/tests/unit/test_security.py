import pytest
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, decode_access_token,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("Secret@123")
        assert hashed != "Secret@123"

    def test_correct_password_verifies(self):
        hashed = get_password_hash("Secret@123")
        assert verify_password("Secret@123", hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("Secret@123")
        assert verify_password("Wrong@999", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        h1 = get_password_hash("Secret@123")
        h2 = get_password_hash("Secret@123")
        assert h1 != h2  # bcrypt salts are random


class TestJWT:
    def test_encode_and_decode_roundtrip(self):
        token = create_access_token(subject=42)
        user_id = decode_access_token(token)
        assert user_id == "42"

    def test_invalid_token_returns_none(self):
        assert decode_access_token("not.a.valid.token") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token(subject=1)
        tampered = token[:-5] + "XXXXX"
        assert decode_access_token(tampered) is None
