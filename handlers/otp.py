# handlers/otp.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    FloodWait,
    BadRequest
)
from bot import bot
from utils.login_manager import create_client, login_data, save_session
import asyncio
import re
import logging

logging.basicConfig(level=logging.WARNING)


def get_cancel_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_login")]])


async def _cleanup_login(user_id):
    if user_id in login_
        app = login_data[user_id].get("app")
        if app:
            try:
                await app.stop()
            except Exception:
                pass
        login_data.pop(user_id, None)


@bot.on_message(filters.private & filters.text & ~filters.command(["start", "cancel"]))
async def login_flow(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text.startswith("+"):
        await _cleanup_login(user_id)

        if not re.match(r"^\+\d{7,15}$", text):
            await message.reply("❌ Invalid phone number format.\n\nExample: `+14155552671`")
            return

        msg = await message.reply("📱 Sending verification code...\n⏳ Please wait...")
        try:            app = await create_client(user_id)
            sent_code = await app.send_code(text)
        except FloodWait as e:
            await msg.edit_text(f"⏳ Too many requests. Please wait {e.value} seconds before trying again.")
            return
        except BadRequest as e:
            await msg.edit_text(f"⚠️ Invalid phone number: {str(e)}")
            return
        except Exception as e:
            logging.exception("Error during send_code")
            await msg.edit_text("⚠️ Failed to send code. Please try again later.")
            return

        # Store app + message ID for future editing
        login_data[user_id] = {
            "app": app,
            "phone": text,
            "phone_code_hash": sent_code.phone_code_hash,
            "awaiting_otp": True,
            "last_msg_id": msg.id  # ← store message ID
        }

        await msg.edit_text(
            "📲 Verification code sent!\n\n"
            f"✅ Sent to: `{text}`\n"
            "📬 Check your Telegram messages from **Telegram** (official account)\n"
            "⏰ Code expires in 5 minutes\n\n"
            "💡 Reply with the 5-digit code (e.g., `12345`)",
            reply_markup=get_cancel_button()
        )
        return

    # Handle OTP
    if user_id in login_data and login_data[user_id].get("awaiting_otp"):
        return await otp_verify(message)

    # Handle password
    if user_id in login_data and login_data[user_id].get("awaiting_password"):
        return await password_verify(message)

    await message.reply(
        "📱 Please send your phone number in international format.\n\n"
        "Example: `+14155552671`"
    )


@bot.on_message(filters.command("cancel") & filters.private)
async def cancel_login_cmd(client, message):
    user_id = message.from_user.id
    await _cleanup_login(user_id)    await message.reply("✅ Login process cancelled.\n\nUse /start to begin again.")


# --- OTP & Password Handlers ---
async def otp_verify(message):
    user_id = message.from_user.id
    raw = message.text.strip()
    otp = "".join(re.findall(r"\d+", raw))

    if len(otp) != 5 or not otp.isdigit():
        await message.reply("❌ Invalid OTP. Please send exactly 5 digits (e.g., `12345`).")
        return

    data = login_data.get(user_id)
    if not data or "app" not in 
        await message.reply("⚠️ Login session expired. Please start again with your phone number.")
        return

    app = data["app"]
    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]

    try:
        await app.sign_in(phone_number=phone, phone_code_hash=phone_code_hash, phone_code=otp)

        session_string = await app.export_session_string()
        save_session(user_id, session_string)

        # Edit last message to success
        if "last_msg_id" in 
            try:
                await message._client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=data["last_msg_id"],
                    text="✨ Login successful! Your account is now connected.",
                    reply_markup=None
                )
            except Exception:
                await message.reply("✨ Login successful!")
        else:
            await message.reply("✨ Login successful!")

        await _cleanup_login(user_id)

    except SessionPasswordNeeded:
        # Switch to password mode + update message
        data["awaiting_password"] = True
        data.pop("awaiting_otp", None)

        # Update the original message to prompt for password        if "last_msg_id" in 
            try:
                await message._client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=data["last_msg_id"],
                    text=(
                        "🔐 **Two-Step Verification** is enabled.\n\n"
                        "Please send your account password to continue."
                    ),
                    reply_markup=get_cancel_button()
                )
            except Exception:
                await message.reply(
                    "🔐 **Two-Step Verification** is enabled.\n\n"
                    "Please send your account password to continue.",
                    reply_markup=get_cancel_button()
                )
        else:
            await message.reply(
                "🔐 **Two-Step Verification** is enabled.\n\n"
                "Please send your account password to continue.",
                reply_markup=get_cancel_button()
            )

    except PhoneCodeInvalid:
        await message.reply("❌ Incorrect code. Please check and resend the 5-digit code.")
    except PhoneCodeExpired:
        await message.reply("⏰ The code has expired. Please restart by sending your phone number.")
    except FloodWait as e:
        await message.reply(f"⏳ Too many attempts. Wait {e.value} seconds before retrying.")
    except Exception as e:
        logging.exception("Unexpected error during OTP verification")
        await message.reply("⚠️ An unexpected error occurred. Please restart the login process.")
        await _cleanup_login(user_id)


async def password_verify(message):
    user_id = message.from_user.id
    password = message.text.strip()

    data = login_data.get(user_id)
    if not data or "app" not in 
        await message.reply("⚠️ Login session expired. Please start again with your phone number.")
        return

    app = data["app"]

    try:
        await app.check_password(password)
        session_string = await app.export_session_string()
        save_session(user_id, session_string)

        if "last_msg_id" in 
            try:
                await message._client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=data["last_msg_id"],
                    text="✨ Login successful! Your account is now connected.",
                    reply_markup=None
                )
            except Exception:
                await message.reply("✨ Login successful!")
        else:
            await message.reply("✨ Login successful!")

        await _cleanup_login(user_id)

    except PasswordHashInvalid:
        await message.reply("❌ Incorrect password. Please try again.")
    except FloodWait as e:
        await message.reply(f"⏳ Too many attempts. Wait {e.value} seconds before retrying.")
    except Exception as e:
        logging.exception("Unexpected error during password verification")
        await message.reply("⚠️ An error occurred. Please restart the login process.")
        await _cleanup_login(user_id)


# --- Cancel via Inline Button ---
@bot.on_callback_query(filters.regex("^cancel_login$"))
async def cancel_login_inline(client, callback_query):
    user_id = callback_query.from_user.id
    await _cleanup_login(user_id)

    # Return to start screen
    from .start import get_main_menu  # Ensure this function exists in start.py

    await callback_query.message.edit_text(
        "✨ Welcome to Nexa Ads Bot ✨\n\n"
        "💎 Your Premium Ad Automation Platform\n\n"
        "🔐 To unlock all features, connect your Telegram account below.",
        reply_markup=get_main_menu()
    )
    await callback_query.answer("✅ Login cancelled.", show_alert=False)