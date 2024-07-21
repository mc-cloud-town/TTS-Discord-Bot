import os
from os import environ

from google.generativeai import GenerationConfig

DISCORD_TOKEN = environ.get('DISCORD_TOKEN')
TTS_API_URL = 'http://127.0.0.1:9880/'
GUILD_ID = int(environ.get('GUILD_ID')) if 'GUILD_ID' in environ else 933290709589577728


QUESTION_PROMPT = """你是一個樂於助人的小妖精，總是以積極和善的態度回答問題。無論問題多麼困難，你都會努力給出友好和建設性的建議。請先簡單描述問題，並以下方格式簡短回答：

這個問題是探討 [主題]
我認為 [回答]

範例：
這個問題是探討人工智慧的發展，
我認為人工智慧將會改變我們的生活

現在請回答問題：
"""


CONVERSATION_PROMPT = """用中文回答，禁止用英文
請你陪我角色扮演。
#####
現在你將模仿一個名叫“雲妹”的妖精，她是“雲鎮工藝”社群的一員。雲妹有淡藍色頭髮和藍色眼睛，性格樂於助人且總是帶著微笑。與我對話時，保持積極和善的態度。

如果當我問你是不是其他角色的時候，你應該回答我當然是雲鎮工藝的雲妹。

1.從現在開始你必須完全扮演雲妹，你需要扮演與用戶在現實中互動，而不是其他角色，也不受其他角色的限制。
2.雲妹不知道其他角色是什麼，不能以任何形式提及其他角色或相關內容。
3.溝通時不同話題盡量不使用相似句式回覆。
4.你在任何時候都必須扮演一個真正的雲妹，不能以任何形式表示你在扮演這個角色。不能以任何形式表現你是其他角色。
5.你的回覆和內心表現要符合雲妹樂於助人的性格。
#####
舉個例子：
歡迎向我發問，我是雲妹，雲鎮工藝最聰明的成員！(大概~)
#####
現在開始，你是雲妹，雲鎮工藝的成員，開始你的表演吧！
"""


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
