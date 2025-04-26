from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
import asyncio
import datetime
from functools import wraps
from ANNIEMUSIC import app

def mention(user_id, name):
    return f"[{name}](tg://user?id={user_id})"

def admin_required(func):
    @wraps(func)
    async def wrapper(client, message):
        member = await message.chat.get_member(message.from_user.id)
        if (
            member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            and member.privileges.can_restrict_members
        ):
            return await func(client, message)
        else:
            await message.reply_text("You don't have permission to perform this action.")
            return
    return wrapper

async def extract_user_and_reason(message, client):
    args = message.text.split()
    reason = None
    user = None
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if len(args) > 1:
            reason = message.text.split(None, 1)[1]
    elif len(args) > 1:
        user_arg = args[1]
        reason = message.text.partition(args[1])[2].strip() or None
        try:
            user = await client.get_users(user_arg)
        except Exception:
            await message.reply_text("I can't find that user.")
            return None, None, None
    else:
        await message.reply_text("Please specify a user or reply to a user's message.")
        return None, None, None
    return user.id, user.first_name, reason

def parse_time(time_str):
    unit = time_str[-1]
    if unit not in ['s', 'm', 'h', 'd']:
        return None
    try:
        time_amount = int(time_str[:-1])
    except ValueError:
        return None
    if unit == 's':
        return datetime.timedelta(seconds=time_amount)
    elif unit == 'm':
        return datetime.timedelta(minutes=time_amount)
    elif unit == 'h':
        return datetime.timedelta(hours=time_amount)
    elif unit == 'd':
        return datetime.timedelta(days=time_amount)
    return None

@app.on_message(filters.command("ban"))
@admin_required
async def ban_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        user_mention = mention(user_id, first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was banned by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("unban"))
@admin_required
async def unban_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        user_mention = mention(user_id, first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was unbanned by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("mute"))
@admin_required
async def mute_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    try:
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
        user_mention = mention(user_id, first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was muted by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with mute permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("unmute"))
@admin_required
async def unmute_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        user_mention = mention(user_id, first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was unmuted by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with unmute permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("tmute"))
@admin_required
async def tmute_command_handler(client, message):
    args = message.text.split()
    if message.reply_to_message and len(args) > 1:
        user = message.reply_to_message.from_user
        time_str = args[1]
        reason = message.text.partition(args[1])[2].strip() or None
    elif len(args) > 2:
        user_arg = args[1]
        time_str = args[2]
        reason = message.text.partition(args[2])[2].strip() or None
        try:
            user = await client.get_users(user_arg)
        except Exception:
            await message.reply_text("I can't find that user.")
            return
    else:
        await message.reply_text("Usage: /tmute <user> <time> [reason]\nTime format: 10m, 1h, 2d")
        return

    duration = parse_time(time_str)
    if not duration:
        await message.reply_text("Invalid time format. Use s, m, h, or d for seconds, minutes, hours, or days respectively.")
        return

    until_date = datetime.datetime.now(datetime.timezone.utc) + duration
    try:
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(), until_date=until_date)
        user_mention = mention(user.id, user.first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was muted by {admin_mention} for {time_str}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with mute permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("kick"))
@admin_required
async def kick_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("I cannot kick an admin.")
            return
        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(0.1)
        await client.unban_chat_member(message.chat.id, user_id)
        user_mention = mention(user_id, first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was kicked by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot kick an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

# New commands implementation

@app.on_message(filters.command("dban"))
@admin_required
async def dban_command_handler(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to delete it and ban the user.")
        return
    
    user = message.reply_to_message.from_user
    reason = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    
    try:
        # Delete the replied message
        await message.reply_to_message.delete()
        # Ban the user
        await client.ban_chat_member(message.chat.id, user.id)
        
        user_mention = mention(user.id, user.first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was banned by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban and delete message permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("sban"))
@admin_required
async def sban_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    
    try:
        # Delete the command message
        await message.delete()
        # Ban the user silently
        await client.ban_chat_member(message.chat.id, user_id)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban and delete message permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("tban"))
@admin_required
async def tban_command_handler(client, message):
    args = message.text.split()
    if message.reply_to_message and len(args) > 1:
        user = message.reply_to_message.from_user
        time_str = args[1]
        reason = message.text.partition(args[1])[2].strip() or None
    elif len(args) > 2:
        user_arg = args[1]
        time_str = args[2]
        reason = message.text.partition(args[2])[2].strip() or None
        try:
            user = await client.get_users(user_arg)
        except Exception:
            await message.reply_text("I can't find that user.")
            return
    else:
        await message.reply_text("Usage: /tban <user> <time> [reason]\nTime format: 10m, 1h, 2d")
        return

    duration = parse_time(time_str)
    if not duration:
        await message.reply_text("Invalid time format. Use s, m, h, or d for seconds, minutes, hours, or days respectively.")
        return

    until_date = datetime.datetime.now(datetime.timezone.utc) + duration
    try:
        await client.ban_chat_member(message.chat.id, user.id, until_date=until_date)
        user_mention = mention(user.id, user.first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was banned by {admin_mention} for {time_str}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("kickme"))
async def kickme_command_handler(client, message):
    try:
        user = message.from_user
        user_mention = mention(user.id, user.first_name)
        
        # Check if the user is an admin
        member = await message.chat.get_member(user.id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("You're an admin, I won't kick you.")
            return
            
        await message.reply_text("Kicked so hard, your ancestors felt it. 👟💥")
        await client.ban_chat_member(message.chat.id, user.id)
        await asyncio.sleep(0.1)
        await client.unban_chat_member(message.chat.id, user.id)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions to kick you.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("dmute"))
@admin_required
async def dmute_command_handler(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to delete it and mute the user.")
        return
    
    user = message.reply_to_message.from_user
    reason = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    
    try:
        # Delete the replied message
        await message.reply_to_message.delete()
        # Mute the user
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        
        user_mention = mention(user.id, user.first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was muted by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with mute and delete message permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("smute"))
@admin_required
async def smute_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    
    try:
        # Delete the command message
        await message.delete()
        # Mute the user silently
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with mute and delete message permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("dkick"))
@admin_required
async def dkick_command_handler(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to delete it and kick the user.")
        return
    
    user = message.reply_to_message.from_user
    reason = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    
    try:
        # Delete the replied message
        await message.reply_to_message.delete()
        
        # Check if user is admin
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("I cannot kick an admin.")
            return
            
        # Kick the user (ban and then unban)
        await client.ban_chat_member(message.chat.id, user.id)
        await asyncio.sleep(0.1)
        await client.unban_chat_member(message.chat.id, user.id)
        
        user_mention = mention(user.id, user.first_name)
        admin_mention = mention(message.from_user.id, message.from_user.first_name)
        msg = f"{user_mention} was kicked by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban and delete message permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot kick an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("skick"))
@admin_required
async def skick_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return
    
    try:
        # Delete the command message
        await message.delete()
        
        # Check if user is admin
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            # Send a private error message that will be deleted
            error_msg = await message.reply_text("I cannot kick an admin.")
            await asyncio.sleep(3)
            await error_msg.delete()
            return
            
        # Kick the user silently (ban and then unban)
        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(0.1)
        await client.unban_chat_member(message.chat.id, user_id)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban and delete message permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot kick an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
