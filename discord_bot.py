import os
import json
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands
from loguru import logger

from utils.config_loader import ConfigManager

# 載入設定檔
config = ConfigManager()

# 載入環境變數
load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")

# 設定系統日誌
log_path = "./log/discord_bot.log"
level = os.getenv("LOG_LEVEL")
logger.add(log_path, level = level, format="{time} | {level} | {message}", rotation="10 MB")

# 機器初始化設定
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=config.bot_config['prefix'], help_command=None, intents=intents)

status_dict = {
    'online': discord.Status.online,
    'idle': discord.Status.idle,
    'dnd': discord.Status.dnd,
    'invisible': discord.Status.invisible
}

@bot.event
async def on_ready():
    logger.info(f"已成功登入為 {bot.user}！")
    game = discord.Game(config.bot_config['activity'])
    await bot.tree.sync()
    await bot.change_presence(status=status_dict[config.bot_config['status']], activity=game)

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

# 載入功能
async def load_extensions():
    all_cogs = os.listdir("./cogs")
    
    # 優先載入
    priority_cogs = ['llm.py']
    for filename in priority_cogs:
        if filename in all_cogs:
            await bot.load_extension(f"cogs.{filename[:-3]}")
        else:
            logger.error(f"初始化載入失敗: 無效的檔案 {filename}")
            continue

    # 依序載入
    for filename in all_cogs:
        if filename.endswith(".py") and filename not in priority_cogs:
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
