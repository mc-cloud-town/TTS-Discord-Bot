import asyncio
import os
import tempfile

import disnake
from disnake.ext import commands

from bot import user_settings
from bot.api.tts_handler import text_to_speech
from bot.utils.extract_user_nickname import extract_user_nickname
from config import VOICE_TEXT_INPUT_CHANNEL_ID
from utils.logger import logger


class VoiceChatTextChannelListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = VOICE_TEXT_INPUT_CHANNEL_ID
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return

        if message.channel.id != self.target_channel_id:
            return

        user_id = message.author.id
        settings = user_settings.get_user_settings(user_id)

        if message.content.strip() == "!!tts start":
            settings["tts_enabled"] = True
            user_settings.set_user_settings(user_id, settings)
            await message.channel.send(f"TTS 已啟用，針對用戶：{message.author.name}")
            logger.info(f"TTS enabled for user: {message.author.name}")
            return

        if message.content.strip() == "!!tts stop":
            settings["tts_enabled"] = False
            user_settings.set_user_settings(user_id, settings)
            await message.channel.send(f"TTS 已禁用，針對用戶：{message.author.name}")
            logger.info(f"TTS disabled for user: {message.author.name}")
            return

        if message.content.strip().startswith("!!"):
            return

        if not settings.get("tts_enabled", False):
            logger.info(f"TTS is not enabled for user: {message.author.name}")
            return

        character_name = settings.get("selected_sample", "老簡")

        guild = message.guild
        member = guild.get_member(user_id)
        voice_state = member.voice if member else None

        if not voice_state or not voice_state.channel:
            logger.info(f"User {message.author.name} is not in a voice channel.")
            return

        voice_client: disnake.VoiceClient | None = guild.voice_client

        if not voice_client:
            channel = voice_state.channel
            await channel.connect()
            voice_client = guild.voice_client

        if voice_state.channel != voice_client.channel:
            logger.info(f"Bot and user {message.author.name} are not in the same voice channel.")
            return

        async with self.lock:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Fetching TTS audio (attempt {attempt})...")
                    player_name = extract_user_nickname(member.display_name)

                    audio_data = text_to_speech(
                        f'{player_name} 說: {message.content}',
                        character_name,
                    )
                    logger.info("Audio data fetched successfully")
                    logger.info(f"Audio data length: {len(audio_data)} bytes")

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
                        temp_audio_file.write(audio_data)
                        temp_audio_file_path = temp_audio_file.name

                    def after_playing(error):
                        logger.info(f'Finished playing: {error}')
                        os.remove(temp_audio_file_path)

                    voice_client.play(disnake.FFmpegPCMAudio(temp_audio_file_path), after=after_playing)
                    logger.info("Playing audio...")
                    break
                except Exception as e:
                    logger.error(f"Error fetching TTS audio: {e}")
                    if attempt < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        logger.error("Failed to fetch TTS audio after multiple attempts.")
                        return


def setup(bot: commands.Bot):
    bot.add_cog(VoiceChatTextChannelListener(bot))
