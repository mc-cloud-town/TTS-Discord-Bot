import requests


def make_post_request(url: str, data: dict) -> dict:
    """
    使用POST方法發送請求
    Args:
        url: 請求的URL
        data: 請求的數據

    Returns:
        dict: 請求的結果
    """
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()


def make_get_request(url: str) -> dict:
    """
    使用GET方法發送請求
    Args:
        url: 請求的URL

    Returns:
        dict: 請求的結果
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
