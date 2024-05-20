import requests
import config


def text_to_speech(text: str, character: str) -> bytes:
    """
    與TTS API互動的函數

    Args:
        text (str): 要轉換的文本
        character (str): 語音角色
    """
    # TODO: 請求實作 TTS API
    response = requests.post(config.TTS_API_URL, json={'text': text, 'character': character})
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"TTS API請求失敗: {response.status_code}, {response.text}")
