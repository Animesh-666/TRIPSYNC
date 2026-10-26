# IT WORKSHOP MINI PROJECT REPORT
## Title: Travel Booking Data Organizer (TripSync)
### Academic Year: 2026-2027

---

## ABSTRACT

The **Travel Booking Data Organizer** is a centralized, cloud-backed web information system designed to record, categorize, retrieve, update, and analyze travel booking records across four transport and hospitality domains: Flights, Trains, Buses, and Hotels. Developed as an IT Workshop Mini Project, the platform addresses critical problems associated with traditional manual reservation tracking, including data duplication, calculation discrepancies, fragmented customer records, and lack of visibility into outstanding receivables.

The system is implemented using a full-stack Python Flask architecture integrated with Firebase Cloud Firestore for persistent document storage and Firebase Authentication for secure identity management. Role-Based Access Control (RBAC) enforces strict privilege boundaries between Administrators and Staff members. All monetary figures are computed and stored as integer paise to guarantee currency precision. A modern, responsive user interface incorporates subtle 3D CSS perspective transforms, animated KPI metrics, interactive Chart.js analytics, real-time calculation previews, countdown timers for upcoming journeys, and print-ready internal vouchers. Automated testing through Pytest achieves 100% pass rates across calculations, role security boundaries, and data export operations.

---

## 1. INTRODUCTION

Travel coordinators, small-to-medium agencies, and corporate travel desks manage large volumes of customer itineraries across heterogeneous travel modes. While booking engines exist for individual end-user ticketing, reservation coordinators require an internal management command center to record confirmed bookings, monitor payment schedules, maintain customer histories, track approaching departures, and generate standardized vouchers.

The Travel Booking Data Organizer (v1.0.0) provides a dedicated management portal combining lightweight Flask backend processing with Cloud Firestore's high-availability document storage.

---

## 2. PROBLEM STATEMENT

Manual and spreadsheet-based reservation management introduces severe operational bottlenecks:
1. **Data Fragmentation:** Customer details, ticket records, and hotel bookings stored across disparate spreadsheets or paper ledgers.
2. **Financial Inaccuracies:** Floating-point rounding errors and untracked partial payments lead to uncollected receivables.
3. **Lack of Operational Visibility:** Difficulty in identifying upcoming departures within 7 days, resulting in missed coordination deadlines.
4. **Weak Access Controls:** Spreadsheets lack granular permissions, allowing unauthorized staff to view financial reports, alter historical records, or accidentally delete documents.
5. **Inconsistent Customer Documentation:** Lack of standardized confirmation vouchers.

---

## 3. OBJECTIVES

The primary objectives of this project are:
- To design and implement a centralized, web-based travel reservation record repository.
- To support unified CRUD operations across Flights, Trains, Buses, and Hotels.
- To implement server-side Role-Based Access Control (Admin vs Staff).
- To automate monetary calculations using integer paise to eliminate floating-point rounding errors.
- To track received payments and dynamically derive payment states (Paid, Partially Paid, Unpaid).
- To detect upcoming journeys within a 7-day window and display intuitive countdown badges.
- To produce professional, printable A4 confirmation vouchers without third-party PDF dependencies.
- To visualize category distributions and payment status breakdowns using Chart.js.
- To provide secure, formula-injection-resistant CSV export for administrative analysis.

---

## 4. SYSTEM REQUIREMENTS

### 4.1 Hardware Requirements
- **Processor:** Dual-core 2.0 GHz or higher.
- **RAM:** 4 GB minimum (8 GB recommended).
- **Disk Storage:** 500 MB free disk space for application files and dependencies.
- **Display:** 1024x768 minimum resolution (fully responsive across mobile, tablet, and desktop).

### 4.2 Software Requirements
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Programming Language:** Python 3.10+ (Tested on Python 3.11 & 3.14).
- **Backend Framework:** Flask 3.1+.
- **Database & Auth:** Firebase Cloud Firestore & Firebase Authentication (via `firebase-admin` 7.7+).
- **Frontend Frameworks:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4.4.
- **Testing Framework:** Pytest 9.1+.
- **WSGI Production Server:** Gunicorn 21.2+.

---

## 5. SYSTEM ARCHITECTURE & MODULES

```
[Browser Client: HTML5/Bootstrap/JS] 
       | (HTTPS / CSRF-Protected JSON)
       v
[Flask Web Server (app.py, decorators.py, services.py)]
       | (Firebase Admin SDK)
       v
[Google Cloud Platform: Firestore Database & Firebase Auth]
```

### Module 1: Authentication & Role-Based Authorization
- Integrates Firebase Authentication (Email/Password) with server-side session cookies.
- Verifies ID tokens via Firebase Admin SDK and resolves authoritative roles from Firestore `/users/{uid}`.
- Enforces `@login_required` and `@admin_required` decorators across routes.

### Module 2: Booking Record Management (CRUD)
- Sequential ID generator assigning unique IDs (`TB-0001`, `TB-0002`...) via Firestore transactions.
- Category-adaptive forms showing transport fields (departure, destination, passengers) or hotel fields (hotel name, rooms, check-in, check-out, guests).
- Admin-controlled cancellation (soft status update) and permanent deletion.

### Module 3: Search, Filtering, and Sorting
- Case-insensitive search across Booking ID, Customer Name, Destination, and Contact.
- Multi-dimensional filtering by Category, Booking Status, Payment Status, Destination, and Date Range.
- Server-side sorting by Travel Date, Creation Date, Customer Name, and Total Amount.

### Module 4: Financial Calculations & Payment Tracking
- Transport Total: `Passengers × Fare per Passenger`.
- Hotel Total: `Rooms × Nights × Rate per Room per Night`.
- Derived States: Unpaid (Paid == 0), Partially Paid (0 < Paid < Total), Paid (Paid == Total).
- Integer paise representation prevents currency rounding defects.

### Module 5: Upcoming Journeys & Countdowns
- Evaluates bookings occurring between today and today + 7 days in `Asia/Kolkata` timezone.
- Assigns countdown labels: "Today", "Tomorrow", "In N days".

### Module 6: Printable Confirmation Vouchers
- Dedicated print stylesheet (`@media print`) hides navigation bars and interactive chrome.
- Formats customer, journey, and financial records onto a clean A4 voucher sheet with official disclaimer.

### Module 7 & 8: Analytics & Data Export
- Dashboard KPI cards and Chart.js visualizations (Category Doughnut, Payment Status, Top Destinations).
- Admin-only CSV export with defense against spreadsheet formula injection (`=, +, -, @`).

---

## 6. DATABASE DESIGN

The Cloud Firestore database structure is modeled as follows:

```
Firestore
├── users/
│   └── {uid}
│       ├── name: string
│       ├── email: string
│       ├── role: "admin" | "staff"
│       ├── active: boolean
│       ├── created_at: string (ISO 8601)
│       └── updated_at: string (ISO 8601)
│
├── bookings/
│   └── {booking_id}  (e.g., "TB-0001")
│       ├── booking_id: string
│       ├── customer_name: string
│       ├── contact: string (10-digit Indian format)
│       ├── travel_type: "flight" | "train" | "bus" | "hotel"
│       ├── source: string | null
│       ├── destination: string
│       ├── travel_date: string (YYYY-MM-DD)
│       ├── hotel_name: string | null
│       ├── check_out_date: string (YYYY-MM-DD) | null
│       ├── passengers: int | null
│       ├── rooms: int | null
│       ├── guests: int | null
│       ├── unit_fare_paise: int
│       ├── total_amount_paise: int
│       ├── amount_paid_paise: int
│       ├── booking_status: "Pending" | "Confirmed" | "Cancelled"
│       ├── created_by: string
│       ├── updated_by: string
│       ├── created_at: string (ISO 8601)
│       └── updated_at: string (ISO 8601)
│
└── counters/
    └── bookings
        └── next_sequence: int
```

---

## 7. TESTING & QUALITY ASSURANCE

Automated tests were written and executed using `pytest`. All 26 test cases passed without failures.

| Test Category | Number of Tests | Status | Description |
|---|---|---|---|
| Business Calculations | 8 | PASSED | Transport fares, hotel nights, paise conversion, balance, and payment status derivation |
| Input Validation | 4 | PASSED | Valid transport, invalid phone numbers, duplicate source/destination, invalid checkout dates |
| Access Control (RBAC) | 6 | PASSED | Unauthenticated redirects, admin privileges, staff restrictions (reports/csv/cancel/delete) |
| Booking Lifecycle | 5 | PASSED | Sequential ID generation, edit persistence, voucher rendering, cancellation, deletion |
| Reporting & Export | 3 | PASSED | KPI calculation, cancelled record exclusion, formula sanitization, CSV downloads |

---

## 8. CONCLUSION & FUTURE ENHANCEMENTS

The **Travel Booking Data Organizer** successfully delivers a robust, secure, and modern management platform tailored for travel record administration. By combining Python Flask with Firebase Cloud Firestore and enforcing secure session cookies with RBAC, the application achieves enterprise-grade reliability while remaining approachable for academic presentation and college viva evaluation.

### Future Enhancements:
- Direct PDF export via server-side headless Chromium.
- Automated email/SMS notification reminders to customers prior to departure.
- Integration of multi-currency support for international itineraries.
- Activity audit log viewer for administrators.
