"""
Application Constants for Travel Booking Data Organizer.
Centralizes enums, regexes, timezones, and system defaults.
"""

# User Roles
ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"
VALID_ROLES = [ROLE_ADMIN, ROLE_STAFF]

# Travel Categories
CATEGORY_FLIGHT = "flight"
CATEGORY_TRAIN = "train"
CATEGORY_BUS = "bus"
CATEGORY_HOTEL = "hotel"
VALID_CATEGORIES = [CATEGORY_FLIGHT, CATEGORY_TRAIN, CATEGORY_BUS, CATEGORY_HOTEL]

CATEGORY_LABELS = {
    CATEGORY_FLIGHT: "Flight",
    CATEGORY_TRAIN: "Train",
    CATEGORY_BUS: "Bus",
    CATEGORY_HOTEL: "Hotel",
}

CATEGORY_ICONS = {
    CATEGORY_FLIGHT: "bi-airplane-engines",
    CATEGORY_TRAIN: "bi-train-front",
    CATEGORY_BUS: "bi-bus-front",
    CATEGORY_HOTEL: "bi-building",
}

# Booking Statuses
STATUS_PENDING = "Pending"
STATUS_CONFIRMED = "Confirmed"
STATUS_CANCELLED = "Cancelled"
VALID_BOOKING_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_CANCELLED]

# Payment Statuses (Derived)
PAYMENT_UNPAID = "Unpaid"
PAYMENT_PARTIAL = "Partially Paid"
PAYMENT_PAID = "Paid"
VALID_PAYMENT_STATUSES = [PAYMENT_UNPAID, PAYMENT_PARTIAL, PAYMENT_PAID]

# Application Timezone
APP_TIMEZONE = "Asia/Kolkata"

# Pagination Defaults
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 50

# Regex Patterns
PHONE_REGEX = r"^[6-9]\d{9}$"
BOOKING_ID_PREFIX = "TB-"
BOOKING_ID_REGEX = r"^TB-\d{4,}$"

# Standard Indian Travel Destinations
STANDARD_DESTINATIONS = [
    "Bengaluru",
    "Chennai",
    "Darjeeling",
    "Delhi",
    "Goa",
    "Hyderabad",
    "Jaipur",
    "Kolkata",
    "Mumbai",
    "Shimla",
    "Varanasi",
    "Udaipur",
    "Kochi",
    "Agra",
    "Pune",
]
