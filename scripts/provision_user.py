"""
CLI Tool for Provisioning Admin and Staff Accounts.
Creates the user in Firebase Authentication and stores the role in Firestore 'users/{uid}'.

Usage:
    python scripts/provision_user.py --email admin@example.com --name "Administrator" --role admin
    python scripts/provision_user.py --email staff@example.com --name "Staff Member" --role staff
"""

import argparse
import getpass
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from auth import provision_user_account
from constants import ROLE_ADMIN, ROLE_STAFF, VALID_ROLES
from firebase_config import initialize_firebase, is_firebase_ready


def main():
    parser = argparse.ArgumentParser(description="Provision Admin or Staff user for Travel Booking Data Organizer.")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--password", help="Optional password; preferably omit to enter without shell-history exposure")
    parser.add_argument("--name", default="User", help="Display name")
    parser.add_argument("--role", default=ROLE_ADMIN, choices=VALID_ROLES, help="Role: admin or staff")

    args = parser.parse_args()

    password = args.password or getpass.getpass("Enter a new strong password for this user: ")
    if len(password) < 12:
        print("[ERROR] Password must be at least 12 characters long.")
        sys.exit(1)

    print(f"Connecting to Firebase...")
    app = initialize_firebase()
    if not is_firebase_ready():
        print("[WARNING] Firebase credentials not configured or Firestore unavailable.")
        print("Please verify GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_CREDENTIALS_JSON in .env.")
        sys.exit(1)

    try:
        user_doc = provision_user_account(
            email=args.email.strip().lower(),
            password=password,
            name=args.name.strip(),
            role=args.role,
        )
        print("=" * 60)
        print("[SUCCESS] User successfully provisioned!")
        print(f"  Name:  {user_doc.get('name')}")
        print(f"  Email: {user_doc.get('email')}")
        print(f"  Role:  {user_doc.get('role').upper()}")
        print(f"  Active: {user_doc.get('active')}")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Failed to provision user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
