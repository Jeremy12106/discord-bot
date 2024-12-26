import os
import json
import discord
import asyncio
from loguru import logger
from dotenv import load_dotenv
from discord.ext import commands

PROJECT_ROOT = os.getcwd()
SETTING_PATH=f"{PROJECT_ROOT}/config"
music_config_path = os.path.join(SETTING_PATH, "bot_config.json")
with open(music_config_path, "r", encoding="utf-8") as file:
    bot_config = json.load(file)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

log_path = "./log/discord_bot.log"
level = os.getenv("LOG_LEVEL")
logger.add(log_path, level = level, format="{time} | {level} | {message}", rotation="10 MB")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # 確保機器人能讀取消息內容

# 機器人前綴
bot = commands.Bot(command_prefix=bot_config['prefix'], help_command=None, intents=intents)

status_dict = {
    'online': discord.Status.online,
    'idle': discord.Status.idle,
    'dnd': discord.Status.dnd,
    'invisible': discord.Status.invisible
}

# 當機器人啟動時觸發
@bot.event
async def on_ready():
    logger.info(f"已成功登入為 {bot.user}！")
    game = discord.Game(bot_config['activity'])
    await bot.tree.sync()
    await bot.change_presence(status=status_dict[bot_config['status']], activity=game)

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

@bot.command(name="燒魚")
async def sauyu(ctx):
    async with ctx.typing():
        await ctx.send("燒魚燒魚燒魚")

# 載入功能
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            logger.info(f"功能 {filename[:-3]} 載入成功！")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("關閉機器人...")
