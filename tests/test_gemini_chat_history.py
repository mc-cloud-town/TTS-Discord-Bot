import pytest
from unittest.mock import patch, MagicMock
from bot.api.gemini_chat_history import GeminiChatHistory


class TestGeminiChatHistory:
    @patch('bot.api.gemini_chat_history.load_user_conversation', return_value=[])
    def test_init_empty_history(self, mock_load):
        history = GeminiChatHistory(123)
        assert history.user_id == 123
        assert history.history == []

    @patch('bot.api.gemini_chat_history.load_user_conversation', return_value=[{"parts": ["old format"], "role": "user"}])
    def test_init_legacy_format(self, mock_load):
        history = GeminiChatHistory(123)
        assert history.history == [{"parts": [{"text": "old format"}], "role": "user"}]

    @patch('bot.api.gemini_chat_history.load_user_conversation', return_value=[{"parts": [{"text": "new format"}], "role": "user"}])
    def test_init_new_format(self, mock_load):
        history = GeminiChatHistory(123)
        assert history.history == [{"parts": [{"text": "new format"}], "role": "user"}]

    def test_add_message(self):
        history = GeminiChatHistory(123)
        history.add_message("Hello", "user")
        assert history.history == [{"parts": [{"text": "Hello"}], "role": "user"}]

    def test_get_history(self):
        history = GeminiChatHistory(123)
        history.history = [{"test": "data"}]
        assert history.get_history() == [{"test": "data"}]

    @patch('bot.api.gemini_chat_history.save_user_conversation')
    def test_clear_history(self, mock_save):
        history = GeminiChatHistory(123)
        history.history = [{"test": "data"}]
        history.clear_history()
        assert history.history == []
        mock_save.assert_called_once_with(123, [])

    @patch('bot.api.gemini_chat_history.save_user_conversation')
    def test_save_history(self, mock_save):
        history = GeminiChatHistory(123)
        history.history = [{"test": "data"}]
        history.save_history()
        mock_save.assert_called_once_with(123, [{"test": "data"}])