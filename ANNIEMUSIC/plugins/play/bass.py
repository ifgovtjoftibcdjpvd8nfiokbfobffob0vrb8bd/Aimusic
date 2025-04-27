import os
import tempfile
from pydub import AudioSegment
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from ANNIEMUSIC import app


@app.on_message(filters.command("bass"))
async def bass_boost_command(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.audio or message.reply_to_message.voice):
        return await message.reply_text(
            "🎵 **Please reply to an audio or voice message with `/bass` to apply a bass boost.**",
            parse_mode=ParseMode.MARKDOWN
        )

    try:
        file_path = await client.download_media(
            message.reply_to_message.audio or message.reply_to_message.voice
        )

        boosted_path = apply_bass_boost_with_watermark(file_path)

        await message.reply_audio(
            audio=boosted_path,
            caption="🔊 Bass Boosted",
            reply_to_message_id=message.reply_to_message.message_id
        )

    except Exception as e:
        print(f"[BASS ERROR] {e}")
        await message.reply_text("❌ Failed to process audio. Try again.")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if 'boosted_path' in locals() and os.path.exists(boosted_path):
            os.remove(boosted_path)


def apply_bass_boost_with_watermark(audio_path: str) -> str:
    audio = AudioSegment.from_file(audio_path)

    boosted = (
        audio
        .low_pass_filter(150)
        .high_pass_filter(15)
        .apply_gain(10)
    )

    watermark_text = "Boosted by Annie"
    tts = gTTS(text=watermark_text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_file:
        tts_path = tts_file.name
        tts.save(tts_path)

    watermark = AudioSegment.from_file(tts_path)

    final_audio = boosted + watermark

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
        final_audio.export(out_file.name, format="mp3")
        final_path = out_file.name

    os.remove(tts_path)
    return final_path
