import json
import os

DB_FILE = "database.json"

# Create file if not exists
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "sessions": {}}, f)


def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


# 👤 Save user
def save_user(user_id, username=None):
    data = load_db()
    data["users"][str(user_id)] = {
        "username": username,
    }
    save_db(data)


# 💾 Save session string
def save_session(user_id, session_string):
    data = load_db()
    data["sessions"][str(user_id)] = session_string
    save_db(data)


# 📤 Get session
def get_session(user_id):
    data = load_db()
    return data["sessions"].get(str(user_id))
