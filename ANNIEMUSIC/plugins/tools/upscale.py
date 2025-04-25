import os

import aiofiles
import aiohttp
import requests
from pyrogram import filters
from pyrogram.types import Message

from ANNIEMUSIC import app
from config import BOT_USERNAME, DEEP_API


async def download_from_url(path: str, url: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(path, mode="wb") as f:
                    await f.write(await resp.read())
                return path
    return None


@app.on_message(filters.command("upscale"))
async def upscale_image(_, message: Message):
    if not DEEP_API:
        return await message.reply_text("🚫 ᴍɪssɪɴɢ ᴅᴇᴇᴘᴀɪ ᴀᴘɪ ᴋᴇʏ.")

    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await message.reply_text("📎 ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ.")

    status = await message.reply_text("🔄 ᴜᴘsᴄᴀʟɪɴɢ ɪᴍᴀɢᴇ...")

    try:
        local_path = await reply.download()
        resp = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={"image": open(local_path, "rb")},
            headers={"api-key": DEEP_API},
        ).json()

        image_url = resp.get("output_url")
        if not image_url:
            return await status.edit("❌ ᴜᴘsᴄᴀʟᴇ ʀᴇǫᴜᴇsᴛ ꜰᴀɪʟᴇᴅ.")

        final_path = await download_from_url(local_path, image_url)
        if not final_path:
            return await status.edit("❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇsᴜʟᴛ.")

        await status.delete()
        await message.reply_document(final_path)

    except Exception as e:
        await status.edit(f"⚠️ ᴇʀʀᴏʀ: `{str(e)}`")


@app.on_message(filters.command("getdraw"))
async def draw_image(_, message: Message):
    if not DEEP_API:
        return await message.reply_text("🚫 ᴅᴇᴇᴘᴀɪ ᴀᴘɪ ᴋᴇʏ ɪs ᴍɪssɪɴɢ.")

    reply = message.reply_to_message
    query = None

    if reply and reply.text:
        query = reply.text
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]

    if not query:
        return await message.reply_text("💬 ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ.")

    status = await message.reply_text("🎨 ɢᴇɴᴇʀᴀᴛɪɴɢ ɪᴍᴀɢᴇ...")
    user_id = message.from_user.id
    chat_id = message.chat.id
    temp_path = f"cache/{user_id}_{chat_id}_{message.id}.png"

    try:
        resp = requests.post(
            "https://api.deepai.org/api/text2img",
            data={"text": query, "grid_size": "1", "image_generator_version": "hd"},
            headers={"api-key": DEEP_API},
        ).json()

        image_url = resp.get("output_url")
        if not image_url:
            return await status.edit("❌ ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ɪᴍᴀɢᴇ.")

        final_path = await download_from_url(temp_path, image_url)
        if not final_path:
            return await status.edit("❌ ᴇʀʀᴏʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ.")

        await status.delete()
        await message.reply_photo(final_path, caption=f"`{query}`")

    except Exception as e:
        await status.edit(f"⚠️ ᴇʀʀᴏʀ: `{str(e)}`")
