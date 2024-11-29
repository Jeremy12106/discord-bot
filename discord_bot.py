import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

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

@bot.command(name = "哈囉")
async def hello(ctx):
    async with ctx.typing():
        await ctx.send("哈囉！我是你最好的朋友！")

@bot.command()
async def ping(ctx):
    async with ctx.typing():
        await ctx.send(f"Pong! 延遲為 {round(bot.latency * 1000)}ms")

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
