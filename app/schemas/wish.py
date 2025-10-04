"""Wish schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WishBase(BaseModel):
    """Base wish model with common fields"""

    title: str = Field(..., min_length=1, max_length=200)
    link: Optional[str] = Field(None, max_length=500)
    price_estimate: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class WishCreate(WishBase):
    """Schema for creating a new wish"""

    pass


class WishUpdate(BaseModel):
    """Schema for updating a wish (all fields optional)"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    link: Optional[str] = Field(None, max_length=500)
    price_estimate: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class Wish(WishBase):
    """Complete wish model with all fields"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
