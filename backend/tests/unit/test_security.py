import pytest
from src.core.security import get_password_hash, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_flow():
    user_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    token = create_access_token(subject=user_id)
    assert isinstance(token, str)
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == user_id
    assert "exp" in payload
