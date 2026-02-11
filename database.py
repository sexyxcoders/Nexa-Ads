# database.py

import json
import os
import threading

DB_FILE = "database.json"
_lock = threading.Lock()  # Prevent race conditions


# Initialize DB if missing
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "sessions": {}}, f, indent=2)


def load_db():
    """Load entire database safely."""
    with _lock:
        with open(DB_FILE, "r") as f:
            return json.load(f)


def save_db(data):
    """Save entire database safely."""
    with _lock:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)


def save_user(user_id: int, username: str = None):
    """Save or update user info."""
    data = load_db()
    data["users"][str(user_id)] = {
        "username": username or None,
    }
    save_db(data)


def save_session(user_id: int, session_string: str):
    """Save user session string securely (consider encryption in production)."""
    data = load_db()
    data["sessions"][str(user_id)] = session_string
    save_db(data)


def get_session(user_id: int) -> str | None:
    """Get session string for user, or None if not found."""
    data = load_db()
    return data["sessions"].get(str(user_id))  # Fixed: no trailing dot!