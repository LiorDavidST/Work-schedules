# -*- coding: utf-8 -*-
"""Firestore client setup for local development and hosted environments."""
import json
import os
from pathlib import Path
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_SERVICE_ACCOUNT_FILE = ROOT_DIR / "service_accounts.json"
ENV_CREDENTIALS_JSON = "GOOGLE_APPLICATION_CREDENTIALS_JSON"
APP_STATE_COLLECTION = "shift_management"
APP_STATE_DOCUMENT = "app_state"


def _load_credentials():
    credentials_json = os.environ.get(ENV_CREDENTIALS_JSON)
    if credentials_json:
        return credentials.Certificate(json.loads(credentials_json))

    if not LOCAL_SERVICE_ACCOUNT_FILE.exists():
        raise FileNotFoundError(
            "Firebase credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS_JSON "
            "or add service_accounts.json for local development."
        )

    return credentials.Certificate(str(LOCAL_SERVICE_ACCOUNT_FILE))


def get_firestore_client():
    """Initialize Firebase once and return a Firestore client."""
    if not firebase_admin._apps:
        firebase_admin.initialize_app(_load_credentials())

    return firestore.client()


def check_firestore_connection():
    """Write and read a small health document to verify Firestore connectivity."""
    client = get_firestore_client()
    doc_ref = client.collection("system").document("health")
    doc_ref.set({"status": "ok"}, merge=True)
    snapshot = doc_ref.get()

    if not snapshot.exists or snapshot.to_dict().get("status") != "ok":
        raise RuntimeError("Firestore health document did not return the expected status.")

    return True


def get_app_state():
    """Return the stored Shift Management app state, or None if it does not exist."""
    client = get_firestore_client()
    snapshot = client.collection(APP_STATE_COLLECTION).document(APP_STATE_DOCUMENT).get()

    if not snapshot.exists:
        return None

    return snapshot.to_dict().get("state")


def save_app_state(state):
    """Save the full Shift Management app state document."""
    if not isinstance(state, dict):
        raise ValueError("State must be a JSON object.")

    updated_at = datetime.now(timezone.utc).isoformat()
    version = 1
    document = {
        "version": version,
        "updatedAt": updated_at,
        "state": state,
    }

    client = get_firestore_client()
    client.collection(APP_STATE_COLLECTION).document(APP_STATE_DOCUMENT).set(document)

    return {
        "version": version,
        "updatedAt": updated_at,
    }
