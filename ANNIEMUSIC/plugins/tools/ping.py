from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import *
from ANNIEMUSIC import app
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.utils import bot_sys_stats
from ANNIEMUSIC.utils.decorators.language import language
from ANNIEMUSIC.utils.inline import supp_markup
from config import BANNED_USERS


@app.on_message(filters.command("ping", prefixes=["/"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_text("ᴘɪɴɢɪɴɢ...")
    
    pytgping = await JARVIS.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    
    await response.edit_text(
        f"""ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ! 🖤
ᴛɪᴍᴇ ᴛᴀᴋᴇɴ: `{resp}` ms
ᴜᴘᴛɪᴍᴇ: `{UP}`""",
        reply_markup=supp_markup(_),
    )