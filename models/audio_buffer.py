import asyncio
import disnake
import tempfile
import os
from utils.logger import logger


class AudioBuffer:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def add_to_queue(self, audio_data):
        await self.queue.put(audio_data)

    async def play_audio(self, voice_client):
        if voice_client.is_playing():
            return
        audio_data = await self.queue.get()
        if audio_data is None:
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_file_path = temp_audio_file.name

        def after_playing(error):
            logger.info(f'Finished playing: {error}')
            asyncio.run_coroutine_threadsafe(self.queue.task_done(), asyncio.get_event_loop()).result()
            asyncio.run_coroutine_threadsafe(self.play_audio(voice_client), asyncio.get_event_loop()).result()
            os.remove(temp_audio_file_path)

        voice_client.play(disnake.FFmpegPCMAudio(temp_audio_file_path), after=after_playing)
