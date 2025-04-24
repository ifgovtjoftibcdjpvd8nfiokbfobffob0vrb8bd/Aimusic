import os
import random
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from typing import Union, Optional
from ANNIEMUSIC import app

# Default profile photos if user has none
anniephoto = [
    "https://telegra.ph/file/07fd9e0e34bc84356f30d.jpg",
    "https://telegra.ph/file/3c4de59511e179018f902.jpg",
    "https://telegra.ph/file/07fd9e0e34bc84356f30d.jpg",
    "https://telegra.ph/file/3c4de59511e179018f902.jpg"
]

INFO_TEXT = """**
❅─────✧❅✦❅✧─────❅
            ✦ ᴜsᴇʀ ɪɴғᴏ ✦

➻ ᴜsᴇʀ ɪᴅ ‣ **`{}`
**➻ ғɪʀsᴛ ɴᴀᴍᴇ ‣ **{}
**➻ ʟᴀsᴛ ɴᴀᴍᴇ ‣ **{}
**➻ ᴜsᴇʀɴᴀᴍᴇ ‣ **{}
**➻ ᴍᴇɴᴛɪᴏɴ ‣ **{}
**➻ ʟᴀsᴛ sᴇᴇɴ ‣ **{}
**➻ ᴅᴄ ɪᴅ ‣ **{}
**➻ ʙɪᴏ ‣ **`{}`

**❅─────✧❅✦❅✧─────❅**
"""

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        status = user.status
        if status == enums.UserStatus.RECENTLY:
            return "Recently"
        elif status == enums.UserStatus.LAST_WEEK:
            return "Last week"
        elif status == enums.UserStatus.LONG_AGO:
            return "Long time ago"
        elif status == enums.UserStatus.OFFLINE:
            return "Offline"
        elif status == enums.UserStatus.ONLINE:
            return "Online"
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

@app.on_message(filters.command(["info", "userinfo"], prefixes=["/", "!", "."]))
async def userinfo(client: Client, message: Message):
    chat_id = message.chat.id

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user_identifier = message.text.split(None, 1)[1]
        try:
            if user_identifier.isdigit():
                user_id = int(user_identifier)
            else:
                user_id = user_identifier
            target_user = await app.get_users(user_id)
        except Exception as e:
            await message.reply_text(f"Could not find user: {e}")
            return
    else:
        target_user = message.from_user

    user_id = target_user.id

    try:
        user_info = await app.get_chat(user_id)
        status = await userstatus(user_id)
        dc_id = target_user.dc_id or "Unknown"
        first_name = user_info.first_name or "No first name"
        last_name = user_info.last_name or "No last name"
        username = f"@{user_info.username}" if user_info.username else "No username"
        mention = target_user.mention
        bio = user_info.bio or "No bio set"

        # Get user profile photo or use default photo
        if target_user.photo:
            # Use the user's Telegram profile photo directly
            photo = await app.download_media(target_user.photo.big_file_id)
            await app.send_photo(
                chat_id,
                photo=photo,
                caption=INFO_TEXT.format(
                    user_id,
                    first_name,
                    last_name,
                    username,
                    mention,
                    status,
                    dc_id,
                    bio
                ),
                reply_to_message_id=message.id
            )
            # Clean up the downloaded photo
            try:
                os.remove(photo)
            except Exception as e:
                print(f"Error deleting profile photo: {e}")
        else:
            # Use a default photo if the user doesn't have a profile picture
            default_photo = random.choice(anniephoto)
            await app.send_photo(
                chat_id,
                photo=default_photo,
                caption=INFO_TEXT.format(
                    user_id,
                    first_name,
                    last_name,
                    username,
                    mention,
                    status,
                    dc_id,
                    bio
                ),
                reply_to_message_id=message.id
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")