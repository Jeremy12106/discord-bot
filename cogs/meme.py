import os
import glob
import discord
from loguru import logger
from discord.ext import commands
from discord import app_commands

class MyGo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.image_folder = 'assets/image/mygo'
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="mygo", description="畢竟是一輩子的事")
    @app_commands.describe(query="輸入關鍵字")
    async def send_image(self, interaction: discord.Interaction, query: str):
        pattern = os.path.join(self.image_folder, f"*{query}*.jpg")
        matched_images = glob.glob(pattern)

        if matched_images:
            logger.info(f"[MyGo] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {query}, bot 輸出: {os.path.basename(matched_images[0])}")
            await interaction.response.send_message(file=discord.File(matched_images[0]))
        else:
            logger.debug(f"[MyGo] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {query}, bot 輸出: 我不知道")
            unknown_image_path = os.path.join(self.image_folder, "我不知道.jpg")
            if os.path.exists(unknown_image_path):
                await interaction.response.send_message(file=discord.File(unknown_image_path))
            else:
                await interaction.response.send_message("抱歉，找不到相關圖片，也找不到預設的 '我不知道.jpg'")

    @send_image.autocomplete("query")
    async def query_autocomplete(self, interaction: discord.Interaction, current: str):
        pattern = os.path.join(self.image_folder, "*.jpg")
        all_images = glob.glob(pattern)
        image_names = [os.path.splitext(os.path.basename(img))[0] for img in all_images]
        matches = [name for name in image_names if current.lower() in name.lower()]
        return [app_commands.Choice(name=match, value=match) for match in matches[:25]] # 不能超過25

async def setup(bot):
    await bot.add_cog(MyGo(bot))
