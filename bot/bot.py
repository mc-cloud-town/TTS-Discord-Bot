import os

import disnake
from disnake.ext import commands

import config
from utils.logger import logger

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.InteractionBot(intents=intents)

# 加載命令和事件處理器
base_path = 'bot'
subfolders = ['commands', 'events', 'message_command']
errors = []

for subfolder in subfolders:
    folder_path = os.path.join(base_path, subfolder)
    for filename in os.listdir(folder_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f'{base_path}.{subfolder}.{filename[:-3]}'
            try:
                bot.load_extension(module_name)
                logger.info(f'Loaded extension: {module_name}')
            except Exception as e:
                logger.error(f'Failed to load extension {module_name}: {e}')
                errors.append(f'Failed to load extension {module_name}: {e}')

bot.load_extension('bot.event_handlers')


def run():
    logger.info('Starting bot...')
    bot.run(config.DISCORD_TOKEN)
