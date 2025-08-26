import io
import re
from pathlib import Path

import disnake

# 在主模塊或配置文件中添加
import pydub.utils
import requests
from pydub import AudioSegment

from config import USER_VOICE_SETTINGS_FILE, VOICE_DIR, TTS_API_URL
from utils.file_utils import get_samples_by_character, load_sample_data
from utils.logger import logger

original_get_encoder = pydub.utils.get_encoder_name


def custom_get_encoder_name():
    encoder = original_get_encoder()
    return [encoder, "-loglevel", "error"]


pydub.utils.get_encoder_name = custom_get_encoder_name


def preprocess_text(text: str, message: disnake.Message = None) -> str:
    """
    預處理文本，移除Markdown特殊字符和格式符號，替換提及的用戶和頻道
    Args:
        text (str): 要預處理的文本
        message: Discord消息對象，用於獲取用戶和頻道名稱

    Returns:
        str: 預處理後的文本
    """

    if message:
        # 替換提及用戶
        def replace_user_mention(match: re.Match) -> str:
            user_id = int(match.group(1))
            user = message.guild.get_member(user_id)

            return f"，提及 {user.display_name} 用戶，" if user else match.group(0)

        text = re.sub(r"<@!?(\d+)>", replace_user_mention, text)

        # 替換提及頻道
        def replace_channel_mention(match: re.Match) -> str:
            channel_id = int(match.group(1))
            channel = message.guild.get_channel(channel_id)

            return f"，在 {channel.name} 頻道中，" if channel else match.group(0)

        text = re.sub(r"<#(\d+)>", replace_channel_mention, text)

    # 移除Markdown特殊字符和格式符號
    def replace_other_chars(t: str) -> str:
        # 移除Markdown標題
        t = re.sub(r"#*", "", t)
        # 移除Markdown列表項目
        t = re.sub(r"\*", "", t)
        # 移除Markdown鏈接
        t = re.sub(r"\[.*?]\(.*?\)", "", t)
        # 移除多餘的空格和換行符
        t = t.replace("\n", " ").strip()
        # 移除連結
        t = re.sub(r"https?://\S+", "", t)
        # 移除Discord表情符號
        t = re.sub(r"<a?:\w+:\d+>", "", t)

        return t

    text = replace_other_chars(text)

    return text


def split_text_into_chunks(text: str, chunk_size: int = 2) -> list:
    """
    將文本分割為多個文本塊，每個文本塊包含指定數量的句子
    Args:
        text (str): 要分割的文本
        chunk_size (int): 每個文本塊包含的句子數

    Returns:
        list: 包含多個文本塊的列表
    """
    # 使用標點符號和換行符進行分割
    sentences = re.split(r"([。！？!?]|\n)", text)

    # 處理沒有斷句標點符號
    if len(sentences) == 1:
        sentences = [text]
    else:
        sentences = [a + b for a, b in zip(sentences[::2], sentences[1::2])]

    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence.strip())
        if len(current_chunk) == chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if len(current_chunk) > 0:
        chunks.append(" ".join(current_chunk))

    return chunks


def text_to_speech(text: str, character: str, message: disnake.Message = None) -> bytes:
    """
    與TTS API互動的函數
    這個函數將文本轉換為語音。
    TTS API的請求和響應如下:

    POST localhost:9880
    Request:
        {
            "ref_audio_path": "123.wav", // For APIv2
            "refer_wav_path": "123.wav",
            "prompt_text": "一二三。",
            "prompt_lang": "zh", // For APIv2
            "prompt_language": "zh",
            "text": "先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。",
            "text_lang": "zh", // For APIv2
            "text_language": "zh",
        }

    Response:
        成功: 直接返回 wav 音频流， http code 200
        失败: 返回包含错误信息的 json, http code 400

    Args:
        text (str): 要轉換的文本
        character (str): 語音角色
        message: Discord消息對象，用於獲取用戶和頻道名稱
    """
    # 預處理文本
    preprocessed_text = preprocess_text(text, message)

    chunks = split_text_into_chunks(preprocessed_text)

    sample_data = load_sample_data()
    user_voice_dict = load_sample_data(USER_VOICE_SETTINGS_FILE)
    character_content = get_samples_by_character(character, sample_data, user_voice_dict)

    if not character_content:
        raise ValueError(f"角色 '{character}' 不存在")

    character_sample = character_content

    audio_segments = []

    for chunk in chunks:
        try:
            logger.info(f"Sending TTS request for chunk: {chunk}")
            # {
            #     "ref_audio_path": config.VOICE_DIR.joinpath(character_sample["file"]).__str__(),
            #     "refer_wav_path": config.VOICE_DIR.joinpath(character_sample["file"]).__str__(),
            #     "prompt_text": character_sample["text"],
            #     "prompt_lang": "zh",
            #     "prompt_language": "zh",
            #     "text": chunk,
            #     "text_language": "zh",
            #     "text_lang": "zh",
            # }
            audio = str(Path(VOICE_DIR).joinpath(character_sample["file"]).as_posix())
            data = {
                "text": chunk,
                "text_lang": "zh",
                "ref_audio_path": audio,
                "aux_ref_audio_paths": [audio],
                "prompt_lang": "zh",
                "prompt_text": character_sample["text"],
                "top_k": 5,
                "top_p": 1,
                "temperature": 1,
                "text_split_method": "cut5",
                "batch_size": 1,
                "batch_threshold": 0.75,
                "split_bucket": True,
                "speed_factor": 1,
                "fragment_interval": 0.3,
                "seed": -1,
                "media_type": "wav",
                "streaming_mode": False,
                "parallel_infer": True,
                "repetition_penalty": 1.35,
                "sample_steps": 32,
                "super_sampling": False,
            }
            logger.info(data)
            response = requests.post(TTS_API_URL, json=data)
            response.raise_for_status()

            if response.status_code == 200:
                audio_segment = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
                audio_segments.append(audio_segment)
            else:
                logger.error(f"TTS API請求失敗: {response.status_code}, {response.text}")
                raise Exception(f"TTS API請求失敗: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS API請求異常: {e}")
            raise Exception(f"TTS API請求異常: {e}")

    combined_audio = sum(audio_segments, AudioSegment.empty())
    combined_audio_bytes = io.BytesIO()
    combined_audio.export(combined_audio_bytes, format="wav")
    combined_audio_bytes.seek(0)

    return combined_audio_bytes.read()
