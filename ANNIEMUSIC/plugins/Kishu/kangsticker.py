import os
import tempfile
import shutil
import subprocess
import traceback
from pyrogram import Client, filters, raw
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    StickersetInvalid,
    StickersTooMuch,
    StickerEmojiInvalid,
    PeerIdInvalid,
    FloodWait,
    FileReferenceExpired,
    RPCError,
)
from PIL import Image

from ANNIEMUSIC import app
 
BOT_USERNAME = "AnnieMusicRobot"


def stylize_text(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
        'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ',
        'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ',
        'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ',
        'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ',
        'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ',
        'Z': 'ᴢ',
    }
    return ''.join(small_caps.get(c, c) for c in text)


def get_pack_name(user_id, is_animated=False, is_video=False, pack_num=0):
    if is_animated:
        pack_type = "animated"
    elif is_video:
        pack_type = "video"
    else:
        pack_type = "regular"

    pack_suffix = f"pack{pack_num}" if pack_num else ""
    bot_username = BOT_USERNAME.lower()

    user_part = f"user{user_id}"

    parts = [user_part, pack_type, pack_suffix, 'by', bot_username]
    parts = [part for part in parts if part]
    pack_name = '_'.join(parts)

    return pack_name


def get_pack_title(user_first_name, is_animated=False, is_video=False, pack_num=0):
    extra_version = f" {pack_num}" if pack_num else ""
    if is_animated:
        pack_type = "Animated"
    elif is_video:
        pack_type = "Video"
    else:
        pack_type = "Sticker"
    pack_title = f"{user_first_name}'s {pack_type} Pack{extra_version}"
    return pack_title


async def send_pack_message(processing_msg, is_new_pack, type_of_pack, pack_title, pack_name, sticker_count, emoji):
    if is_new_pack:
        message_text = (
            f"**➣ Created a new {type_of_pack} pack and added your sticker!**\n\n"
            f"Pack Name ➣ `{pack_title}`\n"
            f"Sticker Count in Pack ➣ `{sticker_count}`\n"
            f"Sticker Emoji ➣ `{emoji}`"
        )
    else:
        message_text = (
            f"**➣ Sticker added to your existing {type_of_pack} pack!**\n\n"
            f"Pack Name ➣ `{pack_title}`\n"
            f"Sticker Count in Pack ➣ `{sticker_count}`\n"
            f"Sticker Emoji ➣ `{emoji}`"
        )

    await processing_msg.edit(
        stylize_text(message_text),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("View Pack", url=f"https://t.me/addstickers/{pack_name}")
        ]])
    )


@app.on_message(filters.command("kang") & filters.reply)
async def kang(client, message):
    processing_msg = await message.reply_text(stylize_text("➣ Processing..."))
    reply = message.reply_to_message
    user = message.from_user
    user_id = user.id
    user_first_name = user.first_name

    if not reply or (not reply.sticker and not reply.photo and not reply.animation and not reply.document and not reply.video):
        return await processing_msg.edit(stylize_text("Reply to a sticker, photo, GIF, or video to kang it!"))

    if len(message.command) < 2:
        emoji = "🤔"
    else:
        emoji = message.command[1]
        if not emoji:
            emoji = "🤔"

    is_animated = False
    is_video = False
    temp_dir = tempfile.mkdtemp()

    try:
        if reply.sticker:
            await processing_msg.edit(stylize_text("➣ Processing Sticker..."))
            sticker = reply.sticker
            if sticker.is_animated:
                is_animated = True
                file_extension = ".tgs"
            elif sticker.is_video:
                is_video = True
                file_extension = ".webm"
            else:
                file_extension = ".png"
            file_name = sticker.file_name or f"kang_sticker{file_extension}"
            file_path = os.path.join(temp_dir, file_name)
            await reply.download(file_path)
            media = file_path
        elif reply.photo:
            await processing_msg.edit(stylize_text("➣ Converting Image..."))
            file_path = os.path.join(temp_dir, "kang_sticker.png")
            await reply.download(file_path)
            img = Image.open(file_path)
            max_size = (512, 512)
            if img.width > 512 or img.height > 512:
                img.thumbnail(max_size)
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            img.save(file_path, "PNG")
            media = file_path
        elif reply.animation:
            await processing_msg.edit(stylize_text("➣ Processing Animated Sticker..."))
            is_animated = True
            file_path = os.path.join(temp_dir, "kang_sticker.tgs")
            await reply.download(file_path)
            media = file_path
        elif reply.video or (reply.document and reply.document.mime_type.startswith('video/')):
            await processing_msg.edit(stylize_text("➣ Processing Video..."))
            is_video = True
            raw_video_path = os.path.join(temp_dir, "raw_video.mp4")
            await reply.download(raw_video_path)

            file_path = os.path.join(temp_dir, "kang_sticker.webm")

            cmd = [
                'ffmpeg',
                '-y',
                '-i', raw_video_path,
                '-vf', 'scale=512:512:flags=lanczos:force_original_aspect_ratio=decrease',
                '-ss', '0',
                '-t', '3',
                '-c:v', 'libvpx-vp9',
                '-b:v', '500k',
                '-crf', '30',
                '-an',
                '-r', '30',
                file_path
            ]
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode != 0:
                error_message = process.stderr.decode()
                return await processing_msg.edit(f"Error processing video:\n{error_message}")

            media = file_path
        elif reply.document:
            mime_type = reply.document.mime_type
            if "image" in mime_type:
                await processing_msg.edit(stylize_text("➣ Converting Image..."))
                file_path = os.path.join(temp_dir, "kang_sticker.png")
                await reply.download(file_path)
                img = Image.open(file_path)
                max_size = (512, 512)
                if img.width > 512 or img.height > 512:
                    img.thumbnail(max_size)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img.save(file_path, "PNG")
                media = file_path
            elif "tgsticker" in mime_type:
                await processing_msg.edit(stylize_text("➣ Processing Animated Sticker..."))
                is_animated = True
                file_path = os.path.join(temp_dir, "kang_sticker.tgs")
                await reply.download(file_path)
                media = file_path
            elif "video" in mime_type:
                await processing_msg.edit(stylize_text("➣ Processing Video..."))
                is_video = True
                raw_video_path = os.path.join(temp_dir, "raw_video.mp4")
                await reply.download(raw_video_path)

                file_path = os.path.join(temp_dir, "kang_sticker.webm")

                cmd = [
                    'ffmpeg',
                    '-y',
                    '-i', raw_video_path,
                    '-vf', 'scale=512:512:flags=lanczos:force_original_aspect_ratio=decrease',
                    '-ss', '0',
                    '-t', '3',
                    '-c:v', 'libvpx-vp9',
                    '-b:v', '500k',
                    '-crf', '30',
                    '-an',
                    '-r', '30',
                    file_path
                ]
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if process.returncode != 0:
                    error_message = process.stderr.decode()
                    return await processing_msg.edit(f"Error processing video:\n{error_message}")

                media = file_path
            else:
                return await processing_msg.edit("Cannot kang this type of document.")
        else:
            return await processing_msg.edit("Cannot kang this type of media.")

        if is_animated:
            type_of_pack = 'Animated'
        elif is_video:
            type_of_pack = 'Video'
        else:
            type_of_pack = 'Static'

        pack_num = 0
        max_stickers = 50 if is_animated or is_video else 120

        while True:
            pack_name = get_pack_name(user_id, is_animated, is_video, pack_num)
            try:
                sticker_set = await client.invoke(
                    raw.functions.messages.GetStickerSet(
                        stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                        hash=0
                    )
                )
                if len(sticker_set.documents) >= max_stickers:
                    pack_num += 1
                    continue
                else:
                    break
            except StickersetInvalid:
                break
            except Exception as e:
                await processing_msg.edit(f"An error occurred: {e}")
                return

        pack_title = get_pack_title(user_first_name, is_animated, is_video, pack_num)

        uploaded_document = await upload_sticker_file(client, user_id, media, is_animated, is_video)

        try:
            await client.invoke(
                raw.functions.stickers.AddStickerToSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                    sticker=raw.types.InputStickerSetItem(
                        document=raw.types.InputDocument(
                            id=uploaded_document.id,
                            access_hash=uploaded_document.access_hash,
                            file_reference=uploaded_document.file_reference
                        ),
                        emoji=emoji
                    )
                )
            )
            sticker_set = await client.invoke(
                raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                    hash=0
                )
            )
            sticker_count = len(sticker_set.documents)

            await send_pack_message(
                processing_msg,
                is_new_pack=False,
                type_of_pack=type_of_pack,
                pack_title=pack_title,
                pack_name=pack_name,
                sticker_count=sticker_count,
                emoji=emoji
            )

        except StickersTooMuch:
            pack_num += 1
            pack_name = get_pack_name(user_id, is_animated, is_video, pack_num)
            pack_title = get_pack_title(user_first_name, is_animated, is_video, pack_num)
            await create_sticker_pack(
                client, user_id, pack_name, pack_title,
                uploaded_document, emoji, is_animated, is_video
            )
            sticker_set = await client.invoke(
                raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                    hash=0
                )
            )
            sticker_count = len(sticker_set.documents)

            await send_pack_message(
                processing_msg,
                is_new_pack=True,
                type_of_pack=type_of_pack,
                pack_title=pack_title,
                pack_name=pack_name,
                sticker_count=sticker_count,
                emoji=emoji
            )
        except StickersetInvalid:
            await create_sticker_pack(
                client, user_id, pack_name, pack_title,
                uploaded_document, emoji, is_animated, is_video
            )
            sticker_set = await client.invoke(
                raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                    hash=0
                )
            )
            sticker_count = len(sticker_set.documents)

            await send_pack_message(
                processing_msg,
                is_new_pack=True,
                type_of_pack=type_of_pack,
                pack_title=pack_title,
                pack_name=pack_name,
                sticker_count=sticker_count,
                emoji=emoji
            )
        except StickerEmojiInvalid:
            await processing_msg.edit("Invalid emoji provided.")
        except PeerIdInvalid:
            await processing_msg.edit("Cannot access user information.")
        except FloodWait as e:
            await processing_msg.edit(f"Flood wait error. Try again after {e.x} seconds.")
        except FileReferenceExpired:
            await processing_msg.edit("The file reference has expired. Please resend the media and try again.")
        except RPCError as e:
            await processing_msg.edit(f"An error occurred: {e.MESSAGE}")
        except Exception as e:
            await processing_msg.edit(f"An unexpected error occurred:\n{e}")
    except Exception as e:
        error_trace = traceback.format_exc()
        await processing_msg.edit(f"An unexpected error occurred:\n{error_trace}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def upload_sticker_file(client, user_id, media, is_animated, is_video):
    if is_animated:
        mime_type = "application/x-tgsticker"
        file_name = "sticker.tgs"
    elif is_video:
        mime_type = "video/webm"
        file_name = "sticker.webm"
    else:
        mime_type = "image/png"
        file_name = "sticker.png"

    attributes = [
        raw.types.DocumentAttributeFilename(file_name=file_name),
        raw.types.DocumentAttributeSticker(
            alt='',
            stickerset=raw.types.InputStickerSetEmpty(),
            mask=False
        )
    ]

    if is_video:
        attributes.append(
            raw.types.DocumentAttributeVideo(
                duration=0,
                w=512,
                h=512,
                round_message=False,
                supports_streaming=False,
            )
        )

    media_file = await client.save_file(media)

    uploaded_media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=await client.resolve_peer(user_id),
            media=raw.types.InputMediaUploadedDocument(
                file=media_file,
                mime_type=mime_type,
                attributes=attributes,
            )
        )
    )

    return uploaded_media.document


async def create_sticker_pack(client, user_id, pack_name, pack_title, uploaded_document, emoji, is_animated, is_video):
    await client.invoke(
        raw.functions.stickers.CreateStickerSet(
            user_id=await client.resolve_peer(user_id),
            title=pack_title,
            short_name=pack_name,
            stickers=[
                raw.types.InputStickerSetItem(
                    document=raw.types.InputDocument(
                        id=uploaded_document.id,
                        access_hash=uploaded_document.access_hash,
                        file_reference=uploaded_document.file_reference
                    ),
                    emoji=emoji
                )
            ],
            animated=is_animated,
            videos=is_video,
        )
    )