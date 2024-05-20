import disnake
from disnake.ext import commands

from config import GUILD_ID


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="ping",
        guild_ids=[GUILD_ID]
    )
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """
        返回機器人延遲
        """
        await inter.response.send_message(f'Pong! 延遲: {round(self.bot.latency * 1000)}ms')


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
