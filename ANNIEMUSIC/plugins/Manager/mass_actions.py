import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery,
    ChatPermissions, Message
)
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from ANNIEMUSIC import app
from ANNIEMUSIC.misc import SUDOERS

def get_keyboard(command):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=f"{command}_yes"),
            InlineKeyboardButton("No", callback_data=f"{command}_no")
        ]
    ])

async def get_group_owner(client, chat_id):
    try:
        async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.status == ChatMemberStatus.OWNER:
                return member.user
    except Exception as e:
        return None

async def is_owner_or_sudoer(client, chat_id, user_id):
    owner_user = await get_group_owner(client, chat_id)
    if owner_user is None:
        return False, None
    owner_id = owner_user.id
    if user_id == owner_id or user_id in SUDOERS:
        return True, owner_user
    else:
        return False, owner_user

async def get_bot_member(client, chat_id):
    try:
        bot_member = await client.get_chat_member(chat_id, client.me.id)
        return bot_member
    except Exception as e:
        return None

@app.on_message(filters.command(["kickall", "banall", "unbanall", "muteall", "unmuteall", "unpinall"]) & filters.group)
async def group_admin_commands(client: Client, message: Message):
    command = message.command[0]
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_owner, owner_user = await is_owner_or_sudoer(client, chat_id, user_id)
    if not is_owner:
        await message.reply_text(
            f"Sorry {message.from_user.mention}, the '{command}' command can only be executed by the group owner {owner_user.mention}."
        )
        return

    await message.reply(
        f"{message.from_user.mention}, are you sure you want to execute '{command}' in this group?",
        reply_markup=get_keyboard(command)
    )

@app.on_callback_query(filters.regex(r"^(kickall|banall|unbanall|muteall|unmuteall|unpinall)_(yes|no)$"))
async def handle_admin_callback(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    command, action = data.split('_')

    is_owner, owner_user = await is_owner_or_sudoer(client, chat_id, user_id)
    if not is_owner:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return

    if action == "yes":
        await callback_query.message.edit(f"{command.capitalize()} process started...")

        bot_member = await get_bot_member(client, chat_id)
        if not bot_member or bot_member.status != ChatMemberStatus.ADMINISTRATOR:
            await callback_query.message.edit("I need to be an admin to perform this action.")
            return

        required_privileges = {
            'kickall': bot_member.privileges.can_restrict_members,
            'banall': bot_member.privileges.can_restrict_members,
            'unbanall': bot_member.privileges.can_restrict_members,
            'muteall': bot_member.privileges.can_restrict_members,
            'unmuteall': bot_member.privileges.can_restrict_members,
            'unpinall': bot_member.privileges.can_pin_messages,
        }
        if not required_privileges.get(command, False):
            await callback_query.message.edit("I don't have the necessary permissions to perform this action.")
            return

        try:
            if command == "kickall":
                await perform_kick_all(client, chat_id)
            elif command == "banall":
                await perform_ban_all(client, chat_id)
            elif command == "unbanall":
                await perform_unban_all(client, chat_id)
            elif command == "muteall":
                await perform_mute_all(client, chat_id)
            elif command == "unmuteall":
                await perform_unmute_all(client, chat_id)
            elif command == "unpinall":
                await perform_unpin_all(client, chat_id)
        except Exception as e:
            await callback_query.message.edit(f"An error occurred during {command}.")
    elif action == "no":
        await callback_query.message.edit(f"{command.capitalize()} process canceled.")

async def perform_kick_all(client: Client, chat_id: int):
    kicked = 0
    error_count = 0

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        try:
            await client.ban_chat_member(chat_id, member.user.id)
            await asyncio.sleep(0.1)
            await client.unban_chat_member(chat_id, member.user.id)
            kicked += 1
        except Exception as e:
            error_count += 1
        await asyncio.sleep(0.1)
    await client.send_message(chat_id, f"Kicked {kicked} members successfully. Failed to kick {error_count} members.")

async def perform_ban_all(client: Client, chat_id):
    banned = 0
    error_count = 0

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        try:
            await client.ban_chat_member(chat_id, member.user.id)
            banned += 1
        except Exception as e:
            error_count += 1
        await asyncio.sleep(0.1)
    await client.send_message(chat_id, f"Banned {banned} members successfully. Failed to ban {error_count} members.")

async def perform_unban_all(client: Client, chat_id):
    unbanned = 0
    error_count = 0

    async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.BANNED):
        try:
            await client.unban_chat_member(chat_id, member.user.id)
            unbanned += 1
        except Exception as e:
            error_count += 1
        await asyncio.sleep(0.1)
    await client.send_message(chat_id, f"Unbanned {unbanned} members successfully. Failed to unban {error_count} members.")

async def perform_mute_all(client: Client, chat_id):
    muted = 0
    error_count = 0
    permissions = ChatPermissions()

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        try:
            await client.restrict_chat_member(chat_id, member.user.id, permissions)
            muted += 1
        except Exception as e:
            error_count += 1
        await asyncio.sleep(0.1)
    await client.send_message(chat_id, f"Muted {muted} members successfully. Failed to mute {error_count} members.")

async def perform_unmute_all(client: Client, chat_id):
    unmuted = 0
    error_count = 0
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
    )

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        try:
            await client.restrict_chat_member(chat_id, member.user.id, permissions)
            unmuted += 1
        except Exception as e:
            error_count += 1
        await asyncio.sleep(0.1)
    await client.send_message(chat_id, f"Unmuted {unmuted} members successfully. Failed to unmute {error_count} members.")

async def perform_unpin_all(client: Client, chat_id):
    try:
        await client.unpin_all_chat_messages(chat_id)
        await client.send_message(chat_id, "All messages unpinned successfully.")
    except Exception as e:
        await client.send_message(chat_id, "An error occurred while trying to unpin the messages.")