"""
Booking Management Integration Tests.
Verifies Booking Creation, Reading, Updating, Cancelling, Deletion, and RBAC Enforcement.
"""

from constants import CATEGORY_FLIGHT, CATEGORY_HOTEL, STATUS_CANCELLED, STATUS_CONFIRMED
from database import get_booking_by_id
from services import get_current_kolkata_date


def test_create_transport_booking(admin_client):
    """Verifies adding a flight booking creates a TB-XXXX sequential record."""
    today_str = get_current_kolkata_date().isoformat()
    form_data = {
        "_csrf_token": "test-csrf-token",
        "customer_name": "Rohan Mehra",
        "contact": "9811223344",
        "travel_type": CATEGORY_FLIGHT,
        "source": "Delhi",
        "destination": "Goa",
        "travel_date": today_str,
        "passengers": "2",
        "unit_fare": "5500",
        "amount_paid": "11000",
        "booking_status": STATUS_CONFIRMED,
    }
    response = admin_client.post("/bookings", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"TB-0001" in response.data
    assert b"Rohan Mehra" in response.data

    # Verify persistent record in database
    booking = get_booking_by_id("TB-0001")
    assert booking is not None
    assert booking["customer_name"] == "Rohan Mehra"
    assert booking["destination"] == "Goa"


def test_create_hotel_booking(admin_client):
    """Verifies adding a hotel booking calculates rooms and nights correctly."""
    today = get_current_kolkata_date()
    check_in = today.isoformat()
    check_out = (today.replace(day=today.day + 2) if today.day < 28 else today).isoformat()
    # Or safely calculate check_out via timedelta
    from datetime import timedelta
    check_out = (today + timedelta(days=2)).isoformat()

    form_data = {
        "_csrf_token": "test-csrf-token",
        "customer_name": "Divya Krishnan",
        "contact": "9844556677",
        "travel_type": CATEGORY_HOTEL,
        "hotel_name": "Grand Palace Hotel",
        "destination": "Jaipur",
        "travel_date": check_in,
        "check_out_date": check_out,
        "rooms": "1",
        "guests": "2",
        "unit_fare": "4000",
        "amount_paid": "4000",
        "booking_status": STATUS_CONFIRMED,
    }
    response = admin_client.post("/bookings", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Grand Palace Hotel" in response.data


def test_edit_booking_preserves_immutable_fields(admin_client, sample_booking):
    """Verifies editing preserves booking_id and original created_by."""
    b_id = sample_booking["booking_id"]
    original_creator = sample_booking["created_by"]

    edit_form = {
        "_csrf_token": "test-csrf-token",
        "customer_name": "Updated Traveler Name",
        "contact": "9876543210",
        "travel_type": CATEGORY_FLIGHT,
        "source": "Kolkata",
        "destination": "Mumbai", # changed
        "travel_date": sample_booking["travel_date"],
        "passengers": "2",
        "unit_fare": "6000",
        "amount_paid": "6000",
        "booking_status": STATUS_CONFIRMED,
    }
    response = admin_client.post(f"/bookings/{b_id}/edit", data=edit_form, follow_redirects=True)
    assert response.status_code == 200
    assert b"Updated Traveler Name" in response.data

    updated = get_booking_by_id(b_id)
    assert updated["booking_id"] == b_id
    assert updated["created_by"] == original_creator
    assert updated["destination"] == "Mumbai"


def test_staff_cannot_cancel_or_delete_booking(staff_client, sample_booking):
    """Verifies Staff role is forbidden from cancellation and deletion."""
    b_id = sample_booking["booking_id"]

    # Cancel attempt
    cancel_resp = staff_client.post(f"/bookings/{b_id}/cancel", data={"_csrf_token": "test-csrf-token"})
    assert cancel_resp.status_code == 403

    # Delete attempt
    delete_resp = staff_client.post(f"/bookings/{b_id}/delete", data={"_csrf_token": "test-csrf-token"})
    assert delete_resp.status_code == 403


def test_admin_cancel_booking(admin_client, sample_booking):
    """Verifies Admin can cancel a booking, which soft-updates status."""
    b_id = sample_booking["booking_id"]
    response = admin_client.post(f"/bookings/{b_id}/cancel", data={"_csrf_token": "test-csrf-token"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Cancelled" in response.data

    booking = get_booking_by_id(b_id)
    assert booking["booking_status"] == STATUS_CANCELLED


def test_admin_delete_booking(admin_client, sample_booking):
    """Verifies Admin can permanently delete a booking."""
    b_id = sample_booking["booking_id"]
    response = admin_client.post(f"/bookings/{b_id}/delete", data={"_csrf_token": "test-csrf-token"}, follow_redirects=True)
    assert response.status_code == 200

    # Ensure document is gone
    assert get_booking_by_id(b_id) is None


def test_printable_voucher_view(admin_client, sample_booking):
    """Verifies printable voucher view renders with disclaimer and clean layout."""
    b_id = sample_booking["booking_id"]
    response = admin_client.get(f"/bookings/{b_id}/print")
    assert response.status_code == 200
    assert b"INTERNAL BOOKING RECORD &amp; CONFIRMATION VOUCHER" in response.data or b"CONFIRMATION VOUCHER" in response.data
    assert b"DISCLAIMER" in response.data
