import re


def extract_user_nickname(display_name: str) -> str:
    """
    Extract user nickname from display name
    Args:
        display_name (str): Display name of the user

    Returns:
        str: User nickname
    """
    # Remove any text within parentheses () or （）
    cleaned_name = re.sub(r'\s*[(（].*?[)）]\s*', '', display_name)

    # Get the first part of the name (split by space)
    return cleaned_name.split(' ')[0]