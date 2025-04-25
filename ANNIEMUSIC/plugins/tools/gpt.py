import os
from gtts import gTTS

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from lexica import AsyncClient, languageModels, Messages
from ANNIEMUSIC import app


def extract_content(response) -> str:
    if isinstance(response, dict):
        return response.get("content", "No content available.")
    return str(response)


async def get_gpt_response(prompt: str) -> str:
    lexica_client = AsyncClient()
    try:
        messages = [Messages(content=prompt, role="user")]
        response = await lexica_client.ChatCompletion(messages, languageModels.gpt)
        return extract_content(response)
    finally:
        await lexica_client.close()


@app.on_message(filters.command(["arvis"], prefixes=["j", "J"]))
async def jarvis_handler(client: Client, message: Message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    if len(message.command) < 2:
        return await message.reply_text(
            f"Hello {message.from_user.first_name}, I am Jarvis. How can I help you today?"
        )

    query = message.text.split(" ", 1)[1]
    try:
        content = await get_gpt_response(query)
        await message.reply_text(content)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command(["chatgpt", "ai", "ask", "Master"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def chatgpt_handler(client: Client, message: Message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    if len(message.command) < 2:
        return await message.reply_text(
            f"Hello {message.from_user.first_name}, how can I assist you today?"
        )

    query = message.text.split(" ", 1)[1]
    try:
        content = await get_gpt_response(query)
        await message.reply_text(content)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command(["ssis"], prefixes=["a", "A"]))
async def annie_tts_handler(client: Client, message: Message):
    await client.send_chat_action(message.chat.id, ChatAction.RECORD_AUDIO)

    if len(message.command) < 2:
        return await message.reply_text(
            f"Hello {message.from_user.first_name}, I am Annie. How can I assist you today?"
        )

    query = message.text.split(" ", 1)[1]
    audio_file = "response.mp3"

    try:
        content = await get_gpt_response(query)
        tts = gTTS(text=content, lang="en")
        tts.save(audio_file)

        await client.send_voice(chat_id=message.chat.id, voice=audio_file)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
