"""
Unit Tests for Domain Services and Business Logic.
Verifies Fare Calculations, Currency Conversions, Payment Status Derivations,
Input Validations, Filter Operations, and CSV Sanitization.
"""

from datetime import date, timedelta
import pytest

import services
from constants import (
    CATEGORY_FLIGHT,
    CATEGORY_HOTEL,
    CATEGORY_TRAIN,
    PAYMENT_PAID,
    PAYMENT_PARTIAL,
    PAYMENT_UNPAID,
    STATUS_CONFIRMED,
    STATUS_CANCELLED,
)


def test_rupees_and_paise_conversion():
    """Verifies floating rupee and integer paise bidirectional conversion."""
    paise = services.rupees_to_paise(1250.50)
    assert paise == 125050
    assert services.paise_to_rupees(paise) == 1250.50

    # Zero and integers
    assert services.rupees_to_paise(0) == 0
    assert services.rupees_to_paise(100) == 10000


def test_format_currency_inr():
    """Verifies Indian rupee formatting with commas."""
    formatted = services.format_currency_inr(12500000) # 1,25,000.00
    assert "₹1,25,000.00" == formatted
    assert services.format_currency_inr(0) == "₹0.00"


def test_transport_total_calculation():
    """Verifies transport fare calculation: passengers * unit fare."""
    unit_paise = services.rupees_to_paise(4500)
    total = services.calculate_total_amount_paise(
        travel_type=CATEGORY_FLIGHT,
        unit_fare_paise=unit_paise,
        passengers=3,
    )
    assert total == services.rupees_to_paise(13500)


def test_hotel_total_calculation():
    """Verifies hotel calculation: rooms * nights * unit fare."""
    unit_paise = services.rupees_to_paise(3000)
    total = services.calculate_total_amount_paise(
        travel_type=CATEGORY_HOTEL,
        unit_fare_paise=unit_paise,
        rooms=2,
        check_in_str="2026-11-01",
        check_out_str="2026-11-04", # 3 nights
    )
    # 2 rooms * 3 nights * 3000 = 18000
    assert total == services.rupees_to_paise(18000)


def test_payment_status_derivation():
    """Verifies payment status is strictly derived from amounts."""
    total = services.rupees_to_paise(10000)

    # 1. Zero paid -> Unpaid
    assert services.derive_payment_status(total, 0) == PAYMENT_UNPAID

    # 2. Partially paid -> Partially Paid
    assert services.derive_payment_status(total, services.rupees_to_paise(4000)) == PAYMENT_PARTIAL

    # 3. Exact full amount paid -> Paid
    assert services.derive_payment_status(total, total) == PAYMENT_PAID


def test_outstanding_balance_calculation():
    """Verifies outstanding balance = total - paid."""
    total = services.rupees_to_paise(5000)
    paid = services.rupees_to_paise(2000)
    balance = services.calculate_outstanding_balance_paise(total, paid)
    assert balance == services.rupees_to_paise(3000)


def test_validate_booking_input_valid_transport():
    """Verifies valid transport booking input passes validation."""
    today_str = services.get_current_kolkata_date().isoformat()
    form = {
        "customer_name": "Aarav Sharma",
        "contact": "9876543210",
        "travel_type": CATEGORY_FLIGHT,
        "source": "Mumbai",
        "destination": "Delhi",
        "travel_date": today_str,
        "passengers": "2",
        "unit_fare": "4500",
        "amount_paid": "9000",
        "booking_status": STATUS_CONFIRMED,
    }
    cleaned, errors = services.validate_booking_input(form)
    assert not errors
    assert cleaned["customer_name"] == "Aarav Sharma"
    assert cleaned["total_amount_paise"] == services.rupees_to_paise(9000)
    assert cleaned["amount_paid_paise"] == services.rupees_to_paise(9000)


def test_validate_booking_input_invalid_phone():
    """Verifies invalid phone number format is caught."""
    form = {
        "customer_name": "Aarav Sharma",
        "contact": "12345", # Invalid Indian phone
        "travel_type": CATEGORY_TRAIN,
        "source": "Kolkata",
        "destination": "Delhi",
        "travel_date": "2026-11-10",
        "passengers": "1",
        "unit_fare": "1000",
    }
    cleaned, errors = services.validate_booking_input(form)
    assert "contact" in errors


def test_validate_booking_input_same_source_and_destination():
    """Verifies error when departure and destination are identical."""
    form = {
        "customer_name": "Priya Sen",
        "contact": "9876543210",
        "travel_type": CATEGORY_TRAIN,
        "source": "Delhi",
        "destination": "Delhi",
        "travel_date": "2026-11-10",
        "passengers": "1",
        "unit_fare": "1000",
    }
    cleaned, errors = services.validate_booking_input(form)
    assert "destination" in errors


def test_validate_booking_input_checkout_before_checkin():
    """Verifies hotel check-out date must be after check-in date."""
    form = {
        "customer_name": "Vikram Malhotra",
        "contact": "9876543210",
        "travel_type": CATEGORY_HOTEL,
        "hotel_name": "Grand Resort",
        "destination": "Goa",
        "travel_date": "2026-11-05",
        "check_out_date": "2026-11-04", # Before check-in
        "rooms": "1",
        "guests": "2",
        "unit_fare": "5000",
    }
    cleaned, errors = services.validate_booking_input(form)
    assert "check_out_date" in errors


def test_csv_sanitization_formula_injection():
    """Verifies leading formula characters are escaped to prevent CSV injection."""
    assert services.sanitize_csv_field("=cmd|'/C calc'!A0") == "'=cmd|'/C calc'!A0"
    assert services.sanitize_csv_field("+123456") == "'+123456"
    assert services.sanitize_csv_field("-SUM(A1:A10)") == "'-SUM(A1:A10)"
    assert services.sanitize_csv_field("@admin") == "'@admin"
    assert services.sanitize_csv_field("Safe Customer") == "Safe Customer"
