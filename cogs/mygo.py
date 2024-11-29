import os
import glob
import discord
from discord.ext import commands

class MyGo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "mygo")
    async def send_image(self, ctx, query: str):
        # 定義圖片的資料夾路徑
        image_folder = 'assets/pic/mygo'

        # 使用 glob 模組來匹配包含 query 的圖片檔案
        pattern = os.path.join(image_folder, f"*{query}*.jpg")  # 可以匹配包含 query 的圖片名稱
        matched_images = glob.glob(pattern)

        # 檢查是否有符合條件的圖片
        if matched_images:
            # 只發送找到的第一張圖片
            await ctx.send(file=discord.File(matched_images[0]))
        else:
            await ctx.send("窩不知道")

# 註冊 cog
async def setup(bot):
    await bot.add_cog(MyGo(bot))
    print("MYGO 載入了一輩子！")