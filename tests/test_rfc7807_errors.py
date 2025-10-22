"""Tests for RFC 7807 error format implementation (ADR-001)"""

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRFC7807ErrorFormat:
    """Test RFC 7807 Problem Details format implementation"""

    def test_validation_error_format(self):
        """Test validation error returns RFC 7807 format"""
        response = client.post(
            "/wishes",
            json={
                "title": "",  # Invalid: empty title
                "price_estimate": -100.0,  # Invalid: negative price
            },
        )

        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()

        # Check RFC 7807 required fields
        assert "type" in error_data
        assert "title" in error_data
        assert "status" in error_data
        assert "detail" in error_data
        assert "correlation_id" in error_data
        assert "timestamp" in error_data

        # Check field values
        assert error_data["status"] == 422
        assert "validation" in error_data["type"].lower()

    def test_not_found_error_format(self):
        """Test not found error returns RFC 7807 format"""
        response = client.get("/wishes/99999")

        assert response.status_code == 404
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()

        # Check RFC 7807 required fields
        assert error_data["type"] is not None
        assert error_data["title"] is not None
        assert error_data["status"] == 404
        assert error_data["detail"] is not None
        assert error_data["correlation_id"] is not None
        assert error_data["timestamp"] is not None

    def test_correlation_id_presence(self):
        """Test that correlation_id is present in all error responses"""
        response = client.get("/wishes/99999")

        error_data = response.json()
        correlation_id = error_data["correlation_id"]

        # Should be a valid UUID
        uuid.UUID(correlation_id)

        # Should be present in response headers
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] == correlation_id

    def test_negative_scenario_large_payload(self):
        """Test error handling with extremely large payload"""
        large_title = "x" * 1000  # Exceeds max_length=200

        response = client.post(
            "/wishes", json={"title": large_title, "price_estimate": 100.0}
        )

        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()
        assert error_data["status"] == 422
        assert "validation" in error_data["type"].lower()

    def test_negative_scenario_invalid_json(self):
        """Test error handling with malformed JSON"""
        response = client.post(
            "/wishes",
            data="invalid json{",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()
        assert error_data["status"] == 422
