# handlers/start.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.errors import (
    UserNotParticipant,
    ChatAdminRequired,
    ChannelInvalid,
    UsernameInvalid,
    PeerIdInvalid
)
from bot import bot
from config import START_IMAGE, FORCE_JOIN_CHANNEL


# ================= BUTTONS =================

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Connect Account", callback_data="connect")]
    ])


def get_join_markup(channel: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel}")],
        [InlineKeyboardButton("✅ I've Joined", callback_data="recheck_join")]
    ])


# ================= START COMMAND =================

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    channel = (FORCE_JOIN_CHANNEL or "").replace("@", "").strip()

    # 🔒 FORCE JOIN CHECK
    if channel:
        try:
            await client.get_chat_member(channel, user_id)

        except UserNotParticipant:
            await message.reply_photo(
                photo=START_IMAGE or "https://files.catbox.moe/zttfbe.jpg",
                caption="🔒 You must join our channel to use this bot.",
                reply_markup=get_join_markup(channel)
            )
            return

        except (ChannelInvalid, UsernameInvalid, PeerIdInvalid):
            await message.reply_text("❌ Force join channel is invalid.")
            return

        except ChatAdminRequired:
            await message.reply_text(
                "⚠️ Bot is not admin in the force-join channel.\n"
                "Give the bot *administrator* rights."
            )
            return

        except Exception as e:
            await message.reply_text(f"⚠️ Join check failed:\n`{e}`")
            return

    # ✅ MAIN MENU
    caption = (
        "✨ Welcome to Nexa Ads Bot ✨\n\n"
        "💎 Your Premium Ad Automation Platform\n\n"
        "🔐 To unlock all features, connect your Telegram account below."
    )

    try:
        if START_IMAGE:
            await message.reply_photo(START_IMAGE, caption=caption, reply_markup=get_main_menu())
        else:
            await message.reply_text(caption, reply_markup=get_main_menu())
    except:
        await message.reply_text(caption, reply_markup=get_main_menu())


# ================= RECHECK BUTTON =================

@bot.on_callback_query(filters.regex("^recheck_join$"))
async def recheck_join(client, callback_query):
    await callback_query.answer("Checking...", show_alert=False)

    user_id = callback_query.from_user.id
    channel = (FORCE_JOIN_CHANNEL or "").replace("@", "").strip()

    caption = (
        "✨ Welcome to Nexa Ads Bot ✨\n\n"
        "💎 Your Premium Ad Automation Platform\n\n"
        "🔐 To unlock all features, connect your Telegram account below."
    )

    # If no force join set
    if not channel:
        await send_menu(callback_query, caption)
        return

    try:
        await client.get_chat_member(channel, user_id)
        await send_menu(callback_query, caption)
        await callback_query.answer("✅ Access granted!", show_alert=False)

    except UserNotParticipant:
        await callback_query.answer("❌ Please join the channel first.", show_alert=True)

    except ChatAdminRequired:
        await callback_query.answer("⚠️ Bot must be admin in channel.", show_alert=True)

    except Exception:
        await callback_query.answer("⚠️ Verification failed.", show_alert=True)


# ================= SAFE EDIT FUNCTION =================

async def send_menu(callback_query, caption):
    """Safely edits message whether it's text or photo."""
    try:
        if START_IMAGE:
            await callback_query.message.edit_media(
                InputMediaPhoto(START_IMAGE, caption=caption),
                reply_markup=get_main_menu()
            )
        else:
            await callback_query.message.edit_text(caption, reply_markup=get_main_menu())

    except Exception:
        # fallback if media edit fails
        await callback_query.message.edit_text(caption, reply_markup=get_main_menu())