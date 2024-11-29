import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

from feature.gemini_api import get_response
from feature.mrt_food import MRT

mrt = MRT()
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 設定機器人前綴，例如使用 "@豆白" 作為指令的開頭
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # 確保機器人能讀取消息內容

bot = commands.Bot(command_prefix="豆白 ", intents=intents)

# 當機器人啟動時觸發
@bot.event
async def on_ready():
    print(f"已成功登入為 {bot.user}！")

    game = discord.Game('沙威玛传奇')
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command()
async def hello(ctx):
    async with ctx.typing():
        await ctx.send("哈囉! 我是你最好的朋友！")

@bot.command()
async def ping(ctx):
    async with ctx.typing():
        await ctx.send(f"Pong! 延遲為 {round(bot.latency * 1000)}ms")

@bot.command(name = "捷運")
async def mrt_select(ctx, line: str):
    """根據捷運線名稱隨機選擇一個站點並發送"""
    async with ctx.typing():
        message = mrt.get_random_station(line)
        await ctx.send(message)

@bot.command(name = "拉麵")
async def mrt_select(ctx, line: str):
    """根據捷運線名稱隨機選擇一個站點並發送"""
    async with ctx.typing():
        message = mrt.recommend_ramen(line)
        await ctx.send(message)

# LLM輸入：如果用戶輸入的不是已定義的指令
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        user_input = ctx.message.content[len(ctx.prefix):].strip()
        # 使用 async with ctx.typing() 顯示正在輸入的狀態
        async with ctx.typing():
            response = get_response(user_input)  # 使用 LLM 處理輸入
            if response:
                await ctx.send(response)
            else:
                await ctx.send("抱歉..我無法處理這個訊息。")
    else:
        raise error

# 啟動機器人
if TOKEN:
    bot.run(TOKEN)
else:
    print("未找到 Discord Token，請檢查 .env 檔案！")
