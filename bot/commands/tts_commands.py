import asyncio
import os
import tempfile

import disnake
from disnake.ext import commands

from bot import user_settings
from bot.api.tts_handler import text_to_speech
from bot.user_settings import is_user_voice_exist
from bot.utils.extract_user_nickname import extract_user_nickname
from config import GUILD_ID, DEFAULT_VOICE
from utils.file_utils import list_characters, load_sample_data
from utils.logger import logger


class TTSCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sample_data = load_sample_data()
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2

        if not disnake.opus.is_loaded():
            logger.info("Loading opus...")
            if os.name == "nt":
                disnake.opus.load_opus("libopus-0.dll")
            else:
                disnake.opus.load_opus("/usr/lib/libopus.so")

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
                for character in (list_characters(load_sample_data()) + ["自己聲音 (需要先上傳語音樣本）"])
            ],
        ),
    ):
        """
        設置用戶的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            character_name (str): 角色名稱
        """
        await inter.response.defer(ephemeral=True)
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        settings["selected_sample"] = character_name
        user_settings.set_user_settings(user_id, settings)
        logger.info(f"Set voice sample to {character_name} for user {inter.author}")

        embed = disnake.Embed(
            title="語音樣本", description=f"語音樣本設置為 {character_name}", color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)

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
        logger.info(f"Get voice sample for user {inter.author}")

        embed = disnake.Embed(
            title="語音樣本", description=f"你當前的語音樣本是 {sample_name}", color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)

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
        character_name = settings.get("selected_sample", DEFAULT_VOICE)

        if character_name == "自己聲音 (需要先上傳語音樣本）":
            if not is_user_voice_exist(user_id):
                embed = disnake.Embed(
                    title="錯誤", description="請先上傳語音樣本。", color=disnake.Color.red()
                )
                await inter.edit_original_response(embed=embed)
                return

            # 當前用戶的語音樣本名稱為 "自己聲音 (需要先上傳語音樣本）"，且用戶已上傳語音樣本
            # 使用用戶的語音樣本名稱作為角色名稱
            character_name = str(user_id)

        voice_state = inter.author.voice
        if not voice_state or not voice_state.channel:
            embed = disnake.Embed(
                title="錯誤", description="你需要在語音頻道使用該命令。", color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        voice_client: disnake.VoiceClient | None = inter.guild.voice_client

        if not voice_client:
            channel = voice_state.channel
            await channel.connect()
            voice_client = inter.guild.voice_client

        if voice_state.channel != voice_client.channel:
            embed = disnake.Embed(
                title="錯誤",
                description="你和機器人需要在同一個語音頻道中使用該命令。",
                color=disnake.Color.red(),
            )
            await inter.edit_original_response(embed=embed)
            return

        async with self.lock:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Fetching TTS audio (attempt {attempt})...")
                    player_name = extract_user_nickname(inter.author.display_name)
                    text = f"{player_name} 說: {text}" if character_name != str(user_id) else text
                    audio_data = text_to_speech(text, character_name, )
                    logger.info("Audio data fetched successfully")
                    logger.info(f"Audio data length: {len(audio_data)} bytes")

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                        temp_audio_file.write(audio_data)
                        temp_audio_file_path = temp_audio_file.name

                    def after_playing(error):
                        logger.info(f"Finished playing: {error}")
                        os.remove(temp_audio_file_path)

                    voice_client.play(disnake.FFmpegPCMAudio(temp_audio_file_path), after=after_playing)
                    logger.info("Playing audio...")

                    embed = disnake.Embed(
                        title="TTS 播放", description=f"正在播放: {text}", color=disnake.Color.green()
                    )
                    await inter.edit_original_response(embed=embed)
                    break
                except ValueError as e:
                    logger.error(f'無法找到 {inter.author.name} 語音: ', e)
                    embed = disnake.Embed(
                        title="錯誤",
                        description="無法取的該角色，請切換角色後嘗試。",
                        color=disnake.Color.red(),
                    )
                    await inter.edit_original_response(embed=embed)
                except Exception as e:
                    logger.debug(type(e))
                    logger.debug(type(e).__name__)
                    logger.error(f"Error fetching TTS audio: {e}")
                    if attempt < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        embed = disnake.Embed(
                            title="錯誤",
                            description="獲取TTS音頻時出錯。",
                            color=disnake.Color.red(),
                        )
                        await inter.edit_original_response(embed=embed)

    @commands.slash_command(name="tts_start", guild_ids=[GUILD_ID], description="啟用文字轉語音功能")
    async def tts_start(self, inter: disnake.ApplicationCommandInteraction):
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        settings["tts_enabled"] = True
        user_settings.set_user_settings(user_id, settings)
        await inter.response.send_message(f"TTS 已啟用，針對用戶：{inter.author.name}", ephemeral=True)
        logger.info(f"TTS enabled for user: {inter.author.name}")

    @commands.slash_command(name="tts_stop", guild_ids=[GUILD_ID], description="禁用文字轉語音功能")
    async def tts_stop(self, inter: disnake.ApplicationCommandInteraction):
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        settings["tts_enabled"] = False
        user_settings.set_user_settings(user_id, settings)
        await inter.response.send_message(f"TTS 已禁用，針對用戶：{inter.author.name}", ephemeral=True)
        logger.info(f"TTS disabled for user: {inter.author.name}")


def setup(bot: commands.Bot):
    bot.add_cog(TTSCommands(bot))
