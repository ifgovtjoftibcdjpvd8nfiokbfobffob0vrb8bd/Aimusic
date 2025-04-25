import asyncio
from typing import List

from pyrogram import Client, enums, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.admin_check import is_admin


chatQueue: set[int] = set()
stopProcess: bool = False


async def scan_deleted_members(chat_id: int) -> List:
    deleted = []
    async for member in app.get_chat_members(chat_id):
        if member.user and member.user.is_deleted:
            deleted.append(member.user)
    return deleted


async def safe_edit(msg: Message, text: str):
    try:
        await msg.edit(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await msg.edit(text)
    except Exception:
        pass


@app.on_message(filters.command(["zombies", "clean"]))
async def prompt_zombie_cleanup(_: Client, message: Message):
    if not await is_admin(message):
        return await message.reply("👮🏻 | **ᴏɴʟʏ ᴀᴅᴍɪɴs** ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    deleted_list = await scan_deleted_members(message.chat.id)
    if not deleted_list:
        return await message.reply("⟳ | **ɴᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ғᴏᴜɴᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")

    total = len(deleted_list)
    est_time = total * 10

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ ʏᴇs, ᴄʟᴇᴀɴ", callback_data=f"confirm_zombies:{message.chat.id}"),
                InlineKeyboardButton("❌ ɴᴏᴛ ɴᴏᴡ", callback_data="cancel_zombies"),
            ]
        ]
    )

    await message.reply(
        (
            f"⚠️ | **ғᴏᴜɴᴅ `{total}` ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs.**\n"
            f"🥀 | **ᴇsᴛɪᴍᴀᴛᴇᴅ ᴄʟᴇᴀɴᴜᴘ ᴛɪᴍᴇ:** `{est_time}s`\n\n"
            "ᴅᴏ ʏᴏᴜ ᴡᴀɴɴᴀ ᴄʟᴇᴀɴ ᴛʜᴇᴍ?"
        ),
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex(r"^confirm_zombies"))
async def execute_zombie_cleanup(_: Client, cq: CallbackQuery):
    global stopProcess
    chat_id = int(cq.data.split(":")[1])

    if not await is_admin(cq):
        return await cq.answer("👮🏻 | ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄᴏɴғɪʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ.", show_alert=True)

    if chat_id in chatQueue:
        return await cq.answer("⚠️ | ᴄʟᴇᴀɴᴜᴘ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss.", show_alert=True)

    bot_me = await app.get_chat_member(chat_id, "self")
    if bot_me.status == ChatMemberStatus.MEMBER:
        return await cq.edit_message_text("➠ | **ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs.**")

    chatQueue.add(chat_id)
    deleted_list = await scan_deleted_members(chat_id)
    total = len(deleted_list)

    status = await cq.edit_message_text(
        f"🧭 | **ғᴏᴜɴᴅ `{total}` ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs.**\n🥀 | **sᴛᴀʀᴛɪɴɢ ᴄʟᴇᴀɴᴜᴘ...**"
    )

    removed = 0
    for user in deleted_list:
        if stopProcess:
            break
        try:
            await app.ban_chat_member(chat_id, user.id)
            removed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass

        if removed % 10 == 0 or removed == total:
            await safe_edit(status, f"♻️ | **ʀᴇᴍᴏᴠᴇᴅ {removed}/{total}...**")
        await asyncio.sleep(10)

    chatQueue.discard(chat_id)
    await safe_edit(status, f"✅ | **sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ `{removed}` ᴏꜰ `{total}`.**")


@app.on_callback_query(filters.regex(r"^cancel_zombies$"))
async def cancel_zombie_cleanup(_: Client, cq: CallbackQuery):
    await cq.edit_message_text("❌ | **ᴄʟᴇᴀɴᴜᴘ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜsᴇʀ.**")


@app.on_message(filters.command(["admins", "staff"]))
async def list_admins(_: Client, message: Message):
    try:
        owners, admins = [], []
        async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if m.privileges.is_anonymous or m.user.is_bot:
                continue
            (owners if m.status == ChatMemberStatus.OWNER else admins).append(m.user)

        txt = f"**ɢʀᴏᴜᴘ sᴛᴀғғ – {message.chat.title}**\n\n"
        owner_line = owners[0].mention if owners else "<i>Hidden</i>"
        txt += f"👑 ᴏᴡɴᴇʀ\n└ {owner_line}\n\n👮🏻 ᴀᴅᴍɪɴs\n"

        if not admins:
            txt += "└ <i>Admins are hidden</i>"
        else:
            for i, adm in enumerate(admins):
                branch = "└" if i == len(admins) - 1 else "├"
                txt += f"{branch} {'@'+adm.username if adm.username else adm.mention}\n"
        txt += f"\n✅ | **Total admins**: {len(owners)+len(admins)}"
        await app.send_message(message.chat.id, txt)
    except FloodWait as e:
        await asyncio.sleep(e.value)



@app.on_message(filters.command("bots"))
async def list_bots(_: Client, message: Message):
    try:
        bots = [b.user async for b in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)]
        txt = f"**ʙᴏᴛ ʟɪsᴛ – {message.chat.title}**\n\n🤖 ʙᴏᴛs\n"
        for i, bt in enumerate(bots):
            branch = "└" if i == len(bots) - 1 else "├"
            txt += f"{branch} @{bt.username}\n"
        txt += f"\n✅ | **Total bots**: {len(bots)}"
        await app.send_message(message.chat.id, txt)
    except FloodWait as e:
        await asyncio.sleep(e.value)