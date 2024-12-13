import os
import json
import absl.logging
import google.generativeai as genai
from loguru import logger
from discord.ext import commands
from dotenv import load_dotenv

# 設定 Google API 日誌級別
absl.logging.set_verbosity('fatal')
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class LLMCommands(commands.Cog):
    def __init__(self, bot, setting_path=f'{PROJECT_ROOT}/assets/data/gemini_api_setting'):
        self.bot = bot
        load_dotenv(override=True)
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.personality = None

        personality_path = os.path.join(setting_path, "personality.json")
        with open(personality_path, "r", encoding="utf-8") as file:
            self.personality = json.load(file).get("personality", None)

    def get_response(self, text):
        """豆白的回應"""          
        if self.personality == "None":
            prompt = f"""
            [用繁體中文回答] {text}
            """
        else:
            prompt = f"""
            [用繁體中文回答] 根據以下人物設定來回答使用者輸入。
            {self.personality}
            使用者輸入：{text}
            """

        response = self.model.generate_content(prompt)
        return response.text
    
    def get_weather_recommendation(self, weather_info):
        """生成出門建議"""
        prompt = f"[用繁體中文回答] 根據以下天氣預報資訊，給予一個簡短的出門建議：\n{weather_info}"
        response = self.model.generate_content(prompt)
        return response.text

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
        response = self.model.generate_content(prompt)
        return response.text

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
    logger.info("LLM 功能載入成功！")
