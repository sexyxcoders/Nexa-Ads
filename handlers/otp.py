from pyrogram import filters
from pyrogram.errors import SessionPasswordNeeded
from bot import bot
from utils.login_manager import create_client, login_data, save_session
import asyncio, re


@bot.on_message(filters.private & filters.text & ~filters.command(["start"]))
async def login_flow(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    # OTP STEP
    if user_id in login_data and login_data[user_id].get("awaiting_otp"):
        return await otp_verify(message)

    # PASSWORD STEP
    if user_id in login_data and login_data[user_id].get("awaiting_password"):
        return await password_verify(message)

    # PHONE STEP
    if not text.startswith("+"):
        return

    msg = await message.reply("📱 Sending OTP...\n⏳ Please wait...")
    await asyncio.sleep(5)

    app = await create_client(user_id)
    sent_code = await app.send_code(text)

    login_data[user_id] = {
        "app": app,
        "phone": text,
        "phone_code_hash": sent_code.phone_code_hash,
        "awaiting_otp": True
    }

    await msg.edit_text(
        "📲 OTP Sent Successfully!\n\n"
        f"✅ Code sent to: {text}\n"
        "📱 Check Telegram app for code\n"
        "⏰ Expires in 5 minutes\n\n"
        "💡 Format: mycode12345"
    )


async def otp_verify(message):
    user_id = message.from_user.id
    raw = message.text.strip()
    otp = "".join(re.findall(r"\d+", raw))  # extract digits

    data = login_data[user_id]
    app = data["app"]

    try:
        await app.sign_in(
            phone_number=data["phone"],
            phone_code_hash=data["phone_code_hash"],
            phone_code=otp
        )

        session_string = await app.export_session_string()
        save_session(user_id, session_string)

        await message.reply("✨ Instant account connection successful!")
        await app.disconnect()
        login_data.pop(user_id)

    except SessionPasswordNeeded:
        data["awaiting_password"] = True
        data.pop("awaiting_otp", None)
        await message.reply(
            "🔐 2-Step Verification Enabled\n\n"
            "Please enter your password to continue."
        )

    except:
        await message.reply("❌ Invalid code. Try again.")


async def password_verify(message):
    user_id = message.from_user.id
    password = message.text.strip()
    data = login_data[user_id]
    app = data["app"]

    try:
        await app.check_password(password)

        session_string = await app.export_session_string()
        save_session(user_id, session_string)

        await message.reply("✨ Instant account connection successful!")
        await app.disconnect()
        login_data.pop(user_id)

    except:
        await message.reply("❌ Wrong password. Try again.")
