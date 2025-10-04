"""Tests for error handling"""


def test_not_found_wish(client):
    """Test 404 error for non-existent wish"""
    response = client.get("/wishes/999")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_validation_error_empty_title(client):
    """Test validation error for empty title"""
    response = client.post("/wishes", json={"title": ""})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body  # FastAPI validation error format


def test_validation_error_negative_price(client):
    """Test validation error for negative price"""
    response = client.post("/wishes", json={"title": "Test", "price_estimate": -10.0})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body  # FastAPI validation error format
