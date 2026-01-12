from typing import Iterator

from PIL import Image
from google import genai
from google.genai.types import GenerateContentResponse, ContentOrDict

from config import ModelConfig


class GeminiAPIClient:
    """
    API client for the Gemini model.

    Attributes:
        model_name (str): The name of the model to use. Default is 'gemini-pro'.
        default_image_prompt (str): The default prompt for image generation.
        default_text_prompt (str): The default prompt for text generation.
        model_config (ModelConfig): The model config
    """

    def __init__(
        self,
        model_name=None,
        default_image_prompt='請用簡短中文回答:',
        default_text_prompt='請用簡短中文回答:',
        model_config=None,
    ):
        """
        Initialize the API client with the model name and API key.
        """
        if model_config:
            self.model_config = model_config
        else:
            self.model_config = ModelConfig()

        self.model_name = model_name or self.model_config.model_name
        self.default_image_prompt = default_image_prompt
        self.default_text_prompt = default_text_prompt
        self.client = genai.Client(api_key=self.model_config.api_key)

    def get_response_from_text_image(self, image_path: str, prompt: str = None) -> GenerateContentResponse | None:
        """
        Send the image to the API and get the prediction result.
        """
        # Use default prompt if none provided
        if not prompt:
            prompt = self.default_image_prompt

        try:
            with Image.open(image_path) as image_data:
                # Prepare and send the request to the API
                send_content = [{"text": prompt}, image_data]

                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=send_content,
                    config=self.model_config.generation_config,
                )
        except IOError as e:
            # Handle errors related to file operations
            print(f"Error opening image file: {e}")
            return None
        except Exception as e:
            # Handle other unexpected errors
            print(f"Error during API call: {e}")
            return None

    def get_response_from_text(self, text: str, prompt: str = None) -> Iterator[GenerateContentResponse] | None:
        """
        Send the text to the API and get the prediction result.
        """
        # Use default prompt if none provided
        if not prompt:
            prompt = self.default_text_prompt

        combined_prompt = f"{prompt}\n{text}"

        try:
            return self.client.models.generate_content_stream(
                model=self.model_name,
                contents=combined_prompt,
                config=self.model_config.generation_config,
            )
        except Exception as e:
            # Handle unexpected errors
            print(f"Error during text prediction: {e}")
            return None

    def get_response_from_text_and_history(self, history: list[ContentOrDict], text: str, prompt: str = None) -> (
        GenerateContentResponse | None
    ):
        """
        Send the text history to the API and get the prediction result.

        Args:
            history: The history of the conversation.
            text: The text to send to the API.
            prompt: The prompt to use for the model.
        """
        # Use default prompt if none provided
        if not prompt:
            prompt = self.default_text_prompt

        # If history is not provided, use the default prompt
        if not history:
            text = f"{prompt}\n{text}"

        chat = self.client.chats.create(
            model=self.model_name,
            history=history,
            config=self.model_config.generation_config,
        )

        try:
            return chat.send_message_stream(text, config=self.model_config.generation_config)
        except Exception as e:
            # Handle unexpected errors
            print(f"Error during text prediction: {e}")
            return None
