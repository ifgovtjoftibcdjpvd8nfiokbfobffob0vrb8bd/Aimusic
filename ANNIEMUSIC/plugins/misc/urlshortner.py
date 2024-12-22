from pyrogram import Client, enums, filters, idle
from requests import get
import asyncio
from ANNIEMUSIC import app as app
from pyrogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm
from pyrogram.enums import ChatAction
import pyshorteners

shortener = pyshorteners.Shortener()

@app.on_message(filters.command(["short"]))
async def short_urls(bot, message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    if len(message.command) < 2:
        return await message.reply_text("**Example:**\n\n`/short [url]`")
    link = message.command[1]
    try:
        tiny_link = shortener.tinyurl.short(link)
        dagd_link = shortener.dagd.short(link)
        clckru_link = shortener.clckru.short(link)
        url = [[ikb("Tiny Url", url=tiny_link)], [ikb("Dagd Url", url=dagd_link), ikb("Clckru Url", url=clckru_link)]]
        await message.reply_text("Here are few shortened links:", reply_markup=ikm(url))
    except Exception as e:
        await message.reply_text("Either the link is already shortened or is invalid.")

@app.on_message(filters.command(["unshort"]))
async def unshort(bot, message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    if len(message.command) < 2:
        return await message.reply_text("**Example:**\n\n`/unshort [short-url]`")
    link = message.text.split(' ')[1]
    try:
        x = get(link, allow_redirects=True).url
        url = [[ikb("View Link", url=x)]]
        await message.reply_text(f"Here's the unshortened link:\n`{x}`", reply_markup=ikm(url))
    except Exception as e:
        await message.reply_text(f"Error: {e}")
