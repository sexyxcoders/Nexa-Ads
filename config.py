import os

# Telegram API credentials (from my.telegram.org)
API_ID = int(os.getenv("API_ID", "22657083"))  # replace if not using env
API_HASH = os.getenv("API_HASH", "d6186691704bd901bdab275ceaab88f3")

# Bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525366225:AAG_nUH9HfmDz8TpBxg-gt2pMDesnfY71L4")

START_IMAGE = "https://telegram.me/share/url?url=https://files.catbox.moe/zttfbe.jpg"  # image URL or file_id

FORCE_JOIN_CHANNEL = "TechyNetwork"  # without @

# Folder where user session files will be stored
SESSION_FOLDER = "sessions/"
