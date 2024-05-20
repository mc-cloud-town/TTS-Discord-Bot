import disnake
from disnake.ext import commands

from bot import user_settings
from config import GUILD_ID


class TTSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="set_voice",
        guild_ids=[GUILD_ID]
    )
    async def set_voice(self, inter: disnake.ApplicationCommandInteraction, sample_name: str):
        """
        設置用戶的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            sample_name (str): 語音樣本名稱
        """
        user_id = inter.author.id
        settings = {"selected_sample": sample_name}
        user_settings.set_user_settings(user_id, settings)
        await inter.response.send_message(f'語音樣本設置為 {sample_name}')

    @commands.slash_command(
        name="get_voice",
        guild_ids=[GUILD_ID]
    )
    async def get_voice(self, inter: disnake.ApplicationCommandInteraction):
        """
        獲取用戶設置的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
        """
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        sample_name = settings.get("selected_sample", "未設置")
        await inter.response.send_message(f'你當前的語音樣本是 {sample_name}')


def setup(bot):
    bot.add_cog(TTSCommands(bot))
