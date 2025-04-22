import asyncio
from datetime import datetime, timedelta, timezone
from pyrogram import Client, filters, enums
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, Message
from logging import getLogger

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.jarvis_ban import admin_filter

LOGGER = getLogger(__name__)


class WelDatabase:
    def __init__(self):
        self.data = {}
        self.join_counts = {}
        self.join_timestamps = {}
        self.auto_disabled = {}

    async def find_one(self, chat_id):
        return self.data.get(chat_id, {"state": "on"})

    async def set_state(self, chat_id, state):
        self.data[chat_id] = {"state": state}

    async def is_welcome_on(self, chat_id):
        chat_data = await self.find_one(chat_id)
        return chat_data.get("state") == "on"

    async def track_join(self, chat_id):
        now = datetime.now(timezone.utc)
        last_join_time = self.join_timestamps.get(chat_id, now)
        if (now - last_join_time).total_seconds() > 8:
            self.join_counts[chat_id] = 1
        else:
            self.join_counts[chat_id] = self.join_counts.get(chat_id, 0) + 1
        self.join_timestamps[chat_id] = now
        return self.join_counts[chat_id]

    async def auto_disable_welcome(self, chat_id):
        await self.set_state(chat_id, "off")
        self.auto_disabled[chat_id] = datetime.now(timezone.utc) + timedelta(minutes=30)

    async def check_auto_reenable(self, chat_id):
        disable_time = self.auto_disabled.get(chat_id)
        if disable_time and datetime.now(timezone.utc) >= disable_time:
            await self.set_state(chat_id, "on")
            del self.auto_disabled[chat_id]
            return True
        return False

wlcm = WelDatabase()

class temp:
    MELCOW = {}


@app.on_message(filters.command("wel") & ~filters.private)
async def auto_state(client, message):
    usage = "**Usage:**\n⦿/wel [on|off]\n➤ANNIE SPECIAL WELCOME.........."
    if len(message.command) != 2:
        return await message.reply_text(usage)
    
    chat_id = message.chat.id
    user_status = await client.get_chat_member(chat_id, message.from_user.id)
    if user_status.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ sᴛᴀᴛᴜs!**")
    
    state = message.text.split(None, 1)[1].strip().lower()
    current_state = await wlcm.find_one(chat_id)
    if state == "off":
        if current_state.get("state") == "off":
            await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
        else:
            await wlcm.set_state(chat_id, "off")
            await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")
    elif state == "on":
        if current_state.get("state") == "on":
            await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**")
        else:
            await wlcm.set_state(chat_id, "on")
            await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")
    else:
        await message.reply_text(usage)


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(client, member: ChatMemberUpdated):
    chat_id = member.chat.id
    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    welcome_enabled = await wlcm.is_welcome_on(chat_id)
    if not welcome_enabled:
        auto_reenabled = await wlcm.check_auto_reenable(chat_id)
        if auto_reenabled:
            await client.send_message(
                chat_id,
                "**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇ-ᴇɴᴀʙʟᴇᴅ.**"
            )
        else:
            return

    join_count = await wlcm.track_join(chat_id)
    if join_count >= 10:
        await wlcm.auto_disable_welcome(chat_id)
        await client.send_message(
            chat_id,
            "**ᴍᴀssɪᴠᴇ ᴊᴏɪɴ ᴅᴇᴛᴇᴄᴛᴇᴅ. ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʀᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ 30 ᴍɪɴᴜᴛᴇs.**"
        )
        return

    if member.new_chat_member and member.new_chat_member.status == enums.ChatMemberStatus.MEMBER:
        try:
            previous_message = temp.MELCOW.get(f"welcome-{chat_id}")
            if previous_message:
                try:
                    await previous_message.delete()
                except Exception as e:
                    LOGGER.error(f"Error deleting previous welcome message: {e}")

            count = await client.get_chat_members_count(chat_id)
            button_text = "๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏"
            add_button_text = "๏ ᴋɪᴅɴᴀᴘ ᴍᴇ ๏"
            deep_link = f"tg://openmessage?user_id={user.id}"
            add_link = f"https://t.me/{client.username}?startgroup=true"
            
            welcome_message = await client.send_message(
                chat_id,
                f"""
**❅────✦ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ✦────❅
{member.chat.title}
▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ Nᴀᴍᴇ ✧ {user.mention}
➻ Iᴅ ✧ `{user.id}`
➻ Usᴇʀɴᴀᴍᴇ ✧ @{user.username or "No Username"}
➻ Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs ✧ {count}
▰▰▰▰▰▰▰▰▰▰▰▰▰**
**❅─────✧❅✦❅✧─────❅**
""",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(button_text, url=deep_link)],
                    [InlineKeyboardButton(add_button_text, url=add_link)],
                ])
            )
            temp.MELCOW[f"welcome-{chat_id}"] = welcome_message

        except Exception as e:
            LOGGER.error(f"Error in greeting new member: {e}")
