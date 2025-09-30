"""Tests for health endpoint"""


def test_health_endpoint(client):
    """Test health endpoint returns ok status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
