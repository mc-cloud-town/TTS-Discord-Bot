from disnake import Member, VoiceState
from disnake.ext.commands import Cog, Bot

from utils.logger import logger


class AutoLeaveVoice(Cog):
    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, _: VoiceState):
        voice_client = member.guild.voice_client
        bot = member.guild.me
        if voice_client is None or before is None:
            return
        if member.id == bot.id or before.channel.id != bot.voice.channel.id:
            return
        if len(before.channel.members) != 1:
            return
        logger.info(f'無人在語音中，自動離開{before.channel}')
        await voice_client.disconnect(force=True)


def setup(bot: Bot):
    bot.add_cog(AutoLeaveVoice(bot))
