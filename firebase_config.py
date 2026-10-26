"""
Firebase Admin SDK Initialization and Client Provider.
Handles secure credential loading from files, JSON strings, or Application Default Credentials.
"""

import json
import logging
import os
from typing import Optional
import firebase_admin
from firebase_admin import credentials, auth
from config import Config, BASE_DIR

try:
    from firebase_admin import firestore
except Exception as _fe:
    firestore = None

logger = logging.getLogger(__name__)

_firebase_app: Optional[firebase_admin.App] = None
_firestore_client = None
_init_attempted = False


def initialize_firebase() -> Optional[firebase_admin.App]:
    """
    Initializes the Firebase Admin SDK if not already initialized.
    Checks for credentials in this order:
    1. GOOGLE_APPLICATION_CREDENTIALS file path
    2. FIREBASE_CREDENTIALS_JSON inline JSON string
    3. serviceAccountKey.json in project root
    4. Application Default Credentials (ADC)
    """
    global _firebase_app, _firestore_client, _init_attempted

    if _firebase_app is not None:
        return _firebase_app

    if _init_attempted:
        return None

    _init_attempted = True

    # Check if an existing Firebase app is already registered in this process
    if len(firebase_admin._apps) > 0:
        _firebase_app = firebase_admin.get_app()
        if firestore is not None:
            try:
                _firestore_client = firestore.client(app=_firebase_app)
            except Exception as e:
                logger.warning("Could not obtain firestore client from existing app: %s", e)
        return _firebase_app

    cred = None

    # 1. Custom file path or standard env var
    cred_path = Config.GOOGLE_APPLICATION_CREDENTIALS
    if cred_path and os.path.exists(cred_path):
        try:
            logger.info("Initializing Firebase using credentials file: %s", cred_path)
            cred = credentials.Certificate(cred_path)
        except Exception as e:
            logger.error("Failed to load credentials from %s: %s", cred_path, e)

    # 2. Raw JSON string from environment variable (useful on Render/Cloud)
    if not cred and Config.FIREBASE_CREDENTIALS_JSON:
        try:
            logger.info("Initializing Firebase using FIREBASE_CREDENTIALS_JSON env var")
            cred_dict = json.loads(Config.FIREBASE_CREDENTIALS_JSON)
            cred = credentials.Certificate(cred_dict)
        except Exception as e:
            logger.error("Failed to parse FIREBASE_CREDENTIALS_JSON: %s", e)

    # 3. Local serviceAccountKey.json in base dir
    if not cred:
        local_key = BASE_DIR / "serviceAccountKey.json"
        if local_key.exists():
            try:
                logger.info("Initializing Firebase using local %s", local_key)
                cred = credentials.Certificate(str(local_key))
            except Exception as e:
                logger.error("Failed to load local serviceAccountKey.json: %s", e)

    # 4. Fallback to Application Default Credentials if project ID is provided
    if not cred and Config.FIREBASE_PROJECT_ID:
        try:
            logger.info("Initializing Firebase using Application Default Credentials")
            cred = credentials.ApplicationDefault()
        except Exception as e:
            logger.warning("Application Default Credentials not available: %s", e)

    if cred:
        try:
            options = {}
            if Config.FIREBASE_PROJECT_ID:
                options["projectId"] = Config.FIREBASE_PROJECT_ID
            if Config.FIREBASE_STORAGE_BUCKET:
                options["storageBucket"] = Config.FIREBASE_STORAGE_BUCKET

            _firebase_app = firebase_admin.initialize_app(cred, options)
            if firestore is not None:
                _firestore_client = firestore.client(app=_firebase_app)
            logger.info("Firebase Admin SDK successfully initialized.")
            return _firebase_app
        except Exception as e:
            logger.error("Failed to initialize Firebase Admin app: %s", e)
            return None
    else:
        logger.warning(
            "Firebase credentials not found: authentication and persistent database operations are unavailable."
        )
        return None


def get_db():
    """Returns the Firestore client, initializing Firebase if necessary."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
    return _firestore_client


def get_auth_client():
    """Returns the Firebase Auth module if app is initialized."""
    app = initialize_firebase()
    if app is None:
        return None
    return auth


def is_firebase_ready() -> bool:
    """Returns True if Firestore is initialized and ready to communicate."""
    return get_db() is not None
