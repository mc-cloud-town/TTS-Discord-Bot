import asyncio
import os
from tempfile import NamedTemporaryFile
from typing import NamedTuple, Optional
from disnake import FFmpegPCMAudio, VoiceClient, VoiceState

from utils import logger


class AudioItem(NamedTuple):
    audio_data: bytes
    voice_state: VoiceState
    text: str
    guild_id: int


class AudioQueue:
    def __init__(self):
        self._log = logger
        self._queues: dict[int, asyncio.Queue] = {}
        self._play_tasks: dict[int, asyncio.Task] = {}

    def get_queue(self, guild_id: int) -> asyncio.Queue:
        if guild_id not in self._queues:
            self._queues[guild_id] = asyncio.Queue()
        return self._queues[guild_id]

    async def add_to_queue(self, item: AudioItem):
        self._log.debug("add to queue")
        queue = self.get_queue(item.guild_id)
        await queue.put(item)

        if (
            item.guild_id not in self._play_tasks
            or self._play_tasks[item.guild_id].done()
        ):
            self._log.debug("start to play audio")
            self._play_tasks[item.guild_id] = asyncio.create_task(
                self._play_loop(item.guild_id)
            )

    async def _play_loop(self, guild_id: int):
        queue = self.get_queue(guild_id)

        while not queue.empty():
            item: AudioItem = await queue.get()
            guild = item.voice_state.channel.guild
            voice_client: Optional[VoiceClient] = guild.voice_client

            try:
                if not voice_client or not voice_client.is_connected():
                    voice_client = await item.voice_state.channel.connect(
                        timeout=20, reconnect=True
                    )
                elif voice_client.channel != item.voice_state.channel:
                    await voice_client.move_to(item.voice_state.channel)

                if voice_client and voice_client.is_connected():
                    await self.__run_player(item.audio_data, voice_client)
            except Exception as e:
                self._log.error(f"播放循環錯誤: {e}")

            queue.task_done()
            await asyncio.sleep(1)

    async def __run_player(self, audio_data: bytes, voice_client: VoiceClient):
        """封裝播放邏輯，確保在這一階段是阻塞的 (直到播放結束)"""
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        done = asyncio.Event()

        def after_playing(error):
            if error:
                self._log.error(f"Playback error: {error}")
            voice_client.loop.call_soon_threadsafe(done.set)

        try:
            if voice_client.is_playing():
                voice_client.stop()
            voice_client.play(FFmpegPCMAudio(temp_path), after=after_playing)
            self._log.info(f"Started playing: {temp_path}")
            await done.wait()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            self._log.info("Finished playing and cleaned up temp file.")

    def clear(self, guild_id: int):
        if guild_id in self._queues:
            self._queues[guild_id] = asyncio.Queue()
        if guild_id in self._play_tasks:
            self._play_tasks[guild_id].cancel()
