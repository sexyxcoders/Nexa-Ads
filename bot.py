# bot.py

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Initialize the bot client
bot = Client(
    "nexa_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

if __name__ == "__main__":
    # Import handlers only when running the bot (prevents circular imports)
    import handlers.start
    import handlers.connect
    import handlers.otp

    print("🚀 Nexa Ads Bot is starting...")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped manually.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise