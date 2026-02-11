import os

# Telegram API credentials (from my.telegram.org)
API_ID = int(os.getenv("API_ID", "123456"))  # replace if not using env
API_HASH = os.getenv("API_HASH", "your_api_hash_here")

# Bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Folder where user session files will be stored
SESSION_FOLDER = "sessions/"
