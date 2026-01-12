import disnake
import asyncio

from disnake import HTTPException
from disnake.ext import commands
from bot.api.async_tts_handler import text_to_speech
from bot import user_settings
from bot.client.base_cog import BaseCog
from bot.user_settings import is_user_voice_exist
from bot.utils.audio_queue import AudioItem
from bot.utils.extract_user_nickname import extract_user_nickname
from config import GUILD_ID, DEFAULT_VOICE
from utils.logger import logger


class PlayTTS(BaseCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
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

        character_name = settings.get("selected_sample", DEFAULT_VOICE)

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

        try:
            player_name = extract_user_nickname(inter.author.display_name)
            speech_text = f"{player_name} 說: {message.content}" if character_name != str(user_id) else message.content
            audio_data = await text_to_speech(speech_text, character_name)
            logger.info(f"Audio data length: {len(audio_data)} bytes")
            audio_item = AudioItem(
                audio_data=audio_data,
                voice_state=voice_state,
                text=speech_text,
                guild_id=inter.guild.id,
            )
            await self.audio_manager.add_to_queue(audio_item)
            logger.info("Audio data add to queue")
            embed = disnake.Embed(
                title="TTS 播放",
                description=f"已加入代播放清單: {message.content}",
                color=disnake.Color.green()
            )
            await inter.edit_original_response(embed=embed)
        except HTTPException as e:
            logger.info(f"{e.args}")
            logger.error(f"Error fetching TTS audio: {e}")
            embed = disnake.Embed(
                title="錯誤",
                description="獲取TTS音頻時出錯。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)


def setup(bot):
    bot.add_cog(PlayTTS(bot))
