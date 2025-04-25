import asyncio
import json
import os
import re
from typing import Dict, List, Optional, Tuple, Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from ANNIEMUSIC.utils.database import is_on_off
from ANNIEMUSIC.utils.downloader import api_download_song
from ANNIEMUSIC.utils.errors import capture_internal_err
from ANNIEMUSIC.utils.formatters import time_to_seconds

cookies_file = "ANNIEMUSIC/assets/cookies.txt"


@capture_internal_err
async def shell_cmd(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, error = await proc.communicate()
    return out.decode() if out else error.decode()


@capture_internal_err
async def cached_youtube_search(query: str) -> List[Dict]:
    search = VideosSearch(query, limit=1)
    results = await search.next()
    return results.get("result", [])


class YouTubeAPI:
    def __init__(self):
        self.base_url = "https://www.youtube.com/watch?v="
        self.playlist_url = "https://youtube.com/playlist?list="
        self.url_pattern = re.compile(r"(?:youtube\.com|youtu\.be)")

    def _prepare_link(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base_url + link
        if "youtu.be" in link:
            video_id = link.split("/")[-1].split("?")[0]
            link = self.base_url + video_id
        elif "youtube.com/shorts/" in link or "youtube.com/live/" in link:
            video_id = link.split("/")[-1].split("?")[0]
            link = self.base_url + video_id
        return link.split("&")[0] if "&" in link else link

    @capture_internal_err
    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        link = self._prepare_link(link, videoid)
        return bool(self.url_pattern.search(link))

    @capture_internal_err
    async def url(self, message: Message) -> Optional[str]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        for msg in messages:
            text = msg.text or msg.caption or ""
            entities = msg.entities or msg.caption_entities
            if not entities:
                continue
            for entity in entities:
                if entity.type == MessageEntityType.URL:
                    return text[entity.offset : entity.offset + entity.length]
                elif entity.type == MessageEntityType.TEXT_LINK:
                    return entity.url
        return None

    @capture_internal_err
    async def _fetch_video_info(
        self, query: str, use_cache: bool = True
    ) -> Optional[Dict]:
        if use_cache and not query.startswith("http"):
            result = await cached_youtube_search(query)
        else:
            search = VideosSearch(query, limit=1)
            result = (await search.next()).get("result", [])
        return result[0] if result else None

    @capture_internal_err
    async def is_live(self, link: str) -> bool:
        prepared = self._prepare_link(link)
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies",
            cookies_file,
            "--dump-json",
            prepared,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await proc.communicate()
        if out:
            try:
                info = json.loads(out.decode())
                return info.get("is_live") is True
            except:
                return False
        return False

    @capture_internal_err
    async def details(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[str, Optional[str], int, str, str]:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        if not info:
            raise ValueError("Video not found")
        return (
            info.get("title", ""),
            info.get("duration"),
            int(time_to_seconds(info["duration"])) if info.get("duration") else 0,
            info.get("thumbnails", [{}])[0].get("url", "").split("?")[0],
            info.get("id", ""),
        )

    @capture_internal_err
    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return info.get("title", "") if info else ""

    @capture_internal_err
    async def duration(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Optional[str]:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return info.get("duration") if info else None

    @capture_internal_err
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return (
            info.get("thumbnails", [{}])[0].get("url", "").split("?")[0] if info else ""
        )

    @capture_internal_err
    async def video(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[int, str]:
        link = self._prepare_link(link, videoid)
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies",
            cookies_file,
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        return 0, stderr.decode()

    @capture_internal_err
    async def playlist(
        self, link: str, limit: int, user_id, videoid: Union[bool, str] = None
    ) -> list:
        if videoid:
            link = self.playlist_url + videoid
        if "&" in link:
            link = link.split("&")[0]
        cmd = (
            f"yt-dlp --cookies {cookies_file} -i --get-id --flat-playlist "
            f"--playlist-end {limit} --skip-download {link}"
        )
        playlist_data = await shell_cmd(cmd)
        return [item for item in playlist_data.strip().split("\n") if item]

    @capture_internal_err
    async def track(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[Dict, str]:
        try:
            info = await self._fetch_video_info(self._prepare_link(link, videoid))
            if not info:
                raise ValueError("Track not found via API")
        except:
            prepared_link = self._prepare_link(link, videoid)
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--cookies",
                cookies_file,
                "--dump-json",
                prepared_link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, _ = await proc.communicate()
            if not out:
                raise ValueError("Track not found (yt-dlp fallback)")
            try:
                info = json.loads(out.decode())
            except json.JSONDecodeError:
                raise ValueError("Failed to parse yt-dlp output")

        return {
            "title": info.get("title", ""),
            "link": info.get("webpage_url", link),
            "vidid": info.get("id", ""),
            "duration_min": (
                info.get("duration") if isinstance(info.get("duration"), str) else None
            ),
            "thumb": info.get("thumbnail", ""),
        }, info.get("id", "")

    @capture_internal_err
    async def formats(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[List[Dict], str]:
        link = self._prepare_link(link, videoid)
        opts = {"quiet": True, "cookiefile": cookies_file}
        formats = []
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(link, download=False)
            for fmt in info.get("formats", []):
                if "dash" in fmt.get("format", "").lower():
                    continue
                if all(
                    k in fmt
                    for k in ("format", "filesize", "format_id", "ext", "format_note")
                ):
                    formats.append(
                        {
                            "format": fmt["format"],
                            "filesize": fmt["filesize"],
                            "format_id": fmt["format_id"],
                            "ext": fmt["ext"],
                            "format_note": fmt["format_note"],
                            "yturl": link,
                        }
                    )
        return formats, link

    @capture_internal_err
    async def slider(
        self, link: str, query_type: int, videoid: Union[bool, str] = None
    ) -> Tuple[str, Optional[str], str, str]:
        search = VideosSearch(self._prepare_link(link, videoid), limit=10)
        results = (await search.next()).get("result", [])
        if not results or query_type >= len(results):
            raise IndexError("Query type index out of range")
        result = results[query_type]
        return (
            result.get("title", ""),
            result.get("duration"),
            result.get("thumbnails", [{}])[0].get("url", "").split("?")[0],
            result.get("id", ""),
        )

    @capture_internal_err
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> Union[Tuple[str, Optional[bool]], str]:
        link = self._prepare_link(link, videoid)
        loop = asyncio.get_running_loop()

        def audio_dl():
            opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookies_file,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = f"downloads/{info['id']}.{info['ext']}"
                if os.path.exists(path):
                    return path
                ydl.download([link])
                return path

        def video_dl():
            opts = {
                "format": "best[height<=?720][width<=?1280]",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookies_file,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = f"downloads/{info['id']}.{info['ext']}"
                if os.path.exists(path):
                    return path
                ydl.download([link])
                return path

        def song_video_dl():
            opts = {
                "format": f"{format_id}+140",
                "outtmpl": f"downloads/{title}",
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
                "cookiefile": cookies_file,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([link])

        def song_audio_dl():
            opts = {
                "format": format_id,
                "outtmpl": f"downloads/{title}.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "cookiefile": cookies_file,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([link])

        # === Priority logic ===
        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"
        elif video:
            if await self.is_live(link):
                status, stream_url = await self.video(link)
                if status == 1:
                    return stream_url, None
                raise ValueError("Unable to fetch live stream link")
            if await is_on_off(1):
                path = await loop.run_in_executor(None, video_dl)
                return path, True
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--cookies",
                cookies_file,
                "-g",
                "-f",
                "best[height<=?720][width<=?1280]",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            if stdout:
                return stdout.decode().split("\n")[0], None
            return ""
        else:
            try:
                api_path = await api_download_song(link)
                if api_path:
                    return api_path, True
            except Exception as e:
                print(f"[API ERROR] {e}")

            print("[FALLBACK] API failed, using yt-dlp fallback...")
            path = await loop.run_in_executor(None, audio_dl)
            return path, True
