"""DateTime normalization utilities (ADR-003)"""

from datetime import datetime, timezone

from pydantic import BaseModel, validator


class DateTimeNormalizer:
    """DateTime normalization utilities"""

    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC time"""
        return datetime.now(timezone.utc)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Convert datetime to UTC"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def parse_iso(iso_string: str) -> datetime:
        """Parse ISO 8601 string to UTC datetime"""
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return DateTimeNormalizer.to_utc(dt)


class DateTimeField(BaseModel):
    """Pydantic model for datetime fields"""

    value: datetime

    @validator("value", pre=True)
    def normalize_datetime(cls, v):
        if isinstance(v, str):
            return DateTimeNormalizer.parse_iso(v)
        elif isinstance(v, datetime):
            return DateTimeNormalizer.to_utc(v)
        return v
