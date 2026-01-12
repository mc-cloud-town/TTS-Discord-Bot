import os

import disnake
from disnake.ext import commands

from config import GUILD_ID, BOT_MANAGER_ROLES
from utils.logger import logger


class GeneralCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.allowed_roles = BOT_MANAGER_ROLES
        self.bot = bot

    @commands.slash_command(
        name="ping",
        guild_ids=[GUILD_ID]
    )
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """
        返回機器人延遲
        """
        logger.info(f'Pong! 延遲: {round(self.bot.latency * 1000)}ms')
        await inter.response.send_message(f'Pong! 延遲: {round(self.bot.latency * 1000)}ms')

    @commands.slash_command(
        name="reload",
        description="重新加載所有命令",
        guild_ids=[GUILD_ID]
    )
    async def reload(self, inter: disnake.ApplicationCommandInteraction):
        """
        重新加載所有命令
        """
        if not any(role.id in [allowed_role_id for allowed_role_id in self.allowed_roles] for role in
                   inter.author.roles):
            await inter.response.send_message("你沒有權限執行此命令。", ephemeral=True)
            return

        await inter.response.defer(ephemeral=True)

        base_path = 'bot'
        subfolders = ['commands', 'events', 'message_command']
        errors = []

        for subfolder in subfolders:
            folder_path = os.path.join(base_path, subfolder)
            for filename in os.listdir(folder_path):
                if filename.endswith('.py') and filename != '__init__.py':
                    module_name = f'{base_path}.{subfolder}.{filename[:-3]}'
                    try:
                        self.bot.reload_extension(module_name)
                        logger.info(f'Reloaded extension: {module_name}')
                    except Exception as e:
                        logger.error(f'Failed to reload extension {module_name}: {e}')
                        errors.append(f'Failed to reload extension {module_name}: {e}')

        if errors:
            await inter.followup.send("\n".join(errors), ephemeral=True)
        else:
            await inter.followup.send("所有命令已重新加載。", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(GeneralCommands(bot))
