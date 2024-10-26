import re
import disnake
import tempfile
import asyncio
import os
from disnake.ext import commands
from bot import user_settings
from bot.api.tts_handler import text_to_speech
from utils.logger import logger
from config import TTS_TARGET_CHANNEL_ID, MESSAGE_BOT_TARGET_USER_ID


class MessageListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = TTS_TARGET_CHANNEL_ID
        self.target_user_id = MESSAGE_BOT_TARGET_USER_ID
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return

        if message.channel.id != self.target_channel_id:
            return

        if message.author.id != self.target_user_id:
            return

        # 匹配信息格式 [伺服器] <遊戲內用戶名> message
        match = re.match(r'\[(.+?)] <(.+?)> (.+)', message.content)
        if match:
            server_name = match.group(1)
            game_username = match.group(2)
            user_message = match.group(3)

            logger.info(f"Message detected from {game_username} on {server_name}: {user_message}")

            # 使用反向映射找到用户ID
            user_id = user_settings.get_user_id_by_game_id(game_username.replace('\\', ''))
            if not user_id:
                logger.warning(f"No Discord user linked to game username: {game_username}")
                return

            settings = user_settings.get_user_settings(user_id)

            # 檢查是否為 !!tts start 或 !!tts stop 命令
            if user_message.strip() == "!!tts start":
                settings["tts_enabled"] = True
                user_settings.set_user_settings(user_id, settings)
                await message.channel.send(f"TTS 已啟用，針對用戶：{game_username}")
                logger.info(f"TTS enabled for user: {game_username}")
                return

            if user_message.strip() == "!!tts stop":
                settings["tts_enabled"] = False
                user_settings.set_user_settings(user_id, settings)
                await message.channel.send(f"TTS 已禁用，針對用戶：{game_username}")
                logger.info(f"TTS disabled for user: {game_username}")
                return

            # 如果 TTS 未啟用，則不執行 TTS
            if not settings.get("tts_enabled", False):
                logger.info(f"TTS is not enabled for user: {game_username}")
                return

            character_name = settings.get("selected_sample", "老簡")

            # 檢查用戶是否在語音頻道中
            guild = message.guild
            member = guild.get_member(user_id)
            voice_state = member.voice if member else None

            if not voice_state or not voice_state.channel:
                logger.info(f"User {game_username} is not in a voice channel.")
                return

            voice_client: disnake.VoiceClient | None = guild.voice_client

            if not voice_client:
                channel = voice_state.channel
                await channel.connect()
                voice_client = guild.voice_client

            if voice_state.channel != voice_client.channel:
                logger.info(f"Bot and user {game_username} are not in the same voice channel.")
                return

            async with self.lock:
                for attempt in range(1, self.max_retries + 1):
                    try:
                        logger.info(f"Fetching TTS audio (attempt {attempt})...")
                        # Remove the any (any text) the display name
                        player_name = member.display_name.replace(
                            re.search(r'\s\(.+?\)', member.display_name).group(),
                            ''
                        )
                        audio_data = text_to_speech(
                            f'{player_name} 說: {user_message}',
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
    bot.add_cog(MessageListener(bot))
