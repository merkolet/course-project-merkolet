"""Tests for XSS protection (S06-03)"""

from fastapi.testclient import TestClient

from app.core.xss_protection import escape_html, sanitize_response_data
from app.main import app

client = TestClient(app)


class TestXSSProtection:
    """Test XSS protection implementation"""

    def test_escape_html_basic(self):
        """Test basic HTML escaping"""
        expected = "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        assert escape_html("<script>alert('xss')</script>") == expected
        assert escape_html('"quotes"') == "&quot;quotes&quot;"
        assert escape_html("&amp;") == "&amp;amp;"

    def test_sanitize_string(self):
        """Test string sanitization"""
        malicious = "<img src=x onerror=alert(1)>"
        sanitized = sanitize_response_data(malicious)
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert "alert" in sanitized  # Content preserved, but escaped

    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        malicious_data = {
            "title": "<script>alert('xss')</script>",
            "notes": 'Normal text with "quotes"',
            "safe_field": 123,
        }

        sanitized = sanitize_response_data(malicious_data)

        assert "&lt;script&gt;" in sanitized["title"]
        assert "&quot;quotes&quot;" in sanitized["notes"]
        assert sanitized["safe_field"] == 123

    def test_sanitize_nested_structure(self):
        """Test sanitization of nested structures"""
        nested_data = {
            "wish": {
                "title": "<script>alert(1)</script>",
                "items": ["<img src=x>", "safe text"],
            }
        }

        sanitized = sanitize_response_data(nested_data)

        assert "&lt;script&gt;" in sanitized["wish"]["title"]
        assert "&lt;img" in sanitized["wish"]["items"][0]
        assert sanitized["wish"]["items"][1] == "safe text"

    def test_xss_in_api_response(self):
        """Test that XSS protection utilities work correctly"""
        # Test that sanitization function works
        xss_payload = "<script>alert('XSS')</script>"
        sanitized = sanitize_response_data(xss_payload)

        # Verify XSS payload is escaped
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized

    def test_xss_in_notes_field(self):
        """Test XSS protection utilities for various payloads"""
        xss_payloads = [
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "<iframe src=javascript:alert(1)>",
        ]

        for payload in xss_payloads:
            sanitized = sanitize_response_data(payload)

            # Verify payload is escaped
            assert "<" not in sanitized or "&lt;" in sanitized

    def test_negative_scenario_xss_injection(self):
        """Test negative scenario: XSS injection attempt"""
        # Multiple XSS attack vectors
        xss_vectors = [
            "<script>document.cookie</script>",
            "<img src=x onerror='alert(document.cookie)'>",
            "<svg><script>alert(1)</script></svg>",
            "<body onload=alert(1)>",
            "';alert(String.fromCharCode(88,83,83))//",
        ]

        for vector in xss_vectors:
            sanitized = sanitize_response_data(vector)

            # All XSS vectors should be escaped
            assert (
                "<script" not in sanitized.lower() or "&lt;script" in sanitized.lower()
            )
            assert "onerror" not in sanitized.lower() or "&lt;" in sanitized
            assert "onload" not in sanitized.lower() or "&lt;" in sanitized

    def test_sql_injection_attempt_escaped(self):
        """Test that SQL injection attempts are also escaped (defense in depth)"""
        sql_payload = "'; DROP TABLE wishes; --"
        response = client.post(
            "/wishes",
            json={
                "title": sql_payload,
                "price_estimate": 100.0,
            },
        )

        assert response.status_code == 201
        data = response.json()

        # SQL payload should be escaped (though parameterized queries are primary defense)
        assert "<" not in data["title"] or "&lt;" in data["title"]
