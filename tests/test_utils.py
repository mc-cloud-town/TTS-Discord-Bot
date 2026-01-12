import pytest
from unittest.mock import patch, mock_open
import json
import logging
from utils import api_utils, file_utils, logger


class TestApiUtils:
    @patch('utils.api_utils.requests.post')
    def test_make_post_request_success(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'key': 'value'}

        result = api_utils.make_post_request('http://example.com', {'data': 'test'})

        assert result == {'key': 'value'}
        mock_post.assert_called_once_with('http://example.com', json={'data': 'test'})

    @patch('utils.api_utils.requests.post')
    def test_make_post_request_failure(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.raise_for_status.side_effect = Exception('Request failed')

        with pytest.raises(Exception):
            api_utils.make_post_request('http://example.com', {'data': 'test'})

    @patch('utils.api_utils.requests.get')
    def test_make_get_request_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'key': 'value'}

        result = api_utils.make_get_request('http://example.com')

        assert result == {'key': 'value'}
        mock_get.assert_called_once_with('http://example.com')

    @patch('utils.api_utils.requests.get')
    def test_make_get_request_failure(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.raise_for_status.side_effect = Exception('Request failed')

        with pytest.raises(Exception):
            api_utils.make_get_request('http://example.com')


class TestFileUtils:
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_sample_data(self, mock_file):
        result = file_utils.load_sample_data('data/sample_data.json')
        assert result == {'key': 'value'}
        mock_file.assert_called_once_with('data/sample_data.json', 'r', encoding='utf-8')

    def test_get_samples_by_character(self):
        sample_data = {'char1': {'file': 'a.wav', 'text': 'hello'}}
        user_voice = {'char2': {'file': 'b.wav', 'text': 'hi'}}
        result = file_utils.get_samples_by_character('char1', sample_data, user_voice)
        assert result == {'file': 'a.wav', 'text': 'hello'}

        result = file_utils.get_samples_by_character('char2', sample_data, user_voice)
        assert result == {'file': 'b.wav', 'text': 'hi'}

        result = file_utils.get_samples_by_character('nonexistent', sample_data, user_voice)
        assert result == {}

    def test_list_characters(self):
        sample_data = {'char1': {}, 'char2': {}}
        result = file_utils.list_characters(sample_data)
        assert result == ['char1', 'char2']

    @patch('builtins.open', new_callable=mock_open, read_data='[{"parts": ["text1"]}]')
    def test_load_user_conversation_legacy(self, mock_file):
        result = file_utils.load_user_conversation(123)
        assert result == [{"parts": [{"text": "text1"}]}]
        mock_file.assert_called_once_with('data/conversations/123.json', 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_load_user_conversation_empty(self, mock_file):
        result = file_utils.load_user_conversation(123)
        assert result == []

    @patch('builtins.open')
    @patch('os.path.exists', return_value=False)
    def test_load_user_conversation_not_found(self, mock_exists, mock_file):
        mock_file.side_effect = FileNotFoundError
        result = file_utils.load_user_conversation(123)
        assert result == []

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_user_conversation(self, mock_dump, mock_file):
        conversation = [{'parts': [{'text': 'hello'}]}]
        file_utils.save_user_conversation(123, conversation)
        mock_file.assert_called_once_with('data/conversations/123.json', 'w', encoding='utf-8')
        mock_dump.assert_called_once_with(conversation, mock_file(), ensure_ascii=False, indent=4)

    @patch('utils.file_utils.load_sample_data', return_value={'char1': {}})
    @patch('utils.file_utils.save_sample_data')
    def test_add_character_success(self, mock_save, mock_load):
        file_utils.add_character('char2', 'file.wav', 'text')
        mock_load.assert_called_once_with('data/sample_data.json')
        mock_save.assert_called_once_with({'char1': {}, 'char2': {'file': 'file.wav', 'text': 'text'}}, 'data/sample_data.json')

    @patch('utils.file_utils.load_sample_data', return_value={'char1': {}})
    def test_add_character_exists(self, mock_load):
        with pytest.raises(ValueError, match='character already exists'):
            file_utils.add_character('char1', 'file.wav', 'text')

    @patch('utils.file_utils.load_sample_data', return_value={'char1': {'file': 'a.wav', 'text': 'hello'}})
    @patch('utils.file_utils.save_sample_data')
    def test_remove_character_success(self, mock_save, mock_load):
        result = file_utils.remove_character('char1')
        assert result == {'file': 'a.wav', 'text': 'hello'}
        mock_save.assert_called_once_with({}, 'data/sample_data.json')

    @patch('utils.file_utils.load_sample_data', return_value={})
    def test_remove_character_not_found(self, mock_load):
        with pytest.raises(ValueError, match='character not found'):
            file_utils.remove_character('char1')

    @patch('utils.file_utils.load_sample_data', return_value={'char1': {'file': 'a.wav', 'text': 'hello'}})
    @patch('utils.file_utils.save_sample_data')
    def test_edit_character_filename(self, mock_save, mock_load):
        file_utils.edit_character('char1', filename='b.wav')
        mock_save.assert_called_once_with({'char1': {'file': 'b.wav', 'text': 'hello'}}, 'data/sample_data.json')

    @patch('utils.file_utils.load_sample_data', return_value={'char1': {'file': 'a.wav', 'text': 'hello'}})
    @patch('utils.file_utils.save_sample_data')
    def test_edit_character_text(self, mock_save, mock_load):
        file_utils.edit_character('char1', text='hi')
        mock_save.assert_called_once_with({'char1': {'file': 'a.wav', 'text': 'hi'}}, 'data/sample_data.json')

    @patch('utils.file_utils.load_sample_data', return_value={})
    def test_edit_character_not_found(self, mock_load):
        with pytest.raises(ValueError, match='character not found'):
            file_utils.edit_character('char1', filename='b.wav')


class TestLogger:
    @patch('utils.logger.logging.getLogger')
    @patch('utils.logger.logging.StreamHandler')
    @patch('utils.logger.logging.handlers.RotatingFileHandler')
    @patch('utils.logger.os.path.exists', return_value=True)
    @patch('utils.logger.os.makedirs')
    def test_setup_logger(self, mock_makedirs, mock_exists, mock_file_handler, mock_stream_handler, mock_get_logger):
        from config import LOGGER_LEVEL
        mock_logger = mock_get_logger.return_value
        mock_console = mock_stream_handler.return_value
        mock_file = mock_file_handler.return_value

        result = logger.setup_logger()

        assert result == mock_logger
        mock_logger.setLevel.assert_called_with(LOGGER_LEVEL)
        mock_console.setLevel.assert_called_with(LOGGER_LEVEL)
        mock_file.setLevel.assert_called_with(logging.INFO)
        mock_logger.addHandler.assert_any_call(mock_console)
        mock_logger.addHandler.assert_any_call(mock_file)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_sample_data(self, mock_dump, mock_file):
        data = {'key': 'value'}
        file_utils.save_sample_data(data, 'test.json')
        mock_file.assert_called_once_with('test.json', 'w', encoding='utf-8')
        mock_dump.assert_called_once_with(data, mock_file(), ensure_ascii=False, indent=4)
