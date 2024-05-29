from disnake.ext import commands

import config
from utils.logger import logger

bot = commands.InteractionBot()


# 加載命令和事件處理器
bot.load_extension('bot.commands.general')
bot.load_extension('bot.commands.tts_commands')
bot.load_extension('bot.commands.voice_commands')
bot.load_extension('bot.commands.llm_commands')
bot.load_extension('bot.event_handlers')
bot.load_extension('bot.events.on_ready')


def run():
    logger.info('Starting bot...')
    bot.run(config.DISCORD_TOKEN)
