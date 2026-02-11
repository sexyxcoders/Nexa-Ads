from pyrogram import filters
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

# Optional: enable logging for debugging unexpected errors
logging.basicConfig(level=logging.WARNING)

@bot.on_message(filters.private & filters.text & ~filters.command(["start", "cancel"]))
async def login_flow(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    # If user sends a new phone number, reset any existing flow
    if text.startswith("+"):
        if user_id in login_data:
            old_app = login_data[user_id].get("app")
            if old_app:
                try:
                    await old_app.stop()
                except Exception:
                    pass
            login_data.pop(user_id, None)

        # Validate basic phone format (at least + followed by digits)
        if not re.match(r"^\+\d{7,15}$", text):
            await message.reply("❌ Invalid phone number format.\n\nExample: `+14155552671`")
            return

        msg = await message.reply("📱 Sending verification code...\n⏳ Please wait...")
        try:
            app = await create_client(user_id)
            sent_code = await app.send_code(text)
        except FloodWait as e:
            await msg.edit_text(f"⏳ Too many requests. Please wait {e.value} seconds before trying again.")
            return
        except BadRequest as e:
            await msg.edit_text(f"⚠️ Invalid phone number: {str(e)}")
            return
        except Exception as e:            logging.exception("Error during send_code")
            await msg.edit_text("⚠️ Failed to send code. Please try again later.")
            return

        login_data[user_id] = {
            "app": app,
            "phone": text,
            "phone_code_hash": sent_code.phone_code_hash,
            "awaiting_otp": True
        }

        await msg.edit_text(
            "📲 Verification code sent!\n\n"
            f"✅ Sent to: `{text}`\n"
            "📬 Check your Telegram messages from **Telegram** (official account)\n"
            "⏰ Code expires in 5 minutes\n\n"
            "💡 Reply with the 5-digit code (e.g., `12345`)"
        )
        return

    # Handle OTP input
    if user_id in login_data and login_data[user_id].get("awaiting_otp"):
        return await otp_verify(message)

    # Handle password input
    if user_id in login_data and login_data[user_id].get("awaiting_password"):
        return await password_verify(message)

    # Ignore unrelated messages
    await message.reply("📱 Please send your phone number in international format.\n\nExample: `+14155552671`")


async def otp_verify(message):
    user_id = message.from_user.id
    raw = message.text.strip()
    otp = "".join(re.findall(r"\d+", raw))

    if len(otp) != 5 or not otp.isdigit():
        await message.reply("❌ Invalid OTP. Please send exactly 5 digits (e.g., `12345`).")
        return

    data = login_data.get(user_id)
    if not data or "app" not in data:
        await message.reply("⚠️ Login session expired. Please start again with your phone number.")
        return

    app = data["app"]
    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]
    try:
        await app.sign_in(phone_number=phone, phone_code_hash=phone_code_hash, phone_code=otp)

        session_string = await app.export_session_string()
        save_session(user_id, session_string)

        await message.reply("✨ Login successful! Your account is now connected.")
        await app.stop()
        login_data.pop(user_id, None)

    except SessionPasswordNeeded:
        data["awaiting_password"] = True
        data.pop("awaiting_otp", None)
        await message.reply(
            "🔐 **Two-Step Verification** is enabled.\n\n"
            "Please send your account password to continue."
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
        await app.stop()
        login_data.pop(user_id, None)


async def password_verify(message):
    user_id = message.from_user.id
    password = message.text.strip()

    data = login_data.get(user_id)
    if not data or "app" not in data:
        await message.reply("⚠️ Login session expired. Please start again with your phone number.")
        return

    app = data["app"]

    try:
        await app.check_password(password)

        session_string = await app.export_session_string()
        save_session(user_id, session_string)

        await message.reply("✨ Login successful! Your account is now connected.")
        await app.stop()        login_data.pop(user_id, None)

    except PasswordHashInvalid:
        await message.reply("❌ Incorrect password. Please try again.")
    except FloodWait as e:
        await message.reply(f"⏳ Too many attempts. Wait {e.value} seconds before retrying.")
    except Exception as e:
        logging.exception("Unexpected error during password verification")
        await message.reply("⚠️ An error occurred. Please restart the login process.")
        await app.stop()
        login_data.pop(user_id, None)