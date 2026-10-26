"""
Database Layer for Travel Booking Data Organizer.
Encapsulates all Firestore database operations, transactions, and sequential ID generation.
"""

from datetime import datetime, timezone
from flask import has_app_context, current_app
import logging
from typing import Dict, Any, List, Optional
try:
    from google.cloud import firestore
except Exception:
    firestore = None
from firebase_config import get_db, is_firebase_ready
from constants import (
    BOOKING_ID_PREFIX,
    STATUS_CANCELLED,
    ROLE_STAFF,
)

logger = logging.getLogger(__name__)

# In-memory store used exclusively in an explicitly configured testing application.
_MEM_COUNTERS: Dict[str, int] = {"bookings": 1}
_MEM_BOOKINGS: Dict[str, Dict[str, Any]] = {}
_MEM_USERS: Dict[str, Dict[str, Any]] = {}


def _get_database_or_test_memory():
    """Use memory *only* in an explicitly configured pytest application.

    Production and normal development must never pretend an unavailable
    Firestore database is persistent storage.
    """
    if has_app_context() and current_app.config.get("TESTING") and current_app.config.get("ALLOW_IN_MEMORY_DB"):
        return None
    db = get_db()
    if db is None:
        raise RuntimeError("Firestore is unavailable; booking data was not saved.")
    return db


def _get_utc_now():
    """Returns current UTC datetime."""
    return datetime.now(timezone.utc)


def _format_booking_id(sequence_num: int) -> str:
    """Formats an integer sequence number as TB-0001, TB-0002, etc."""
    return f"{BOOKING_ID_PREFIX}{sequence_num:04d}"


def create_booking(booking_data: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Atomically allocate an ID and create its Firestore document.

    The counter increment and document write either commit together or both
    roll back. A failed write cannot leave a misleading successful booking.
    """
    db = _get_database_or_test_memory()
    now = _get_utc_now()
    user_identifier = user_info.get("email") or user_info.get("uid") or "system"
    doc_data = dict(booking_data)
    doc_data.update({
        "created_by": user_identifier,
        "updated_by": user_identifier,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    })

    if db is None:
        sequence = _MEM_COUNTERS["bookings"]
        booking_id = _format_booking_id(sequence)
        _MEM_COUNTERS["bookings"] += 1
        doc_data["booking_id"] = booking_id
        _MEM_BOOKINGS[booking_id] = dict(doc_data)
        return doc_data

    if firestore is None:
        raise RuntimeError("Firestore transactions are unavailable")
    counter_ref = db.collection("counters").document("bookings")
    transaction = db.transaction()

    @firestore.transactional
    def _create(txn):
        snapshot = counter_ref.get(transaction=txn)
        sequence = snapshot.get("next_sequence") if snapshot.exists else 1
        if type(sequence) is not int or sequence < 1:
            raise ValueError("Invalid booking counter state")
        booking_id = _format_booking_id(sequence)
        booking_ref = db.collection("bookings").document(booking_id)
        record = {**doc_data, "booking_id": booking_id}
        txn.set(counter_ref, {"next_sequence": sequence + 1, "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
        txn.create(booking_ref, record)
        return record

    return _create(transaction)


def get_booking_by_id(booking_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single booking by its unique booking ID."""
    db = _get_database_or_test_memory()
    if db is None:
        booking = _MEM_BOOKINGS.get(booking_id)
        return dict(booking) if booking else None

    doc = db.collection("bookings").document(booking_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["booking_id"] = doc.id
        return data
    return None


def get_all_bookings() -> List[Dict[str, Any]]:
    """
    Retrieves all bookings from Firestore.
    Returns bounded list of records.
    """
    db = _get_database_or_test_memory()
    if db is None:
        return [dict(b) for b in _MEM_BOOKINGS.values()]

    docs = db.collection("bookings").stream()
    results = []
    for doc in docs:
        item = doc.to_dict()
        item["booking_id"] = doc.id
        results.append(item)
    return results


def update_booking(booking_id: str, update_data: Dict[str, Any], user_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a non-cancelled booking without allowing status reactivation races."""
    if update_data.get("booking_status") == STATUS_CANCELLED:
        raise PermissionError("Use the administrator cancellation operation")

    safe_updates = dict(update_data)
    for immutable in ("booking_id", "created_by", "created_at", "updated_by", "updated_at"):
        safe_updates.pop(immutable, None)
    user_identifier = user_info.get("email") or user_info.get("uid") or "system"
    now = _get_utc_now()
    safe_updates.update({"updated_by": user_identifier, "updated_at": now.isoformat()})
    db = _get_database_or_test_memory()
    if db is None:
        existing = _MEM_BOOKINGS.get(booking_id)
        if not existing:
            return None
        if existing.get("booking_status") == STATUS_CANCELLED:
            raise PermissionError("Cancelled records are locked")
        existing.update(safe_updates)
        return dict(existing)

    if firestore is None:
        raise RuntimeError("Firestore transactions are unavailable")
    ref = db.collection("bookings").document(booking_id)
    transaction = db.transaction()

    @firestore.transactional
    def _update(txn):
        snapshot = ref.get(transaction=txn)
        if not snapshot.exists:
            return None
        record = snapshot.to_dict()
        if record.get("booking_status") == STATUS_CANCELLED:
            raise PermissionError("Cancelled records are locked")
        txn.update(ref, safe_updates)
        return {**record, **safe_updates, "booking_id": booking_id}

    return _update(transaction)


def cancel_booking(booking_id: str, user_info: Dict[str, Any]) -> bool:
    """Soft-cancel an active booking, atomically preventing double cancellation."""
    user_identifier = user_info.get("email") or user_info.get("uid") or "system"
    changes = {
        "booking_status": STATUS_CANCELLED,
        "updated_by": user_identifier,
        "updated_at": _get_utc_now().isoformat(),
    }
    db = _get_database_or_test_memory()
    if db is None:
        existing = _MEM_BOOKINGS.get(booking_id)
        if not existing or existing.get("booking_status") == STATUS_CANCELLED:
            return False
        existing.update(changes)
        return True

    if firestore is None:
        raise RuntimeError("Firestore transactions are unavailable")
    ref = db.collection("bookings").document(booking_id)
    transaction = db.transaction()

    @firestore.transactional
    def _cancel(txn):
        snapshot = ref.get(transaction=txn)
        if not snapshot.exists or snapshot.get("booking_status") == STATUS_CANCELLED:
            return False
        txn.update(ref, changes)
        return True

    return _cancel(transaction)


def delete_booking(booking_id: str) -> bool:
    """
    Permanently deletes a booking record.
    ADMIN ONLY. Booking IDs are never reused.
    """
    existing = get_booking_by_id(booking_id)
    if not existing:
        return False

    db = _get_database_or_test_memory()
    if db is None:
        if booking_id in _MEM_BOOKINGS:
            del _MEM_BOOKINGS[booking_id]
            return True
        return False

    db.collection("bookings").document(booking_id).delete()
    return True


# ============================================================================
# USER MANAGEMENT (Firestore Collection: 'users/{uid}')
# ============================================================================

def get_user_by_uid(uid: str) -> Optional[Dict[str, Any]]:
    """Retrieves user profile and role document from Firestore."""
    if not uid:
        return None

    db = _get_database_or_test_memory()
    if db is None:
        user = _MEM_USERS.get(uid)
        return dict(user) if user else None

    doc = db.collection("users").document(uid).get()
    if doc.exists:
        data = doc.to_dict()
        data["uid"] = doc.id
        return data
    return None


def upsert_user(uid: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates or updates a user profile with role and active status in Firestore."""
    now = _get_utc_now()
    doc_payload = dict(user_data)
    doc_payload["updated_at"] = now.isoformat()

    existing = get_user_by_uid(uid)
    if not existing:
        doc_payload["created_at"] = now.isoformat()
        if "active" not in doc_payload:
            doc_payload["active"] = True
        if "role" not in doc_payload:
            doc_payload["role"] = ROLE_STAFF

    db = _get_database_or_test_memory()
    if db is None:
        if uid in _MEM_USERS:
            _MEM_USERS[uid].update(doc_payload)
        else:
            _MEM_USERS[uid] = doc_payload
        _MEM_USERS[uid]["uid"] = uid
        return dict(_MEM_USERS[uid])

    user_ref = db.collection("users").document(uid)
    user_ref.set(doc_payload, merge=True)
    return get_user_by_uid(uid) or doc_payload


def reset_memory_db():
    """Helper for testing: resets the in-memory data store."""
    global _MEM_COUNTERS, _MEM_BOOKINGS, _MEM_USERS
    _MEM_COUNTERS = {"bookings": 1}
    _MEM_BOOKINGS = {}
    _MEM_USERS = {}
