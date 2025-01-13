from PIL import Image
import google.generativeai as genai
from google.ai.generativelanguage_v1 import Content
from google.generativeai.types import ContentDict, GenerateContentResponse

from config import ModelConfig


class GeminiAPIClient:
    """
    API client for the Gemini model.

    Attributes:
        model_name (str): The name of the model to use. Default is 'gemini-pro'.
        default_image_prompt (str): The default prompt for image generation.
        default_text_prompt (str): The default prompt for text generation.
        model (GenerativeModel): The generative model instance.
    """

    def __init__(
        self,
        model_name='gemini-2.0-flash-exp',
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

        self.model_name = model_name
        self.default_image_prompt = default_image_prompt
        self.default_text_prompt = default_text_prompt
        self.model = self._initialize_model()

    def _initialize_model(self) -> genai.GenerativeModel:
        """
        Configure the API client and initialize the model.
        """
        genai.configure(api_key=self.model_config.api_key)
        model = genai.GenerativeModel(
            self.model_name,
            generation_config=self.model_config.generation_config,
            safety_settings=self.model_config.safety_settings
        )
        return model

    def get_response_from_text_image(self, image_path: str, prompt: str = None) -> tuple[str, str]:
        """
        Send the image to the API and get the prediction result.
        """
        # Use default prompt if none provided
        if not prompt:
            prompt = self.default_image_prompt

        try:
            with Image.open(image_path) as image_data:
                # Prepare and send the request to the API
                send_content = [prompt, image_data]
                response = self.model.generate_content(send_content)
                return response.text, response.prompt_feedback
        except IOError as e:
            # Handle errors related to file operations
            print(f"Error opening image file: {e}")
            return "", ""
        except Exception as e:
            # Handle other unexpected errors
            print(f"Error during API call: {e}")
            return "", ""

    def get_response_from_text(self, text: str, prompt: str = None) -> tuple[str, str]:
        """
        Send the text to the API and get the prediction result.
        """
        # Use default prompt if none provided
        if not prompt:
            prompt = self.default_text_prompt

        combined_prompt = f"{prompt}\n{text}"

        try:
            response = self.model.generate_content(combined_prompt)
            return response.text, response.prompt_feedback
        except Exception as e:
            # Handle unexpected errors
            print(f"Error during text prediction: {e}")
            return "", ""

    def get_response_from_text_and_history(self, history: [Content | ContentDict], text: str, prompt: str = None) -> (
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

        chat = self.model.start_chat(history=history)

        try:
            response = chat.send_message(text, stream=True)
            return response
        except Exception as e:
            # Handle unexpected errors
            print(f"Error during text prediction: {e}")
            return None
