def test_index_route(client):
    """Test the root API endpoint."""
    response = client.get("/api/")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"


class TestAuthEndpoints:
    """Test authentication-related endpoints."""
    
    def test_me_endpoint_without_auth(self, client):
        """Test /api/auth/me endpoint fails without authentication."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        
    def test_me_endpoint_with_auth(self, auth_client, test_user):
        """Test /api/auth/me endpoint returns user data when authenticated."""
        response = auth_client.get("/api/auth/me")
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["id"] == test_user.id
        assert json_data["name"] == test_user.name
        assert json_data["email"] == test_user.email
        assert json_data["image"] == test_user.image
        
    def test_refresh_endpoint_without_refresh_token(self, client):
        """Test /api/auth/refresh endpoint fails without refresh token."""
        response = client.post("/api/auth/refresh")
        assert response.status_code == 401
        
    def test_logout_endpoint_redirect(self, client):
        """Test /api/auth/logout endpoint redirects to frontend."""
        response = client.get("/api/auth/logout")
        # Should redirect to frontend
        assert response.status_code == 302
        assert "localhost:8000" in response.location  # TestingConfig FRONTEND_URL


class TestErrorHandling:
    """Test centralized error handling."""
    
    def test_404_error_format(self, client):
        """Test that 404 errors return consistent JSON format."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        json_data = response.get_json()
        assert "error" in json_data
        assert json_data["error"] == "Resource not found"
        
    def test_protected_route_without_auth_format(self, client):
        """Test that protected routes return consistent error format."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        
        # Should still be JSON even for JWT errors
        json_data = response.get_json()
        assert json_data is not None
