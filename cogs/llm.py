import os
import json
from loguru import logger
from discord.ext import commands
from dotenv import load_dotenv

from .gpt.gemini_api import GeminiAPI
from .gpt.openai_api import OpenaiAPI


load_dotenv(override=True)
PROJECT_ROOT = os.getcwd()
SETTING_PATH = os.path.join(PROJECT_ROOT, 'config')

class LLMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.personality = None

        bot_config_path = os.path.join(SETTING_PATH, "bot_config.json")
        with open(bot_config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
            self.personality = config.get("personality", None)
            self.gpt_api = config.get("gpt_api", None)
            self.model = config.get("model", None)


        if self.gpt_api == "openai":
            self.gpt = OpenaiAPI(self.model)
        elif self.gpt_api == "gemini":
            self.gpt = GeminiAPI(self.model)


    def get_response(self, text):
        """豆白的回應"""          
        if self.personality == None:
            prompt = f"""
            [用繁體中文回答] {text}
            """
        else:
            prompt = f"""
            [用繁體中文回答] 根據以下人物設定來回答使用者輸入。
            {self.personality}
            使用者輸入：{text}
            """

        response = self.gpt.get_response(prompt)
                                               
        return response
    
    def get_weather_recommendation(self, weather_info):
        """生成出門建議"""
        prompt = f"[用繁體中文回答] 根據以下天氣預報資訊，給予一個簡短的出門建議：\n{weather_info}"
        response = self.gpt.get_response(prompt)
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
        response = self.gpt.get_response(prompt)
        return response

    def get_keyword(self, text):
        prompt = f"""
        [以繁體中文提取關鍵字並用List形式輸出] {text}
        """
        response = self.gpt.get_response(prompt)
        return response

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """當命令錯誤時，觸發該事件處理"""
        if isinstance(error, commands.CommandNotFound):
            user_input = ctx.message.content[len(ctx.prefix):].strip()
            async with ctx.typing():
                response = self.get_response(user_input)  # 使用 LLM 處理輸入
                logger.info(f"[LLM] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {ctx.message.content}, bot 輸出: \n{response[:100]}")
                if response:
                    await ctx.send(response)
                else:
                    await ctx.send("抱歉..我無法處理這個訊息。")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(LLMCommands(bot))