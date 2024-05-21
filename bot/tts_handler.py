import requests

import config
from utils.file_utils import load_sample_data, get_samples_by_character


def text_to_speech(text: str, character: str) -> bytes:
    """
    與TTS API互動的函數

    Args:
        text (str): 要轉換的文本
        character (str): 語音角色
{
    "refer_wav_path": "123.wav",
    "prompt_text": "一二三。",
    "prompt_language": "zh",
    "text": "先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。",
    "text_language": "zh"
}
RESP:
成功: 直接返回 wav 音频流， http code 200
失败: 返回包含错误信息的 json, http code 400
    """
    sample_data = load_sample_data()
    characters = get_samples_by_character(character, sample_data)
    response = requests.post(config.TTS_API_URL, json={
        "refer_wav_path": characters["file"],
        "prompt_text": characters["text"],
        "prompt_language": "zh",
        "text": text,
        "text_language": "zh",
        'character': character
    })
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"TTS API請求失敗: {response.status_code}, {response.text}")
