from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CONFIG = Path(__file__).resolve().parent.parent / "config"

# 資料 (JSON)
DATA = ASSETS / "data"
MEMORY_DIR = DATA / "memory"
MRT_DIR = DATA / "mrt_food"
PERSONALITY_DIR = DATA / "personality"

# 字體
FONT = ASSETS / "font"
FONT_FILE = FONT / "TW-Kai-98_1.ttf"

# 圖片
IMAGE = ASSETS / "image"
MYGO_DIR = IMAGE / "mygo"
README_DIR = IMAGE / "readme"

# 音樂下載暫存
MUSIC_TEMP = ASSETS / "music_temp"