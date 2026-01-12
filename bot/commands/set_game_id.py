import disnake
from disnake.ext import commands

from bot import user_settings
from bot.client.base_cog import BaseCog
from config import GUILD_ID
from utils.logger import logger


class SetGameID(BaseCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.slash_command(
        name="set_game_id",
        guild_ids=[GUILD_ID],
        description="綁定你的遊戲ID以便TTS觸發",
    )
    async def set_game_id(
        self,
        inter: disnake.ApplicationCommandInteraction,
        game_id: str = commands.Param(
            name="遊戲id",
            desc="請輸入你的遊戲內id",
        )
    ):
        """
        綁定用戶的遊戲ID

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
            game_id (str): 用戶的遊戲ID
        """
        await inter.response.defer(ephemeral=True)
        user_id = inter.author.id
        settings = user_settings.get_user_settings(user_id)
        settings["game_id"] = game_id
        user_settings.set_user_settings(user_id, settings)
        user_settings.generate_game_id_to_user_id_mapping()

        logger.info(f'Set game ID to {game_id} for user {inter.author}')

        embed = disnake.Embed(
            title="遊戲ID綁定成功",
            description=f"你的遊戲ID已綁定為 {game_id}",
            color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(SetGameID(bot))
