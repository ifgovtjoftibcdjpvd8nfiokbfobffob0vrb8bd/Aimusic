import os
import random
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from ANNIEMUSIC import app

anniephoto = [
    "https://telegra.ph/file/07fd9e0e34bc84356f30d.jpg",
    "https://telegra.ph/file/3c4de59511e179018f902.jpg",
    "https://telegra.ph/file/07fd9e0e34bc84356f30d.jpg",
    "https://telegra.ph/file/3c4de59511e179018f902.jpg",
]


bg_path = "ANNIEMUSIC/assets/annie/AnnieNinfo.png"
font_path = "ANNIEMUSIC/assets/annie/jarvisinf.ttf"


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


async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None,
):
    bg = Image.open(bg_path).convert("RGBA")

    if profile_path:
        img = Image.open(profile_path).convert("RGBA")
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), img.size], fill=255)
        circular_img = Image.new("RGBA", img.size)
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((977, 979))
        bg.paste(resized, (1673, 293), resized)

    img_draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype(font_path, 95)
    img_draw.text(
        (460, 1055),
        text=str(user_id).upper(),
        font=font,
        fill=(125, 227, 230),
    )

    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path


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

        if target_user.photo:
            photo_file_id = target_user.photo.big_file_id
            profile_photo_path = await app.download_media(photo_file_id)

            welcome_photo = await get_userinfo_img(
                bg_path=bg_path,
                font_path=font_path,
                user_id=user_id,
                profile_path=profile_photo_path,
            )
            await app.send_photo(
                chat_id,
                photo=welcome_photo,
                caption=INFO_TEXT.format(
                    user_id,
                    first_name,
                    last_name,
                    username,
                    mention,
                    status,
                    dc_id,
                    bio,
                ),
                reply_to_message_id=message.id,
            )
            try:
                os.remove(profile_photo_path)
                os.remove(welcome_photo)
            except Exception as e:
                print(f"Error deleting files: {e}")
        else:
            welcome_photo = random.choice(anniephoto)
            await app.send_photo(
                chat_id,
                photo=welcome_photo,
                caption=INFO_TEXT.format(
                    user_id,
                    first_name,
                    last_name,
                    username,
                    mention,
                    status,
                    dc_id,
                    bio,
                ),
                reply_to_message_id=message.id,
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
