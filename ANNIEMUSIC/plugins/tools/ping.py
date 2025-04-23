from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from ANNIEMUSIC import app
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.utils import bot_sys_stats
from ANNIEMUSIC.utils.decorators.language import language
from config import BANNED_USERS


@app.on_message(filters.command("ping", prefixes=["/"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_text("🏓 ᴘɪɴɢɪɴɢ ʙᴀʙʏ....")
    
    pytgping = await JARVIS.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    
    await response.edit_text(
        "ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ! 🖤\n"
        "<b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{}</code> <code>ms</code>\n"
        "<b>ᴜᴘᴛɪᴍᴇ:</b> <code>{}</code>".format(resp, UP)
    )
