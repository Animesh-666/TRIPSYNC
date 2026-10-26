# TRIPSYNC — Phases A–D Combined Maintenance Update

**Scope:** The supplied TRIPSYNC Flask/Bootstrap/Firestore codebase.
**Result:** Updated project files, additional regression tests and an updated deployment blueprint.
**Cloud deployment:** Not performed; no production Firebase credentials were supplied.

## Phase A — Security corrections (implemented)

- Removed hardcoded Admin/Staff demo-password login paths and frontend Quick Demo Fill controls. Attempts to submit `demo_mode` now return HTTP 403.
- Used distinct cookie names: `flask_csrf_session` for Flask CSRF state and `tb_firebase_session` for Firebase authentication.
- Removed ordinary Flask-session authentication fallback outside explicitly configured `TESTING` mode. Firebase session creation failure now denies login with HTTP 503.
- Require recent Firebase ID-token authentication (at most five minutes) before session issuance.
- Reject missing, inactive or invalid-role Firestore users.
- Require production `SECRET_KEY` instead of a known default.
- Enforce cancelled booking restrictions at both Flask and database levels. Staff cannot bypass Admin-only cancellation by posting the edit form. Cancelled records cannot be reactivated through the standard edit route.
- Corrected Firebase browser persistence to `NONE` for the login flow.
- Updated setup instructions and CLI user provisioning examples to remove shared default passwords.

## Phase B — Backend reliability (implemented)

- Exact `Decimal` conversion rejects invalid, negative, non-finite and over-precise monetary values before converting them to integer paise.
- Booking creation now combines counter increment and document creation in one Firestore transaction.
- Booking updates and cancellations now run through Firestore transactions with status guards, avoiding ordinary update/cancel race conditions.
- In-memory storage is allowed only in explicit `TESTING` mode; production and normal development fail closed when Firestore is unavailable.
- Added a `/readyz` route (client initialization readiness only, not a live Firestore network transaction).
- User-facing create/edit errors no longer display raw exception contents; exceptions are logged server-side.

## Phase C — Reporting (implemented)

- Added a six-month active-booking creation trend, calculated by the existing services layer and rendered with Chart.js.
- Added consistent active-only chart labels and retained original accounting definitions: active booking value and balances exclude cancelled records, recorded collections include payments on cancelled records.
- CSV export now honors booking-list query filters. The list-page export link forwards active filters.
- Existing CSV formula-injection safeguards were retained.

## Phase D — Frontend verification (limited)

- All six major page templates — Login, Dashboard, Bookings, Add Booking, Reports, Printable Voucher — returned HTTP 200 using the Flask testing client and an in-memory fixture.
- Chromium rendered the generated HTML structure for all six templates at 1440x900 and 390x844: **12 DOM-render checks passed**.
- All project JavaScript files passed `node --check`, and Python files passed Python compilation checks.
- Existing Bootstrap/CSS/3D code was preserved and no frontend framework replacement was introduced.

**Limitations:** The review environment blocked Chromium navigation to the local Flask server. CDN assets were blocked during the standalone DOM checks. Therefore full visual styling, responsive overflow, 3D hover behavior, client-side Firebase login, live Chart.js rendering, voucher printing and cross-browser behavior were **not** verified end-to-end. Use the separate Frontend QA checklist before release.

## Tests performed

- 44 automated tests passed using a deliberately isolated Flask testing setup, with Firebase modules stubbed and the repository's pure-Python Flask/Werkzeug packages from the supplied Windows ZIP.
- This was **not** a live Firebase test and did not install the project's official full dependencies in a clean environment.
- A dedicated regression test checks that Firestore booking creation stages the counter update and booking creation in the same transaction (mock, not live transaction).

## Remaining release steps

1. Install requirements into a clean Python environment; execute `pytest -q tests` again.
2. Provision unique Firebase Auth accounts; test real browser login, session expiry and Staff/Admin permissions.
3. Run a Firestore integration test in a separate development Firebase project, including an intentionally failed transaction.
4. Verify desktop/mobile browser layouts with the CDN assets loaded, CSS animations, filter forms and responsive tables.
5. Complete Render deployment, inspect log warnings and test the live service over HTTPS.
6. Do not include `venv/`, `.env`, or `serviceAccountKey.json` in GitHub or any shared ZIP.

**Note:** The dashboard shows Cloud Firestore as its intended storage backend, not as proof of a successful live connection.
