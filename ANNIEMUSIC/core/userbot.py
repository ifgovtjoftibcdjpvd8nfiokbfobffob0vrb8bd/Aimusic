from pyrogram import Client
import config
from ..logging import LOGGER

assistants = []
assistantids = []


class Userbot:
    def __init__(self):
        self.one = (
            Client(
                name="Annie1",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING1),
                no_updates=True,
            )
            if config.STRING1
            else None
        )
        self.two = (
            Client(
                name="Annie2",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING2),
                no_updates=True,
            )
            if config.STRING2
            else None
        )
        self.three = (
            Client(
                name="Annie3",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING3),
                no_updates=True,
            )
            if config.STRING3
            else None
        )
        self.four = (
            Client(
                name="Annie4",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING4),
                no_updates=True,
            )
            if config.STRING4
            else None
        )
        self.five = (
            Client(
                name="Annie5",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING5),
                no_updates=True,
            )
            if config.STRING5
            else None
        )

    async def start(self):
        LOGGER(__name__).info("Annie's Assistant starting...")
        if self.one:
            await self.one.start()
            # Removed join_chat calls
            assistants.append(1)
            try:
                await self.one.send_message(config.LOGGER_ID, "Annie's Assistant 1 Started")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Assistant Account 1 failed to access the log group: {e}"
                )
                exit()
            me = await self.one.get_me()
            self.one.id = me.id
            self.one.name = me.mention
            self.one.username = me.username
            assistantids.append(self.one.id)
            LOGGER(__name__).info(f"Assistant 1 started as {self.one.name}")

        if self.two:
            await self.two.start()
            # Removed join_chat calls
            assistants.append(2)
            try:
                await self.two.send_message(config.LOGGER_ID, "Annie's Assistant 2 Started")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Assistant Account 2 failed to access the log group: {e}"
                )
                exit()
            me = await self.two.get_me()
            self.two.id = me.id
            self.two.name = me.mention
            self.two.username = me.username
            assistantids.append(self.two.id)
            LOGGER(__name__).info(f"Assistant 2 started as {self.two.name}")

        if self.three:
            await self.three.start()
            # Removed join_chat calls
            assistants.append(3)
            try:
                await self.three.send_message(config.LOGGER_ID, "Annie's Assistant 3 Started")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Assistant Account 3 failed to access the log group: {e}"
                )
                exit()
            me = await self.three.get_me()
            self.three.id = me.id
            self.three.name = me.mention
            self.three.username = me.username
            assistantids.append(self.three.id)
            LOGGER(__name__).info(f"Assistant 3 started as {self.three.name}")

        if self.four:
            await self.four.start()
            # Removed join_chat calls
            assistants.append(4)
            try:
                await self.four.send_message(config.LOGGER_ID, "Annie's Assistant 4 Started")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Assistant Account 4 failed to access the log group: {e}"
                )
                exit()
            me = await self.four.get_me()
            self.four.id = me.id
            self.four.name = me.mention
            self.four.username = me.username
            assistantids.append(self.four.id)
            LOGGER(__name__).info(f"Assistant 4 started as {self.four.name}")

        if self.five:
            await self.five.start()
            # Removed join_chat calls
            assistants.append(5)
            try:
                await self.five.send_message(config.LOGGER_ID, "Annie's Assistant 5 Started")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Assistant Account 5 failed to access the log group: {e}"
                )
                exit()
            me = await self.five.get_me()
            self.five.id = me.id
            self.five.name = me.mention
            self.five.username = me.username
            assistantids.append(self.five.id)
            LOGGER(__name__).info(f"Assistant 5 started as {self.five.name}")

    async def stop(self):
        LOGGER(__name__).info("Annie's assistants stopping...")
        if self.one:
            try:
                await self.one.stop()
            except Exception as e:
                LOGGER(__name__).warning(f"Assistant 1 failed to stop: {e}")
        if self.two:
            try:
                await self.two.stop()
            except Exception as e:
                LOGGER(__name__).warning(f"Assistant 2 failed to stop: {e}")
        if self.three:
            try:
                await self.three.stop()
            except Exception as e:
                LOGGER(__name__).warning(f"Assistant 3 failed to stop: {e}")
        if self.four:
            try:
                await self.four.stop()
            except Exception as e:
                LOGGER(__name__).warning(f"Assistant 4 failed to stop: {e}")
        if self.five:
            try:
                await self.five.stop()
            except Exception as e:
                LOGGER(__name__).warning(f"Assistant 5 failed to stop: {e}")