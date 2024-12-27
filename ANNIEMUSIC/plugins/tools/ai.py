import base64
import mimetypes
import os

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from lexica import AsyncClient, languageModels, Messages

from ANNIEMUSIC import app


def get_prompt(message: Message):
    prompt = message.text.split(' ', 1)
    if len(prompt) < 2:
        return None
    return prompt[1]


def extract_content(response) -> str:
    if 'content' in response:
        content = response['content']
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
            return '\n'.join(texts)
        elif isinstance(content, dict):
            if 'parts' in content and isinstance(content['parts'], list):
                parts = content['parts']
                texts = []
                for part in parts:
                    if 'text' in part:
                        texts.append(part['text'])
                return '\n'.join(texts)
            elif 'text' in content:
                return content['text']
    return None


def format_response(model_name: str, response_content: str) -> str:
    return f"**Model:** {model_name}\n\n**Response:**\n{response_content}"


@app.on_message(filters.command("bard"))
async def bard_handler(client: Client, message: Message):
    prompt = get_prompt(message)
    if not prompt:
        await message.reply_text("Please provide a prompt after the command.")
        return
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    lexica_client = AsyncClient()
    try:
        response = await lexica_client.ChatCompletion(
            prompt, languageModels.bard)
        content = extract_content(response)
        if content:
            formatted_response = format_response('Bard', content)
            await message.reply_text(formatted_response)
        else:
            await message.reply_text("No content received from the API.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()


@app.on_message(filters.command("gemini"))
async def gemini_handler(client: Client, message: Message):
    prompt = get_prompt(message)
    if not prompt:
        await message.reply_text("Please provide a prompt after the command.")
        return
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    lexica_client = AsyncClient()
    try:
        messages = [Messages(content=prompt, role="user")]
        response = await lexica_client.ChatCompletion(
            messages, languageModels.gemini)
        content = extract_content(response)
        if content:
            formatted_response = format_response('Gemini', content)
            await message.reply_text(formatted_response)
        else:
            await message.reply_text("No content received from the API.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()


@app.on_message(filters.command("gpt"))
async def gpt_handler(client: Client, message: Message):
    prompt = get_prompt(message)
    if not prompt:
        await message.reply_text("Please provide a prompt after the command.")
        return
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    lexica_client = AsyncClient()
    try:
        messages = [Messages(content=prompt, role="user")]
        response = await lexica_client.ChatCompletion(
            messages, languageModels.gpt)
        content = extract_content(response)
        if content:
            formatted_response = format_response('GPT', content)
            await message.reply_text(formatted_response)
        else:
            await message.reply_text("No content received from the API.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()


@app.on_message(filters.command("llama"))
async def llama_handler(client: Client, message: Message):
    prompt = get_prompt(message)
    if not prompt:
        await message.reply_text("Please provide a prompt after the command.")
        return
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    lexica_client = AsyncClient()
    try:
        messages = [Messages(content=prompt, role="user")]
        response = await lexica_client.ChatCompletion(
            messages, languageModels.llama)
        content = extract_content(response)
        if content:
            formatted_response = format_response('LLaMA', content)
            await message.reply_text(formatted_response)
        else:
            await message.reply_text("No content received from the API.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()


@app.on_message(filters.command("mistral"))
async def mistral_handler(client: Client, message: Message):
    prompt = get_prompt(message)
    if not prompt:
        await message.reply_text("Please provide a prompt after the command.")
        return
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    lexica_client = AsyncClient()
    try:
        messages = [Messages(content=prompt, role="user")]
        response = await lexica_client.ChatCompletion(
            messages, languageModels.mistral)
        content = extract_content(response)
        if content:
            formatted_response = format_response('Mistral', content)
            await message.reply_text(formatted_response)
        else:
            await message.reply_text("No content received from the API.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()


@app.on_message(filters.command("geminivision"))
async def geminivision_handler(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.photo:
        prompt = get_prompt(message)
        if not prompt:
            await message.reply_text("Please provide a prompt after the command.")
            return
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        status_message = await message.reply_text("Processing your image, please wait...")
        photo = message.reply_to_message.photo

        file_path = await client.download_media(photo.file_id)
        lexica_client = AsyncClient()
        try:
            image_info = []
            with open(file_path, "rb") as image_file:
                data = base64.b64encode(
                    image_file.read()).decode("utf-8")
                mime_type, _ = mimetypes.guess_type(file_path)
                image_info.append(
                    {"data": data, "mime_type": mime_type})

            response = await lexica_client.ChatCompletion(
                prompt, languageModels.geminiVision, images=image_info)

            content = extract_content(response)
            if content:
                formatted_response = format_response('Gemini Vision', content)
                await message.reply_text(formatted_response)
            else:
                await message.reply_text("No content received from the API.")
            await status_message.delete()
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
            await status_message.delete()
        finally:
            await lexica_client.close()
            os.remove(file_path)
    else:
        await message.reply_text(
            "Please reply to an image with the /geminivision command and a prompt."
        )


@app.on_message(filters.command("enhance"))
async def upscale_handler(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo

        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        status_message = await message.reply_text("Upscaling your image, please wait...")
        file_path = await client.download_media(photo.file_id)
        lexica_client = AsyncClient()
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()

            upscaled_image_bytes = await lexica_client.upscale(image_bytes)
            upscaled_image_path = "upscaled.png"
            with open(upscaled_image_path, 'wb') as f:
                f.write(upscaled_image_bytes)

            await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
            await message.reply_photo(upscaled_image_path)
            await status_message.delete()
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
            await status_message.delete()
        finally:
            await lexica_client.close()
            os.remove(file_path)
            if os.path.exists(upscaled_image_path):
                os.remove(upscaled_image_path)
    else:
        await message.reply_text(
            "Please reply to the image you want to upscale with the /enhance command."
        )