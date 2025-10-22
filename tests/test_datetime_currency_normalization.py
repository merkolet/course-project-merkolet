"""Tests for datetime and currency normalization implementation (ADR-003)"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.core.currency_utils import CurrencyNormalizer
from app.core.datetime_utils import DateTimeNormalizer


class TestDateTimeNormalization:
    """Test datetime normalization functionality"""

    def test_now_utc(self):
        """Test getting current UTC time"""
        now = DateTimeNormalizer.now_utc()
        assert now.tzinfo == timezone.utc
        assert isinstance(now, datetime)

    def test_to_utc_naive_datetime(self):
        """Test converting naive datetime to UTC"""
        naive_dt = datetime(2025, 10, 13, 15, 30, 0)
        utc_dt = DateTimeNormalizer.to_utc(naive_dt)
        assert utc_dt.tzinfo == timezone.utc
        assert utc_dt.hour == 15

    def test_parse_iso(self):
        """Test parsing ISO 8601 string to UTC datetime"""
        iso_str = "2025-10-13T15:30:00Z"
        dt = DateTimeNormalizer.parse_iso(iso_str)
        assert dt.tzinfo == timezone.utc
        assert dt.year == 2025
        assert dt.month == 10
        assert dt.day == 13
        assert dt.hour == 15
        assert dt.minute == 30

    def test_negative_scenario_invalid_iso_string(self):
        """Test error handling with invalid ISO string"""
        with pytest.raises(ValueError):
            DateTimeNormalizer.parse_iso("invalid-iso-string")


class TestCurrencyNormalization:
    """Test currency normalization functionality"""

    def test_normalize_amount_float(self):
        """Test normalizing float amount"""
        result = CurrencyNormalizer.normalize_amount(123.45, "USD")
        assert result == Decimal("123.45")

    def test_normalize_amount_rounding(self):
        """Test rounding behavior with ROUND_HALF_UP"""
        result = CurrencyNormalizer.normalize_amount(123.456, "USD")
        assert result == Decimal("123.46")

    def test_format_currency_usd(self):
        """Test USD currency formatting"""
        result = CurrencyNormalizer.format_currency(Decimal("123.45"), "USD")
        assert result == "$123.45"

    def test_parse_currency_string_usd(self):
        """Test parsing USD currency string"""
        amount, currency = CurrencyNormalizer.parse_currency_string("$123.45")
        assert amount == Decimal("123.45")
        assert currency == "USD"

    def test_unsupported_currency(self):
        """Test error with unsupported currency"""
        with pytest.raises(ValueError, match="Unsupported currency: BTC"):
            CurrencyNormalizer.normalize_amount(100, "BTC")

    def test_negative_scenario_invalid_amount_string(self):
        """Test error handling with invalid amount string"""
        with pytest.raises(Exception):  # Decimal will raise exception
            CurrencyNormalizer.normalize_amount("invalid_amount", "USD")

    def test_negative_scenario_traversal_attempt(self):
        """Test handling potential path traversal in currency string"""
        malicious_input = "../../../etc/passwd"
        with pytest.raises(Exception):
            CurrencyNormalizer.normalize_amount(malicious_input, "USD")

    def test_negative_scenario_sql_injection_attempt(self):
        """Test handling potential SQL injection in currency string"""
        malicious_input = "'; DROP TABLE wishes; --"
        with pytest.raises(Exception):
            CurrencyNormalizer.normalize_amount(malicious_input, "USD")
