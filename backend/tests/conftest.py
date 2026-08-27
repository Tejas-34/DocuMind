import pytest
import os

# Set test env vars
os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "postgresql+asyncpg://tejaspatare@localhost:5432/documind")
os.environ["JWT_SECRET"] = "test_secret_key_for_unit_tests_32charsmin"
os.environ["GEMINI_API_KEY"] = "mock_api_key"
