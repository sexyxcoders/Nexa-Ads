# handlers/start.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.errors import (
    UserNotParticipant,
    ChatAdminRequired,
    ChannelInvalid,
    UsernameInvalid
)
from bot import bot
from config import START_IMAGE, FORCE_JOIN_CHANNEL


def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Connect Account", callback_data="connect")]
    ])


def get_join_markup(channel: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel}")],
        [InlineKeyboardButton("✅ I've Joined", callback_data="recheck_join")]
    ])


@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    channel = (FORCE_JOIN_CHANNEL or "").replace("@", "").strip()

    if channel:
        try:
            await client.get_chat_member(channel, user_id)
        except (UserNotParticipant, ChannelInvalid, UsernameInvalid):
            await message.reply_photo(
                photo=START_IMAGE or "https://files.catbox.moe/zttfbe.jpg",
                caption="🔒 You must join our channel to use this bot.",
                reply_markup=get_join_markup(channel)
            )
            return
        except ChatAdminRequired:
            await message.reply_text(
                "⚠️ The bot is not an admin in the force-join channel.\n"
                "Please contact the owner to fix this."
            )
            return
        except Exception:
            await message.reply_text("⚠️ Unable to verify your membership. Please try again later.")            return

    caption = (
        "✨ Welcome to Nexa Ads Bot ✨\n\n"
        "💎 Your Premium Ad Automation Platform\n\n"
        "🔐 To unlock all features, connect your Telegram account below."
    )

    try:
        if START_IMAGE:
            await message.reply_photo(
                photo=START_IMAGE,
                caption=caption,
                reply_markup=get_main_menu()
            )
        else:
            await message.reply_text(caption, reply_markup=get_main_menu())
    except Exception:
        await message.reply_text(caption, reply_markup=get_main_menu())


@bot.on_callback_query(filters.regex("^recheck_join$"))
async def recheck_join(client, callback_query):
    user_id = callback_query.from_user.id
    channel = (FORCE_JOIN_CHANNEL or "").replace("@", "").strip()

    if not channel:
        caption = (
            "✨ Welcome to Nexa Ads Bot ✨\n\n"
            "💎 Your Premium Ad Automation Platform\n\n"
            "🔐 To unlock all features, connect your Telegram account below."
        )
        if START_IMAGE:
            await callback_query.message.edit_media(
                InputMediaPhoto(START_IMAGE, caption=caption),
                reply_markup=get_main_menu()
            )
        else:
            await callback_query.message.edit_text(caption, reply_markup=get_main_menu())
        await callback_query.answer("✅ Access granted!", show_alert=False)
        return

    try:
        await client.get_chat_member(channel, user_id)

        caption = (
            "✨ Welcome to Nexa Ads Bot ✨\n\n"
            "💎 Your Premium Ad Automation Platform\n\n"
            "🔐 To unlock all features, connect your Telegram account below."
        )        if START_IMAGE:
            await callback_query.message.edit_media(
                InputMediaPhoto(START_IMAGE, caption=caption),
                reply_markup=get_main_menu()
            )
        else:
            await callback_query.message.edit_text(caption, reply_markup=get_main_menu())

        await callback_query.answer("✅ Thank you for joining!", show_alert=False)

    except (UserNotParticipant, ChannelInvalid, UsernameInvalid):
        await callback_query.answer("❌ Please join the channel first.", show_alert=True)
    except ChatAdminRequired:
        await callback_query.answer("⚠️ Bot isn't admin in the channel.", show_alert=True)
    except Exception:
        await callback_query.answer("⚠️ Verification failed. Try again.", show_alert=True)