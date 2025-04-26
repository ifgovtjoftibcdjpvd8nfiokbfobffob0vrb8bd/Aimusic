import os
import asyncio
import re
import aiohttp
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from ANNIEMUSIC import app, YouTube
from config import BANNED_USERS, SONG_DOWNLOAD_DURATION_LIMIT, API_URL, API_KEY
from ANNIEMUSIC.utils.decorators.language import language

SONG_COMMAND = ["song"]

@app.on_message(
    filters.command(SONG_COMMAND)
    & ~BANNED_USERS
)
@language
async def song_command(client, message: Message, _):
    # Check if query is provided
    if len(message.command) < 2:
        return await message.reply_text(_["song_2"])
    
    # Get the search query
    query = message.text.split(None, 1)[1]
    mystic = await message.reply_text(_["play_1"])
    
    try:
        # Get video details
        (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        ) = await YouTube.details(query)
    except Exception as e:
        print(f"Error getting video details: {e}")
        return await mystic.edit_text(_["play_3"])
    
    # Check duration
    if str(duration_min) == "None":
        return await mystic.edit_text(_["song_3"])
    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            _["play_6"].format(SONG_DOWNLOAD_DURATION_LIMIT // 60, duration_min)
        )
    
    await mystic.edit_text(_["song_8"])
    
    # Download from API
    file_path = await download_song_from_api(vidid)
    
    if not file_path:
        return await mystic.edit_text(_["song_9"].format("Failed to download from API"))
    
    # Clean title for caption
    title = re.sub("\W+", " ", title.title())
    
    # Send as audio file
    await mystic.edit_text(_["song_11"])
    await app.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_AUDIO,
    )
    
    try:
        await app.send_audio(
            chat_id=message.chat.id,
            audio=file_path,
            caption=title,
            title=title,
            duration=duration_sec,
            thumb=thumbnail,
            reply_to_message_id=message.id,
        )
        await mystic.delete()
    except Exception as e:
        print(e)
        return await mystic.edit_text(_["song_10"])
    
    try:
        os.remove(file_path)
    except:
        pass

# Function to download song from API
async def download_song_from_api(vidid):
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)
    file_path = f"{download_folder}/{vidid}.mp3"
    
    # Check if already downloaded
    if os.path.exists(file_path):
        return file_path
    
    # API endpoint
    song_url = f"{API_URL}/song/{vidid}?api={API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        # Check song status and wait for download
        while True:
            try:
                async with session.get(song_url) as response:
                    if response.status != 200:
                        print(f"API request failed with status code {response.status}")
                        return None
                    
                    data = await response.json()
                    status = data.get("status", "").lower()
                    
                    if status == "downloading":
                        await asyncio.sleep(2)
                        continue
                    elif status == "error":
                        error_msg = data.get("error") or data.get("message") or "Unknown error"
                        print(f"API error: {error_msg}")
                        return None
                    elif status == "done":
                        download_url = data.get("link")
                        if not download_url:
                            print("API response did not provide a download URL.")
                            return None
                        break
                    else:
                        print(f"Unexpected status '{status}' from API.")
                        return None
            except Exception as e:
                print(f"Error while checking API status: {e}")
                return None
        
        # Download the file
        try:
            async with session.get(download_url) as file_response:
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await file_response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return file_path
        except Exception as e:
            print(f"Error occurred while downloading song: {e}")
            return None