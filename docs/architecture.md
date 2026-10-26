# SYSTEM ARCHITECTURE DOCUMENTATION
## Travel Booking Data Organizer (TripSync) — v1.0.0

---

## 1. Architectural Overview

The **Travel Booking Data Organizer** is designed following a modular, layered architecture that strictly separates presentation, controller routing, domain business logic, data persistence, and identity security.

```
+-----------------------------------------------------------------------+
|                         PRESENTATION LAYER                            |
|  - HTML5 & Jinja2 Templates (Responsive layout, Mobile drawer)       |
|  - Bootstrap 5 & CSS3 Design System (Deep Navy / Teal / 3D tilt)      |
|  - Vanilla JavaScript & ES Modules (Forms, Live calculations, Modals) |
|  - Chart.js (Interactive Category & Payment analytics)                |
+-----------------------------------▲-----------------------------------+
                                    │ HTTPS (HTTP POST / GET / JSON)
                                    ▼
+-----------------------------------------------------------------------+
|                          FLASK APPLICATION LAYER                      |
|  - app.py: WSGI entrypoint, Routing, Context processors, Error pages  |
|  - decorators.py: RBAC (@admin_required, @login_required), CSRF guard  |
|  - services.py: Validation, Integer paise calculations, Filters, CSV  |
+-----------------------------------▲-----------------------------------+
                                    │ Python Admin SDK calls
                                    ▼
+-----------------------------------------------------------------------+
|                    FIREBASE INTEGRATION & SECURITY                    |
|  - firebase_config.py: Secure credential loader (File / JSON / ADC)   |
|  - auth.py: ID token verification, Session cookie minting & revoking  |
|  - database.py: Firestore collection operations & Transactions        |
+-----------------------------------▲-----------------------------------+
                                    │ Google Cloud API (gRPC / HTTPS)
                                    ▼
+-----------------------------------------------------------------------+
|                           PERSISTENCE LAYER                           |
|  - Firebase Cloud Firestore:                                          |
|      * /users/{uid}        -> Profile, Role (admin/staff), Active      |
|      * /bookings/{id}      -> Booking documents (TB-0001...)          |
|      * /counters/bookings  -> Sequential ID sequence generator       |
|  - Firebase Authentication: Identity provider & Token issuer          |
+-----------------------------------------------------------------------+
```

---

## 2. Key Architectural Decisions

### 2.1 Integer Paise Currency Architecture
Floating-point arithmetic in software introduces precision errors (e.g. `0.1 + 0.2 = 0.30000000000000004`). In financial record keeping, monetary amounts must be stored and computed as **integers in the smallest currency unit (paise)**:
- Stored fields: `unit_fare_paise`, `total_amount_paise`, `amount_paid_paise`.
- Conversion: `rupees_to_paise(rupees)` and `paise_to_rupees(paise)`.
- Derived fields: `outstanding_balance_paise = max(0, total_amount_paise - amount_paid_paise)`.
- Presentation: Formatted with Indian numerical grouping (`₹1,25,000.00`).

### 2.2 Transactional Sequential Booking ID Generation
Rather than relying on client timestamps or document counts (which collide under concurrent submissions), IDs are generated using a **Cloud Firestore Transaction** on document `/counters/bookings`:
- The transaction reads the current sequence number atomically.
- Increments `next_sequence` by 1.
- Formats the resulting integer into `TB-XXXX` (e.g., `TB-0001`, `TB-0002`).
- Deletions never decrement or reuse numbers.

### 2.3 Server-Side Role-Based Access Control (RBAC)
Role assignment is never trusted from the client or embedded in unverified tokens:
1. Client logs in with Firebase Authentication (Email/Password) and obtains a signed Firebase ID Token.
2. The ID token is transmitted to Flask route `/session/login` via CSRF-protected POST.
3. The server validates the token using `firebase_admin.auth.verify_id_token(id_token, check_revoked=True)`.
4. The server queries Firestore document `/users/{uid}` to look up the authoritative role (`admin` or `staff`) and the `active` status.
5. Inactive or unprovisioned users are rejected immediately with HTTP 401.
6. A session cookie is issued with `HttpOnly`, `SameSite=Lax`, and `Secure` (in production).
7. Mutating admin endpoints (`/reports`, `/export/csv`, `/bookings/<id>/cancel`, `/bookings/<id>/delete`) strictly enforce `@admin_required`.

---

## 3. Module Responsibilities

| Module | Primary Responsibility |
|---|---|
| `app.py` | Flask application factory, route definitions, error handlers, and WSGI export. |
| `config.py` | Environment variable parsing, session policies, Firebase credentials path. |
| `constants.py` | Role definitions, valid categories, statuses, Indian destinations, and regexes. |
| `firebase_config.py` | Thread-safe Firebase Admin SDK initialization with multi-source credential loading. |
| `auth.py` | Server-side Firebase ID token verification, session cookies, user provisioning. |
| `decorators.py` | `@login_required`, `@admin_required`, and CSRF protection interceptors. |
| `database.py` | Firestore CRUD operations, atomic sequential ID transactions, explicit pytest-only in-memory test repository (production fails closed). |
| `services.py` | Server-side validation, money calculations, filtering, countdowns, CSV export. |
| `seed_data.py` | Safe, explicit seeding script with 25 diverse Indian travel booking records. |
