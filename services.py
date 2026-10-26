"""
Business Logic and Domain Services for Travel Booking Data Organizer.
Encapsulates calculations, validations, filtering, reporting, and CSV generation.
"""

import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from collections import Counter
import io
import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
import zoneinfo

from constants import (
    APP_TIMEZONE,
    VALID_CATEGORIES,
    CATEGORY_FLIGHT,
    CATEGORY_TRAIN,
    CATEGORY_BUS,
    CATEGORY_HOTEL,
    VALID_BOOKING_STATUSES,
    STATUS_CONFIRMED,
    STATUS_CANCELLED,
    STATUS_PENDING,
    PAYMENT_PAID,
    PAYMENT_PARTIAL,
    PAYMENT_UNPAID,
    PHONE_REGEX,
    DEFAULT_PER_PAGE,
)


def get_current_kolkata_date() -> date:
    """Returns the current date in the configured Asia/Kolkata timezone."""
    try:
        tz = zoneinfo.ZoneInfo(APP_TIMEZONE)
        return datetime.now(tz).date()
    except Exception:
        # Fallback to local date if timezone data is unavailable
        return date.today()


def rupees_to_paise(rupees: float) -> int:
    """Converts a rupee float or int value to integer paise."""
    try:
        value = Decimal(str(rupees))
        if not value.is_finite() or value < 0 or value.as_tuple().exponent < -2:
            raise ValueError("Amount must be a non-negative number with at most two decimal places.")
        if value > Decimal("1000000000"):
            raise ValueError("Amount exceeds the permitted booking limit.")
        return int((value * 100).to_integral_exact())
    except (InvalidOperation, TypeError, OverflowError) as exc:
        raise ValueError("Enter a valid currency amount.") from exc


def paise_to_rupees(paise: int) -> float:
    """Converts integer paise to rupee float."""
    return round(paise / 100.0, 2)


def format_currency_inr(paise: int) -> str:
    """
    Formats an amount in paise to Indian Rupee format.
    Example: 12500000 paise -> ₹1,25,000.00
    """
    if paise is None:
        paise = 0
    rupees = paise / 100.0
    is_negative = rupees < 0
    rupees = abs(rupees)
    
    parts = f"{rupees:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    # Indian number grouping: last 3 digits, then groups of 2 digits
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last_three
    else:
        formatted_int = integer_part

    sign = "-" if is_negative else ""
    return f"{sign}₹{formatted_int}.{decimal_part}"


def calculate_nights(check_in_str: str, check_out_str: str) -> int:
    """Calculates number of nights between two ISO YYYY-MM-DD dates."""
    check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
    check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
    delta = (check_out - check_in).days
    if delta < 1:
        raise ValueError("Check-out must be after check-in.")
    return delta


def calculate_total_amount_paise(
    travel_type: str,
    unit_fare_paise: int,
    passengers: Optional[int] = None,
    rooms: Optional[int] = None,
    check_in_str: Optional[str] = None,
    check_out_str: Optional[str] = None,
) -> int:
    """
    Authoritative server-side calculation for booking total in paise.
    Transport: passengers * unit_fare_paise
    Hotel: rooms * nights * unit_fare_paise
    """
    if not isinstance(unit_fare_paise, int) or isinstance(unit_fare_paise, bool):
        raise ValueError("Fare must be represented in integer paise.")
    if unit_fare_paise < 0:
        raise ValueError("Unit fare cannot be negative.")

    if travel_type in (CATEGORY_FLIGHT, CATEGORY_TRAIN, CATEGORY_BUS):
        p_count = int(passengers if passengers is not None else 1)
        if p_count < 1:
            raise ValueError("Passenger count must be at least 1.")
        return p_count * unit_fare_paise

    elif travel_type == CATEGORY_HOTEL:
        r_count = int(rooms if rooms is not None else 1)
        if r_count < 1:
            raise ValueError("Room count must be at least 1.")
        if not check_in_str or not check_out_str:
            raise ValueError("Check-in and Check-out dates are required for hotel bookings.")
        nights = calculate_nights(check_in_str, check_out_str)
        return r_count * nights * unit_fare_paise

    raise ValueError(f"Unsupported travel category: {travel_type}")


def derive_payment_status(total_amount_paise: int, amount_paid_paise: int) -> str:
    """
    Derives payment status according to business rules:
    - Unpaid: Amount paid == 0
    - Partially Paid: 0 < Amount paid < Total
    - Paid: Amount paid == Total
    """
    if amount_paid_paise <= 0:
        return PAYMENT_UNPAID
    if amount_paid_paise >= total_amount_paise:
        return PAYMENT_PAID
    return PAYMENT_PARTIAL


def calculate_outstanding_balance_paise(total_amount_paise: int, amount_paid_paise: int) -> int:
    """Calculates outstanding balance in paise."""
    return max(0, total_amount_paise - amount_paid_paise)


def validate_booking_input(form_data: Dict[str, Any], is_edit: bool = False) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Strict server-side validation of booking form data.
    Returns (cleaned_data, errors_dict).
    """
    cleaned: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    # Customer Name
    customer_name = str(form_data.get("customer_name", "")).strip()
    if not customer_name:
        errors["customer_name"] = "Customer name is required."
    elif len(customer_name) < 2 or len(customer_name) > 100:
        errors["customer_name"] = "Customer name must be between 2 and 100 characters."
    cleaned["customer_name"] = customer_name

    # Contact Number (10 digits Indian format)
    contact = str(form_data.get("contact", "")).strip().replace(" ", "").replace("-", "")
    if not contact:
        errors["contact"] = "Contact number is required."
    elif not re.match(PHONE_REGEX, contact):
        errors["contact"] = "Enter a valid 10-digit Indian mobile number (e.g., 9876543210)."
    cleaned["contact"] = contact

    # Travel Category
    travel_type = str(form_data.get("travel_type", "")).strip().lower()
    if travel_type not in VALID_CATEGORIES:
        errors["travel_type"] = f"Invalid travel category. Must be one of: {', '.join(VALID_CATEGORIES)}."
    cleaned["travel_type"] = travel_type

    # Travel / Check-in Date
    travel_date_str = str(form_data.get("travel_date", "")).strip()
    travel_date_obj: Optional[date] = None
    if not travel_date_str:
        errors["travel_date"] = "Travel or check-in date is required."
    else:
        try:
            travel_date_obj = datetime.strptime(travel_date_str, "%Y-%m-%d").date()
            today_kolkata = get_current_kolkata_date()
            if not is_edit and travel_date_obj < today_kolkata:
                errors["travel_date"] = "Travel date cannot be in the past."
            cleaned["travel_date"] = travel_date_str
        except ValueError:
            errors["travel_date"] = "Travel date must be in YYYY-MM-DD format."

    # Booking Status
    booking_status = str(form_data.get("booking_status", STATUS_CONFIRMED)).strip()
    if booking_status not in VALID_BOOKING_STATUSES:
        errors["booking_status"] = "Choose a valid booking status."
        booking_status = STATUS_CONFIRMED
    cleaned["booking_status"] = booking_status

    # Parse exact decimal money values; reject NaN, infinity and excess precision.
    try:
        cleaned["unit_fare_paise"] = rupees_to_paise(form_data.get("unit_fare", 0))
    except (ValueError, TypeError, OverflowError):
        errors["unit_fare"] = "Enter a valid numeric fare amount."
        cleaned["unit_fare_paise"] = 0

    # Category Specific Validations
    if travel_type in (CATEGORY_FLIGHT, CATEGORY_TRAIN, CATEGORY_BUS):
        source = str(form_data.get("source", "")).strip()
        destination = str(form_data.get("destination", "")).strip()

        if not source:
            errors["source"] = "Departure location is required."
        if not destination:
            errors["destination"] = "Destination is required."
        if source and destination and source.lower() == destination.lower():
            errors["destination"] = "Departure location and destination cannot be identical."

        cleaned["source"] = source
        cleaned["destination"] = destination
        cleaned["hotel_name"] = None
        cleaned["check_out_date"] = None
        cleaned["rooms"] = None
        cleaned["guests"] = None

        try:
            passengers = int(form_data.get("passengers", 1))
            if passengers < 1 or passengers > 50:
                errors["passengers"] = "Passengers count must be between 1 and 50."
            cleaned["passengers"] = passengers
        except (ValueError, TypeError):
            errors["passengers"] = "Passengers count must be a positive number."
            cleaned["passengers"] = 1

    elif travel_type == CATEGORY_HOTEL:
        hotel_name = str(form_data.get("hotel_name", "")).strip()
        hotel_location = str(form_data.get("destination", "")).strip()
        check_out_str = str(form_data.get("check_out_date", "")).strip()

        if not hotel_name:
            errors["hotel_name"] = "Hotel name is required."
        if not hotel_location:
            errors["destination"] = "Hotel location / city is required."

        cleaned["hotel_name"] = hotel_name
        cleaned["destination"] = hotel_location
        cleaned["source"] = None
        cleaned["passengers"] = None

        if not check_out_str:
            errors["check_out_date"] = "Check-out date is required."
        else:
            try:
                check_out_obj = datetime.strptime(check_out_str, "%Y-%m-%d").date()
                cleaned["check_out_date"] = check_out_str
                if travel_date_obj and check_out_obj <= travel_date_obj:
                    errors["check_out_date"] = "Check-out date must be after check-in date."
            except ValueError:
                errors["check_out_date"] = "Check-out date must be in YYYY-MM-DD format."

        try:
            rooms = int(form_data.get("rooms", 1))
            if rooms < 1 or rooms > 20:
                errors["rooms"] = "Room count must be between 1 and 20."
            cleaned["rooms"] = rooms
        except (ValueError, TypeError):
            errors["rooms"] = "Room count must be a positive integer."
            cleaned["rooms"] = 1

        try:
            guests = int(form_data.get("guests", 1))
            if guests < 1 or guests > 50:
                errors["guests"] = "Guest count must be between 1 and 50."
            cleaned["guests"] = guests
        except (ValueError, TypeError):
            errors["guests"] = "Guest count must be a positive integer."
            cleaned["guests"] = 1

    # Total Amount Calculation
    if not errors:
        try:
            total_paise = calculate_total_amount_paise(
                travel_type=cleaned["travel_type"],
                unit_fare_paise=cleaned["unit_fare_paise"],
                passengers=cleaned.get("passengers"),
                rooms=cleaned.get("rooms"),
                check_in_str=cleaned.get("travel_date"),
                check_out_str=cleaned.get("check_out_date"),
            )
            cleaned["total_amount_paise"] = total_paise
        except ValueError as ve:
            errors["calculation"] = str(ve)
            cleaned["total_amount_paise"] = 0
    else:
        cleaned["total_amount_paise"] = 0

    # Amount Paid in Rupees -> Paise
    try:
        paid_paise = rupees_to_paise(form_data.get("amount_paid", 0))

        if not errors and paid_paise > cleaned["total_amount_paise"]:
            errors["amount_paid"] = (
                f"Amount paid ({format_currency_inr(paid_paise)}) cannot exceed total amount "
                f"({format_currency_inr(cleaned['total_amount_paise'])})."
            )
        cleaned["amount_paid_paise"] = paid_paise
    except (ValueError, TypeError):
        errors["amount_paid"] = "Enter a valid numeric paid amount."
        cleaned["amount_paid_paise"] = 0

    return cleaned, errors


def enrich_booking(booking: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches raw booking document with derived presentation properties:
    - payment_status
    - outstanding_balance_paise
    - formatted rupee strings
    - countdown labels
    - readable dates
    """
    b = dict(booking)
    total_paise = int(b.get("total_amount_paise", 0))
    paid_paise = int(b.get("amount_paid_paise", 0))

    b["payment_status"] = derive_payment_status(total_paise, paid_paise)
    b["outstanding_balance_paise"] = calculate_outstanding_balance_paise(total_paise, paid_paise)

    b["formatted_total"] = format_currency_inr(total_paise)
    b["formatted_paid"] = format_currency_inr(paid_paise)
    b["formatted_balance"] = format_currency_inr(b["outstanding_balance_paise"])
    b["formatted_unit_fare"] = format_currency_inr(int(b.get("unit_fare_paise", 0)))

    # Countdown computation
    travel_date_str = b.get("travel_date")
    if travel_date_str:
        try:
            travel_d = datetime.strptime(travel_date_str, "%Y-%m-%d").date()
            today_d = get_current_kolkata_date()
            diff_days = (travel_d - today_d).days
            b["days_until"] = diff_days

            if diff_days < 0:
                b["countdown_label"] = f"{abs(diff_days)} day{'s' if abs(diff_days) > 1 else ''} ago"
                b["countdown_badge"] = "badge-past"
            elif diff_days == 0:
                b["countdown_label"] = "Today"
                b["countdown_badge"] = "badge-today"
            elif diff_days == 1:
                b["countdown_label"] = "Tomorrow"
                b["countdown_badge"] = "badge-tomorrow"
            else:
                b["countdown_label"] = f"In {diff_days} days"
                b["countdown_badge"] = "badge-upcoming"
        except ValueError:
            b["days_until"] = None
            b["countdown_label"] = "Date Unknown"
            b["countdown_badge"] = "badge-secondary"
    else:
        b["days_until"] = None
        b["countdown_label"] = "N/A"
        b["countdown_badge"] = "badge-secondary"

    return b


def filter_and_sort_bookings(
    bookings: List[Dict[str, Any]],
    search_query: Optional[str] = None,
    category: Optional[str] = None,
    booking_status: Optional[str] = None,
    payment_status: Optional[str] = None,
    destination: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = "travel_date",
    sort_dir: Optional[str] = "asc",
) -> List[Dict[str, Any]]:
    """
    Filters and sorts booking list based on query parameters.
    Search is case-insensitive across booking ID, customer name, destination, contact.
    """
    enriched = [enrich_booking(b) for b in bookings]
    filtered = []

    search_term = search_query.strip().lower() if search_query else None

    for b in enriched:
        # Search query check
        if search_term:
            matches_search = (
                search_term in str(b.get("booking_id", "")).lower() or
                search_term in str(b.get("customer_name", "")).lower() or
                search_term in str(b.get("destination", "")).lower() or
                search_term in str(b.get("contact", "")).lower() or
                search_term in str(b.get("hotel_name", "") or "").lower() or
                search_term in str(b.get("source", "") or "").lower()
            )
            if not matches_search:
                continue

        # Category filter
        if category and category != "all" and b.get("travel_type") != category:
            continue

        # Booking Status filter
        if booking_status and booking_status != "all" and b.get("booking_status") != booking_status:
            continue

        # Payment Status filter
        if payment_status and payment_status != "all" and b.get("payment_status") != payment_status:
            continue

        # Destination filter
        if destination and destination != "all" and str(b.get("destination", "")).lower() != destination.lower():
            continue

        # Date range filter
        travel_date_val = b.get("travel_date")
        if travel_date_val:
            if start_date and travel_date_val < start_date:
                continue
            if end_date and travel_date_val > end_date:
                continue

        filtered.append(b)

    # Sorting
    reverse = (sort_dir or "asc").lower() == "desc"

    def sort_key(item):
        if sort_by == "created_at":
            return item.get("created_at") or ""
        elif sort_by == "customer_name":
            return str(item.get("customer_name", "")).lower()
        elif sort_by == "total_amount":
            return int(item.get("total_amount_paise", 0))
        elif sort_by == "destination":
            return str(item.get("destination", "")).lower()
        # Default to travel_date
        return item.get("travel_date") or ""

    filtered.sort(key=sort_key, reverse=reverse)
    return filtered


def paginate_items(items: List[Any], page: int = 1, per_page: int = DEFAULT_PER_PAGE) -> Tuple[List[Any], Dict[str, Any]]:
    """Paginates a list of items."""
    page = max(1, page)
    per_page = max(1, min(per_page, 100))
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated = items[start_idx:end_idx]

    pagination = {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }
    return paginated, pagination


def get_upcoming_trips(bookings: List[Dict[str, Any]], days_window: int = 7) -> List[Dict[str, Any]]:
    """
    Returns upcoming active (non-cancelled) trips occurring within the next N days (default 7).
    Sorted by travel date ascending.
    """
    enriched = [enrich_booking(b) for b in bookings]
    today = get_current_kolkata_date()
    max_date = today + timedelta(days=days_window)

    upcoming = []
    for b in enriched:
        if b.get("booking_status") == STATUS_CANCELLED:
            continue

        travel_date_str = b.get("travel_date")
        if not travel_date_str:
            continue

        try:
            travel_d = datetime.strptime(travel_date_str, "%Y-%m-%d").date()
            if today <= travel_d <= max_date:
                upcoming.append(b)
        except ValueError:
            continue

    upcoming.sort(key=lambda x: x.get("travel_date", ""))
    return upcoming


def calculate_dashboard_metrics(bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates summary KPI cards and reporting figures from real Firestore records.
    Explicitly distinguishes:
    - Active Booking Value
    - Recorded Payments
    - Pending Balances (active only)
    """
    enriched = [enrich_booking(b) for b in bookings]

    total_all_bookings = len(enriched)
    active_bookings = [b for b in enriched if b.get("booking_status") != STATUS_CANCELLED]
    cancelled_bookings = [b for b in enriched if b.get("booking_status") == STATUS_CANCELLED]
    confirmed_bookings = [b for b in enriched if b.get("booking_status") == STATUS_CONFIRMED]

    upcoming = get_upcoming_trips(bookings, days_window=7)

    # Active value (excludes cancelled bookings)
    active_booking_value_paise = sum(int(b.get("total_amount_paise", 0)) for b in active_bookings)
    
    # Total recorded payments collected (sum of amount_paid across all bookings)
    total_recorded_payments_paise = sum(int(b.get("amount_paid_paise", 0)) for b in enriched)

    # Outstanding pending balance for active bookings only
    active_outstanding_balance_paise = sum(int(b.get("outstanding_balance_paise", 0)) for b in active_bookings)

    # Category distribution
    categories_count: Dict[str, int] = {cat: 0 for cat in VALID_CATEGORIES}
    for b in active_bookings:
        cat = b.get("travel_type")
        if cat in categories_count:
            categories_count[cat] += 1

    # Payment status distribution (active)
    payment_status_count: Dict[str, int] = {
        PAYMENT_PAID: 0,
        PAYMENT_PARTIAL: 0,
        PAYMENT_UNPAID: 0,
    }
    for b in active_bookings:
        p_stat = b.get("payment_status")
        if p_stat in payment_status_count:
            payment_status_count[p_stat] += 1

    # Top destinations
    dest_counts: Dict[str, int] = {}
    for b in active_bookings:
        dest = b.get("destination")
        if dest:
            dest_counts[dest] = dest_counts.get(dest, 0) + 1
    top_destinations = sorted(dest_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Monthly trend: last six calendar months, based on creation date.
    # Cancelled reservations are intentionally excluded, matching category KPIs.
    today = get_current_kolkata_date()
    monthly_keys = []
    for offset in range(5, -1, -1):
        year = today.year
        month = today.month - offset
        while month < 1:
            month += 12
            year -= 1
        monthly_keys.append(f"{year:04d}-{month:02d}")
    month_counter = Counter()
    for booking in active_bookings:
        created = booking.get("created_at")
        if isinstance(created, datetime):
            key = created.strftime("%Y-%m")
        elif isinstance(created, str) and len(created) >= 7:
            key = created[:7]
        else:
            continue
        if key in monthly_keys:
            month_counter[key] += 1
    monthly_booking_counts = [month_counter[key] for key in monthly_keys]
    monthly_labels = [datetime.strptime(key, "%Y-%m").strftime("%b %Y") for key in monthly_keys]

    return {
        "monthly_labels": monthly_labels,
        "monthly_booking_counts": monthly_booking_counts,
        "total_active_bookings": len(active_bookings),
        "confirmed_bookings": len(confirmed_bookings),
        "cancelled_bookings": len(cancelled_bookings),
        "total_all_bookings": total_all_bookings,
        "upcoming_trips_count": len(upcoming),
        "active_booking_value_paise": active_booking_value_paise,
        "formatted_active_value": format_currency_inr(active_booking_value_paise),
        "recorded_payments_paise": total_recorded_payments_paise,
        "formatted_recorded_payments": format_currency_inr(total_recorded_payments_paise),
        "outstanding_balance_paise": active_outstanding_balance_paise,
        "formatted_outstanding_balance": format_currency_inr(active_outstanding_balance_paise),
        "category_counts": categories_count,
        "payment_status_counts": payment_status_count,
        "top_destinations": top_destinations,
    }


def sanitize_csv_field(value: Any) -> str:
    """
    Guards against CSV / Spreadsheet formula injection.
    Prefixes values starting with '=', '+', '-', '@' with a single quote.
    """
    if value is None:
        return ""
    val_str = str(value).strip()
    if val_str and val_str[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val_str}"
    return val_str


def generate_bookings_csv(bookings: List[Dict[str, Any]]) -> str:
    """
    Generates a secure, well-structured CSV string of bookings.
    Includes proper UTF-8 BOM encoding for Excel.
    """
    enriched = [enrich_booking(b) for b in bookings]
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    headers = [
        "Booking ID",
        "Customer Name",
        "Contact",
        "Category",
        "Departure / Details",
        "Destination",
        "Travel / Check-in Date",
        "Check-out Date",
        "Quantity (Pax/Rooms)",
        "Unit Fare (INR)",
        "Total Amount (INR)",
        "Amount Paid (INR)",
        "Outstanding Balance (INR)",
        "Payment Status",
        "Booking Status",
        "Created At",
    ]
    writer.writerow(headers)

    for b in enriched:
        category = b.get("travel_type", "")
        qty = b.get("passengers") if category in (CATEGORY_FLIGHT, CATEGORY_TRAIN, CATEGORY_BUS) else b.get("rooms", "")
        detail = b.get("source", "") if category != CATEGORY_HOTEL else b.get("hotel_name", "")

        row = [
            sanitize_csv_field(b.get("booking_id")),
            sanitize_csv_field(b.get("customer_name")),
            sanitize_csv_field(b.get("contact")),
            sanitize_csv_field(category.capitalize()),
            sanitize_csv_field(detail),
            sanitize_csv_field(b.get("destination")),
            sanitize_csv_field(b.get("travel_date")),
            sanitize_csv_field(b.get("check_out_date") or "N/A"),
            sanitize_csv_field(qty),
            paise_to_rupees(int(b.get("unit_fare_paise", 0))),
            paise_to_rupees(int(b.get("total_amount_paise", 0))),
            paise_to_rupees(int(b.get("amount_paid_paise", 0))),
            paise_to_rupees(int(b.get("outstanding_balance_paise", 0))),
            sanitize_csv_field(b.get("payment_status")),
            sanitize_csv_field(b.get("booking_status")),
            sanitize_csv_field(b.get("created_at")),
        ]
        writer.writerow(row)

    return output.getvalue()
