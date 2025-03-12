import os
import re
import json
from loguru import logger
from discord.ext import commands
from dotenv import load_dotenv

from .gpt.gemini_api import GeminiAPI
from .gpt.github import GithubAPI
from .gpt.search import google_search
from .gpt.prompt import get_prompt
from .gpt.memory import get_memory, save_memory


load_dotenv(override=True)
PROJECT_ROOT = os.getcwd()
SETTING_PATH = os.path.join(PROJECT_ROOT, 'config')
PERSONALITY_FOLDER = os.path.join(PROJECT_ROOT, "assets/data/personality")
os.makedirs(PERSONALITY_FOLDER, exist_ok=True)

class LLMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.personality = None

        bot_config_path = os.path.join(SETTING_PATH, "bot_config.json")
        with open(bot_config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
            self.system_prompt = config.get("system_prompt", None)
            self.personality = config.get("personality", None)
            self.gpt_api = config.get("gpt_api", None)
            self.model = config.get("model", None)
            self.use_search_engine = config.get("use_search_engine", False)
            self.chat_memory = config.get("chat_memory", False)

        if self.gpt_api == "github":
            self.gpt = GithubAPI(self.model)
        elif self.gpt_api == "gemini":
            self.gpt = GeminiAPI(self.model)

    def get_response(self, chanel_id, user_nick, text, search_results=None, memory=None):
        """豆白的回應"""
        # 檢查是否有頻道專屬的個性
        file_path = os.path.join(PERSONALITY_FOLDER, f"{chanel_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8-sig") as file:
                data = json.load(file)
                personality = data.get("personality", None)
            prompt = get_prompt(self.system_prompt, user_nick, text, personality, search_results, memory)
        else:
            prompt = get_prompt(self.system_prompt, user_nick, text, self.personality, search_results, memory)

        # 如果有搜尋結果，則使用較低的溫度生成回應
        if search_results is not None:
            response = self.gpt.get_response(prompt, temperature=0.5)
        else:
            response = self.gpt.get_response(prompt, temperature=1)
                               
        return response

    def get_search_results(self, text, channel_id=None):
        prompt = self.system_prompt + """\n
                    請根據以下使用者輸入及對話歷史，判斷是否需要擷取網路即時資訊，並提供適合搜尋的關鍵字（若無需搜尋則回答"無"）。 
                    你的任務是：
                    1. 判斷使用者問題是否涉及即時性、最新資訊或超出通用知識範疇的主題。
                    2. 若需要搜尋，提供有效的搜尋關鍵字，並根據對話上下文調整搜尋內容。
                    3. 若不需要搜尋，回答 {"search": false, "query":"無"}。
                    """
        if self.chat_memory:
            prompt += f"""\n
                    ### 對話歷史：
                    {get_memory(channel_id)}
                    """
        prompt +=   """\n
                    ### 使用者輸入：
                    """ + text + """

                    ### 輸出格式要求：
                    - 使用 JSON 格式。
                    - 範例輸出：
                    {"search": true, "query":"2025年台灣總統選舉候選人"}
                    {"search": true, "query":"昨天 NBA 勇士隊比賽結果"}
                    {"search": false, "query":"無"}
                    """
        try:
            # 處理回傳的訊息
            response = self.gpt.get_response(prompt, temperature=0.5)
            response = re.search(r"\{.*\}", response)
            response = response.group(0).strip()
            response = response.replace("True", "true").replace("False", "false")
            result = json.loads(response)

            if "search" in result and "query" in result:
                if result["search"]:
                    query = result["query"]
                    search_results = google_search(query)
                    return search_results
                else:
                    return None
            else:
                logger.error(f"[LLM] 模型回應的格式無效")
        except Exception as e:
            logger.error(f"[LLM] 發生錯誤: {e}")
    
    def get_weather_recommendation(self, weather_info):
        """生成出門建議"""
        prompt = f"[用繁體中文回答] 根據以下天氣預報資訊，給予一個簡短的出門建議：\n{weather_info}"
        response = self.gpt.get_response(prompt, temperature=0)
        return response

    def get_seaturtle_question(self, directions):
        """使用 LLM 生成海龜湯題目與解答"""
        prompt = f"""
        [用繁體中文回答] 根據方向：{directions}，生成一個「海龜湯」風格的推理解謎題目與解答。

        題目應該是一段引人入勝、帶有懸念的敘述，能讓玩家透過提問和推理拼湊出完整故事。  
        解答需詳細描述故事的完整背景、原因和情節，且內容可以包含任何相關元素，不限於「海龜」或其他具體主題。請確保解答令人感到意外但合理。

        輸出格式：
        題目: <簡短敘述，營造懸念>
        解答: <完整故事，包含細節與合理解釋>
        """
        response = self.gpt.get_response(prompt, temperature=1)
        return response

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """當命令未定義時，觸發LLM事件"""
        if isinstance(error, commands.CommandNotFound):
            user_input = ctx.message.content[len(ctx.prefix):].strip()
            async with ctx.typing():
                chanel_id = ctx.channel.id
                user_nick = ctx.author.display_name
                
                if self.use_search_engine:
                    search_results = self.get_search_results(user_input, chanel_id)
                else:
                    search_results = None
                
                if self.chat_memory:
                    memory = get_memory(chanel_id)
                    response = self.get_response(chanel_id, user_nick, user_input, search_results, memory)
                    save_memory(chanel_id, user_nick, user_input, search_results, response)
                else:
                    response = self.get_response(chanel_id, user_nick, user_input, search_results)
                
                logger.info(f"[LLM] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {ctx.message.content}, bot 輸出: \n{response[:100]}")
                if response:
                    await ctx.send(response)
                else:
                    await ctx.send("抱歉..我無法處理這個訊息。")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(LLMCommands(bot))