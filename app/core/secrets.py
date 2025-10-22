"""Secrets management implementation (ADR-002)"""

import os
from typing import Optional


class SecretsManager:
    """Centralized secrets management"""

    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """Get secret from environment variables"""
        value = os.getenv(key, default)
        if not value:
            raise ValueError(f"Secret {key} not found in environment variables")
        return value

    def get_jwt_secret(self) -> str:
        """Get JWT signing key"""
        return self.get_secret("JWT_SECRET_KEY")

    def get_db_password(self) -> str:
        """Get database password"""
        return self.get_secret("DB_PASSWORD")

    def get_encryption_key(self) -> bytes:
        """Get encryption key"""
        key_str = self.get_secret("ENCRYPTION_KEY")
        return key_str.encode()

    def mask_secret(self, secret: str, visible_chars: int = 4) -> str:
        """Mask secret for logging"""
        if len(secret) <= visible_chars:
            return "***"
        return secret[:visible_chars] + "***" + secret[-visible_chars:]


# Global instance
secrets_manager = SecretsManager()
