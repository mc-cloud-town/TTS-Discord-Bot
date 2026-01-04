from disnake.ext.commands import Cog, Bot

from bot.utils.audio_queue import AudioQueue


class BaseCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.audio_manager = AudioQueue()
