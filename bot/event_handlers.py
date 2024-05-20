from disnake.ext import commands

from utils.logger import logger


class EventHandlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        處理用戶加入事件
        """
        logger.info(f'{member} 加入了伺服器.')


def setup(bot):
    bot.add_cog(EventHandlers(bot))
