import requests
import os
import config
from utils.file_utils import load_sample_data, get_samples_by_character
from utils.logger import logger
import re


def preprocess_text(text: str) -> str:
    """
    預處理文本，移除Markdown特殊字符和格式符號
    Args:
        text (str): 要預處理的文本

    Returns:
        str: 預處理後的文本
    """
    # 移除Markdown標題
    text = re.sub(r'#*', '', text)
    # 移除Markdown列表項目
    text = re.sub(r'\*', '', text)
    # 移除Markdown鏈接
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    # 移除多餘的空格和換行符
    text = text.replace('\n', ' ').strip()
    return text


def text_to_speech(text: str, character: str) -> bytes:
    """
    與TTS API互動的函數
    這個函數將文本轉換為語音。
    TTS API的請求和響應如下:

    POST localhost:9880
    Request:
        {
            "refer_wav_path": "123.wav",
            "prompt_text": "一二三。",
            "prompt_language": "zh",
            "text": "先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。",
            "text_language": "zh"
        }

    Response:
        成功: 直接返回 wav 音频流， http code 200
        失败: 返回包含错误信息的 json, http code 400

    Args:
        text (str): 要轉換的文本
        character (str): 語音角色
    """
    # 預處理文本
    preprocessed_text = preprocess_text(text)

    sample_data = load_sample_data()
    character_content = get_samples_by_character(character, sample_data)

    if not character_content:
        raise Exception(f"角色 '{character}' 不存在")

    character_sample = character_content

    try:
        logger.info("Sending TTS request...")
        response = requests.post(config.TTS_API_URL, json={
            "refer_wav_path": os.path.join(os.getcwd(), "data", "samples", character_sample["file"]),
            "prompt_text": character_sample["text"],
            "prompt_language": "zh",
            "text": preprocessed_text,
            "text_language": "zh"
        })

        response.raise_for_status()

        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"TTS API請求失敗: {response.status_code}, {response.text}")
            raise Exception(f"TTS API請求失敗: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"TTS API請求異常: {e}")
        raise Exception(f"TTS API請求異常: {e}")
