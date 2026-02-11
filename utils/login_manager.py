# utils/login_manager.py

from pyrogram import Client
from config import API_ID, API_HASH, SESSION_FOLDER
import os

# Ensure session directory exists
os.makedirs(SESSION_FOLDER, exist_ok=True)

# Shared login state (in-memory only)
login_data = {}


async def create_client(user_id: int) -> Client:
    """
    Create a new Pyrogram client for temporary login flow.
    Uses in-memory session (not saved to disk until successful login).
    """
    # Use in-memory session during login to avoid partial writes
    app = Client(
        name=str(user_id),
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True  # ← Critical: don't save incomplete sessions
    )
    await app.connect()
    return app


def save_session(user_id: int, session_string: str) -> None:
    """
    Save the final session string to a secure, user-specific file.
    """
    session_path = os.path.join(SESSION_FOLDER, f"{user_id}.session")
    try:
        with open(session_path, "w") as f:
            f.write(session_string)
        # Restrict file permissions (Unix-like systems)
        os.chmod(session_path, 0o600)
    except Exception as e:
        # Log error in production
        raise RuntimeError(f"Failed to save session for {user_id}: {e}")


def load_session(user_id: int) -> str | None:
    """
    Load a saved session string for reuse.
    Returns None if no session exists.
    """
    session_path = os.path.join(SESSION_FOLDER, f"{user_id}.session")
    if not os.path.exists(session_path):
        return None
    try:
        with open(session_path, "r") as f:
            return f.read().strip()
    except Exception:
        return None


async def get_user_client(user_id: int) -> Client | None:
    """
    Get a ready-to-use client for a logged-in user.
    Returns None if no valid session exists.
    """
    session_string = load_session(user_id)
    if not session_string:
        return None

    app = Client(
        name=str(user_id),
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        workdir=SESSION_FOLDER  # optional, for consistency
    )
    try:
        await app.start()
        return app
    except Exception:
        # Session invalid/expired — delete it
        session_path = os.path.join(SESSION_FOLDER, f"{user_id}.session")
        if os.path.exists(session_path):
            os.remove(session_path)
        return None