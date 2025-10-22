"""Tests for error handling"""


def test_not_found_wish(client):
    """Test 404 error for non-existent wish"""
    response = client.get("/wishes/999")
    assert response.status_code == 404
    body = response.json()
    assert "type" in body and "not_found" in body["type"]


def test_validation_error_empty_title(client):
    """Test validation error for empty title"""
    response = client.post("/wishes", json={"title": ""})
    assert response.status_code == 422
    body = response.json()
    assert "type" in body and "validation-error" in body["type"]


def test_validation_error_negative_price(client):
    """Test validation error for negative price"""
    response = client.post("/wishes", json={"title": "Test", "price_estimate": -10.0})
    assert response.status_code == 422
    body = response.json()
    assert "type" in body and "validation-error" in body["type"]
