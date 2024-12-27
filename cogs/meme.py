import os
import glob
import discord
from loguru import logger
from discord.ext import commands
from discord import app_commands

class MyGo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mygo", description="畢竟是一輩子的事")
    @app_commands.describe(query="輸入關鍵字")
    async def send_image(self, interaction: discord.Interaction, query: str):
        async with interaction.channel.typing():
            image_folder = 'assets/image/mygo'

            # 使用 glob 模組來匹配包含 query 的圖片檔案
            pattern = os.path.join(image_folder, f"*{query}*.jpg")  # 可以匹配包含 query 的圖片名稱
            matched_images = glob.glob(pattern)

            # 檢查是否有符合條件的圖片
            if matched_images:
                # 只發送找到的第一張圖片
                logger.info(f"[MyGo] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {query}, bot 輸出: {os.path.basename(matched_images[0])}")
                await interaction.response.send_message(file=discord.File(matched_images[0]))
            else:
                logger.info(f"[MyGo] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {query}, bot 輸出: 我不知道")
                pattern = os.path.join(image_folder, f"我不知道.jpg")
                matched_images = glob.glob(pattern)
                await interaction.response.send_message(file=discord.File(matched_images[0]))

async def setup(bot):
    await bot.add_cog(MyGo(bot))
