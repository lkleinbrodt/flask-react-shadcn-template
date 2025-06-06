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
    JWT_SECRET_KEY = SECRET_KEY
    ENV = os.environ.get("ENV", "development").lower()

    CORS_HEADERS = "Content-Type"

    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    REMEMBER_COOKIE_SECURE = True  # Same for "remember me" cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevent client-side JS access to cookie

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Short-lived access token
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Long-lived refresh token

    # Tell Flask-JWT-Extended to look for JWTs in headers and cookies
    JWT_TOKEN_LOCATION = ["headers", "cookies"]

    # Only allow JWT cookies to be sent over HTTPS
    JWT_COOKIE_SECURE = ENV.lower() == "production"  # True in production, False in dev

    # Set SameSite for CSRF protection
    JWT_COOKIE_SAMESITE = "Lax"  # "Lax" or "Strict". "Lax" is often a good balance

    # Configure which cookie(s) to look for JWTs in
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"
    JWT_COOKIE_PATH = "/api/auth"
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

    # CSRF protection for cookie-based JWTs
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True

    OAUTH_CREDENTIALS = {
        "google": {
            "id": os.environ.get("GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        }
    }


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
