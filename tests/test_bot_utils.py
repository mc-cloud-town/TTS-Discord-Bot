import pytest
from bot.utils import extract_user_nickname


class TestExtractUserNickname:
    def test_extract_user_nickname_simple(self):
        assert extract_user_nickname.extract_user_nickname("John") == "John"

    def test_extract_user_nickname_with_space(self):
        assert extract_user_nickname.extract_user_nickname("John Doe") == "John"

    def test_extract_user_nickname_with_parentheses(self):
        assert extract_user_nickname.extract_user_nickname("John (admin)") == "John"

    def test_extract_user_nickname_with_chinese_parentheses(self):
        assert extract_user_nickname.extract_user_nickname("John（admin）") == "John"

    def test_extract_user_nickname_with_space_and_parentheses(self):
        assert extract_user_nickname.extract_user_nickname("John Doe (admin)") == "John"

    def test_extract_user_nickname_only_parentheses(self):
        assert extract_user_nickname.extract_user_nickname("(admin)") == ""

    def test_extract_user_nickname_empty(self):
        assert extract_user_nickname.extract_user_nickname("") == ""

    def test_extract_user_nickname_multiple_spaces(self):
        assert extract_user_nickname.extract_user_nickname("John  Doe") == "John"
