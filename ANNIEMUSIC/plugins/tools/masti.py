import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ANNIEMUSIC import app
from config import SUPPORT_CHAT


BUTTON = [[InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}")]]


CUTIE = "https://graph.org/file/24375c6e54609c0e4621c.mp4"
HORNY = "https://graph.org/file/eaa834a1cbfad29bd1fe4.mp4"
HOT = "https://graph.org/file/745ba3ff07c1270958588.mp4"
SEMXY = "https://graph.org/file/58da22eb737af2f8963e6.mp4"
LESBIAN = "https://graph.org/file/ff258085cf31f5385db8a.mp4"
GAY = "https://graph.org/file/850290f1f974c5421ce54.mp4"
BIGBALL = "https://i.gifer.com/8ZUg.gif"
LANGD = "https://telegra.ph/file/423414459345bf18310f5.gif"


def get_user_mention(message: Message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    return f"[{user.first_name}](tg://user?id={user.id})"


def get_reply_id(message: Message):
    return message.reply_to_message.message_id if message.reply_to_message else None


@app.on_message(filters.command("cutie"))
async def cutie(_, message):
    mention = get_user_mention(message)
    percent = random.randint(1, 100)
    text = f"🍑 {mention} ɪꜱ {percent}% ᴄᴜᴛᴇ ʙᴀʙʏ🥀"
    await app.send_document(message.chat.id, CUTIE, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("horny"))
async def horny(_, message):
    mention = get_user_mention(message)
    percent = random.randint(1, 100)
    text = f"🔥 {mention} ɪꜱ {percent}% ʜᴏʀɴʏ!"
    await app.send_document(message.chat.id, HORNY, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("hot"))
async def hot(_, message):
    mention = get_user_mention(message)
    percent = random.randint(1, 100)
    text = f"🔥 {mention} ɪꜱ {percent}% ʜᴏᴛ!"
    await app.send_document(message.chat.id, HOT, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("sexy"))
async def sexy(_, message):
    mention = get_user_mention(message)
    percent = random.randint(1, 100)
    text = f"💋 {mention} ɪꜱ {percent}% ꜱᴇxʏ!"
    await app.send_document(message.chat.id, SEMXY, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("gay"))
async def gay(_, message):
    mention = get_user_mention(message)
    percent = random.randint(1, 100)
    text = f"🍷 {mention} ɪꜱ {percent}% ɢᴀʏ!"
    await app.send_document(message.chat.id, GAY, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("lesbian"))
async def lesbian(_, message):
    mention = get_user_mention(message)
    percent = random.randint(1, 100)
    text = f"💜 {mention} ɪꜱ {percent}% ʟᴇꜱʙɪᴀɴ!"
    await app.send_document(message.chat.id, LESBIAN, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("boob"))
async def boob(_, message):
    mention = get_user_mention(message)
    size = random.randint(1, 100)
    text = f"🍒 {mention}ꜱ ʙᴏᴏʙ ꜱɪᴢᴇ ɪꜱ {size}!"
    await app.send_document(message.chat.id, BIGBALL, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))


@app.on_message(filters.command("cock"))
async def cock(_, message):
    mention = get_user_mention(message)
    size = random.randint(1, 100)
    text = f"🍆 {mention} ᴄᴏᴄᴋ ꜱɪᴢᴇ ɪꜱ {size}ᴄᴍ!"
    await app.send_document(message.chat.id, LANGD, caption=text, reply_markup=InlineKeyboardMarkup(BUTTON), reply_to_message_id=get_reply_id(message))