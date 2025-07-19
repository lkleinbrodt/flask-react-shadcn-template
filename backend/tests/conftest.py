import pytest
from flask_jwt_extended import create_access_token, create_refresh_token

from backend import create_app
from backend.config import TestingConfig
from backend.extensions import db
from backend.models.user import User


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        # Clean up after tests
        db.drop_all()
        db.session.remove()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            google_id="test_google_id_123",
            name="Test User",
            email="test@example.com",
            image="https://example.com/avatar.jpg"
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(app, test_user):
    """Create authorization headers with a valid access token."""
    with app.app_context():
        access_token = create_access_token(
            identity=str(test_user.id),
            additional_claims={
                "name": test_user.name,
                "email": test_user.email,
                "image": test_user.image,
            },
        )
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_client(client, auth_headers):
    """A test client with authentication headers pre-configured."""
    class AuthenticatedClient:
        def __init__(self, client, headers):
            self.client = client
            self.headers = headers
        
        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return self.client.get(*args, **kwargs)
        
        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return self.client.post(*args, **kwargs)
        
        def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return self.client.put(*args, **kwargs)
        
        def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return self.client.delete(*args, **kwargs)
    
    return AuthenticatedClient(client, auth_headers)
