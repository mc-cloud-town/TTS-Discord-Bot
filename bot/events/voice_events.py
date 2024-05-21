from disnake.ext import commands, tasks

from utils.logger import logger


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_voice_channel = None
        self.check_voice_channel.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, _before, after):
        """
        監聽成員加入或離開語音頻道的事件
        Args:
            member: 有狀態更新的成員
            _before: 之前的狀態
            after: 更新後的狀態
        """
        if member != self.bot.user:
            return

        if after.channel is not None:
            self.current_voice_channel = after.channel
            logger.info(f'Bot joined voice channel: {self.current_voice_channel.name}')
        else:
            logger.info('Bot left the voice channel')
            self.current_voice_channel = None

    @tasks.loop(minutes=5)
    async def check_voice_channel(self):
        """
        檢查當前語音頻道是否為空，如果是，則斷開連接
        """
        if self.current_voice_channel is None:
            return

        if len(self.current_voice_channel.members) == 1:
            logger.info(f'Disconnecting from empty voice channel: {self.current_voice_channel.name}')
            await self.current_voice_channel.guild.voice_client.disconnect()
            self.current_voice_channel = None

    @check_voice_channel.before_loop
    async def before_check_voice_channel(self):
        """
        在 check_voice_channel 開始之前等待 bot 完全啟動
        """
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(VoiceEvents(bot))
