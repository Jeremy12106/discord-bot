import json
from loguru import logger
from pathlib import Path

from .path_manager import DATA

class FileManager:
    @staticmethod
    def load_json_data(folder: str, filename: str):
        filename = filename if filename.endswith(".json") else filename + ".json"
        full_path = DATA / folder / filename
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[FileManager] Failed to read {full_path}: {e}")
            return {}

    @staticmethod
    def save_json_data(folder: str, filename: str, data: dict):
        filename = filename if filename.endswith(".json") else filename + ".json"
        full_path = DATA / folder / filename
        full_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[FileManager] Failed to write {full_path}: {e}")