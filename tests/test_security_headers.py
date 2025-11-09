"""Tests for Security Headers middleware (S06-06)"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestSecurityHeaders:
    """Test security headers implementation"""

    def test_security_headers_present(self):
        """Test that all required security headers are present"""
        response = client.get("/health")

        assert response.status_code == 200

        # Required security headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

        assert "Referrer-Policy" in response.headers
        assert "strict-origin-when-cross-origin" in response.headers["Referrer-Policy"]

        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

        assert "Permissions-Policy" in response.headers

    def test_security_headers_on_all_endpoints(self):
        """Test that security headers are present on all endpoints"""
        endpoints = [
            ("GET", "/health"),
            ("GET", "/wishes"),
            ("POST", "/wishes", {"json": {"title": "Test", "price_estimate": 100.0}}),
        ]

        for method, path, *args in endpoints:
            if method == "GET":
                response = client.get(path)
            elif method == "POST":
                response = client.post(path, **args[0] if args else {})

            assert "X-Frame-Options" in response.headers
            assert "X-Content-Type-Options" in response.headers
            assert "Content-Security-Policy" in response.headers

    def test_csp_policy_strict(self):
        """Test that CSP policy prevents inline scripts and styles"""
        response = client.get("/health")

        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'none'" in csp
        assert "style-src 'none'" in csp
        assert "default-src 'self'" in csp

    def test_negative_scenario_missing_headers(self):
        """Test that missing security headers would be a vulnerability"""
        # This test documents the requirement
        # In a real scenario, we would test against a version without headers
        response = client.get("/health")

        # Verify all critical headers are present
        critical_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Content-Security-Policy",
        ]

        for header in critical_headers:
            assert (
                header in response.headers
            ), f"Critical security header {header} is missing"

    def test_permissions_policy_restricts_features(self):
        """Test that Permissions-Policy restricts browser features"""
        response = client.get("/health")

        permissions_policy = response.headers["Permissions-Policy"]
        assert "geolocation=()" in permissions_policy
        assert "microphone=()" in permissions_policy
        assert "camera=()" in permissions_policy
