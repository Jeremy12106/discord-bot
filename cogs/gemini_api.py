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

# 定義 Cog 類別
class LLMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv(override=True)
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_response(self, text):
        """處理 LLM 輸入並回傳生成的回應"""
        prompt = f"[用繁體中文回答] {text}"
        response = self.model.generate_content(prompt)
        return response.text

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """當命令錯誤時，觸發該事件處理"""
        if isinstance(error, commands.CommandNotFound):
            user_input = ctx.message.content[len(ctx.prefix):].strip()
            async with ctx.typing():
                response = self.get_response(user_input)  # 使用 LLM 處理輸入
                logger.info(f"[LLM] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {ctx.message.content}, bot 輸出: {response[:100]}")
                if response:
                    await ctx.send(response)
                else:
                    await ctx.send("抱歉..我無法處理這個訊息。")
        else:
            raise error

# 註冊並加載 Cog
async def setup(bot):
    await bot.add_cog(LLMCommands(bot))
    logger.info("LLM 功能載入成功！")
