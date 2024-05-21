import asyncio

import disnake
from utils.logger import logger


class AudioBuffer:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def add_to_queue(self, audio_data: bytes):
        """
        添加音頻數據到隊列
        Args:
            audio_data: 音頻數據
        """
        await self.queue.put(audio_data)

    async def play_audio(self, voice_client: disnake.VoiceClient):
        """
        播放音頻
        Args:
            voice_client: 聲音客戶端
        """
        if voice_client.is_playing():
            return
        audio_data = await self.queue.get()
        if audio_data is None:
            return

        def after_playing(error):
            logger.info(f'Finished playing: {error}')
            asyncio.run_coroutine_threadsafe(self.queue.task_done(), asyncio.get_event_loop()).result()
            asyncio.run_coroutine_threadsafe(self.play_audio(voice_client), asyncio.get_event_loop()).result()

        voice_client.play(disnake.FFmpegPCMAudio(audio_data), after=after_playing)
