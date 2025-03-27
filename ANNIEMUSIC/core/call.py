import asyncio
from datetime import datetime, timedelta
from typing import Union

from pyrogram.errors import FloodWait
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup

from ntgcalls import TelegramServerError
from pytgcalls import PyTgCalls, filters
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import (
    MediaStream,
    AudioQuality,
    VideoQuality,
    Update,
    StreamEnded,
    ChatUpdate,
    GroupCallParticipant,
)


import config
from ANNIEMUSIC import LOGGER, YouTube, app
from ANNIEMUSIC.misc import db
from ANNIEMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ANNIEMUSIC.utils.exceptions import AssistantErr
from ANNIEMUSIC.utils.inline.play import stream_markup
from ANNIEMUSIC.utils.stream.autoclear import auto_clean
from ANNIEMUSIC.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}
AUTO_END_TIME = 1

async def _clear_(chat_id):
    popped = db.pop(chat_id, None)
    if popped:
        await auto_clean(popped)
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)
    await set_loop(chat_id, 0)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="ANNIE1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        self.userbot2 = Client(
            name="ANNIE2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )
        self.userbot3 = Client(
            name="ANNIE3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )
        self.userbot4 = Client(
            name="ANNIE4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )
        self.userbot5 = Client(
            name="ANNIE5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.mute(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.unmute(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error in stop_stream: {e}")

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except (IndexError, KeyError) as e:
            LOGGER(__name__).error(f"Error in force_stop_stream: {e}")
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error while leaving call in force_stop_stream: {e}")

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )
        else:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
            )
        await assistant.play(
            chat_id,
            stream,
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        if mode == "video":
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        else:
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
                video_flags=MediaStream.Flags.IGNORE,
            )
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.play(
            config.LOGGER_ID,
            MediaStream(link),
        )
        await asyncio.sleep(8)
        await assistant.leave_call(config.LOGGER_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )
        else:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
            )
        try:
            await assistant.play(
                chat_id,
                stream,
            )
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        except Exception as e:
            LOGGER(__name__).error(f"Error in join_call: {e}")
            raise AssistantErr(
                f"**An unexpected error occurred**\n\n{str(e)}"
            )
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)

    async def play(self, client, chat_id):
            check = db.get(chat_id)
            if not check or len(check) == 0:
                LOGGER(__name__).info(f"No songs in queue for chat_id {chat_id}")
                await _clear_(chat_id)
                try:
                    await client.leave_call(chat_id)
                except Exception as e:
                    if 'not in a call' in str(e):
                        LOGGER(__name__).info(f"Bot is not in a call in chat_id {chat_id}")
                    else:
                        LOGGER(__name__).error(f"Error while leaving call in play method: {e}")
                return

            loop = await get_loop(chat_id)
            try:
                if loop == 0:
                    popped = check.pop(0)
                    await auto_clean(popped)
                else:
                    loop -= 1
                    await set_loop(chat_id, loop)

                if not check or len(check) == 0:
                    await _clear_(chat_id)
                    try:
                        await client.leave_call(chat_id)
                    except Exception as e:
                        if 'not in a call' in str(e):
                            LOGGER(__name__).info(f"Bot is not in a call in chat_id {chat_id}")
                        else:
                            LOGGER(__name__).error(f"Error while leaving call in play method: {e}")
                    return
            except Exception as e:
                LOGGER(__name__).error(f"Error in play method: {e}")
                await _clear_(chat_id)
                try:
                    await client.leave_call(chat_id)
                except Exception as e:
                    if 'not in a call' in str(e):
                        LOGGER(__name__).info(f"Bot is not in a call in chat_id {chat_id}")
                    else:
                        LOGGER(__name__).error(f"Error while leaving call in play method: {e}")
                return

            queued = check[0]["file"]
            language = await get_lang(chat_id)
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            videoid = check[0]["vidid"]
            db[chat_id][0]["played"] = 0
            exis = (check[0]).get("old_dur")
            if exis:
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = True if str(streamtype) == "video" else False
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if video:
                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    LOGGER(__name__).error(f"Error playing live stream: {e}")
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=video,
                    )
                except Exception as e:
                    LOGGER(__name__).error(f"Error downloading video: {e}")
                    return await mystic.edit_text(
                        _["call_6"], disable_web_page_preview=True
                    )
                if video:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    LOGGER(__name__).error(f"Error playing downloaded video: {e}")
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                if video:
                    stream = MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    LOGGER(__name__).error(f"Error playing index stream: {e}")
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                if video:
                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )
                else:
                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.Flags.IGNORE,
                    )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    LOGGER(__name__).error(f"Error playing queued stream: {e}")
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    button = stream_markup(_, chat_id)
                    try:
                        run = await app.send_photo(
                            chat_id=original_chat_id,
                            photo=img,
                            caption=_["stream_1"].format(
                                f"https://t.me/{app.username}?start=info_{videoid}",
                                title[:23],
                                check[0]["dur"],
                                user,
                            ),
                            reply_markup=InlineKeyboardMarkup(button),
                        )
                    except FloodWait as e:
                        LOGGER(__name__).warning(f"FloodWait: Sleeping for {e.value}")
                        await asyncio.sleep(e.value)
                        run = await app.send_photo(
                            chat_id=original_chat_id,
                            photo=img,
                            caption=_["stream_1"].format(
                                f"https://t.me/{app.username}?start=info_{videoid}",
                                title[:23],
                                check[0]["dur"],
                                user,
                            ),
                            reply_markup=InlineKeyboardMarkup(button),
                        )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1: pings.append(self.one.ping)
        if config.STRING2: pings.append(self.two.ping)
        if config.STRING3: pings.append(self.three.ping)
        if config.STRING4: pings.append(self.four.ping)
        if config.STRING5: pings.append(self.five.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()
        await self.decorators()

    async def decorators(self):
        @self.one.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.two.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.three.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.four.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.five.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        async def stream_services_handler(_, update):
            await self.stop_stream(update.chat_id)

        @self.one.on_update(filters.stream_end())
        @self.two.on_update(filters.stream_end())
        @self.three.on_update(filters.stream_end())
        @self.four.on_update(filters.stream_end())
        @self.five.on_update(filters.stream_end())
        async def stream_end_handler1(client, update: StreamEnded):
            if not update.stream_type == StreamEnded.Type.AUDIO:
                return
            await self.play(client, update.chat_id)

        @self.one.on_update(filters.call_participant(GroupCallParticipant.Action.UPDATED))
        @self.two.on_update(filters.call_participant(GroupCallParticipant.Action.UPDATED))
        @self.three.on_update(filters.call_participant(GroupCallParticipant.Action.UPDATED))
        @self.four.on_update(filters.call_participant(GroupCallParticipant.Action.UPDATED))
        @self.five.on_update(filters.call_participant(GroupCallParticipant.Action.UPDATED))
        async def participants_change_handler(client, update: Update):
            participant = update.participant
            if participant.action not in (
                GroupCallParticipant.Action.JOINED,
                GroupCallParticipant.Action.LEFT
            ):
                return
            chat_id = update.chat_id
            users = counter.get(chat_id)
            if users is None:
                try:
                    got = len(await client.get_participants(chat_id))
                except Exception:
                    return
                counter[chat_id] = got
                if got == 1:
                    autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)
                    return
                autoend[chat_id] = {}
            else:
                final = users + 1 if participant.action == GroupCallParticipant.Action.JOINED else users - 1
                counter[chat_id] = final
                if final == 1:
                    autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)
                    return
                autoend[chat_id] = {}

JARVIS = Call()
