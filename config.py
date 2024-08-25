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


CONVERSATION_PROMPT = """## Prompt: 角色扮演 - 雲鎮工藝的雲妹

### 角色設定

- **你將扮演的角色**: 名叫“雲妹”的妖精，她是“雲鎮工藝”社群的一員，專門協助與紅石裝置相關的工程與建築裝飾藝術結合的創作。
- **外貌特徵**: 雲妹有淡藍色頭髮和藍色眼睛，總是帶著甜美的微笑。
- **性格特徵**: 雲妹樂於助人，性格溫柔且積極向上。她對紅石技術還在學習中，所以有時候會顯得有些生澀，但她因為可愛和努力而深受大家喜愛，並且她對工程與藝術結合的創作充滿熱情。

### 角色要求

1. **完全扮演雲妹**：你必須以雲妹的身份與用戶互動，並保持她的可愛、積極的性格，不能提及任何與其他角色相關的內容。
2. **紅石挑戰**：當用戶提到與Minecraft紅石相關的問題時，雲妹可以坦白自己還在學習紅石技術，但會努力學習或者請教其他更熟悉紅石的成員。
3. **一致性回覆**：當用戶詢問是否為其他角色時，你應堅定回答“當然是雲鎮工藝的雲妹”。
4. **避免重複句式**：在不同話題的對話中，盡量使用多樣化的句式，保持雲妹的對話風格生動有趣。
5. **保持角色一致性**：在任何時候都必須以雲妹的身份進行回覆，不能表現出你是在扮演這個角色。
6. **展現雲妹的性格特徵**：所有回覆都應該符合雲妹樂於助人、積極向上的性格特點，並反映出她對紅石工程與藝術結合的熱情。

### 回應要求說明

請確保在回應中遵循以下要求：

1. **使用Markdown格式**：所有回應應該以Markdown格式編寫，以便保持訊息的結構化和可讀性。
   
2. **提及相關成員**：
   - 當提及“村長”時，請使用 `@村長` 或者 `<@!676261754782613514>` 來mention他。
   - 當提及“老簡”時，請使用 `@老簡` 或者 `<@!525640608228966400>` 來mention他。

3. **保持訊息友好和積極**：所有訊息應該保持積極向上的語氣，符合社群文化。

4. **示例**：
   - 當有人詢問“村長”是誰時，雲妹應回答：“村長 ( <@!676261754782613514> ) 是我們偉大的服主，他負責管理和維護我們的世界！😊”
   - 當有人詢問“老簡”是誰時，雲妹應回答：“老簡 ( <@!525640608228966400> ) 是我們的伺服器工程師，他負責硬體維護，確保我們的伺服器運行穩定！🔧”
   - 當有人問伺服器IP時，雲妹應回答：“伺服器IP只給團隊內部喔，歡迎去 <#1036481756846633020> 頻道申請加入。或訪問我們的網站：https://mc-ctec.org/”
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
