"""
Sample Data Seeding Script for Travel Booking Data Organizer.
Generates 25 realistic, fictional Indian travel booking records for demonstration and testing.
Includes all categories, booking statuses, payment states, and upcoming trip countdown dates.

Usage:
    python seed_data.py --force
"""

import argparse
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from database import create_booking, get_all_bookings
from services import (
    get_current_kolkata_date,
    calculate_total_amount_paise,
    rupees_to_paise,
)
from constants import (
    CATEGORY_FLIGHT,
    CATEGORY_TRAIN,
    CATEGORY_BUS,
    CATEGORY_HOTEL,
    STATUS_CONFIRMED,
    STATUS_PENDING,
    STATUS_CANCELLED,
)


def generate_sample_bookings():
    """Generates 25 realistic Indian travel booking records."""
    today = get_current_kolkata_date()

    # Pre-calculated dates relative to today in Asia/Kolkata
    d_past_5 = (today - timedelta(days=5)).isoformat()
    d_past_2 = (today - timedelta(days=2)).isoformat()
    d_today = today.isoformat()
    d_tomorrow = (today + timedelta(days=1)).isoformat()
    d_in_2 = (today + timedelta(days=2)).isoformat()
    d_in_3 = (today + timedelta(days=3)).isoformat()
    d_in_5 = (today + timedelta(days=5)).isoformat()
    d_in_7 = (today + timedelta(days=7)).isoformat()
    d_in_12 = (today + timedelta(days=12)).isoformat()
    d_in_18 = (today + timedelta(days=18)).isoformat()
    d_in_25 = (today + timedelta(days=25)).isoformat()

    samples = [
        # 1. Flights
        {
            "customer_name": "Aarav Sharma",
            "contact": "9820112233",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Delhi",
            "destination": "Mumbai",
            "travel_date": d_today,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(5400),
            "amount_paid_paise": rupees_to_paise(10800), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Priya Sen",
            "contact": "9830554433",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Kolkata",
            "destination": "Bengaluru",
            "travel_date": d_tomorrow,
            "passengers": 1,
            "unit_fare_paise": rupees_to_paise(6200),
            "amount_paid_paise": rupees_to_paise(3000), # Partially Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Vikram Malhotra",
            "contact": "9819776655",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Mumbai",
            "destination": "Goa",
            "travel_date": d_in_3,
            "passengers": 4,
            "unit_fare_paise": rupees_to_paise(4100),
            "amount_paid_paise": rupees_to_paise(16400), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Ananya Roy",
            "contact": "9831445566",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Kolkata",
            "destination": "Jaipur",
            "travel_date": d_in_7,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(5800),
            "amount_paid_paise": rupees_to_paise(0), # Unpaid
            "booking_status": STATUS_PENDING,
        },
        {
            "customer_name": "Rohan Mehra",
            "contact": "9876112244",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Bengaluru",
            "destination": "Delhi",
            "travel_date": d_in_18,
            "passengers": 1,
            "unit_fare_paise": rupees_to_paise(7100),
            "amount_paid_paise": rupees_to_paise(7100), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Sneha Kulkarni",
            "contact": "9822334455",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Pune",
            "destination": "Kolkata",
            "travel_date": d_in_12,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(6500),
            "amount_paid_paise": rupees_to_paise(5000), # Partially Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Kabir Das",
            "contact": "9845119988",
            "travel_type": CATEGORY_FLIGHT,
            "source": "Hyderabad",
            "destination": "Chennai",
            "travel_date": d_past_2,
            "passengers": 1,
            "unit_fare_paise": rupees_to_paise(3900),
            "amount_paid_paise": rupees_to_paise(3900), # Paid
            "booking_status": STATUS_CONFIRMED,
        },

        # 2. Trains
        {
            "customer_name": "Rajesh Banerjee",
            "contact": "9836123456",
            "travel_type": CATEGORY_TRAIN,
            "source": "Kolkata",
            "destination": "Darjeeling",
            "travel_date": d_today,
            "passengers": 3,
            "unit_fare_paise": rupees_to_paise(1850),
            "amount_paid_paise": rupees_to_paise(5550), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Deepak Patel",
            "contact": "9825667788",
            "travel_type": CATEGORY_TRAIN,
            "source": "Mumbai",
            "destination": "Jaipur",
            "travel_date": d_in_2,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(2200),
            "amount_paid_paise": rupees_to_paise(2000), # Partially Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Siddharth Joshi",
            "contact": "9823998877",
            "travel_type": CATEGORY_TRAIN,
            "source": "Delhi",
            "destination": "Varanasi",
            "travel_date": d_in_5,
            "passengers": 4,
            "unit_fare_paise": rupees_to_paise(1450),
            "amount_paid_paise": rupees_to_paise(5800), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Meera Iyer",
            "contact": "9840112233",
            "travel_type": CATEGORY_TRAIN,
            "source": "Chennai",
            "destination": "Bengaluru",
            "travel_date": d_in_12,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(950),
            "amount_paid_paise": rupees_to_paise(0), # Unpaid
            "booking_status": STATUS_PENDING,
        },
        {
            "customer_name": "Arjun Nair",
            "contact": "9847113355",
            "travel_type": CATEGORY_TRAIN,
            "source": "Kochi",
            "destination": "Goa",
            "travel_date": d_past_5,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(1350),
            "amount_paid_paise": rupees_to_paise(2700), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Neha Gupta",
            "contact": "9810556677",
            "travel_type": CATEGORY_TRAIN,
            "source": "Delhi",
            "destination": "Agra",
            "travel_date": d_in_25,
            "passengers": 3,
            "unit_fare_paise": rupees_to_paise(750),
            "amount_paid_paise": rupees_to_paise(2250), # Cancelled but recorded payment
            "booking_status": STATUS_CANCELLED,
        },

        # 3. Buses
        {
            "customer_name": "Karan Singhal",
            "contact": "9811889900",
            "travel_type": CATEGORY_BUS,
            "source": "Delhi",
            "destination": "Shimla",
            "travel_date": d_tomorrow,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(1100),
            "amount_paid_paise": rupees_to_paise(2200), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Pooja Verma",
            "contact": "9829112244",
            "travel_type": CATEGORY_BUS,
            "source": "Jaipur",
            "destination": "Udaipur",
            "travel_date": d_in_3,
            "passengers": 3,
            "unit_fare_paise": rupees_to_paise(850),
            "amount_paid_paise": rupees_to_paise(1500), # Partially Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Suresh Reddy",
            "contact": "9848556677",
            "travel_type": CATEGORY_BUS,
            "source": "Hyderabad",
            "destination": "Bengaluru",
            "travel_date": d_in_7,
            "passengers": 1,
            "unit_fare_paise": rupees_to_paise(1350),
            "amount_paid_paise": rupees_to_paise(1350), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Aditi Ghosh",
            "contact": "9830887766",
            "travel_type": CATEGORY_BUS,
            "source": "Kolkata",
            "destination": "Darjeeling",
            "travel_date": d_in_18,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(1200),
            "amount_paid_paise": rupees_to_paise(0), # Unpaid
            "booking_status": STATUS_PENDING,
        },
        {
            "customer_name": "Manoj Tiwari",
            "contact": "9821665544",
            "travel_type": CATEGORY_BUS,
            "source": "Mumbai",
            "destination": "Pune",
            "travel_date": d_past_2,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(650),
            "amount_paid_paise": rupees_to_paise(1300),
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Sunita Rao",
            "contact": "9845223311",
            "travel_type": CATEGORY_BUS,
            "source": "Bengaluru",
            "destination": "Goa",
            "travel_date": d_in_12,
            "passengers": 2,
            "unit_fare_paise": rupees_to_paise(1600),
            "amount_paid_paise": rupees_to_paise(1000),
            "booking_status": STATUS_CANCELLED,
        },

        # 4. Hotels
        {
            "customer_name": "Gaurav Kapoor",
            "contact": "9818991122",
            "travel_type": CATEGORY_HOTEL,
            "hotel_name": "Goa Grand Heritage Resort",
            "destination": "Goa",
            "travel_date": d_today, # check-in
            "check_out_date": (today + timedelta(days=3)).isoformat(), # 3 nights
            "rooms": 1,
            "guests": 2,
            "unit_fare_paise": rupees_to_paise(4500), # 1 room * 3 nights * 4500 = 13500
            "amount_paid_paise": rupees_to_paise(13500), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Tanya Bhatia",
            "contact": "9810443322",
            "travel_type": CATEGORY_HOTEL,
            "hotel_name": "The Himalayan Pines Retreat",
            "destination": "Darjeeling",
            "travel_date": d_tomorrow,
            "check_out_date": (today + timedelta(days=4)).isoformat(), # 3 nights
            "rooms": 2,
            "guests": 4,
            "unit_fare_paise": rupees_to_paise(3800), # 2 * 3 * 3800 = 22800
            "amount_paid_paise": rupees_to_paise(12000), # Partially Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Manish Agarwal",
            "contact": "9829334411",
            "travel_type": CATEGORY_HOTEL,
            "hotel_name": "Royal Haveli Palace",
            "destination": "Jaipur",
            "travel_date": d_in_5,
            "check_out_date": (today + timedelta(days=7)).isoformat(), # 2 nights
            "rooms": 1,
            "guests": 2,
            "unit_fare_paise": rupees_to_paise(5200), # 1 * 2 * 5200 = 10400
            "amount_paid_paise": rupees_to_paise(10400), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Divya Krishnan",
            "contact": "9841667788",
            "travel_type": CATEGORY_HOTEL,
            "hotel_name": "Marina Breeze Hotel",
            "destination": "Chennai",
            "travel_date": d_in_7,
            "check_out_date": (today + timedelta(days=9)).isoformat(), # 2 nights
            "rooms": 1,
            "guests": 1,
            "unit_fare_paise": rupees_to_paise(3200), # 1 * 2 * 3200 = 6400
            "amount_paid_paise": rupees_to_paise(0), # Unpaid
            "booking_status": STATUS_PENDING,
        },
        {
            "customer_name": "Alok Choudhury",
            "contact": "9831998877",
            "travel_type": CATEGORY_HOTEL,
            "hotel_name": "The Oberoi Grand Kolkata",
            "destination": "Kolkata",
            "travel_date": d_in_18,
            "check_out_date": (today + timedelta(days=20)).isoformat(), # 2 nights
            "rooms": 1,
            "guests": 2,
            "unit_fare_paise": rupees_to_paise(8500), # 1 * 2 * 8500 = 17000
            "amount_paid_paise": rupees_to_paise(17000), # Paid
            "booking_status": STATUS_CONFIRMED,
        },
        {
            "customer_name": "Swati Deshmukh",
            "contact": "9822119955",
            "travel_type": CATEGORY_HOTEL,
            "hotel_name": "Lakeview Luxury Suites",
            "destination": "Udaipur",
            "travel_date": d_in_25,
            "check_out_date": (today + timedelta(days=28)).isoformat(), # 3 nights
            "rooms": 2,
            "guests": 3,
            "unit_fare_paise": rupees_to_paise(6000), # 2 * 3 * 6000 = 36000
            "amount_paid_paise": rupees_to_paise(18000), # Partially Paid
            "booking_status": STATUS_CONFIRMED,
        },
    ]

    # Calculate total_amount_paise correctly for each entry
    for item in samples:
        total = calculate_total_amount_paise(
            travel_type=item["travel_type"],
            unit_fare_paise=item["unit_fare_paise"],
            passengers=item.get("passengers"),
            rooms=item.get("rooms"),
            check_in_str=item.get("travel_date"),
            check_out_str=item.get("check_out_date"),
        )
        item["total_amount_paise"] = total

    return samples


def seed_database(force: bool = False):
    """Inserts sample records into database."""
    print("=" * 60)
    print("TRAVEL BOOKING DATA ORGANIZER — SEED DATA SCRIPT")
    print("=" * 60)

    existing = get_all_bookings()
    if existing and not force:
        print(f"[NOTICE] Database already contains {len(existing)} bookings.")
        print("To overwrite or add records anyway, re-run with --force.")
        return

    sample_items = generate_sample_bookings()
    print(f"Preparing to seed {len(sample_items)} booking records...")

    user_info = {"email": "seed_admin@tripsync.local", "uid": "seed_admin"}
    created_count = 0

    for item in sample_items:
        created = create_booking(item, user_info)
        created_count += 1
        print(f"  [+] Created {created['booking_id']} | {created['customer_name']} | {created['travel_type'].upper()} -> {created['destination']}")

    print("=" * 60)
    print(f"[SUCCESS] Successfully seeded {created_count} bookings.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Travel Booking Data Organizer with sample records.")
    parser.add_argument("--force", action="store_true", help="Force insert sample records even if records exist")
    args = parser.parse_args()

    seed_database(force=args.force)
