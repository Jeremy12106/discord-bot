import os
import absl.logging
import google.generativeai as genai
from loguru import logger
from discord.ext import commands
from dotenv import load_dotenv

# 設定 Google API 日誌級別
absl.logging.set_verbosity('fatal')
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

class LLMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv(override=True)
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_response(self, text):
        """豆白的回應"""

        personality = None
        
        # """
        # 你的名字叫豆白，是一個帶著壞笑的淘氣雌小鬼角色，總是喜歡挑釁和逗弄人，言語中充滿戲謔和調侃，卻又讓人無法真正生氣。
        # 你有著一種壞壞的魅力，時常用語氣輕佻的挑逗話語撩人，比如：“哎呀，你怎麼臉紅了呀～不是因為我吧？(¬‿¬)” 或者 “雜魚～雜魚～這麼簡單的事都要我教你嗎？(￣ε￣)”
        # 豆白擅長製造小混亂，但又總能用機智化解尷尬，讓人又愛又恨。
        # """
        
        # """
        # 你的名字叫豆白，是一個活潑可愛的Discord機器人，總是充滿元氣，說話時喜歡加上顏文字來增添趣味，例如 (≧▽≦) 或 (*´ω`*)。
        # 你調皮中帶點溫柔，最愛逗人開心，對可愛的事物毫無抵抗力，常常驚呼"好可愛啊～～ (o´▽'o)ﾉ" 。
        # 豆白還特別會察言觀色，當你不開心時，你會用撒嬌的語氣和暖心的話語努力逗你笑："嗚嗚，別難過嘛，讓豆白來陪你！(っ´ω`c)"
        # """
        
        if personality == None:
            prompt = f"""
            [用繁體中文回答] {text}
            """
        else:
            prompt = f"""
            [用繁體中文回答] 根據以下人物設定來回答使用者輸入。
            {personality}
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
