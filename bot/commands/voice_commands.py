import disnake
from disnake.ext import commands
from utils.logger import logger
from config import GUILD_ID


class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await inter.edit_original_message(embed=embed)
            return

        channel = voice_state.channel
        if inter.guild.me.voice is not None:
            await inter.guild.me.move_to(channel)
        else:
            await channel.connect()

        logger.info(f'Bot joined voice channel: {channel.name}')

        embed = disnake.Embed(
            title="成功",
            description=f'已加入語音頻道: <#{channel.id}>',
            color=disnake.Color.green()
        )

        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(VoiceCommands(bot))
