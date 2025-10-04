"""Wish API endpoints"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from app.core.config import get_db
from app.core.exceptions import ApiError
from app.schemas.wish import Wish, WishCreate, WishUpdate

router = APIRouter(prefix="/wishes", tags=["wishes"])


@router.post("", response_model=Wish, status_code=201)
def create_wish(wish: WishCreate, user_id: int = 1):
    """Создать новое желание"""
    db = get_db()
    new_id = max([w["id"] for w in db["wishes"]], default=0) + 1
    now = datetime.now()

    wish_data = {
        "id": new_id,
        "user_id": user_id,
        "title": wish.title,
        "link": wish.link,
        "price_estimate": wish.price_estimate,
        "notes": wish.notes,
        "created_at": now,
        "updated_at": now,
    }

    db["wishes"].append(wish_data)
    return wish_data


@router.get("", response_model=List[Wish])
def get_wishes(
    price_lt: Optional[float] = Query(None, description="Фильтр по максимальной цене")
):
    """Получить все желания с опциональной фильтрацией по цене"""
    db = get_db()
    wishes = db["wishes"]

    if price_lt is not None:
        wishes = [
            w
            for w in wishes
            if w["price_estimate"] is not None and w["price_estimate"] < price_lt
        ]

    return wishes


@router.get("/{wish_id}", response_model=Wish)
def get_wish(wish_id: int):
    """Получить конкретное желание по ID"""
    db = get_db()
    for wish in db["wishes"]:
        if wish["id"] == wish_id:
            return wish
    raise ApiError(code="not_found", message="wish not found", status=404)


@router.put("/{wish_id}", response_model=Wish)
def update_wish(wish_id: int, wish_update: WishUpdate):
    """Обновить желание"""
    db = get_db()
    for i, wish in enumerate(db["wishes"]):
        if wish["id"] == wish_id:
            # Обновляем только переданные поля
            update_data = wish_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                wish[field] = value
            wish["updated_at"] = datetime.now()
            db["wishes"][i] = wish
            return wish

    raise ApiError(code="not_found", message="wish not found", status=404)


@router.delete("/{wish_id}")
def delete_wish(wish_id: int):
    """Удалить желание"""
    db = get_db()
    for i, wish in enumerate(db["wishes"]):
        if wish["id"] == wish_id:
            del db["wishes"][i]
            return {"message": "wish deleted successfully"}

    raise ApiError(code="not_found", message="wish not found", status=404)
