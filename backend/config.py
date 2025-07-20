import json
import os
import uuid
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    ROOT_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent
    DATA_DIR = ROOT_DIR / "data"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        SECRET_KEY = str(uuid.uuid4())

    # Use a dedicated JWT secret key (can be same as SECRET_KEY if not specified)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    ENV = os.environ.get("ENV", "development").lower()

    CORS_HEADERS = "Content-Type"

    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    REMEMBER_COOKIE_SECURE = True  # Same for "remember me" cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevent client-side JS access to cookie

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Short-lived access token
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Long-lived refresh token

    # Tell Flask-JWT-Extended to look for JWTs only in cookies (more secure)
    JWT_TOKEN_LOCATION = ["cookies"]

    # Enable CSRF protection for cookies
    JWT_COOKIE_CSRF_PROTECT = True

    # Set cookie security settings
    # In production, this should be True. For development, False.
    JWT_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"

    # Set SameSite to 'Lax' to prevent most CSRF attacks
    # Can be 'Strict' for higher security if it doesn't break cross-domain functionality
    JWT_COOKIE_SAMESITE = "Lax"

    # Explicitly set cookie domain and path for development
    JWT_COOKIE_DOMAIN = None  # Let browser set domain automatically
    JWT_COOKIE_PATH = "/"  # Available on all paths

    # Ensure HttpOnly is always True. This prevents client-side JS from accessing the cookie.
    JWT_COOKIE_HTTPONLY = True

    # Flask-JWT-Extended will use sensible defaults for cookie names and paths
    # Removed custom JWT_ACCESS_COOKIE_NAME, JWT_REFRESH_COOKIE_NAME, JWT_COOKIE_PATH, etc.

    OAUTH_CREDENTIALS = {
        "google": {
            "id": os.environ.get("GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        }
    }

    # Email configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in [
        "true",
        "on",
        "1",
    ]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@example.com")


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    FRONTEND_URL = "http://localhost:5173"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(Config.ROOT_DIR, "app.db")

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY_TESTING")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY_TESTING")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


class ProductionConfig(Config):
    ENV = "production"
    # FRONTEND_URL = "https://PROJECT_NAME.com"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = os.path.join(os.getenv("TEMP", "/tmp"), "flask_cache")
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    FRONTEND_URL = "http://localhost:8000"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY_TESTING")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY_TESTING")
    MAIL_SUPPRESS_SEND = True  # Do not send emails during tests
