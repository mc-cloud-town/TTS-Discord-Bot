import json


def get_user_settings(user_id: int) -> dict:
    """
    獲取用戶設置
    Args:
        user_id: 用户ID

    Returns:
        dict: 用戶設置
    """
    with open('data/user_settings.json', 'r') as f:
        data = json.load(f)
    return data['user_settings'].get(str(user_id), {})


def set_user_settings(user_id: int, settings: dict):
    """
    設置用戶設置
    Args:
        user_id: 用户ID
        settings: 用戶設置
    """
    with open('data/user_settings.json', 'r+') as f:
        data = json.load(f)
        data['user_settings'][str(user_id)] = settings
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
