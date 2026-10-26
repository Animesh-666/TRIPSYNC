# FIREBASE CONFIGURATION GUIDE
## Travel Booking Data Organizer (TripSync) — v1.0.0

---

## 1. Firebase Project Creation

1. Navigate to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project** (or **Create a project**).
3. Enter a project name (e.g. `tripsync-organizer`).
4. Disable Google Analytics (optional, not required for this project).
5. Click **Create project** and wait for provisioning to complete.

---

## 2. Enable Firebase Authentication

1. In the Firebase Console left sidebar, click **Build** -> **Authentication**.
2. Click **Get Started**.
3. Under the **Sign-in method** tab, click **Email/Password**.
4. Enable **Email/Password** (keep "Email link (passwordless sign-in)" disabled).
5. Click **Save**.

---

## 3. Enable Cloud Firestore Database

1. In the Firebase Console sidebar, click **Build** -> **Firestore Database**.
2. Click **Create database**.
3. Choose a database location close to your users (e.g., `asia-south1` for Mumbai).
4. Start in **Production mode**; do not use permissive Test mode rules for a deployed application.
5. Click **Create**.

### Recommended Firestore Security Rules
Because the application uses the **Firebase Admin SDK on the Flask server** for all database reads and writes, direct client access to Firestore can be safely blocked:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Deny direct read and write from client-side JavaScript SDK
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

---

## 4. Obtain Server Admin Credentials (Service Account Key)

1. In the Firebase Console, click the **Gear icon (Project settings)** in the top left.
2. Select the **Service accounts** tab.
3. Verify that **Python** is selected.
4. Click **Generate new private key**, then confirm by clicking **Generate key**.
5. A JSON file will download (e.g. `tripsync-organizer-firebase-adminsdk-xxxxx.json`).
6. **Rename this file** to `serviceAccountKey.json` and place it in the project root directory (`./serviceAccountKey.json`).
7. **IMPORTANT:** Ensure `serviceAccountKey.json` is listed in `.gitignore` (already configured) so it is never committed to GitHub.

---

## 5. Obtain Public Web Client Configuration

1. In the Firebase Console, go to **Project settings** -> **General** tab.
2. Under **Your apps**, click the **Web icon (`</>`)**.
3. Register the app with nickname `tripsync-web`.
4. Copy the values from the `firebaseConfig` object and place them in your `.env` file:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789012
FIREBASE_APP_ID=1:123456789012:web:abcdef123456
GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json
```

---

## 6. Provision Initial Admin and Staff Accounts

Run the provisioning script to create user credentials in Firebase Auth and set their roles in Firestore:

```bash
# Activate your virtual environment
.\venv\Scripts\activate

# 1. Provision Administrator
python scripts/provision_user.py --email admin@example.com --password "<STRONG_PRIVATE_PASSWORD>" --name "Administrator" --role admin

# 2. Provision Staff Member
python scripts/provision_user.py --email staff@example.com --password "<DIFFERENT_STRONG_PASSWORD>" --name "Staff Member" --role staff
```

---

## 7. Seed Demonstration Records

Populate the Firestore database with 25 fictional Indian travel bookings across all categories:

```bash
python seed_data.py --force
```

**Security:** Use addresses you control and unique passwords. CLI arguments may appear in your local shell history/process list; for stronger security, use a prompt-based secret input rather than command-line passwords. Never share service-account JSON.
