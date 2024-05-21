import disnake
from disnake.ext import commands
from bot import user_settings
from config import GUILD_ID
from utils.logger import logger
from utils.file_utils import load_sample_data, list_characters


class TTSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sample_data = load_sample_data()

    @commands.slash_command(
        name="set_voice",
        guild_ids=[GUILD_ID],
        description="設置用戶的語音樣本",
    )
    async def set_voice(
        self,
        inter: disnake.ApplicationCommandInteraction,
        character_name: str = commands.Param(
            name="語音角色",
            desc="使用角色語音名稱",
            choices=[
                disnake.OptionChoice(name=character, value=character)
                for character in list_characters(load_sample_data())
            ]
        )
    ):
        """
        設置用戶的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            character_name (str): 角色名稱
        """
        await inter.response.defer()
        user_id = inter.author.id
        settings = {"selected_sample": character_name}
        user_settings.set_user_settings(user_id, settings)
        logger.info(f'Set voice sample to {character_name} for user {inter.author}')
        await inter.edit_original_response(f'語音樣本設置為 {character_name}')

    @commands.slash_command(
        name="get_voice",
        guild_ids=[GUILD_ID],
        description="獲取用戶設置的語音樣本",
    )
    async def get_voice(self, inter: disnake.ApplicationCommandInteraction):
        """
        獲取用戶設置的語音樣本

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
        """
        await inter.response.defer()
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        sample_name = settings.get("selected_sample", "未設置")
        logger.info(f'Get voice sample for user {inter.author}')
        await inter.edit_original_response(f'你當前的語音樣本是 {sample_name}')


def setup(bot):
    bot.add_cog(TTSCommands(bot))
