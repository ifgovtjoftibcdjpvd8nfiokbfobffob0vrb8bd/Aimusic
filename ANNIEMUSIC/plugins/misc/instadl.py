import httpx
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from ANNIEMUSIC import app

DOWNLOADING_STICKER_ID = "CAACAgEAAx0CfD7LAgACO7xmZzb83lrLUVhxtmUaanKe0_ionAAC-gADUSkNORIJSVEUKRrhHgQ"
API_URL = "https://karma-api2.vercel.app/instadl"

@app.on_message(filters.command(["ig", "insta"]))
async def instadl_command_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:** `/insta [Instagram URL]`",
            parse_mode=ParseMode.MARKDOWN
        )

    link = message.command[1]
    sticker = None

    try:
        try:
            sticker = await message.reply_sticker(DOWNLOADING_STICKER_ID)
        except Exception:
            pass

        async with httpx.AsyncClient(timeout=15.0) as http:
            response = await http.get(API_URL, params={"url": link})
            response.raise_for_status()
            data = response.json()

        content_url = data.get("content_url")

        if not content_url:
            return await message.reply_text(
                "⚠️ Unable to fetch content.\nMake sure the link is public and valid."
            )

        if "video" in content_url:
            await message.reply_video(content_url)
        elif "photo" in content_url or content_url.endswith((".jpg", ".png", ".jpeg")):
            await message.reply_photo(content_url)
        else:
            await message.reply_text("❌ Unsupported media type returned.")

    except Exception as e:
        print(f"[ERROR] insta downloader: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

    finally:
        if sticker:
            await sticker.delete()
