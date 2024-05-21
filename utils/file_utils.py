import json


def load_sample_data(file_path='data/sample_data.json'):
    """
    載入語音樣本數據
    Args:
        file_path: 文件路徑

    Returns:
        dict: 語音樣本數據
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def get_samples_by_character(character_name: str, sample_data_dict: dict) -> dict:
    """
    通過角色名稱獲取語音樣本
    Args:
        character_name: 角色名稱 
        sample_data_dict: 語音樣本數據

    Returns:
        dict: 語音樣本
    """
    return sample_data_dict.get(character_name, {})


def list_characters(sample_data_dict: dict) -> list:
    """
    列出所有角色
    Args:
        sample_data_dict: 語音樣本數據

    Returns:
        list: 所有角色名稱
    """
    return list(sample_data_dict.keys())
