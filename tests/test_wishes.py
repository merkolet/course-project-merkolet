"""Tests for wishes API endpoints"""


class TestWishesAPI:
    """Test class for wishes API endpoints"""

    def test_create_wish_success(self, client, sample_wish_data):
        """Test successful wish creation"""
        response = client.post("/wishes", json=sample_wish_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == sample_wish_data["title"]
        assert data["link"] == sample_wish_data["link"]
        assert data["price_estimate"] == sample_wish_data["price_estimate"]
        assert data["notes"] == sample_wish_data["notes"]
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_wish_minimal_data(self, client):
        """Test wish creation with minimal required data"""
        minimal_data = {"title": "Minimal Wish"}
        response = client.post("/wishes", json=minimal_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Minimal Wish"
        assert data["link"] is None
        assert data["price_estimate"] is None
        assert data["notes"] is None

    def test_create_wish_validation_error_empty_title(self, client):
        """Test validation error for empty title"""
        invalid_data = {"title": ""}
        response = client.post("/wishes", json=invalid_data)
        assert response.status_code == 422

    def test_create_wish_validation_error_title_too_long(self, client):
        """Test validation error for title too long"""
        invalid_data = {"title": "x" * 201}  # 201 characters
        response = client.post("/wishes", json=invalid_data)
        assert response.status_code == 422

    def test_create_wish_validation_error_negative_price(self, client):
        """Test validation error for negative price"""
        invalid_data = {"title": "Test", "price_estimate": -10.0}
        response = client.post("/wishes", json=invalid_data)
        assert response.status_code == 422

    def test_get_wishes_empty(self, client):
        """Test getting wishes when list is empty"""
        # This test is not applicable since we reset DB to have one wish
        # Instead, test that we get the default wish
        response = client.get("/wishes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Новый iPhone"

    def test_get_wishes_with_data(self, client, sample_wish_data):
        """Test getting wishes with existing data"""
        # Create a wish first
        create_response = client.post("/wishes", json=sample_wish_data)
        assert create_response.status_code == 201

        # Get all wishes
        response = client.get("/wishes")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(wish["title"] == sample_wish_data["title"] for wish in data)

    def test_get_wishes_filter_by_price(self, client):
        """Test filtering wishes by price"""
        # Create wishes with different prices
        client.post("/wishes", json={"title": "Cheap", "price_estimate": 50.0})
        client.post("/wishes", json={"title": "Expensive", "price_estimate": 200.0})

        # Filter by price < 100
        response = client.get("/wishes?price_lt=100")
        assert response.status_code == 200

        data = response.json()
        assert all(
            wish["price_estimate"] < 100
            for wish in data
            if wish["price_estimate"] is not None
        )

    def test_get_wish_by_id_success(self, client, sample_wish_data):
        """Test getting wish by ID successfully"""
        # Create a wish first
        create_response = client.post("/wishes", json=sample_wish_data)
        wish_id = create_response.json()["id"]

        # Get wish by ID
        response = client.get(f"/wishes/{wish_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == wish_id
        assert data["title"] == sample_wish_data["title"]

    def test_get_wish_by_id_not_found(self, client):
        """Test getting non-existent wish by ID"""
        response = client.get("/wishes/99999")
        assert response.status_code == 404

        data = response.json()
        assert data["error"]["code"] == "not_found"
        assert "wish not found" in data["error"]["message"]

    def test_update_wish_success(self, client, sample_wish_data):
        """Test successful wish update"""
        # Create a wish first
        create_response = client.post("/wishes", json=sample_wish_data)
        wish_id = create_response.json()["id"]

        # Update the wish
        update_data = {"title": "Updated Title", "price_estimate": 150.0}
        response = client.put(f"/wishes/{wish_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["price_estimate"] == 150.0
        assert data["link"] == sample_wish_data["link"]  # Should remain unchanged
        assert data["notes"] == sample_wish_data["notes"]  # Should remain unchanged

    def test_update_wish_partial(self, client, sample_wish_data):
        """Test partial wish update"""
        # Create a wish first
        create_response = client.post("/wishes", json=sample_wish_data)
        wish_id = create_response.json()["id"]

        # Update only title
        update_data = {"title": "Only Title Updated"}
        response = client.put(f"/wishes/{wish_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Only Title Updated"
        # Should remain unchanged
        assert data["price_estimate"] == sample_wish_data["price_estimate"]

    def test_update_wish_not_found(self, client):
        """Test updating non-existent wish"""
        update_data = {"title": "Updated Title"}
        response = client.put("/wishes/99999", json=update_data)
        assert response.status_code == 404

        data = response.json()
        assert data["error"]["code"] == "not_found"

    def test_delete_wish_success(self, client, sample_wish_data):
        """Test successful wish deletion"""
        # Create a wish first
        create_response = client.post("/wishes", json=sample_wish_data)
        wish_id = create_response.json()["id"]

        # Delete the wish
        response = client.delete(f"/wishes/{wish_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "wish deleted successfully"

        # Verify wish is deleted
        get_response = client.get(f"/wishes/{wish_id}")
        assert get_response.status_code == 404

    def test_delete_wish_not_found(self, client):
        """Test deleting non-existent wish"""
        response = client.delete("/wishes/99999")
        assert response.status_code == 404

        data = response.json()
        assert data["error"]["code"] == "not_found"

    def test_wish_validation_link_too_long(self, client):
        """Test validation error for link too long"""
        invalid_data = {"title": "Test", "link": "https://example.com/" + "x" * 500}
        response = client.post("/wishes", json=invalid_data)
        assert response.status_code == 422

    def test_wish_validation_notes_too_long(self, client):
        """Test validation error for notes too long"""
        invalid_data = {"title": "Test", "notes": "x" * 1001}  # 1001 characters
        response = client.post("/wishes", json=invalid_data)
        assert response.status_code == 422

    def test_wish_created_at_updated_at_timestamps(self, client, sample_wish_data):
        """Test that created_at and updated_at timestamps are set correctly"""
        response = client.post("/wishes", json=sample_wish_data)
        assert response.status_code == 201

        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] == data["updated_at"]  # Should be equal on creation

        # Update the wish
        update_response = client.put(f"/wishes/{data['id']}", json={"title": "Updated"})
        assert update_response.status_code == 200

        updated_data = update_response.json()
        assert (
            updated_data["created_at"] == data["created_at"]
        )  # Should remain the same
        assert updated_data["updated_at"] != data["updated_at"]  # Should be different
