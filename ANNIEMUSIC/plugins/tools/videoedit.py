import os
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pydub import AudioSegment
from ANNIEMUSIC import app


# ─── /remove Command Handler ──────────────────────────────────

@app.on_message(filters.command("remove") & filters.reply)
async def remove_media(_, message: Message):
    replied = message.reply_to_message
    if not (replied and replied.video):
        return await message.reply_text("❌ Please reply to a video message.")
    if len(message.command) < 2:
        return await message.reply_text("ℹ️ Use `/remove audio` or `/remove video`.", quote=True)

    command = message.command[1].lower()
    processing_msg = await message.reply_text("🔧 Processing video...")

    try:
        file_path = await replied.download(file_name="media_input.mp4")

        if command == "audio":
            output_audio = "output_audio.mp3"
            def process_audio():
                audio = AudioSegment.from_file(file_path)
                audio = audio.set_channels(1)
                audio.export(output_audio, format="mp3")
            await asyncio.to_thread(process_audio)
            await app.send_audio(message.chat.id, output_audio, caption="🎧 Audio extracted.")
            os.remove(output_audio)

        elif command == "video":
            output_video = "output_video.mp4"
            def process_video():
                os.system(f"ffmpeg -i {file_path} -c copy -an {output_video}")
            await asyncio.to_thread(process_video)
            await app.send_video(message.chat.id, output_video, caption="🎞️ Video with no audio.")
            os.remove(output_video)

        else:
            return await message.reply_text("❌ Invalid command. Use `/remove audio` or `/remove video`.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
    finally:
        await processing_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
