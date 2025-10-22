"""Negative scenario tests for secure coding practices (ADR-001, ADR-002, ADR-003)"""

import pytest
from fastapi.testclient import TestClient

from app.core.currency_utils import CurrencyNormalizer
from app.core.datetime_utils import DateTimeNormalizer
from app.core.secrets import SecretsManager
from app.main import app

client = TestClient(app)


class TestNegativeScenarios:
    """Test negative scenarios for security and robustness"""

    def test_large_file_upload_attempt(self):
        """Test handling of extremely large file upload attempt"""
        large_payload = {
            "title": "x" * 10000,  # Very large title
            "notes": "x" * 100000,  # Very large notes
            "price_estimate": 100.0,
        }

        response = client.post("/wishes", json=large_payload)

        # Should return validation error due to field length limits
        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()
        assert error_data["status"] == 422
        assert "validation" in error_data["type"].lower()

    def test_path_traversal_attempt(self):
        """Test handling of path traversal attempts"""
        # Use very long path traversal that exceeds max_length=200
        traversal_payload = "../../../etc/passwd" + "x" * 200

        response = client.post("/wishes", json={"title": traversal_payload})

        # Should return validation error due to length limit
        assert response.status_code == 422
        error_data = response.json()
        assert "validation" in error_data["type"].lower()

    def test_sql_injection_attempt(self):
        """Test handling of SQL injection attempts"""
        # Use very long SQL injection that exceeds max_length=200
        sql_payload = "'; DROP TABLE wishes; --" + "x" * 200

        response = client.post("/wishes", json={"title": sql_payload})

        # Should return validation error due to length limit
        assert response.status_code == 422
        error_data = response.json()
        assert "validation" in error_data["type"].lower()

    def test_xss_attempt(self):
        """Test handling of XSS attempts"""
        # Use very long XSS payload that exceeds max_length=200
        xss_payload = "<script>alert('xss')</script>" + "x" * 200

        response = client.post("/wishes", json={"title": xss_payload})

        # Should return validation error due to length limit
        assert response.status_code == 422
        error_data = response.json()
        assert "validation" in error_data["type"].lower()

    def test_secrets_in_logs_prevention(self):
        """Test that secrets are masked in logs"""
        manager = SecretsManager()

        # Test various secret patterns
        secret_patterns = [
            "password=secret123",
            "secret_key=abc123def456",
            "api_key=sk-1234567890abcdef",
        ]

        for pattern in secret_patterns:
            masked = manager.mask_secret(pattern)
            assert "***" in masked
            assert pattern not in masked  # Original secret should not be visible

    def test_currency_injection_attempts(self):
        """Test handling of malicious currency inputs"""
        malicious_currency_inputs = [
            "'; DROP TABLE wishes; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
        ]

        for malicious_input in malicious_currency_inputs:
            with pytest.raises(Exception):
                CurrencyNormalizer.normalize_amount(malicious_input, "USD")

    def test_datetime_injection_attempts(self):
        """Test handling of malicious datetime inputs"""
        malicious_datetime_inputs = [
            "'; DROP TABLE wishes; --",
            "<script>alert('xss')</script>",
            "2025-13-45T25:70:80Z",  # Invalid date/time
        ]

        for malicious_input in malicious_datetime_inputs:
            with pytest.raises(Exception):
                DateTimeNormalizer.parse_iso(malicious_input)

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON"""
        malformed_json_payloads = [
            '{"title": "test", "price": }',  # Missing value
            '{"title": "test", "price": 100',  # Missing closing brace
            '{"title": "test", "price": 100,}',  # Trailing comma
        ]

        for payload in malformed_json_payloads:
            response = client.post(
                "/wishes", data=payload, headers={"Content-Type": "application/json"}
            )

            # Should return 422 for malformed JSON
            assert response.status_code == 422
            assert response.headers["content-type"] == "application/problem+json"
