from pyrogram import Client, filters
from pyrogram.types import Message

from ANNIEMUSIC import app
from config import BOT_USERNAME, OWNER_ID


@app.on_message(filters.command(["post"], prefixes=["/", "."]) & filters.user(OWNER_ID))
async def copy_messages(_, message):
    if message.reply_to_message:
        destination_group_id = -1002055415055

        await message.reply_to_message.copy(destination_group_id)
        await message.reply("ᴘᴏsᴛ sᴜᴄᴄᴇssғᴜʟ ᴅᴏɴᴇ ")
