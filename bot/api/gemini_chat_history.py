from google.genai.types import ContentOrDict

from utils.file_utils import load_user_conversation, save_user_conversation


class GeminiChatHistory:
    """
    Manages the chat history for the Gemini model.

    Attributes:
        history (list): The chat history.
    """

    def __init__(self, user_id: int):
        """
        Initialize the chat history.
        """
        self.history: list[ContentOrDict] = []
        self.user_id = user_id

        # Try to get the user's conversation from the json file
        user_conversation = load_user_conversation(user_id)

        if user_conversation:
            self.history = user_conversation

    def add_message(self, message: str, role: str):
        """
        Add a message to the chat history.

        Args:
            message (str): The message to add.
            role (str): The role of the message sender.
        """
        self.history.append({"parts": [message], "role": role})

    def get_history(self) -> list[ContentOrDict]:
        """
        Get the chat history.

        Returns:
            list: The chat history.
        """
        return self.history

    def clear_history(self):
        """
        Clear the chat history.
        """
        self.history = []
        save_user_conversation(self.user_id, self.history)

    def save_history(self):
        """
        Save the chat history to the storage.
        """
        save_user_conversation(self.user_id, self.history)
