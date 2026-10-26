# Frontend Browser QA Checklist — TRIPSYNC

Perform these checks against a local Flask server with Firestore configured or the deployed HTTPS URL (not a static file).

## Login and sessions
- Open `/login` in Chrome. No demo credentials/quick-fill buttons should appear.
- Valid Admin and Staff accounts can sign in through Firebase.
- Invalid credentials produce user-friendly errors; no secrets appear in browser logs.
- Refresh and navigate to dashboard without losing the session.
- Log out with POST; protected routes redirect to login.
- Rejected unauthorized Admin/Staff URLs do not expose records.

## Dashboard and reporting
- Open `/dashboard`; verify each metric from actual Firestore documents.
- Visit `/reports` as Admin; verify the six-month trend chart displays, including zero months.
- Check the category, payment and destination charts for real values.
- Filter `/bookings` by destination/status, click Export CSV and confirm only filtered records appear.

## Forms and booking state
- Add transport and hotel records; verify fare and nights calculations.
- Enter invalid amounts (`NaN`, negative values, excessive decimals) and verify errors.
- Create and edit bookings, verify source data stays immutable where required.
- As Staff, try to send `booking_status=Cancelled` to edit POST: should reject (400).
- As Admin, cancel a booking and confirm normal editing is denied thereafter.
- Disconnect database/network: operations should show an error, not pretend to save.

## Responsive + accessibility
- At widths 390px, 768px, 1024px and 1440px inspect `/login`, `/dashboard`, `/bookings`, `/bookings/new`, `/reports` and `/bookings/<id>/print`.
- Verify no unexpected horizontal page scrolling; booking table may scroll within its container.
- Verify navbar, sidebar drawer, form fields and modals are usable via keyboard and touch.
- Verify focus indicators, contrast and readable form errors.
- Verify tilt card transitions are subtle, and reduced-motion preference disables excessive movement.

## Voucher print
- Visit `/bookings/<id>/print`, choose Print and inspect A4 preview.
- Navigation and action controls must be hidden on paper; text must not be clipped.
- Ensure it is labeled as an internal voucher rather than an issued transport ticket.

## Final deployment
- Use HTTPS, verify both Admin and Staff logins, Firestore persistence and Render Secret Files.
- Inspect browser console/network errors and application server logs.
- Confirm `/healthz` is healthy and `/readyz` returns 200 only when client initialization succeeded.
