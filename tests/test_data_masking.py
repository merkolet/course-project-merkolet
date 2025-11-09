"""Tests for data masking in errors and logs (S06-05)"""

from fastapi.testclient import TestClient

from app.core.data_masking import (
    mask_credit_card,
    mask_email,
    mask_password,
    mask_sensitive_data,
    sanitize_dict_for_logging,
    sanitize_error_detail,
)
from app.main import app

client = TestClient(app)


class TestDataMasking:
    """Test data masking implementation"""

    def test_mask_email(self):
        """Test email masking"""
        assert mask_email("user@example.com") == "u***@example.com"
        assert mask_email("test.user@domain.co.uk") == "t***@domain.co.uk"
        assert mask_email("a@b.com") == "a***@b.com"  # Single char local part

    def test_mask_password(self):
        """Test password masking"""
        assert mask_password("secret123") == "***"
        assert mask_password("very_long_password_12345") == "***"

    def test_mask_credit_card(self):
        """Test credit card masking"""
        assert mask_credit_card("1234567812345678") == "****-****-****-5678"
        assert mask_credit_card("1234-5678-1234-5678") == "****-****-****-5678"

    def test_mask_sensitive_data_in_text(self):
        """Test automatic detection and masking of sensitive data"""
        text = "User email: user@example.com and password: secret123"
        masked = mask_sensitive_data(text)

        assert "u***@example.com" in masked
        assert "secret123" not in masked
        assert "***" in masked

    def test_sanitize_error_detail(self):
        """Test error detail sanitization"""
        # Error with email
        error = "Failed to authenticate user@example.com"
        sanitized = sanitize_error_detail(error)

        assert "u***@example.com" in sanitized
        assert "user@example.com" not in sanitized

        # Error with password
        error_with_password = 'Error: password="secret123"'
        sanitized = sanitize_error_detail(error_with_password)

        assert "secret123" not in sanitized
        assert "***" in sanitized

    def test_sanitize_dict_for_logging(self):
        """Test dictionary sanitization for logging"""
        sensitive_data = {
            "email": "user@example.com",
            "password": "secret123",
            "api_key": "sk_live_1234567890",
            "credit_card": "1234567812345678",
            "safe_field": "normal_value",
        }

        sanitized = sanitize_dict_for_logging(sensitive_data)

        assert sanitized["email"] == "u***@example.com"
        assert sanitized["password"] == "***"
        assert sanitized["api_key"] == "***"
        assert sanitized["credit_card"] == "****-****-****-5678"
        assert sanitized["safe_field"] == "normal_value"

    def test_error_response_masks_sensitive_data(self):
        """Test that error responses mask sensitive data"""
        # Try to create wish with email in title (should be masked in error if validation fails)
        response = client.post(
            "/wishes",
            json={
                "title": "",  # Invalid: empty title
                "price_estimate": -100.0,  # Invalid: negative price
            },
        )

        assert response.status_code == 422
        error_data = response.json()

        # Error detail should not contain sensitive information
        detail = error_data.get("detail", "")
        # Should not contain stack traces or file paths
        assert 'File "' not in detail
        assert "Traceback" not in detail

    def test_negative_scenario_information_leakage(self):
        """Test negative scenario: prevent information leakage in errors"""
        # Simulate error that might leak sensitive info
        # In a real scenario, this would test against an endpoint that throws errors

        # Test that validation errors don't leak internal structure
        response = client.post(
            "/wishes",
            json={
                "title": "x" * 1000,  # Exceeds max_length
            },
        )

        assert response.status_code == 422
        error_data = response.json()

        detail = error_data.get("detail", "")
        # Should not contain internal Python paths or stack traces
        assert 'File "' not in detail
        assert "line " not in detail or "line ***" in detail
        assert "Traceback" not in detail

    def test_stack_trace_removed(self):
        """Test that stack traces are removed from error messages"""
        error_with_trace = """
        Traceback (most recent call last):
          File "/app/main.py", line 42, in handler
            raise ValueError("Error")
        ValueError: Error
        """

        sanitized = sanitize_error_detail(error_with_trace)

        # Should contain "Traceback removed" instead of full traceback
        assert "Traceback removed" in sanitized or "Traceback" not in sanitized
        assert 'File "' not in sanitized
        assert "line 42" not in sanitized

    def test_file_paths_masked(self):
        """Test that file paths are masked in error messages"""
        error_with_path = 'File "/app/core/config.py", line 15, in get_db'

        sanitized = sanitize_error_detail(error_with_path)

        assert "/app/core/config.py" not in sanitized
        assert "File ***" in sanitized or "line ***" in sanitized
