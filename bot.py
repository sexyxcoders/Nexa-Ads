from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client(
    "nexa_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Handlers load
import handlers.start
import handlers.connect
import handlers.otp

if __name__ == "__main__":
    print("🚀 Bot Running...")
    bot.run()
