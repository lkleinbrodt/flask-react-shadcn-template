def test_index_route(client):
    """Test the root API endpoint."""
    response = client.get("/api/")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
