
import os
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ANNIEMUSIC import app

def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    files = {"fileToUpload": open(file_path, "rb")}
    response = requests.post(url, data={"reqtype": "fileupload", "json": "true"}, files=files)
    return (response.status_code == 200, response.text.strip() if response.status_code == 200 else f"Error: {response.status_code} - {response.text}")

@app.on_message(filters.command(["tgm", "tgt", "telegraph"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❍ Please reply to a media to upload on Telegraph.")

    media = message.reply_to_message
    file_size = getattr(media, 'photo', None) or getattr(media, 'video', None) or getattr(media, 'document', None)
    if file_size and file_size.file_size > 200 * 1024 * 1024:
        return await message.reply_text("Please provide a media file under 200MB.")

    text = await message.reply("❍ Processing...")

    async def progress(current, total):
        try:
            await text.edit_text(f"❍ Downloading... {current * 100 / total:.1f}%")
        except Exception:
            pass

    try:
        local_path = await media.download(progress=progress)
        await text.edit_text("❍ Uploading to Telegraph...")
        success, upload_path = upload_file(local_path)

        if success:
            await text.edit_text(
                f"❍ | [Tap the link]({upload_path})",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❍ TeleGraph Uploader ❍", url=upload_path)]]
                ),
            )
        else:
            await text.edit_text(f"❍ An error occurred while uploading your file\n{upload_path}")

        os.remove(local_path)
    except Exception as e:
        await text.edit_text(f"❍ File upload failed\n\n❍ <i>Reason: {e}</i>")
        try:
            os.remove(local_path)
        except Exception:
            pass
