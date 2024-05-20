import os
import logging
import logging.handlers


def setup_logger():
    """
    設置全局日誌記錄器
    """
    bot_logger = logging.getLogger('TTSBot')
    bot_logger.setLevel(logging.DEBUG)

    # 創建處理器 - 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 創建處理器 - 文件處理器
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/tts_bot.log', maxBytes=5 * 1024 * 1024, backupCount=2
    )
    file_handler.setLevel(logging.INFO)

    # 創建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加處理器
    bot_logger.addHandler(console_handler)
    bot_logger.addHandler(file_handler)

    return bot_logger


# 創建日誌記錄器目錄
if not os.path.exists('logs'):
    os.makedirs('logs')

# 創建全局日誌記錄器
logger = setup_logger()
