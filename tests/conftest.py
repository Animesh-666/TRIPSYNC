"""
Pytest Fixtures and Test Environment Configuration.
Provides test clients for unauthenticated, Admin, and Staff sessions.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from database import reset_memory_db, create_booking
from constants import ROLE_ADMIN, ROLE_STAFF, CATEGORY_FLIGHT, STATUS_CONFIRMED
from services import rupees_to_paise, get_current_kolkata_date


@pytest.fixture
def app():
    """Creates a test-configured Flask application."""
    app = create_app(config_name="testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "test-secret-key-12345"

    with app.app_context():
        reset_memory_db()
        yield app
        reset_memory_db()


@pytest.fixture
def client(app):
    """Unauthenticated HTTP test client."""
    return app.test_client()


@pytest.fixture
def admin_client(app):
    """Test client authenticated with Admin privileges."""
    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["user"] = {
            "uid": "test_admin_uid",
            "email": "admin@tripsync.test",
            "name": "Test Admin",
            "role": ROLE_ADMIN,
            "active": True,
            "is_admin": True,
        }
        sess["_csrf_token"] = "test-csrf-token"
    return test_client


@pytest.fixture
def staff_client(app):
    """Test client authenticated with Staff privileges."""
    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["user"] = {
            "uid": "test_staff_uid",
            "email": "staff@tripsync.test",
            "name": "Test Staff",
            "role": ROLE_STAFF,
            "active": True,
            "is_admin": False,
        }
        sess["_csrf_token"] = "test-csrf-token"
    return test_client


@pytest.fixture
def sample_booking(app):
    """Creates and returns a sample flight booking in database."""
    today_str = get_current_kolkata_date().isoformat()
    booking_dict = {
        "customer_name": "Test Traveler",
        "contact": "9876543210",
        "travel_type": CATEGORY_FLIGHT,
        "source": "Kolkata",
        "destination": "Delhi",
        "travel_date": today_str,
        "passengers": 2,
        "unit_fare_paise": rupees_to_paise(5000),
        "total_amount_paise": rupees_to_paise(10000),
        "amount_paid_paise": rupees_to_paise(5000),
        "booking_status": STATUS_CONFIRMED,
    }
    user_info = {"email": "admin@tripsync.test", "uid": "test_admin_uid"}
    return create_booking(booking_dict, user_info)
