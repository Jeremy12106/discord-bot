from googleapiclient.discovery import build
from utils.env_loader import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID
from typing import Any

def build_google_search_service() -> Any:
    """初始化 Google Search API 的 service"""
    return build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)

def execute_google_search(service: Any, query: str, num_results: int = 5):
    """執行搜尋請求"""
    return service.cse().list(q=query, cx=GOOGLE_SEARCH_ENGINE_ID, num=num_results).execute()