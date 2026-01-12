import pytest
from unittest.mock import patch, MagicMock
from bot.api.gemini_api import GeminiAPIClient


class TestGeminiAPIClient:
    @patch('bot.api.gemini_api.genai.Client')
    def test_init_default(self, mock_client):
        mock_config = MagicMock()
        mock_config.model_name = 'gemini-pro'
        mock_config.api_key = 'key'

        with patch('bot.api.gemini_api.ModelConfig', return_value=mock_config):
            client = GeminiAPIClient()
            assert client.model_name == 'gemini-pro'
            assert client.default_image_prompt == '請用簡短中文回答:'
            assert client.default_text_prompt == '請用簡短中文回答:'
            mock_client.assert_called_once_with(api_key='key')

    @patch('bot.api.gemini_api.genai.Client')
    def test_init_custom(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'

        client = GeminiAPIClient(
            model_name='custom-model',
            default_image_prompt='custom image',
            default_text_prompt='custom text',
            model_config=mock_config
        )
        assert client.model_name == 'custom-model'
        assert client.default_image_prompt == 'custom image'
        assert client.default_text_prompt == 'custom text'

    @patch('bot.api.gemini_api.genai.Client')
    @patch('bot.api.gemini_api.Image.open')
    def test_get_response_from_text_image_success(self, mock_image_open, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)
        mock_image = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image

        mock_response = MagicMock()
        client.client.models.generate_content.return_value = mock_response

        result = client.get_response_from_text_image('path/to/image.jpg', 'prompt')

        assert result == mock_response
        client.client.models.generate_content.assert_called_once_with(
            model=client.model_name,
            contents=[{"text": "prompt"}, mock_image],
            config={}
        )

    @patch('bot.api.gemini_api.genai.Client')
    @patch('bot.api.gemini_api.Image.open')
    def test_get_response_from_text_image_default_prompt(self, mock_image_open, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)
        mock_image = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image

        mock_response = MagicMock()
        client.client.models.generate_content.return_value = mock_response

        result = client.get_response_from_text_image('path/to/image.jpg')

        assert result == mock_response
        client.client.models.generate_content.assert_called_once_with(
            model=client.model_name,
            contents=[{"text": "請用簡短中文回答:"}, mock_image],
            config={}
        )

    @patch('bot.api.gemini_api.genai.Client')
    @patch('bot.api.gemini_api.Image.open')
    def test_get_response_from_text_image_api_error(self, mock_image_open, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'

        client = GeminiAPIClient(model_config=mock_config)
        mock_image = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image

        client.client.models.generate_content.side_effect = Exception('API error')

        result = client.get_response_from_text_image('path/to/image.jpg')

        assert result is None

    @patch('bot.api.gemini_api.genai.Client')
    def test_get_response_from_text_success(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)

        mock_response = MagicMock()
        client.client.models.generate_content_stream.return_value = mock_response

        result = client.get_response_from_text('Hello world', 'prompt')

        assert result == mock_response
        client.client.models.generate_content_stream.assert_called_once_with(
            model=client.model_name,
            contents='prompt\nHello world',
            config={}
        )

    @patch('bot.api.gemini_api.genai.Client')
    def test_get_response_from_text_default_prompt(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)

        mock_response = MagicMock()
        client.client.models.generate_content_stream.return_value = mock_response

        result = client.get_response_from_text('Hello world')

        assert result == mock_response
        client.client.models.generate_content_stream.assert_called_once_with(
            model=client.model_name,
            contents='請用簡短中文回答:\nHello world',
            config={}
        )

    @patch('bot.api.gemini_api.genai.Client')
    def test_get_response_from_text_exception(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'

        client = GeminiAPIClient(model_config=mock_config)
        client.client.models.generate_content_stream.side_effect = Exception('API error')

        result = client.get_response_from_text('Hello world')

        assert result is None

    @patch('bot.api.gemini_api.genai.Client')
    def test_get_response_from_text_and_history_with_history(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)

        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_chat.send_message_stream.return_value = mock_response
        client.client.chats.create.return_value = mock_chat

        history = [{'role': 'user', 'parts': [{'text': 'hi'}]}]
        result = client.get_response_from_text_and_history(history, 'Hello', 'prompt')

        assert result == mock_response
        client.client.chats.create.assert_called_once_with(
            model=client.model_name,
            history=history,
            config={}
        )
        mock_chat.send_message_stream.assert_called_once_with('Hello', config={})

    @patch('bot.api.gemini_api.genai.Client')
    def test_get_response_from_text_and_history_no_history(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)

        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_chat.send_message_stream.return_value = mock_response
        client.client.chats.create.return_value = mock_chat

        result = client.get_response_from_text_and_history([], 'Hello', 'prompt')

        assert result == mock_response
        client.client.chats.create.assert_called_once_with(
            model=client.model_name,
            history=[],
            config={}
        )
        mock_chat.send_message_stream.assert_called_once_with('prompt\nHello', config={})

    @patch('bot.api.gemini_api.genai.Client')
    def test_get_response_from_text_and_history_exception(self, mock_client):
        mock_config = MagicMock()
        mock_config.api_key = 'key'
        mock_config.generation_config = {}

        client = GeminiAPIClient(model_config=mock_config)

        mock_chat = MagicMock()
        mock_chat.send_message_stream.side_effect = Exception('API error')
        client.client.chats.create.return_value = mock_chat

        result = client.get_response_from_text_and_history([], 'Hello')

        assert result is None
