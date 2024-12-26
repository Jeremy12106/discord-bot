import os
import glob
import discord
from loguru import logger
from discord.ext import commands

class MyGo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "mygo")
    async def send_image(self, ctx, query: str):
        async with ctx.typing():
            image_folder = 'assets/image/mygo'

            # 使用 glob 模組來匹配包含 query 的圖片檔案
            pattern = os.path.join(image_folder, f"*{query}*.jpg")  # 可以匹配包含 query 的圖片名稱
            matched_images = glob.glob(pattern)

            # 檢查是否有符合條件的圖片
            if matched_images:
                # 只發送找到的第一張圖片
                logger.info(f"[MyGo] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {query}, bot 輸出: {os.path.basename(matched_images[0])}")
                await ctx.send(file=discord.File(matched_images[0]))
            else:
                logger.info(f"[MyGo] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {query}, bot 輸出: 我不知道")
                pattern = os.path.join(image_folder, f"我不知道.jpg")
                matched_images = glob.glob(pattern)
                await ctx.send(file=discord.File(matched_images[0]))

# 註冊 cog
async def setup(bot):
    await bot.add_cog(MyGo(bot))
    