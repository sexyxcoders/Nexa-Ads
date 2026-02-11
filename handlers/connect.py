from pyrogram import filters
from bot import bot

@bot.on_callback_query(filters.regex("connect"))
async def connect_account(client, callback_query):
    await callback_query.message.edit_text(
        "⚡ Quick Login\n\n"
        "📱 Enter phone number with country code\n"
        "💡 Example: +1234567890\n\n"
        "✨ Instant account connection"
    )
