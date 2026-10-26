"""
Reporting and CSV Export Tests.
Verifies Metrics Calculation, Category Aggregations, and CSV File Delivery.
"""

from constants import (
    CATEGORY_FLIGHT,
    CATEGORY_TRAIN,
    CATEGORY_HOTEL,
    STATUS_CONFIRMED,
    STATUS_CANCELLED,
)
import services


def test_metrics_calculation_excludes_cancelled():
    """Verifies active booking value excludes cancelled bookings while preserving payment info."""
    bookings = [
        {
            "booking_id": "TB-0001",
            "travel_type": CATEGORY_FLIGHT,
            "total_amount_paise": 1000000, # 10,000 INR
            "amount_paid_paise": 1000000,
            "booking_status": STATUS_CONFIRMED,
            "travel_date": "2026-11-10",
        },
        {
            "booking_id": "TB-0002",
            "travel_type": CATEGORY_TRAIN,
            "total_amount_paise": 500000, # 5,000 INR
            "amount_paid_paise": 200000,
            "booking_status": STATUS_CONFIRMED,
            "travel_date": "2026-11-12",
        },
        {
            "booking_id": "TB-0003",
            "travel_type": CATEGORY_HOTEL,
            "total_amount_paise": 800000, # 8,000 INR
            "amount_paid_paise": 400000,
            "booking_status": STATUS_CANCELLED, # Cancelled
            "travel_date": "2026-11-15",
        },
    ]

    metrics = services.calculate_dashboard_metrics(bookings)

    # Active bookings = 2 (excludes cancelled TB-0003)
    assert metrics["total_active_bookings"] == 2
    assert metrics["cancelled_bookings"] == 1

    # Active value = 10,000 + 5,000 = 15,000 INR (1,500,000 paise)
    assert metrics["active_booking_value_paise"] == 1500000

    # Total recorded collections across all = 10,000 + 2,000 + 4,000 = 16,000 INR (1,600,000 paise)
    assert metrics["recorded_payments_paise"] == 1600000

    # Active outstanding balance = 0 + 3,000 = 3,000 INR (300,000 paise)
    assert metrics["outstanding_balance_paise"] == 300000


def test_csv_export_endpoint(admin_client, sample_booking):
    """Verifies Admin CSV download endpoint outputs formatted CSV."""
    response = admin_client.get("/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["Content-Type"]
    assert "attachment; filename=travel_bookings_" in response.headers["Content-Disposition"]

    content = response.data.decode("utf-8-sig")
    assert "Booking ID" in content
    assert "Customer Name" in content
    assert "Total Amount (INR)" in content
    assert sample_booking["booking_id"] in content
