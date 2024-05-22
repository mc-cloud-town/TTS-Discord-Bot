import disnake
import asyncio
import os
import tempfile
from disnake.ext import commands

from bot import user_settings
from bot.tts_handler import text_to_speech
from config import GUILD_ID
from utils.logger import logger
from utils.file_utils import load_sample_data, list_characters


class TTSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sample_data = load_sample_data()
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    @commands.slash_command(
        name="set_voice",
        guild_ids=[GUILD_ID],
        description="設置用戶的語音樣本",
    )
    async def set_voice(
        self,
        inter: disnake.ApplicationCommandInteraction,
        character_name: str = commands.Param(
            name="語音角色",
            desc="使用角色語音名稱",
            choices=[
                disnake.OptionChoice(name=character, value=character)
                for character in list_characters(load_sample_data())
            ]
        )
    ):
        """
        設置用戶的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            character_name (str): 角色名稱
        """
        await inter.response.defer(ephemeral=True)
        user_id = inter.author.id
        settings = {"selected_sample": character_name}
        user_settings.set_user_settings(user_id, settings)
        logger.info(f'Set voice sample to {character_name} for user {inter.author}')
        await inter.edit_original_response(f'語音樣本設置為 {character_name}')

    @commands.slash_command(
        name="get_voice",
        guild_ids=[GUILD_ID],
        description="獲取用戶設置的語音樣本",
    )
    async def get_voice(self, inter: disnake.ApplicationCommandInteraction):
        """
        獲取用戶設置的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
        """
        await inter.response.defer(ephemeral=True)
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        sample_name = settings.get("selected_sample", "未設置")
        logger.info(f'Get voice sample for user {inter.author}')
        await inter.edit_original_response(f'你當前的語音樣本是 {sample_name}')

    @commands.slash_command(
        name="play_tts",
        guild_ids=[GUILD_ID],
        description="播放文本轉語音",
    )
    async def play_tts(self, inter: disnake.ApplicationCommandInteraction, text: str):
        """
        播放文本轉語音

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            text (str): 要轉換為語音的文本
        """
        await inter.response.defer(ephemeral=True)
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        character_name = settings.get("selected_sample", "")

        if not character_name:
            await inter.edit_original_response("你尚未設置語音樣本。")
            return

        voice_state = inter.author.voice
        if not voice_state or not voice_state.channel:
            embed = disnake.Embed(
                title="錯誤",
                description="你需要在語音頻道使用該命令。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        voice_client = inter.guild.voice_client
        if not voice_client:
            await inter.edit_original_response(
                "機器人不在任何語音頻道。請先使用 `/join_voice` 命令讓機器人加入語音頻道。")
            return

        async with self.lock:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Fetching TTS audio (attempt {attempt})...")
                    audio_data = text_to_speech(text, character_name)
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

                    await inter.edit_original_response("正在播放...")
                    break
                except Exception as e:
                    logger.error(f"Error fetching TTS audio: {e}")
                    if attempt < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        await inter.edit_original_response("獲取TTS音頻時出錯。")


def setup(bot):
    bot.add_cog(TTSCommands(bot))
