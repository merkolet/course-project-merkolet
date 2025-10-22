"""Tests for secrets management implementation (ADR-002)"""

import os
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.core.currency_utils import CurrencyField, CurrencyNormalizer
from app.core.secrets import SecretsManager


class TestSecretsManagement:
    """Test secrets management functionality"""

    def test_get_secret_success(self):
        """Test successful secret retrieval"""
        with patch.dict(os.environ, {"TEST_SECRET": "test_value"}):
            manager = SecretsManager()
            result = manager.get_secret("TEST_SECRET")
            assert result == "test_value"

    def test_get_secret_missing(self):
        """Test error when secret is missing"""
        manager = SecretsManager()
        with pytest.raises(ValueError, match="Secret MISSING_SECRET not found"):
            manager.get_secret("MISSING_SECRET")

    def test_mask_secret_long(self):
        """Test masking of long secrets"""
        manager = SecretsManager()
        result = manager.mask_secret("very_long_secret_key_12345")
        assert result == "very***2345"

    def test_negative_scenario_empty_secret(self):
        """Test error handling with empty secret value"""
        with patch.dict(os.environ, {"EMPTY_SECRET": ""}):
            manager = SecretsManager()
            with pytest.raises(ValueError, match="Secret EMPTY_SECRET not found"):
                manager.get_secret("EMPTY_SECRET")


class TestCurrencyNormalization:
    """Test currency normalization functionality"""

    def test_normalize_amount_float(self):
        """Test normalizing float amount"""
        result = CurrencyNormalizer.normalize_amount(123.45, "USD")
        assert result == Decimal("123.45")

    def test_normalize_amount_rounding(self):
        """Test rounding behavior"""
        result = CurrencyNormalizer.normalize_amount(123.456, "USD")
        assert result == Decimal("123.46")  # ROUND_HALF_UP

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

    def test_currency_field_validation(self):
        """Test CurrencyField Pydantic model validation"""
        field = CurrencyField(amount=123.45, currency="USD")
        assert field.amount == Decimal("123.45")
        assert field.currency == "USD"
