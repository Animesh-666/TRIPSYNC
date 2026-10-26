"""
Security Decorators and Request Interceptors.
Enforces Authentication, Role-Based Access Control, and CSRF Protection.
"""

from functools import wraps
import secrets
from typing import List, Callable, Any
from flask import (
    request,
    session,
    redirect,
    url_for,
    abort,
    g,
    render_template,
    jsonify,
)
from auth import verify_session_cookie
from constants import ROLE_ADMIN, ROLE_STAFF
from config import Config


def generate_csrf_token() -> str:
    """Generates a secure CSRF token and saves it in the Flask session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def validate_csrf():
    """
    Validates CSRF token on mutating requests (POST, PUT, DELETE, PATCH).
    Checks form input '_csrf_token' or 'X-CSRF-Token' request header.
    """
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        token = request.form.get("_csrf_token") or request.headers.get("X-CSRF-Token")
        expected = session.get("_csrf_token")
        if not expected or not token or not secrets.compare_digest(token, expected):
            if request.is_json or request.path.startswith("/session/"):
                return jsonify({"error": "Invalid or missing CSRF token"}), 400
            abort(400, description="Invalid or expired CSRF token. Please refresh the page and try again.")


def get_current_authenticated_user():
    """
    Resolves the current authenticated user from session cookie or Flask session.
    Populates Flask's request context `g.current_user`.
    """
    # 1. Check Firebase session cookie
    cookie = request.cookies.get(Config.FIREBASE_SESSION_COOKIE_NAME)
    if cookie:
        user = verify_session_cookie(cookie)
        if user:
            return user

    # Test-only injection; never authorize using client-editable Flask session in production.
    from flask import current_app
    sess_user = session.get("user") if current_app.config.get("TESTING") else None
    if sess_user and sess_user.get("uid") and sess_user.get("active", True) and sess_user.get("role") in (ROLE_ADMIN, ROLE_STAFF):
        return {
            "uid": sess_user.get("uid"),
            "email": sess_user.get("email"),
            "name": sess_user.get("name", "User"),
            "role": sess_user.get("role", ROLE_STAFF),
            "active": sess_user.get("active", True),
            "is_admin": sess_user.get("role") == ROLE_ADMIN,
        }

    return None


def login_required(f: Callable) -> Callable:
    """Ensures the incoming request is authenticated with an active account."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_authenticated_user()
        if not user:
            if request.is_json:
                return jsonify({"error": "Authentication required", "redirect": url_for("login")}), 401
            return redirect(url_for("login", next=request.path))

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f: Callable) -> Callable:
    """Restricts route access strictly to users with the Admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_authenticated_user()
        if not user:
            if request.is_json:
                return jsonify({"error": "Authentication required", "redirect": url_for("login")}), 401
            return redirect(url_for("login", next=request.path))

        g.current_user = user
        if user.get("role") != ROLE_ADMIN:
            if request.is_json:
                return jsonify({"error": "Administrator privilege required"}), 403
            return render_template("errors/403.html"), 403

        return f(*args, **kwargs)

    return decorated_function


def role_required(allowed_roles: List[str]) -> Callable:
    """Restricts route access to users possessing one of the allowed roles."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_authenticated_user()
            if not user:
                if request.is_json:
                    return jsonify({"error": "Authentication required"}), 401
                return redirect(url_for("login", next=request.path))

            g.current_user = user
            if user.get("role") not in allowed_roles:
                if request.is_json:
                    return jsonify({"error": "Forbidden: Insufficient privileges"}), 403
                return render_template("errors/403.html"), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator
