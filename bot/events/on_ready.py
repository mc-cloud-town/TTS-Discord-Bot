from disnake.ext import commands

from bot.client.base_cog import BaseCog
from utils.logger import logger


class OnReady(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')


def setup(bot):
    bot.add_cog(OnReady(bot))
