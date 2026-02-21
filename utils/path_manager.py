from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS = BASE_DIR / "assets"
CONFIG = BASE_DIR / "config"

# 資料 (JSON)
DATA = ASSETS / "data"
MEMORY_DIR = DATA / "memory"
MRT_DIR = DATA / "mrt_food"
PERSONALITY_DIR = DATA / "personality"
DEBT_DIR = DATA / "debt_log"

# 字體
FONT = ASSETS / "font"

# 圖片
IMAGE = ASSETS / "image"
MYGO_DIR = IMAGE / "mygo"
README_DIR = IMAGE / "readme"
OMIKUJI_DIR = IMAGE / "Omikuji"

# 音樂下載暫存
MUSIC_TEMP = ASSETS / "music_temp"


# 統一創建資料夾
directories = [
    ASSETS, CONFIG,
    DATA, MEMORY_DIR, MRT_DIR, PERSONALITY_DIR,
    DEBT_DIR, FONT, IMAGE, MYGO_DIR, README_DIR, OMIKUJI_DIR,
    MUSIC_TEMP
]

for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)