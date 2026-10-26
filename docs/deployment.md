# RENDER PRODUCTION DEPLOYMENT GUIDE
## Travel Booking Data Organizer (TripSync) — v1.0.0

---

## 1. Overview

TripSync includes Render deployment configuration using **Python 3.11** and **Gunicorn WSGI**. You must configure production secrets and verify the live Firebase connection before considering the deployment complete.

The project includes:
- `render.yaml` — Blueprint infrastructure configuration.
- `.python-version` — Pinned to `3.11.9`.
- `requirements.txt` — Required dependencies. Install and verify compatible versions in your environment.
- `/healthz` — Process health endpoint (does not prove Firestore is reachable).
- `/readyz` — Reports whether a Firestore client initialized (not a full network probe).

---

## 2. Pre-Deployment Checklist

Before deploying, ensure you have:
1. Created a GitHub repository and committed the project files (ensure `.env` and `serviceAccountKey.json` are excluded via `.gitignore`).
2. Generated your `serviceAccountKey.json` from Firebase Console.
3. Created an account on [Render](https://render.com).

---

## 3. Deployment Steps via Render Dashboard

### Step 1: Create a New Web Service
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub account and select your repository (`tripsync` or `travel-booking-organizer`).

### Step 2: Configure Service Details
- **Name:** `travel-booking-organizer` (or your chosen name)
- **Region:** Singapore / Oregon / Frankfurt (select closest to your database)
- **Branch:** `main` (or `master`)
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  gunicorn app:app
  ```
- **Plan:** Free or Starter

### Step 3: Add Secret File (Firebase Credentials)
1. On the service configuration page, scroll down to the **Secret Files** section.
2. Click **Add Secret File**.
3. **Filename:** `serviceAccountKey.json`
4. **Contents:** Open your local `serviceAccountKey.json` file in a text editor, copy its entire contents, and paste them into the box.
5. Render will mount this file at `/etc/secrets/serviceAccountKey.json`.

### Step 4: Configure Environment Variables
In the **Environment Variables** section, add the following key-value pairs:

| Variable Name | Value | Purpose |
|---|---|---|
| `FLASK_ENV` | `production` | Enables production security mode |
| `PYTHON_VERSION` | `3.11.9` | Pins Python runtime |
| `SECRET_KEY` | *(Click 'Generate' on Render)* | Cryptographic session signing |
| `GOOGLE_APPLICATION_CREDENTIALS` | `/etc/secrets/serviceAccountKey.json` | Path to mounted secret file |
| `FIREBASE_PROJECT_ID` | `your-firebase-project-id` | Firebase project identifier |
| `FIREBASE_API_KEY` | `AIzaSy...` | Public web API key |
| `FIREBASE_AUTH_DOMAIN` | `your-project-id.firebaseapp.com` | Public auth domain |
| `FIREBASE_STORAGE_BUCKET` | `your-project-id.appspot.com` | Storage bucket |
| `FIREBASE_MESSAGING_SENDER_ID` | `123456789012` | Messaging sender ID |
| `FIREBASE_APP_ID` | `1:123456789012:web:abcdef` | Web App ID |

### Step 5: Deploy
Click **Create Web Service**. Render will clone the repository, install dependencies, mount the secret file, and start Gunicorn.

---

## 4. Post-Deployment Verification

### 1. Verify Health Endpoint
Visit your application URL:
```
https://<your-service-name>.onrender.com/healthz
```
Expected JSON Response:
```json
{
  "firebase_ready": true,
  "service": "travel-booking-organizer",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Add Domain to Firebase Authorized Domains
If using Firebase Authentication on the client:
1. In Firebase Console, go to **Authentication** -> **Settings** -> **Authorized domains**.
2. Click **Add domain**.
3. Enter your Render domain: `<your-service-name>.onrender.com`.
4. Click **Save**.

### 3. Verify Live Workflows
1. Log in with your provisioned Admin credentials.
2. Verify Dashboard KPI counts and charts.
3. Create a test booking and verify it receives a sequential `TB-XXXX` ID.
4. Verify the printable voucher view.
5. Download the CSV export from the Reports page.

---

## 5. Troubleshooting Common Deployment Issues

- **Build fails on gunicorn:** Ensure Render is using Linux (default) and Python 3.11+.
- **500 Error on login:** Check Render application logs for `FileNotFoundError: /etc/secrets/serviceAccountKey.json`. Ensure the secret file name and path match `GOOGLE_APPLICATION_CREDENTIALS`.
- **Firebase Auth Unauthorized Domain:** If client login displays `auth/unauthorized-domain`, add the Render `.onrender.com` domain to Firebase Authentication settings as shown in Section 4.2.
