import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatJoinRequest

from ANNIEMUSIC import app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.utils.database import get_assistant
from ANNIEMUSIC.utils.jarvis_ban import admin_filter


async def join_userbot(app, chat_id, chat_username=None):
    userbot = await get_assistant(chat_id)
    try:
        member = await app.get_chat_member(chat_id, userbot.id)
        if member.status == ChatMemberStatus.BANNED:
            await app.unban_chat_member(chat_id, userbot.id)
    except Exception:
        pass

    try:
        if chat_username:
            await userbot.join_chat(chat_username)
        else:
            invite_link = await app.create_chat_invite_link(chat_id)
            await userbot.join_chat(invite_link.invite_link)
        return "**✅ Assistant joined.**"
    except Exception as e:
        try:
            if chat_username:
                await userbot.send_chat_join_request(chat_username)
            else:
                invite_link = await app.create_chat_invite_link(chat_id)
                await userbot.send_chat_join_request(invite_link.invite_link)
            return "**✅ Assistant sent a join request.**"
        except Exception as e2:
            return f"Error: {str(e2)}"


@app.on_chat_join_request()
async def approve_join_request(client, chat_join_request: ChatJoinRequest):
    userbot = await get_assistant(chat_join_request.chat.id)
    if chat_join_request.from_user.id == userbot.id:
        await client.approve_chat_join_request(chat_join_request.chat.id, userbot.id)
        await client.send_message(
            chat_join_request.chat.id,
            "**✅ Assistant has been approved and joined the chat.**",
        )


@app.on_message(
    filters.command(["userbotjoin", "assistantjoin"], prefixes=[".", "/"])
    & (filters.group | filters.private)
    & admin_filter
)
async def join_group(app, message):
    chat_id = message.chat.id
    a = await app.get_me()
    done = await message.reply("**Please wait, inviting assistant...**")
    await asyncio.sleep(1)
    chat_member = await app.get_chat_member(chat_id, a.id)

    if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        chat_username = message.chat.username
        response = await join_userbot(app, chat_id, chat_username=chat_username)
    else:
        response = "**I need admin power to invite my assistant.**"

    await done.edit_text(response)


@app.on_message(
    filters.command("userbotleave", prefixes=[".", "/"]) & filters.group & admin_filter
)
async def leave_one(app, message):
    try:
        userbot = await get_assistant(message.chat.id)
        await userbot.leave_chat(message.chat.id)
        await app.send_message(
            message.chat.id, "**✅ Assistant successfully left this chat.**"
        )
    except Exception as e:
        await message.reply(f"Error: {str(e)}")


@app.on_message(filters.command(["leaveall"], prefixes=["."]) & SUDOERS)
async def leave_all(app, message):
    left = 0
    failed = 0
    status_message = await message.reply("🔄 **Assistant is leaving all chats!**")
    try:
        userbot = await get_assistant(message.chat.id)
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1002014167331:
                continue
            try:
                await userbot.leave_chat(dialog.chat.id)
                left += 1
                await status_message.edit(
                    f"**Assistant is leaving all chats...**\n\n**Left:** {left} chats.\n**Failed:** {failed} chats."
                )
            except Exception:
                failed += 1
                await status_message.edit(
                    f"**Assistant is leaving all chats...**\n\n**Left:** {left} chats.\n**Failed:** {failed} chats."
                )
            await asyncio.sleep(1)
    finally:
        await app.send_message(
            message.chat.id,
            f"**✅ Left from:** {left} chats.\n**❌ Failed in:** {failed} chats.",
        )
