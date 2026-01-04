import disnake
from disnake.user import User
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from bot.client.base_cog import BaseCog
from utils.logger import logger
from config import GUILD_ID


class VoiceCommands(BaseCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.slash_command(
        name="join_voice",
        guild_ids=[GUILD_ID],
        description="讓機器人加入當前用戶的語音頻道",
    )
    async def join_voice(self, inter: disnake.ApplicationCommandInteraction):
        """
        讓機器人加入當前用戶的語音頻道

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
        """
        await inter.response.defer(ephemeral=True)

        voice_state = inter.author.voice
        if voice_state is None or voice_state.channel is None:
            embed = disnake.Embed(
                title="錯誤",
                description="你需要在語音頻道使用該命令。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        channel = voice_state.channel
        try:
            if inter.guild.me.voice is not None:
                await inter.guild.voice_client.disconnect(force=True)
                await channel.connect()
            else:
                await channel.connect()
        except CommandInvokeError:
            embed = disnake.Embed(
                title="錯誤",
                description="無法連接至該語音。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            logger.warn(f'can not joined voice channel: {channel.name}')
            return

        logger.info(f'Bot joined voice channel: {channel.name}')

        embed = disnake.Embed(
            title="成功",
            description=f'已加入語音頻道: <#{channel.id}>',
            color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)

    @commands.slash_command(
        name="leave_voice",
        guild_ids=[GUILD_ID],
        description="讓機器人離開當前語音頻道",
    )
    async def leave_voice(self, inter: disnake.ApplicationCommandInteraction):
        """
        讓機器人離開當前語音頻道

        Args:
            inter (disnake.ApplicationCommandInteraction): 交互事件
        """
        await inter.response.defer(ephemeral=True)

        voice_client = inter.guild.voice_client
        if voice_client is None:
            embed = disnake.Embed(
                title="錯誤",
                description="機器人不在任何語音頻道。",
                color=disnake.Color.red()
            )
            await inter.edit_original_response(embed=embed)
            return

        await voice_client.disconnect(force=True)

        logger.info('Bot left the voice channel')

        embed = disnake.Embed(
            title="成功",
            description="已離開語音頻道。",
            color=disnake.Color.green()
        )

        await inter.edit_original_response(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(VoiceCommands(bot))
