# bot.py

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client(
    "nexa_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# import handlers AFTER creating `bot`
import handlers.start
import handlers.connect
import handlers.otp

# Start bot
print("🚀 Nexa Ads Bot is starting...")
bot.run()