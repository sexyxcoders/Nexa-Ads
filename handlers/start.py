from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from bot import bot
from config import START_IMAGE, FORCE_JOIN_CHANNEL


@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id

    # remove @ if user added it in config
    channel = FORCE_JOIN_CHANNEL.replace("@", "")

    # 🔒 Force Join Check
    try:
        await client.get_chat_member(channel, user_id)
    except UserNotParticipant:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="recheck_join")]
        ])

        return await message.reply_photo(
            photo=START_IMAGE,
            caption="🔒 You must join our channel to use this bot.",
            reply_markup=buttons
        )

    except ChatAdminRequired:
        return await message.reply_text(
            "⚠️ Bot must be admin in the force join channel."
        )

    # ✅ Normal Start Screen
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Connect Account", callback_data="connect")]
    ])

    await message.reply_photo(
        photo=START_IMAGE,
        caption=(
            "✨ Welcome to Adimyze Bot ✨\n\n"
            "💎 Premium Automation Platform\n\n"
            "🔐 Connection Required\n"
            "To access all premium features, connect your Telegram account."
        ),
        reply_markup=buttons
    )


# 🔄 Recheck Button
@bot.on_callback_query(filters.regex("^recheck_join$"))
async def recheck_join(client, callback_query):
    user_id = callback_query.from_user.id
    channel = FORCE_JOIN_CHANNEL.replace("@", "")

    try:
        await client.get_chat_member(channel, user_id)
        await callback_query.message.delete()

        # recreate start screen safely
        await start_cmd(client, callback_query.message)

    except UserNotParticipant:
        await callback_query.answer("❌ Please join the channel first.", show_alert=True)

    except ChatAdminRequired:
        await callback_query.answer("⚠️ Bot is not admin in channel.", show_alert=True)