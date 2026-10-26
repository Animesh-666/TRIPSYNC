"""
Authentication Service for Travel Booking Data Organizer.
Integrates Firebase Authentication with server-side session management and Firestore roles.
"""

from datetime import timedelta, datetime, timezone
import logging
from typing import Optional, Dict, Any
from firebase_admin import auth as fb_auth, exceptions as fb_exceptions
from firebase_config import get_auth_client, is_firebase_ready
from database import get_user_by_uid, upsert_user
from constants import ROLE_ADMIN, ROLE_STAFF
from config import Config

logger = logging.getLogger(__name__)


def verify_id_token_and_get_user(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verifies a client-provided Firebase ID Token.
    Ensures token is not revoked, checks auth_time, and resolves the user's role
    from the server-controlled Firestore user document.
    """
    if not id_token:
        return None

    try:
        auth_client = get_auth_client()
        if auth_client is None:
            logger.warning("Firebase Auth client unavailable.")
            return None

        # Verify ID token with revocation check
        decoded_token = auth_client.verify_id_token(id_token, check_revoked=True)
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")

        if not uid:
            logger.warning("Decoded token missing UID")
            return None

        # Require a recent interactive sign-in before issuing a long-lived session.
        auth_time = decoded_token.get("auth_time")
        if not isinstance(auth_time, (int, float)) or not 0 <= datetime.now(timezone.utc).timestamp() - auth_time <= 300:
            logger.warning("Rejecting login: authentication is not recent")
            return None

        # Retrieve user profile & role from Firestore
        user_doc = get_user_by_uid(uid)
        if not user_doc:
            logger.warning("User document not found in Firestore for UID: %s", uid)
            return None

        if not user_doc.get("active", False) or user_doc.get("role") not in (ROLE_ADMIN, ROLE_STAFF):
            logger.warning("User account %s is deactivated.", uid)
            return None

        return {
            "uid": uid,
            "email": email or user_doc.get("email", ""),
            "name": user_doc.get("name", "User"),
            "role": user_doc.get("role", ROLE_STAFF),
            "active": user_doc.get("active", True),
        }
    except fb_auth.RevokedIdTokenError:
        logger.warning("Firebase ID token has been revoked.")
        return None
    except fb_auth.InvalidIdTokenError as e:
        logger.warning("Invalid Firebase ID token: %s", e)
        return None
    except Exception as e:
        logger.error("Error verifying Firebase ID token: %s", e)
        return None


def create_session_cookie(id_token: str) -> Optional[str]:
    """
    Creates a server-side Firebase session cookie from a verified ID token.
    Default lifetime: 5 days.
    """
    try:
        auth_client = get_auth_client()
        if auth_client is None:
            return None

        expires_in = timedelta(seconds=Config.FIREBASE_SESSION_EXPIRY_SECONDS)
        session_cookie = auth_client.create_session_cookie(id_token, expires_in=expires_in)
        return session_cookie
    except Exception as e:
        logger.error("Failed to create Firebase session cookie: %s", e)
        return None


def verify_session_cookie(cookie: str) -> Optional[Dict[str, Any]]:
    """
    Verifies the server session cookie on protected requests.
    Validates token revocation and checks Firestore for role & active status.
    """
    if not cookie:
        return None

    try:
        auth_client = get_auth_client()
        if auth_client is None:
            return None

        decoded_claims = auth_client.verify_session_cookie(cookie, check_revoked=True)
        uid = decoded_claims.get("uid")
        email = decoded_claims.get("email")

        if not uid:
            return None

        # Verify role and active state from Firestore
        user_doc = get_user_by_uid(uid)
        if not user_doc or not user_doc.get("active", False) or user_doc.get("role") not in (ROLE_ADMIN, ROLE_STAFF):
            logger.warning("Session rejected: user %s missing or inactive", uid)
            return None

        return {
            "uid": uid,
            "email": email or user_doc.get("email", ""),
            "name": user_doc.get("name", "User"),
            "role": user_doc.get("role", ROLE_STAFF),
            "active": user_doc.get("active", True),
            "is_admin": user_doc.get("role") == ROLE_ADMIN,
        }
    except fb_auth.RevokedSessionCookieError:
        logger.warning("Session cookie has been revoked.")
        return None
    except Exception as e:
        logger.warning("Session cookie verification failed: %s", e)
        return None


def provision_user_account(email: str, password: str, name: str, role: str) -> Dict[str, Any]:
    """
    Provisions or updates a user in Firebase Auth and Cloud Firestore.
    Used by CLI management scripts.
    """
    auth_client = get_auth_client()
    if auth_client is None:
        raise RuntimeError("Firebase Auth is not available. Please configure credentials.")

    try:
        user_record = auth_client.get_user_by_email(email)
        uid = user_record.uid
        logger.info("Found existing Firebase Auth user: %s (UID: %s)", email, uid)
        if password:
            auth_client.update_user(uid, password=password, display_name=name)
    except fb_exceptions.NotFoundError:
        user_record = auth_client.create_user(
            email=email,
            password=password,
            display_name=name,
            email_verified=True,
        )
        uid = user_record.uid
        logger.info("Created new Firebase Auth user: %s (UID: %s)", email, uid)

    # Upsert user record in Firestore
    user_doc = upsert_user(uid, {
        "email": email,
        "name": name,
        "role": role,
        "active": True,
    })
    return user_doc
