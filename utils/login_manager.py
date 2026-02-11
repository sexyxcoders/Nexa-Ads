from pyrogram import Client
from config import API_ID, API_HASH, SESSION_FOLDER
import os, json

login_data = {}

os.makedirs(SESSION_FOLDER, exist_ok=True)

async def create_client(user_id):
    app = Client(f"{SESSION_FOLDER}{user_id}", api_id=API_ID, api_hash=API_HASH)
    await app.connect()
    return app

def save_session(user_id, session_string):
    try:
        with open("session_store.json", "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[str(user_id)] = session_string

    with open("session_store.json", "w") as f:
        json.dump(data, f, indent=2)
