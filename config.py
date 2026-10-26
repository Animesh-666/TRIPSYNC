"""
Configuration settings for Travel Booking Data Organizer.
Supports local .env loading and production environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    # Flask Core
    SECRET_KEY = os.environ.get("SECRET_KEY") or ("local-dev-not-for-production" if not os.environ.get("RENDER") and os.environ.get("FLASK_ENV", "development") != "production" else None)
    ENV = os.environ.get("FLASK_ENV", "production" if os.environ.get("RENDER") else "development")
    DEBUG = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

    # Security & Cookies
    SESSION_COOKIE_NAME = "flask_csrf_session"
    FIREBASE_SESSION_COOKIE_NAME = "tb_firebase_session"
    ALLOW_IN_MEMORY_DB = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # In production on HTTPS (Render), enable Secure cookies
    SESSION_COOKIE_SECURE = os.environ.get("RENDER") is not None or ENV == "production"

    # Firebase Admin SDK credentials
    # Can be a file path via GOOGLE_APPLICATION_CREDENTIALS
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    # Or raw JSON string (helpful for platforms like Render where setting a secret file or env var is easy)
    FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON")

    # Firebase Client (Public Web Config for login page)
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID", "")

    # Firebase Session duration in seconds (5 days)
    FIREBASE_SESSION_EXPIRY_SECONDS = 5 * 24 * 60 * 60

    @classmethod
    def get_firebase_client_config(cls) -> dict:
        """Returns the public Firebase configuration for client-side JS."""
        return {
            "apiKey": cls.FIREBASE_API_KEY,
            "authDomain": cls.FIREBASE_AUTH_DOMAIN or (f"{cls.FIREBASE_PROJECT_ID}.firebaseapp.com" if cls.FIREBASE_PROJECT_ID else ""),
            "projectId": cls.FIREBASE_PROJECT_ID,
            "storageBucket": cls.FIREBASE_STORAGE_BUCKET or (f"{cls.FIREBASE_PROJECT_ID}.appspot.com" if cls.FIREBASE_PROJECT_ID else ""),
            "messagingSenderId": cls.FIREBASE_MESSAGING_SENDER_ID,
            "appId": cls.FIREBASE_APP_ID,
        }

    @classmethod
    def is_firebase_configured(cls) -> bool:
        """Checks if server-side Firebase credentials or project settings are provided."""
        return bool(
            cls.FIREBASE_PROJECT_ID and (
                cls.GOOGLE_APPLICATION_CREDENTIALS or
                cls.FIREBASE_CREDENTIALS_JSON or
                os.path.exists(BASE_DIR / "serviceAccountKey.json")
            )
        )


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    ALLOW_IN_MEMORY_DB = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
