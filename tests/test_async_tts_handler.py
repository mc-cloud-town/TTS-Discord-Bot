import pytest
from unittest.mock import MagicMock
from bot.api.async_tts_handler import preprocess_text, split_text_into_chunks


class TestAsyncTTSHandler:
    def test_preprocess_text_no_message(self):
        text = "Hello **bold** [link](url) http://example.com <a:emoji:123>"
        result = preprocess_text(text)
        assert result == "Hello bold   "

    def test_preprocess_text_with_message_user_mention(self):
        message = MagicMock()
        guild = MagicMock()
        message.guild = guild
        user = MagicMock()
        user.display_name = "John"
        guild.get_member.return_value = user

        text = "Hello <@123>!"
        result = preprocess_text(text, message)
        assert result == "Hello ，提及 John 用戶，!"

    def test_preprocess_text_with_message_channel_mention(self):
        message = MagicMock()
        guild = MagicMock()
        message.guild = guild
        channel = MagicMock()
        channel.name = "general"
        guild.get_channel.return_value = channel

        text = "Check <#456>!"
        result = preprocess_text(text, message)
        assert result == "Check ，在 general 頻道中，!"

    def test_split_text_into_chunks(self):
        text = "這是第一句。這是第二句！這是第三句？這是第四句。"
        result = split_text_into_chunks(text, 2)
        expected = ["這是第一句。 這是第二句！", "這是第三句？ 這是第四句。"]
        assert result == expected

    def test_split_text_into_chunks_single_chunk(self):
        text = "這是第一句。"
        result = split_text_into_chunks(text, 2)
        assert result == ["這是第一句。"]

    def test_split_text_into_chunks_empty(self):
        text = ""
        result = split_text_into_chunks(text, 2)
        assert result == []