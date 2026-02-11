import os

# Telegram API credentials (from my.telegram.org)
API_ID = int(os.getenv("API_ID", "22657083"))
API_HASH = os.getenv("API_HASH", "d6186691704bd901bdab275ceaab88f3")

# Bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525366225:AAG_nUH9HfmDz8TpBxg-gt2pMDesnfY71L4")

# Direct image URL (must end with .jpg, .png, etc.) or Telegram file_id
START_IMAGE = os.getenv("START_IMAGE", "https://files.catbox.moe/zttfbe.jpg")

# Force join channel username (without @)
FORCE_JOIN_CHANNEL = os.getenv("FORCE_JOIN_CHANNEL", "TechyNetwork")

# Session storage folder
SESSION_FOLDER = os.getenv("SESSION_FOLDER", "sessions/")

# --- Validation ---
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("❌ Missing required environment variables: API_ID, API_HASH, or BOT_TOKEN")
