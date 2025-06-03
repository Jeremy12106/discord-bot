import os
import json
from loguru import logger

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.bot_config = self.load_config("bot_config.json")
        self.music_config = self.load_config("music_config.json")

    def load_config(self, filename) -> dict:
        config_path = os.path.join(self.config_dir, filename)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"⚠️ 設定檔 {config_path} 找不到，請檢查路徑！")
            return {}
        except json.JSONDecodeError:
            logger.error(f"⚠️ 設定檔 {config_path} 格式錯誤，請檢查 JSON 語法！")
            return {}

# 建立全域配置管理器
config = ConfigManager()