import os
from dotenv import load_dotenv

load_dotenv(override=True)

def require_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"❌ 缺少必要環境變數: {key}")
    return value


# 必要環境變數
DISCORD_TOKEN = require_env("DISCORD_TOKEN")

# LLM API 擇一
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", None)

# 可選變數
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", None)
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", None)
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", None)
