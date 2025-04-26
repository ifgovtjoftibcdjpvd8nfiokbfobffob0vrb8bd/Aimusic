import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.admin_filters import admin_filter

spam_chats = set()


@app.on_message(
    filters.command(["utag", "all", "mention"]) & filters.group & admin_filter
)
async def tag_all_users(client: Client, message: Message):
    replied = message.reply_to_message
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    if not replied and not text:
        return await message.reply(
            "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ.**"
        )

    spam_chats.add(message.chat.id)
    usernum, usertxt, total_tagged = 0, "", 0

    try:
        async for member in client.get_chat_members(message.chat.id):
            if message.chat.id not in spam_chats:
                break

            if not member.user or member.user.is_bot:
                continue

            usernum += 1
            total_tagged += 1
            usertxt += f"⊚ [{member.user.first_name}](tg://user?id={member.user.id})\n"

            if usernum == 5:
                try:
                    if replied:
                        await replied.reply_text(
                            f"{text}\n{usertxt}\n📢 ᴛᴀɢɢɪɴɢ {total_tagged} ᴜsᴇʀs ᴅᴏɴᴇ..."
                        )
                    else:
                        await message.reply_text(
                            f"{text}\n{usertxt}\n📢 ᴛᴀɢɢɪɴɢ {total_tagged} ᴜsᴇʀs ᴅᴏɴᴇ..."
                        )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    pass

                await asyncio.sleep(3)
                usernum, usertxt = 0, ""

        if usertxt:
            try:
                if replied:
                    await replied.reply_text(
                        f"{text}\n{usertxt}\n📢 ᴛᴀɢɢɪɴɢ {total_tagged} ᴜsᴇʀs ᴅᴏɴᴇ..."
                    )
                else:
                    await message.reply_text(
                        f"{text}\n{usertxt}\n📢 ᴛᴀɢɢɪɴɢ {total_tagged} ᴜsᴇʀs ᴅᴏɴᴇ..."
                    )
            except Exception:
                pass

        await message.reply(
            f"✅ **ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ. ᴛᴏᴛᴀʟ:** `{total_tagged}` **ᴜsᴇʀs.**"
        )

    finally:
        spam_chats.discard(message.chat.id)


@app.on_message(filters.command(["cancel", "ustop"]))
async def cancel_spam(client: Client, message: Message):
    chat_id = message.chat.id

    if chat_id not in spam_chats:
        return await message.reply("**ɪ'ᴍ ɴᴏᴛ ᴛᴀɢɢɪɴɢ ᴀɴʏᴏɴᴇ ʀɪɢʜᴛ ɴᴏᴡ.**")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ):
            return await message.reply("**ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄᴀɴᴄᴇʟ ᴛᴀɢɢɪɴɢ.**")
    except UserNotParticipant:
        return await message.reply("**ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ ᴏғ ᴛʜɪs ᴄʜᴀᴛ.**")
    except Exception:
        return await message.reply("**ᴇʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ᴀᴅᴍɪɴ sᴛᴀᴛᴜs.**")

    spam_chats.discard(chat_id)
    return await message.reply("**🚫 ᴛᴀɢɢɪɴɢ ᴄᴀɴᴄᴇʟʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
