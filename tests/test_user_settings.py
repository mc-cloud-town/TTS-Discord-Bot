import pytest
from unittest.mock import patch, mock_open, MagicMock
import json
from bot.user_settings import get_user_settings, set_user_settings, generate_game_id_to_user_id_mapping, get_user_id_by_game_id, is_user_voice_exist


class TestUserSettings:
    @patch('builtins.open', new_callable=mock_open, read_data='{"user_settings": {"123": {"key": "value"}}}')
    def test_get_user_settings(self, mock_file):
        result = get_user_settings(123)
        assert result == {"key": "value"}

    @patch('builtins.open', new_callable=mock_open, read_data='{"user_settings": {}}')
    def test_get_user_settings_not_found(self, mock_file):
        result = get_user_settings(123)
        assert result == {}

    @patch('builtins.open', new_callable=mock_open, read_data='{"user_settings": {"123": {"old": "val"}}}')
    @patch('json.dump')
    def test_set_user_settings(self, mock_dump, mock_file):
        mock_file.return_value.seek = MagicMock()
        mock_file.return_value.truncate = MagicMock()

        set_user_settings(123, {"new": "val"})

        expected_data = {"user_settings": {"123": {"new": "val"}}}
        mock_dump.assert_called_once_with(expected_data, mock_file.return_value, indent=4)

    @patch('builtins.open', new_callable=mock_open, read_data='{"user_settings": {"123": {"game_id": "abc"}}}')
    @patch('json.dump')
    def test_generate_game_id_to_user_id_mapping(self, mock_dump, mock_file):
        result = generate_game_id_to_user_id_mapping()

        expected = {"abc": 123}
        assert result == expected
        mock_dump.assert_called_once_with(expected, mock_file.return_value, indent=4)
    @patch('builtins.open', new_callable=mock_open, read_data='{"abc": 123}')
    def test_get_user_id_by_game_id(self, mock_file):
        result = get_user_id_by_game_id("abc")
        assert result == 123

    @patch('builtins.open', new_callable=mock_open, read_data='{"abc": 123}')
    def test_get_user_id_by_game_id_not_found(self, mock_file):
        result = get_user_id_by_game_id("xyz")
        assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data='{"123": {}}')
    def test_is_user_voice_exist_true(self, mock_file):
        result = is_user_voice_exist(123)
        assert result is True

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_is_user_voice_exist_false(self, mock_file):
        result = is_user_voice_exist(123)
        assert result is False