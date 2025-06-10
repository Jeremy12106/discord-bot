import os
import json
import datetime
from loguru import logger

from utils.path_manager import MEMORY_DIR

def get_memory(channel_id, num_memories=5):
    file_path = os.path.join(MEMORY_DIR, f"{channel_id}.json")
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            memories = json.load(f)
            memories = memories[-num_memories:] if memories else []
            for i, memory in enumerate(memories):
                memory_str = f"使用者：{memory['使用者']}"
                memory_str += f"\n使用者輸入：{memory['使用者輸入']}"
                memory_str += f"\n參考資料：{memory['參考資料']}" if memory['參考資料'] else "None"
                memory_str += f"\n機器人回覆：{memory['機器人回覆']}"
                memory_str += f"\n時間：{memory['時間']}\n\n"
            return memory_str

    except Exception as e:
        logger.error(f"[記憶] 讀取時發生錯誤: {e}")
        return None

def save_memory(channel_id, user_nick, user_input, search_results, response, max_memories=100):
    file_path = os.path.join(MEMORY_DIR, f"{channel_id}.json")
    memories = []
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                memories = json.load(f)
        except Exception as e:
            logger.error(f"[記憶] 讀取時發生錯誤: {e}")
    
    # 紀錄記憶
    new_memory = {
        "使用者": user_nick,
        "使用者輸入": user_input,
        "參考資料": search_results,
        "機器人回覆": response,
        "時間": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    memories.append(new_memory)
    
    # 只保留最新的 max_memories 筆資料
    if len(memories) > max_memories:
        memories = memories[-max_memories:]
    
    # 儲存記憶
    try:
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[記憶] 儲存失敗: {e}")