import disnake
import asyncio
import os
import tempfile

from disnake import HTTPException
from disnake.ext import commands
from bot.api.tts_handler import text_to_speech
from bot import user_settings
from bot.user_settings import is_user_voice_exist
from bot.utils.extract_user_nickname import extract_user_nickname
from config import GUILD_ID
from utils.logger import logger


class PlayTTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    @commands.message_command(name="Play TTS (朗誦訊息到語音頻道)", guild_ids=[GUILD_ID])
    async def play_tts(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
        """
        通過用戶右鍵選擇的消息朗誦訊息到語音頻道

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            message (disnake.Message): 用戶右鍵選擇的消息
        """
        await inter.response.defer(ephemeral=True)
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)

        character_name = settings.get("selected_sample", "老簡")

        if character_name == '自己聲音 (需要先上傳語音樣本）':
            if not is_user_voice_exist(user_id):
                embed = disnake.Embed(
                    title="錯誤",
                    description="請先上傳語音樣本。",
                    color=disnake.Color.red()
                )
                await inter.edit_original_response(embed=embed)
                return

            # 當前用戶的語音樣本名稱為 "自己聲音 (需要先上傳語音樣本）"，且用戶已上傳語音樣本
            # 使用用戶的語音樣本名稱作為角色名稱
            character_name = str(user_id)

        voice_state = inter.author.voice
        if not voice_state or not voice_state.channel:
            embed = disnake.Embed(
                title="錯誤",
                description="你需要在語音頻道使用該命令。",
                color=disnake.Color.red()
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
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        async with self.lock:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Fetching TTS audio (attempt {attempt})...")
                    player_name = extract_user_nickname(inter.author.display_name)
                    text = f"{player_name} 說: {message.content}" if character_name != str(user_id) else message.content
                    audio_data = text_to_speech(text, character_name, message)
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

                    embed = disnake.Embed(
                        title="TTS 播放",
                        description=f"正在播放: {message.content}",
                        color=disnake.Color.green()
                    )
                    await inter.edit_original_response(embed=embed)
                    break
                except HTTPException as e:
                    logger.info(f"{e.args}")
                    logger.error(f"Error fetching TTS audio: {e}")
                    if attempt < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        embed = disnake.Embed(
                            title="錯誤",
                            description="獲取TTS音頻時出錯。",
                            color=disnake.Color.red()
                        )
                        await inter.edit_original_response(embed=embed)


def setup(bot):
    bot.add_cog(PlayTTS(bot))
