import asyncio
import io
import re
from pathlib import Path

import pydub.utils
from config import USER_VOICE_SETTINGS_FILE, VOICE_DIR, TTS_API_URL
from utils.file_utils import get_samples_by_character, load_sample_data
from utils.logger import logger
from disnake import Message
from pydub import AudioSegment
from aiohttp import ClientSession, ClientTimeout

original_get_encoder = pydub.utils.get_encoder_name


def custom_get_encoder_name():
    encoder = original_get_encoder()
    return [encoder, "-loglevel", "error"]


pydub.utils.get_encoder_name = custom_get_encoder_name


def preprocess_text(text: str, message: Message = None) -> str:
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

    def insert_commas_for_long_text(t, limit=200):
        segments = re.split(r"(?<=[。！？，])", t)
        processed_segments = []
        for seg in segments:
            if not seg:
                continue
            if len(seg) >= limit:
                sub_chunks = [seg[i : i + limit] for i in range(0, len(seg), limit)]
                new_seg = "，".join(sub_chunks)
                processed_segments.append(new_seg)
            else:
                processed_segments.append(seg)
        return "".join(processed_segments)

    text = replace_other_chars(text)
    if [
        i
        for i in [c for c in re.split(r"(?<=[。！？，])", text) if c.strip()]
        if len(i) >= 200
    ]:
        text = insert_commas_for_long_text(text)
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
    raw_sentences = re.split(r"([。！？!?\n])", text)
    sentences = []
    for i in range(0, len(raw_sentences) - 1, 2):
        s = raw_sentences[i] + raw_sentences[i + 1]
        if s.strip():
            sentences.append(s.strip())
    if len(raw_sentences) % 2 != 0:
        last_piece = raw_sentences[-1].strip()
        if last_piece:
            sentences.append(last_piece)
    if not sentences:
        return [text] if text.strip() else []
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        group = sentences[i : i + chunk_size]
        chunks.append(" ".join(group))
    return chunks


async def text_to_speech(
    text: str, character: str, message: Message = None, is_preprocess: bool = False
) -> bytes:
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
    preprocessed_text = text if is_preprocess else preprocess_text(text, message)
    chunks = split_text_into_chunks(preprocessed_text)

    sample_data = load_sample_data()
    user_voice_dict = load_sample_data(USER_VOICE_SETTINGS_FILE)
    character_content = get_samples_by_character(
        character, sample_data, user_voice_dict
    )

    if not character_content:
        raise ValueError(f"角色 '{character}' 不存在")

    character_sample = character_content
    audio_segments = []

    time_out = ClientTimeout(total=1200)
    async with ClientSession(timeout=time_out) as session:
        for chunk in chunks:
            try:
                logger.info(f"Sending TTS request for chunk: {chunk}")
                audio_path = str(
                    Path(VOICE_DIR)
                    .joinpath(character_sample["file"])
                    .as_posix()
                )
                data = {
                    "text": chunk,
                    "text_lang": "zh",
                    "ref_audio_path": audio_path,
                    "aux_ref_audio_paths": [audio_path],
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
                logger.debug(data)
                async with session.post(
                    TTS_API_URL, json=data
                ) as response:
                    if response.status == 200:
                        content = await response.read()

                        # AudioSegment.from_file 是阻塞操作，建議在 thread 中執行
                        def process_audio(data_bytes):
                            return AudioSegment.from_file(
                                io.BytesIO(data_bytes), format="wav"
                            )

                        audio_segment = await asyncio.to_thread(process_audio, content)
                        audio_segments.append(audio_segment)
                    else:
                        resp_text = await response.text()
                        logger.error(
                            f"TTS API請求失敗: {response.status}, {resp_text}"
                        )
                        raise Exception(f"TTS API請求失敗: {response.status}")

            except Exception as e:
                logger.error(f"TTS API請求異常: {e}")
                raise e

    if not audio_segments:
        return b""

    def finalize_audio(segments):
        combined = sum(segments, AudioSegment.empty())
        out_buf = io.BytesIO()
        combined.export(out_buf, format="wav")
        return out_buf.getvalue()

    combined_audio_bytes = await asyncio.to_thread(finalize_audio, audio_segments)

    return combined_audio_bytes
