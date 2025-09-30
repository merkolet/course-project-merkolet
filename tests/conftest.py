# tests/conftest.py
import sys
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]  # корень репозитория
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ruff: noqa: E402
from app.core.config import get_db
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_wish_data():
    """Sample wish data for testing"""
    return {
        "title": "Test Wish",
        "link": "https://example.com",
        "price_estimate": 100.0,
        "notes": "Test notes",
    }


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    db = get_db()
    # Reset to initial state
    db["wishes"] = [
        {
            "id": 1,
            "user_id": 1,
            "title": "Новый iPhone",
            "link": "https://apple.com/iphone",
            "price_estimate": 999.99,
            "notes": "Хочу новую модель",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    ]
    yield
    # Cleanup after test if needed
