from ANNIEMUSIC import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from os import remove
import os
from typing import Union, Optional
from PIL import Image, ImageDraw, ImageFont
import asyncio
import time
from collections import deque

# --------------------------------------------------------------------------------- #

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)
resize_text = (
    lambda text_size, text: (text[:text_size] + "...").upper()
    if len(text) > text_size
    else text.upper()
)

# --------------------------------------------------------------------------------- #

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None
):
    bg = Image.open(bg_path)

    if profile_path:
        img = Image.open(profile_path)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

        circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((400, 400))
        bg.paste(resized, (440, 160), resized)

    img_draw = ImageDraw.Draw(bg)

    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )

    path = f"./userinfo_img_{user_id}_{int(time.time())}.png"
    bg.save(path)
    return path

# --------------------------------------------------------------------------------- #

bg_path = "ANNIEMUSIC/assets/userinfo.png"
font_path = "ANNIEMUSIC/assets/hiroko.ttf"

# --------------------------------------------------------------------------------- #

leave_events = {}

async def handle_leave_event(chat_id):
    now = time.time()
    if chat_id not in leave_events:
        leave_events[chat_id] = {
            'timestamps': deque(),
            'notifications_disabled_until': 0,
            'lock': asyncio.Lock()
        }
    data = leave_events[chat_id]

    async with data['lock']:
        while data['timestamps'] and now - data['timestamps'][0] > 5:
            data['timestamps'].popleft()
        data['timestamps'].append(now)
        if now < data['notifications_disabled_until']:
            return False
        else:
            if len(data['timestamps']) >= 10:
                data['notifications_disabled_until'] = now + 15 * 60
                data['timestamps'].clear()
                return False
            else:
                return True

# --------------------------------------------------------------------------------- #

@app.on_chat_member_updated(filters.group, group=20)
async def member_has_left(client: app, member: ChatMemberUpdated):
    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {
            "banned", "left", "restricted"
        }
        and member.old_chat_member
    ):
        pass
    else:
        return

    should_notify = await handle_leave_event(member.chat.id)
    if not should_notify:
        return

    user = (
        member.old_chat_member.user
        if member.old_chat_member
        else member.from_user
    )

    if user.photo and user.photo.big_file_id:
        photo = None
        welcome_photo = None
        try:
            photo = await app.download_media(user.photo.big_file_id)

            # Create the user info image
            welcome_photo = await get_userinfo_img(
                bg_path=bg_path,
                font_path=font_path,
                user_id=user.id,
                profile_path=photo,
            )

            caption = f"**#New_Member_Left**\n\n**๏** {user.mention} **has left this group**\n**๏ See you soon again..!**"
            button_text = "๏ View User ๏"

            deep_link = f"tg://openmessage?user_id={user.id}"

            message = await client.send_photo(
                chat_id=member.chat.id,
                photo=welcome_photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(button_text, url=deep_link)]
                ])
            )

            async def delete_message():
                await asyncio.sleep(10)
                await message.delete()
                try:
                    if photo and os.path.exists(photo):
                        remove(photo)
                    if welcome_photo and os.path.exists(welcome_photo):
                        remove(welcome_photo)
                except Exception as e:
                    print(f"Error deleting files: {e}")

            asyncio.create_task(delete_message())

        except RPCError as e:
            print(e)
            return
    else:
        print(f"User {user.id} has no profile photo.")
