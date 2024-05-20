from disnake.ext import commands

from utils.logger import logger


class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')


def setup(bot):
    bot.add_cog(OnReady(bot))
