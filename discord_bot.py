import os
import discord
import asyncio
from loguru import logger
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


log_path = "./log/discord_bot.log"
level = os.getenv("LOG_LEVEL")
logger.add(log_path, level = level, format="{time} | {level} | {message}", rotation="10 MB")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # 確保機器人能讀取消息內容

# 機器人前綴
bot = commands.Bot(command_prefix="豆白 ", help_command=None, intents=intents)

# 當機器人啟動時觸發
@bot.event
async def on_ready():
    logger.info(f"已成功登入為 {bot.user}！")
    game = discord.Game('沙威玛传奇')
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command()
async def hello(ctx):
    async with ctx.typing():
        await ctx.send("哈囉！我是你最好的朋友！")

@bot.command()
async def ping(ctx):
    async with ctx.typing():
        response = f"Pong! 延遲為 {round(bot.latency * 1000)}ms"
        logger.info(f"[Ping] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {ctx.message.content}, bot 輸出: {response}")
        await ctx.send(response)

@bot.command(name = "help", description = "查看功能指令")
async def help(ctx):
    async with ctx.typing():
        """
        提供可用指令的清單和簡要說明。
        """
        help_message = """\
🌟 | **前綴**: 豆白

🚇 | **捷運 [線名]**
🔸 隨機一站帶你去

🍜 | **拉麵 [捷運站名]**
🔸 推薦好吃拉麵

☀️ | **天氣 [縣市]**
🔸 查看指定地點的天氣預報

🎲 | **choose [選項1 選項2 ...]**
🔸 幫你做選擇

🎲 | **dice**
🔸 擲一顆六面骰子

🔢 | **終極密碼**
🔸 開啟一場刺激的終極密碼遊戲

🐢 | **海龜湯 [出題方向1 出題方向2 ...]**
🔸 來一場好玩的海龜湯吧

🎵 | **play [YouTube-URL]**
🔸 播放指定的 YouTube 音樂

🐧 | **mygo [台詞]**
🔸 畢竟是一輩子的事
        """
        embed = discord.Embed(title="豆白指令清單", description=help_message, color=discord.Color.blue())
        await ctx.send(embed=embed)

@bot.command(name = "燒魚")
async def sauyu(ctx):
    async with ctx.typing():
        await ctx.send("燒魚燒魚燒魚")

# 載入功能
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("關閉機器人...")
