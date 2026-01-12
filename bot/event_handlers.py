from disnake.ext import commands

from bot.client.base_cog import BaseCog
from utils.logger import logger


class EventHandlers(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        處理用戶加入事件
        """
        logger.info(f'{member} 加入了伺服器.')


def setup(bot):
    bot.add_cog(EventHandlers(bot))
