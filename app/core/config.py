"""Core configuration settings"""

from datetime import datetime
from typing import Any, Dict

# In-memory storage
_DB: Dict[str, Any] = {
    "users": [{"id": 1, "username": "testuser", "email": "test@example.com"}],
    "wishes": [
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
    ],
}


def get_db():
    """Get in-memory database"""
    return _DB
