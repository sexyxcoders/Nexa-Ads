# handlers/connect.py

from pyrogram import filters
from bot import bot
from utils.login_manager import login_data  # to clear stale sessions


@bot.on_callback_query(filters.regex("^connect$"))
async def connect_account(client, callback_query):
    user_id = callback_query.from_user.id

    # Clear any existing login state for this user
    if user_id in login_data:
        old_app = login_data[user_id].get("app")
        if old_app:
            try:
                await old_app.stop()
            except Exception:
                pass
        login_data.pop(user_id, None)

    # Edit message to prompt for phone number
    await callback_query.message.edit_text(
        "⚡ **Quick Login**\n\n"
        "📱 Please send your **phone number** with country code.\n"
        "💡 Example: `+1234567890`\n\n"
        "✨ We’ll send a verification code via Telegram.\n"
        "🔒 Your session is stored securely and never shared."
    )

    # Acknowledge the callback to remove loading spinner
    await callback_query.answer()