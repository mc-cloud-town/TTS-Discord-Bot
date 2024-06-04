from pathlib import Path

import disnake
import asyncio
import os
import tempfile
from disnake.ext import commands

from bot.api.gemini_chat_history import GeminiChatHistory
from bot.api.tts_handler import text_to_speech
from bot.api.gemini_api import GeminiAPIClient
from config import GUILD_ID, ModelConfig, QUESTION_PROMPT, CONVERSATION_PROMPT
from utils.file_utils import list_characters, load_sample_data
from utils.logger import logger


class LLMCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 2
        self.llm_client = GeminiAPIClient(model_config=ModelConfig())

    @commands.slash_command(
        name="ask",
        guild_ids=[GUILD_ID],
        description="向語言模型提問並將回覆轉成語音播放",
    )
    async def ask(
        self,
        inter: disnake.ApplicationCommandInteraction,
        question: str = commands.Param(
            name="問題",
            desc="提問內容",
        ),
        play_audio: bool = commands.Param(
            name="播放語音",
            description="是否將回覆轉成語音播放",
            default=False,
        ),
        character_name: str = commands.Param(
            name="語音角色",
            desc="使用角色語音名稱",
            choices=[
                disnake.OptionChoice(name=character, value=character)
                for character in list_characters(load_sample_data())
            ],
            default="可莉"
        ),
        image: disnake.Attachment = commands.Param(
            name="附件圖片",
            description="上傳一張圖片作為問題的附加內容",
            default=None,
        )
    ):
        """
        向語言模型提問並將回覆轉成語音播放

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            question (str): 用戶提問
            play_audio (bool): 是否將回覆轉成語音播放
            character_name (str): 使用角色語音名稱
            image (disnake.Attachment): 用戶上傳的圖片（可選）
        """
        await inter.response.defer()

        logger.info(f"Sending question to LLM {'with image' if image is not None else ''}: {question}")

        embed = disnake.Embed(
            title="雲妹思考中",
            description="正在思考，請稍等我一下。",
            color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)

        if image and not image.content_type.startswith("image"):
            embed = disnake.Embed(
                title="錯誤",
                description="請上傳一張圖片。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        if image:
            image_path: os.PathLike = Path(tempfile.mktemp(suffix=".png"))
            await image.save(image_path)
            response_text, feedback = self.llm_client.get_response_from_text_image(str(image_path), question)
            os.remove(image_path)
        else:
            response_text, feedback = self.llm_client.get_response_from_text(question, QUESTION_PROMPT)

        if not response_text:
            embed = disnake.Embed(
                title="錯誤",
                description="語言模型回覆無效。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        logger.info(f"Received response from LLM: {response_text}")

        embed = disnake.Embed(
            title="雲妹回覆",
            description=f"**關於你的問題**: {question}\n\n**我的回答**:\n{response_text}",
            color=disnake.Color.green()
        )

        if image:
            embed.set_image(url=image.url)

        embed.set_footer(text="該技術使用Google Gemini")

        await inter.edit_original_response(embed=embed)

        if not play_audio:
            return

        voice_state = inter.author.voice
        if not voice_state or not voice_state.channel:
            embed = disnake.Embed(
                title="錯誤",
                description="你需要在語音頻道使用該命令。",
                color=disnake.Color.red()
            )
            await inter.followup.send(embed=embed, ephemeral=True)
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
            await inter.followup.send(embed=embed, ephemeral=True)
            return

        async with self.lock:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Fetching TTS audio (attempt {attempt})...")
                    audio_data = text_to_speech(response_text, character_name)
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
                        title="雲妹回覆",
                        description=f"正在播放: {response_text}",
                        color=disnake.Color.green()
                    )
                    await inter.followup.send(embed=embed, ephemeral=True)
                    break
                except Exception as e:
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
                        await inter.followup.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="chat",
        guild_ids=[GUILD_ID],
        description="與語言模型進行對話",
    )
    async def chat(
        self,
        inter: disnake.ApplicationCommandInteraction,
        message: str = commands.Param(
            name="訊息",
            desc="要傳遞給語言模型的訊息",
        ),
    ):
        """
        與語言模型進行對話

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            message (str): 用戶訊息
        """
        await inter.response.defer()

        logger.info(f"Sending message to LLM: {message}")

        user_history = GeminiChatHistory(inter.author.id)
        history = user_history.get_history()

        response = self.llm_client.get_response_from_text_and_history(
            history,
            message,
            CONVERSATION_PROMPT
        )

        if not response:
            embed = disnake.Embed(
                title="錯誤",
                description="語言模型回覆無效。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return
        response_text = ''

        try:
            for chunk in response:
                response_text += chunk.text

                embed = disnake.Embed(
                    title="雲妹回覆",
                    description=f"**你說**: {message}\n\n**我的回答**:\n{response_text}",
                    color=disnake.Color.green()
                )

                await inter.edit_original_response(embed=embed)

            # If history is not provided, use the default prompt
            if history is None or len(history) == 0:
                message = f"{CONVERSATION_PROMPT}\n{message}"

            # Save the conversation history
            user_history.add_message(message, "user")
            user_history.add_message(response_text, "model")
            user_history.save_history()
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            embed = disnake.Embed(
                title="錯誤",
                description="處理回覆時出錯。",
                color=disnake.Color.red()
            )
            await inter.send(embed=embed)

    @commands.slash_command(
        name="clear_chat",
        guild_ids=[GUILD_ID],
        description="清除對話記錄",
    )
    async def clear_chat(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        """
        清除對話記錄

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
        """
        await inter.response.defer(ephemeral=True)

        logger.info("Clearing conversation history")

        user_history = GeminiChatHistory(inter.author.id)
        user_history.clear_history()

        embed = disnake.Embed(
            title="對話記錄已清除",
            description="你的對話記錄已被清除。",
            color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)


def setup(bot):
    bot.add_cog(LLMCommands(bot))
