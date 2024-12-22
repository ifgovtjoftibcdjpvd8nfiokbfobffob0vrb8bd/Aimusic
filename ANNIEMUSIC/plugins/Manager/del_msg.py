import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery,
    Message, ChatPrivileges, ChatInviteLink
)
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from pyrogram.errors import (
    UserNotParticipant, ChatAdminRequired, FloodWait, PeerIdInvalid,
    InviteHashExpired, InviteHashInvalid, UserAlreadyParticipant, ChatAdminInviteRequired
)
from ANNIEMUSIC.utils.database import get_assistant
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
        logging.error(f"Error getting group owner: {e}")
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
        bot_member = await client.get_chat_member(chat_id, "me")
        return bot_member
    except Exception as e:
        logging.error(f"Error getting bot member: {e}")
        return None


@app.on_message(filters.command("deleteall", prefixes=["/", "!", "."]) & filters.group)
async def deleteall(client: Client, message: Message):
    logging.info(f"/deleteall command received from {message.from_user.id} in chat {message.chat.id}")

    chat_id = message.chat.id
    user_id = message.from_user.id

    resp = await message.reply_text(f"Hey {message.from_user.mention}, 'deleteall' checking...")

    bot_member = await get_bot_member(client, chat_id)
    if not bot_member:
        await resp.edit("I couldn't find myself in the group.")
        return
    if bot_member.status != ChatMemberStatus.ADMINISTRATOR or not bot_member.privileges.can_delete_messages or not bot_member.privileges.can_invite_users or not bot_member.privileges.can_promote_members:
        await resp.edit(
            "I don't have enough permissions to perform delete all messages!\n"
            "Mass Action requires the bot to be an admin with 'Delete messages', 'Invite users', and 'Add new admins' permissions."
        )
        return

    await resp.delete()

    await message.reply(
        f"{message.from_user.mention}, are you sure you want to delete all group messages?",
        reply_markup=get_keyboard("deleteall")
    )

@app.on_callback_query(filters.regex(r"^deleteall_(yes|no)$"))
async def handle_deleteall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    is_owner, owner_user = await is_owner_or_sudoer(client, chat_id, user_id)
    if not is_owner:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return

    if callback_query.data == "deleteall_yes":
        await callback_query.answer("Delete all process started...", show_alert=True)

        assistant = await get_assistant(chat_id)
        ass_me = await assistant.get_me()
        ass_id = ass_me.id

        try:
            assistant_member = await client.get_chat_member(chat_id, ass_id)
            assistant_status = assistant_member.status
            if assistant_status == ChatMemberStatus.BANNED:
                logging.info("Assistant is banned. Unbanning now...")
                try:
                    await client.unban_chat_member(chat_id, ass_id)
                    assistant_in_chat = False
                except Exception as e:
                    await callback_query.message.reply(f"Failed to unban assistant: {e}")
                    return
            elif assistant_status in [ChatMemberStatus.RESTRICTED, ChatMemberStatus.LEFT]:
                assistant_in_chat = False
            else:
                assistant_in_chat = True
        except UserNotParticipant:
            assistant_in_chat = False
        except PeerIdInvalid:
            assistant_in_chat = False

        if not assistant_in_chat:
            logging.info("Assistant not in group. Generating invite link.")
            try:
                invite_link: ChatInviteLink = await client.create_chat_invite_link(chat_id, member_limit=1)

                await assistant.join_chat(invite_link.invite_link)
                logging.info("Assistant joined the group via invite link.")
                await asyncio.sleep(2)
            except ChatAdminRequired:
                await callback_query.message.reply("Failed to create invite link. Bot lacks sufficient permissions.")
                return
            except InviteHashInvalid:
                await callback_query.message.reply("Failed to create a valid invite link.")
                return
            except Exception as e:
                await callback_query.message.reply(f"Failed to invite assistant: {e}")
                return

        try:
            await client.get_users(ass_id)
        except PeerIdInvalid:
            logging.info("Bot does not know the assistant yet. Making assistant send a message...")
            await assistant.send_message(chat_id, "Assistant here to help!")
            await asyncio.sleep(1)
            await client.get_users(ass_id)

        try:
            privileges = ChatPrivileges(
                can_delete_messages=True
            )
            await client.promote_chat_member(chat_id, ass_id, privileges=privileges)
        except ChatAdminRequired:
            await callback_query.message.reply("Failed to promote assistant. Bot lacks sufficient permissions.")
            return
        except Exception as e:
            await callback_query.message.reply(f"Failed to promote assistant: {e}")
            return

        batch_size = 100
        message_ids = []

        try:
            status_message_id = callback_query.message.id

            await callback_query.message.edit("Deleting all messages...")

            async for msg in assistant.get_chat_history(chat_id):
                if msg.id == status_message_id:
                    continue

                message_ids.append(msg.id)
                if len(message_ids) == batch_size:
                    try:
                        await assistant.delete_messages(chat_id, message_ids)
                        message_ids = []
                    except FloodWait as e:
                        logging.warning(f"Flood wait: sleeping for {e.value} seconds")
                        await asyncio.sleep(e.value)
                        continue
                    except Exception as e:
                        logging.error(f"Failed to delete messages {message_ids}: {e}")
                        message_ids = []
                        continue
            if message_ids:
                try:
                    await assistant.delete_messages(chat_id, message_ids)
                except Exception as e:
                    logging.error(f"Failed to delete messages {message_ids}: {e}")

            try:
                privileges = ChatPrivileges()
                await client.promote_chat_member(chat_id, ass_id, privileges=privileges)
            except Exception as e:
                logging.error(f"Failed to demote assistant: {e}")

            try:
                await assistant.leave_chat(chat_id)
                logging.info("Assistant left the chat.")
            except Exception as e:
                logging.error(f"Failed to make assistant leave the chat: {e}")

            await callback_query.message.edit("All messages deleted successfully.")
        except Exception as e:
            await callback_query.message.edit(f"An error occurred: {str(e)}")

    elif callback_query.data == "deleteall_no":
        await callback_query.message.edit("Delete all process canceled.")
