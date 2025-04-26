"""
Mass/group administration commands module for ANNIEMUSIC.

Commands (owner or sudoers only):
    • /kickall   – kick all non‑admin members
    • /banall    – ban all non‑admin members
    • /unbanall  – unban all previously banned members
    • /muteall   – mute all non‑admin members
    • /unmuteall – unmute all non‑admin members
    • /unpinall  – unpin all messages

Each command asks for a Yes/No confirmation via inline buttons.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Dict

from pyrogram import filters, enums
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.permissions import is_owner_or_sudoer, mention

log = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────
SLEEP_BETWEEN_ACTIONS = 0.05  # generic throttle for Telegram API limits
SLEEP_AFTER_RESTRICT = 0.1    # extra pause after kick–unban combo

MASS_COMMANDS = (
    "kickall",
    "banall",
    "unbanall",
    "muteall",
    "unmuteall",
    "unpinall",
)

# The bot privilege property required for each command
PERMISSION_REQUIREMENTS: Dict[str, str] = {
    "kickall": "can_restrict_members",
    "banall": "can_restrict_members",
    "unbanall": "can_restrict_members",
    "muteall": "can_restrict_members",
    "unmuteall": "can_restrict_members",
    "unpinall": "can_pin_messages",
}

# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────

def confirmation_keyboard(cmd: str) -> InlineKeyboardMarkup:
    """Return a Yes/No inline keyboard for confirmations."""
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Yes", callback_data=f"{cmd}:yes"),
            InlineKeyboardButton("✖️ No", callback_data=f"{cmd}:no"),
        ]]
    )


async def iterate_normal_members(client, chat_id: int):
    """Yield user IDs for every non‑bot, non‑admin member in *chat_id*."""
    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ):
            continue
        yield member.user.id


# ────────────────────────────────────────────────────────────
# Message handler – ask confirmation
# ────────────────────────────────────────────────────────────


@app.on_message(filters.command(list(MASS_COMMANDS)) & filters.group)
async def ask_mass_confirm(client: app, message: Message) -> None:
    """Prompt the owner/sudoer for confirmation before running a mass command."""
    cmd: str = message.command[0]
    has_perm, owner = await is_owner_or_sudoer(client, message.chat.id, message.from_user.id)

    if not has_perm:
        owner_m = mention(owner.id, owner.first_name) if owner else "the owner"
        return await message.reply_text(f"❌ Only {owner_m} may run “{cmd}”.")

    await message.reply_text(
        f"⚠️ {message.from_user.mention}, confirm *{cmd}* for this chat?",
        reply_markup=confirmation_keyboard(cmd),
        parse_mode=enums.ParseMode.MARKDOWN,
    )


# ────────────────────────────────────────────────────────────
# Callback handler – perform the action
# ────────────────────────────────────────────────────────────


@app.on_callback_query(filters.regex(rf"^({'|'.join(MASS_COMMANDS)}):(yes|no)$"))
async def handle_mass_confirm(client: app, cb: CallbackQuery) -> None:
    cmd, decision = cb.data.split(":")
    chat_id = cb.message.chat.id

    has_perm, _ = await is_owner_or_sudoer(client, chat_id, cb.from_user.id)
    if not has_perm:
        return await cb.answer("Only the group owner can confirm.", show_alert=True)

    if decision == "no":
        return await cb.message.edit(f"❌ *{cmd}* canceled.", parse_mode=enums.ParseMode.MARKDOWN)

    bot_member = await client.get_chat_member(chat_id, client.me.id)
    if not getattr(bot_member.privileges, PERMISSION_REQUIREMENTS[cmd], False):
        return await cb.message.edit("❌ I lack the necessary permissions to continue.")

    await cb.message.edit(f"⏳ Running *{cmd}* …", parse_mode=enums.ParseMode.MARKDOWN)

    try:
        await ACTION_MAP[cmd](client, chat_id)
        await cb.message.edit(f"✅ *{cmd}* completed.", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("Error during %s: %s", cmd, exc)
        await cb.message.edit(f"❌ Error during *{cmd}*:\n`{exc}`", parse_mode=enums.ParseMode.MARKDOWN)


# ────────────────────────────────────────────────────────────
# Mass action implementations
# ────────────────────────────────────────────────────────────


async def kickall(client, chat_id: int) -> None:
    kicked = failed = 0
    async for user_id in iterate_normal_members(client, chat_id):
        try:
            await client.ban_chat_member(chat_id, user_id)
            await asyncio.sleep(SLEEP_AFTER_RESTRICT)
            await client.unban_chat_member(chat_id, user_id)
            kicked += 1
        except Exception:
            failed += 1
        await asyncio.sleep(SLEEP_BETWEEN_ACTIONS)
    await client.send_message(chat_id, f"Kicked: {kicked}\nFailed: {failed}")


async def banall(client, chat_id: int) -> None:
    banned = failed = 0
    async for user_id in iterate_normal_members(client, chat_id):
        try:
            await client.ban_chat_member(chat_id, user_id)
            banned += 1
        except Exception:
            failed += 1
        await asyncio.sleep(SLEEP_BETWEEN_ACTIONS)
    await client.send_message(chat_id, f"Banned: {banned}\nFailed: {failed}")


async def unbanall(client, chat_id: int) -> None:
    unbanned = failed = 0
    async for m in client.get_chat_members(chat_id, filter=ChatMembersFilter.BANNED):
        try:
            await client.unban_chat_member(chat_id, m.user.id)
            unbanned += 1
        except Exception:
            failed += 1
        await asyncio.sleep(SLEEP_BETWEEN_ACTIONS)
    await client.send_message(chat_id, f"Unbanned: {unbanned}\nFailed: {failed}")


async def muteall(client, chat_id: int) -> None:
    muted = failed = 0
    perms = ChatPermissions()  # fully restrictive
    async for user_id in iterate_normal_members(client, chat_id):
        try:
            await client.restrict_chat_member(chat_id, user_id, perms)
            muted += 1
        except Exception:
            failed += 1
        await asyncio.sleep(SLEEP_BETWEEN_ACTIONS)
    await client.send_message(chat_id, f"Muted: {muted}\nFailed: {failed}")


async def unmuteall(client, chat_id: int) -> None:
    unmuted = failed = 0
    perms = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
    )
    async for user_id in iterate_normal_members(client, chat_id):
        try:
            await client.restrict_chat_member(chat_id, user_id, perms)
            unmuted += 1
        except Exception:
            failed += 1
        await asyncio.sleep(SLEEP_BETWEEN_ACTIONS)
    await client.send_message(chat_id, f"Unmuted: {unmuted}\nFailed: {failed}")


async def unpinall(client, chat_id: int) -> None:
    try:
        await client.unpin_all_chat_messages(chat_id)
        await client.send_message(chat_id, "All messages unpinned.")
    except Exception as exc:
        await client.send_message(chat_id, f"Failed to unpin messages:\n{exc}")


# Map commands to their handler functions
ACTION_MAP: Dict[str, Callable[[app, int], None]] = {
    "kickall": kickall,
    "banall": banall,
    "unbanall": unbanall,
    "muteall": muteall,
    "unmuteall": unmuteall,
    "unpinall": unpinall,
}
