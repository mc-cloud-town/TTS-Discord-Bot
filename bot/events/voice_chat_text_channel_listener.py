import asyncio
import os
import tempfile

import disnake
from disnake.ext import commands

from bot import user_settings
from bot.api.async_tts_handler import text_to_speech
from bot.client.base_cog import BaseCog
from bot.user_settings import is_user_voice_exist
from bot.utils.audio_queue import AudioItem
from bot.utils.extract_user_nickname import extract_user_nickname
from config import VOICE_TEXT_INPUT_CHANNEL_IDS, DEFAULT_VOICE
from utils.logger import logger


class VoiceChatTextChannelListener(BaseCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_ids = VOICE_TEXT_INPUT_CHANNEL_IDS
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.target_channel_ids:
            return

        user_id = message.author.id
        settings = user_settings.get_user_settings(user_id)

        if message.content.strip() == '':
            return

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

        character_name = settings.get("selected_sample", DEFAULT_VOICE)

        if character_name == '自己聲音 (需要先上傳語音樣本）':
            if not is_user_voice_exist(user_id):
                return

            # 當前用戶的語音樣本名稱為 "自己聲音 (需要先上傳語音樣本）"，且用戶已上傳語音樣本
            # 使用用戶的語音樣本名稱作為角色名稱
            character_name = str(user_id)

        guild = message.guild
        member = guild.get_member(user_id)
        voice_state = member.voice if member else None

        if not voice_state or not voice_state.channel:
            logger.info(f"User {message.author.name} is not in a voice channel.")
            return

        try:
            player_name = extract_user_nickname(member.display_name)
            speech_text = f'{player_name} 說: {message.content}' if character_name != str(user_id) else message.content,
            audio_data = await text_to_speech(speech_text, character_name)
            logger.info(f"Audio data length: {len(audio_data)} bytes")
            audio_item = AudioItem(
                audio_data=audio_data,
                voice_state=voice_state,
                text=speech_text,
                guild_id=message.guild.id,
            )
            await self.audio_manager.add_to_queue(audio_item)
            logger.info("Audio data add to queue")
        except Exception as e:
            logger.error(f"Error fetching TTS audio: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(VoiceChatTextChannelListener(bot))
