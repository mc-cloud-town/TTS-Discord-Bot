import os
from os import environ

from google.generativeai import GenerationConfig

DISCORD_TOKEN = environ.get('DISCORD_TOKEN')
TTS_API_URL = 'http://127.0.0.1:9880/'
GUILD_ID = 933290709589577728


# Configurations for the API client
class ModelConfig:
    """
    Configuration class for the model.

    The configuration class contains the default values for the model configuration.

    Attributes:
        model_name (str): The name of the model to use.
        default_prompt (str): The default prompt to use for the model.
        api_key (str): The API key for the model.
        safety_settings (list): The safety settings for the model.
        generation_config (GenerationConfig): The generation configuration for the model.
    """

    def __init__(
        self,
        api_key=None,
        candidate_count=1,
        temperature=0.7,
        top_k=1,
        top_p=1,
        max_output_tokens=512,
    ):
        """
        Initialize the model configuration.
        Args:
            api_key (str): The API key for the model.
        """
        self.model_name = 'gemini-pro'
        self.default_prompt = 'Describe the image in a few words.'
        if api_key:
            self.api_key = api_key
        elif 'GOOGLE_API_KEY' in os.environ:
            self.api_key = os.environ['GOOGLE_API_KEY']
        else:
            raise ValueError("API key not provided. Either config a environment variable 'GOOGLE_API_KEY' or pass it "
                             "as an argument 'api_key'.")

        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        self.generation_config = GenerationConfig(
            candidate_count=candidate_count,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_output_tokens=max_output_tokens
        )
