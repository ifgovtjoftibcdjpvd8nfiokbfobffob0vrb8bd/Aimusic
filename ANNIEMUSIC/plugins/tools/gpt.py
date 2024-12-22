import nest_asyncio
import os
import requests
from gtts import gTTS
from pyrogram import filters
from pyrogram.enums import ChatAction
from ANNIEMUSIC import app
from g4f.client import Client
from config import OWNER_ID
from pyrogram.enums import ParseMode

nest_asyncio.apply()

API_URL = "https://sugoi-api.vercel.app/search"

client = Client()

@app.on_message(filters.command(["arvis"], prefixes=["j", "J"]))
async def chat_arvis(app, message):

    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name

        if len(message.command) < 2:
            await message.reply_text(f"Hello {name}, I am Jarvis. How can I help you today?")
            return

        query = message.text.split(' ', 1)[1]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
        )
        reply_text = response.choices[0].message.content
        await message.reply_text(reply_text)
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command(["chatgpt", "ai", "ask", "Master"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def chat_gpt(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            await message.reply_text("Hello sir, I am Jarvis. How can I help you today?")
            return

        query = message.text.split(' ', 1)[1]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
        )
        reply_text = response.choices[0].message.content
        await message.reply_text(reply_text)
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command(["iri"], prefixes=["s", "S"]))
async def chat_annie(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name

        if len(message.command) < 2:
            await message.reply_text(f"Hello {name}, I am Siri. How can I help you today?")
            return

        query = message.text.split(' ', 1)[1]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
        )
        reply_text = response.choices[0].message.content
        tts = gTTS(reply_text, lang='en')
        tts.save('siri.mp3')
        await app.send_voice(chat_id=message.chat.id, voice='siri.mp3')
        os.remove('siri.mp3')
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command(["bing"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def bing_search(app, message):
    try:
        if len(message.command) == 1:
            await message.reply_text("Please provide a keyword to search.")
            return

        keyword = " ".join(message.command[1:])
        response = requests.get(API_URL, params={"keyword": keyword})

        if response.status_code == 200:
            results = response.json()
            if not results:
                await message.reply_text("No results found.")
                return

            message_text = "\n\n".join(f"{res.get('title', '')}\n{res.get('link', '')}" for res in results[:7])
            await message.reply_text(message_text.strip())
        else:
            await message.reply_text("Sorry, something went wrong with the search.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")