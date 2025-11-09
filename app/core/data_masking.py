"""Data masking utilities for error messages and logs (S06-05)"""

import re
from typing import Any, Dict

from app.core.secrets import SecretsManager

secrets_manager = SecretsManager()


def mask_email(email: str) -> str:
    """Mask email address: u***@domain.com"""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        masked_local = local[0] + "***" if local else "***"
    else:
        masked_local = local[0] + "***"
    return f"{masked_local}@{domain}"


def mask_password(text: str) -> str:
    """Mask password or token"""
    return "***"


def mask_secret_value(text: str) -> str:
    """Mask secret value using SecretsManager"""
    return secrets_manager.mask_secret(text)


def mask_credit_card(text: str) -> str:
    """Mask credit card number: ****-****-****-1234"""
    # Remove non-digits
    digits = re.sub(r"\D", "", text)
    if len(digits) < 4:
        return "****"
    return "****-****-****-" + digits[-4:]


def mask_phone(text: str) -> str:
    """Mask phone number: +7 *** *** 1234"""
    digits = re.sub(r"\D", "", text)
    if len(digits) < 4:
        return "***"
    return "+" + digits[0] + " *** *** " + digits[-4:]


def mask_sensitive_data(text: str) -> str:
    """Automatically detect and mask sensitive data in text"""
    # Email pattern
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    text = re.sub(email_pattern, lambda m: mask_email(m.group()), text)

    # Password/token patterns (common keywords)
    password_keywords = [
        r"\bpassword['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?",
        r"\btoken['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?",
        r"\bsecret['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?",
        r"\bapi[_-]?key['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?",
        r"\bauth[_-]?token['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?",
    ]
    for pattern in password_keywords:
        text = re.sub(
            pattern,
            lambda m: m.group(0).replace(m.group(1), "***"),
            text,
            flags=re.IGNORECASE,
        )

    # Credit card pattern
    cc_pattern = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    text = re.sub(cc_pattern, lambda m: mask_credit_card(m.group()), text)

    return text


def sanitize_error_detail(detail: str) -> str:
    """Sanitize error detail message to prevent information leakage"""
    # Mask sensitive data
    sanitized = mask_sensitive_data(detail)

    # Remove stack traces and file paths in production
    # (This would be controlled by environment variable in real app)
    sanitized = re.sub(r'File "[^"]+", line \d+', "File ***, line ***", sanitized)
    # Remove stack traces (multiline pattern)
    sanitized = re.sub(
        r"Traceback\s*\(most recent call last\):.*?(?=\n\n|\Z)",
        "Traceback removed",
        sanitized,
        flags=re.DOTALL,
    )

    return sanitized


def sanitize_dict_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize dictionary for safe logging"""
    sanitized = {}
    sensitive_keys = [
        "password",
        "token",
        "secret",
        "api_key",
        "auth_token",
        "credit_card",
        "ssn",
        "email",
    ]

    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            if isinstance(value, str):
                if "email" in key_lower:
                    sanitized[key] = mask_email(value)
                elif "credit_card" in key_lower or "card" in key_lower:
                    sanitized[key] = mask_credit_card(value)
                else:
                    sanitized[key] = mask_password(value)
            else:
                sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_for_logging(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict_for_logging(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, str):
            # Check if value looks like sensitive data
            if "@" in value and "." in value:
                sanitized[key] = mask_email(value)
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value

    return sanitized
