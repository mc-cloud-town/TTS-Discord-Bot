import json

from config import USER_SETTINGS_FILE, REVERSE_MAPPING_FILE, USER_VOICE_SETTINGS_FILE


def get_user_settings(user_id: int) -> dict:
    """
    獲取用戶設置
    Args:
        user_id: 用户ID

    Returns:
        dict: 用戶設置
    """
    with open(USER_SETTINGS_FILE, 'r') as f:
        data = json.load(f)
    return data['user_settings'].get(str(user_id), {})


def set_user_settings(user_id: int, settings: dict):
    """
    設置用戶設置
    Args:
        user_id: 用户ID
        settings: 用戶設置
    """
    with open(USER_SETTINGS_FILE, 'r+') as f:
        data = json.load(f)
        data['user_settings'][str(user_id)] = settings
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def generate_game_id_to_user_id_mapping():
    """
    生成遊戲ID到用户ID的反向映射
    """
    with open(USER_SETTINGS_FILE, 'r') as f:
        data = json.load(f)

    game_id_to_user_id = {}

    for user_id, settings in data['user_settings'].items():
        game_id = settings.get('game_id')
        if game_id:
            game_id_to_user_id[game_id] = int(user_id)

    with open(REVERSE_MAPPING_FILE, 'w') as f:
        json.dump(game_id_to_user_id, f, indent=4)

    return game_id_to_user_id


def get_user_id_by_game_id(game_id: str) -> int:
    """
    根據遊戲ID獲取用户ID
    Args:
        game_id: 遊戲ID

    Returns:
        int: 用户ID
    """
    with open(REVERSE_MAPPING_FILE, 'r') as f:
        game_id_to_user_id = json.load(f)
    return game_id_to_user_id.get(game_id)


def is_user_voice_exist(user_id: int) -> bool:
    """
    根據用户ID獲取用戶語音
    Args:
        user_id: 用户ID

    Returns:
        int: 用戶語音
    """
    with open(USER_VOICE_SETTINGS_FILE, 'r') as f:
        data = json.load(f)
    return str(user_id) in data.keys()
