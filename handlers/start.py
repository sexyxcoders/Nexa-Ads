from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import bot

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Connect Account", callback_data="connect")]
    ])

    await message.reply_text(
        "✨ Welcome to Adimyze Bot ✨\n\n"
        "💎 Premium Automation Platform\n\n"
        "🔐 Connection Required\n"
        "To access all premium features, connect your Telegram account.",
        reply_markup=buttons
    )
