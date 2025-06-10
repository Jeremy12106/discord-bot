import yaml
from pathlib import Path
from loguru import logger

from .path_manager import CONFIG
from .models import Config

def load_config(filepath: Path, model_cls):
    logger.info(f"[初始化] 載入設定檔：{filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return model_cls(**data)

config: Config = load_config(CONFIG / "config.yml", Config)