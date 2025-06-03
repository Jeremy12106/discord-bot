import yaml
from pathlib import Path
from loguru import logger

from .path_manager import CONFIG
from .models import BotConfig, MusicConfig

class ConfigManager:
    def __init__(self):
        self.bot: BotConfig = self.load_config(CONFIG / "bot_config.yml", BotConfig)
        self.music: MusicConfig = self.load_config(CONFIG / "music_config.yml", MusicConfig)

    def load_config(self, filepath: Path, model_cls):
        logger.info(f"[初始化] 載入設定檔：{filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return model_cls(**data)

# 建立全域配置管理器
config = ConfigManager()