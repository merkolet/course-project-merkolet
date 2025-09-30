"""User schemas"""

from pydantic import BaseModel, Field


class User(BaseModel):
    """User model"""

    id: int
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
