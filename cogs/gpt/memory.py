import datetime

from utils.path_manager import MEMORY_DIR
from utils.file_manager import FileManager

def get_memory(channel_id, num_memories=5):
    filename = f"{channel_id}.json"
    memories = FileManager.load_json_data(MEMORY_DIR, filename)

    if not memories:
        return None

    memories = memories[-num_memories:]  # 保留最新 num_memories 筆
    memory_str = ""
    for memory in memories:
        memory_str += f"使用者：{memory['使用者']}\n"
        memory_str += f"使用者輸入：{memory['使用者輸入']}\n"
        memory_str += f"參考資料：{memory['參考資料'] or 'None'}\n"
        memory_str += f"機器人回覆：{memory['機器人回覆']}\n"
        memory_str += f"時間：{memory['時間']}\n\n"

    return memory_str


def save_memory(channel_id, user_nick, user_input, search_results, response, max_memories=100):
    filename = f"{channel_id}.json"
    memories = FileManager.load_json_data(MEMORY_DIR, filename) or []

    # 新記憶
    new_memory = {
        "使用者": user_nick,
        "使用者輸入": user_input,
        "參考資料": search_results,
        "機器人回覆": response,
        "時間": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    memories.append(new_memory)

    # 限制記憶數量
    if len(memories) > max_memories:
        memories = memories[-max_memories:]

    # 儲存
    FileManager.save_json_data(MEMORY_DIR, filename, memories)
