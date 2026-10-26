"""
Authentication and Authorization Boundary Tests.
Verifies Session Guards, Role Permissions (Admin vs Staff), and Route Protections.
"""

from constants import ROLE_ADMIN, ROLE_STAFF


def test_unauthenticated_redirect(client):
    """Verifies unauthenticated visitors are redirected to login."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    response = client.get("/bookings")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_access_allowed(admin_client):
    """Verifies Admin has access to all operational and administrative routes."""
    # Operational
    assert admin_client.get("/dashboard").status_code == 200
    assert admin_client.get("/bookings").status_code == 200
    assert admin_client.get("/upcoming").status_code == 200

    # Administrative
    assert admin_client.get("/reports").status_code == 200
    assert admin_client.get("/export/csv").status_code == 200


def test_staff_restricted_from_admin_reports(staff_client):
    """Verifies Staff cannot access Admin-only Reports (403 Forbidden)."""
    response = staff_client.get("/reports")
    assert response.status_code == 403


def test_staff_restricted_from_admin_csv_export(staff_client):
    """Verifies Staff cannot download CSV export (403 Forbidden)."""
    response = staff_client.get("/export/csv")
    assert response.status_code == 403


def test_healthz_endpoint(client):
    """Verifies minimal public health endpoint is operational without leaking private keys."""
    response = client.get("/healthz")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "travel-booking-organizer"
    # Ensure sensitive credentials are never leaked
    assert "SECRET_KEY" not in str(json_data)
    assert "private_key" not in str(json_data)


def test_logout_clears_session(admin_client):
    """Verifies session logout POST clears credentials and redirects to login."""
    response = admin_client.post("/session/logout", data={"_csrf_token": "test-csrf-token"})
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Subsequent access should be denied
    dash_response = admin_client.get("/dashboard")
    assert dash_response.status_code == 302
    assert "/login" in dash_response.headers["Location"]
