import pytest

from backend import create_app
from backend.config import TestingConfig
from backend.extensions import db


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
