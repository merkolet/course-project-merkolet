"""Currency normalization utilities (ADR-003)"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Union

from pydantic import BaseModel, validator


class CurrencyNormalizer:
    """Currency normalization utilities"""

    SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP"]
    DEFAULT_CURRENCY = "USD"

    @staticmethod
    def normalize_amount(
        amount: Union[float, str, Decimal], currency: str = DEFAULT_CURRENCY
    ) -> Decimal:
        """Normalize monetary amount"""
        if currency not in CurrencyNormalizer.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")

        if isinstance(amount, str):
            amount = amount.replace(" ", "").replace(",", ".")

        decimal_amount = Decimal(str(amount))
        return decimal_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def format_currency(amount: Decimal, currency: str = DEFAULT_CURRENCY) -> str:
        """Format currency for display"""
        if currency == "USD":
            return f"${amount:.2f}"
        elif currency == "EUR":
            return f"€{amount:.2f}"
        elif currency == "RUB":
            return f"{amount:.2f} ₽"
        elif currency == "GBP":
            return f"£{amount:.2f}"
        else:
            return f"{amount:.2f} {currency}"

    @staticmethod
    def parse_currency_string(currency_str: str) -> tuple[Decimal, str]:
        """Parse currency string (e.g., '$123.45')"""
        currency_str = currency_str.strip()

        currency_map = {"$": "USD", "€": "EUR", "₽": "RUB", "£": "GBP"}

        currency = CurrencyNormalizer.DEFAULT_CURRENCY
        amount_str = currency_str

        for symbol, curr in currency_map.items():
            if currency_str.startswith(symbol):
                currency = curr
                amount_str = currency_str[1:].strip()
                break

        amount = CurrencyNormalizer.normalize_amount(amount_str, currency)
        return amount, currency


class CurrencyField(BaseModel):
    """Pydantic model for currency fields"""

    amount: Decimal
    currency: str = CurrencyNormalizer.DEFAULT_CURRENCY

    @validator("amount", pre=True)
    def normalize_amount(cls, v, values):
        currency = values.get("currency", CurrencyNormalizer.DEFAULT_CURRENCY)
        return CurrencyNormalizer.normalize_amount(v, currency)

    @validator("currency")
    def validate_currency(cls, v):
        if v not in CurrencyNormalizer.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {v}")
        return v
