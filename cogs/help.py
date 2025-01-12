
import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """\
🌟 | **前綴**: @豆白
🔸 與豆白對話！

🍜 | **/ramen [捷運站名]**
🔸 推薦好吃拉麵

☀️ | **/weather [縣市]**
🔸 查看指定地點的天氣預報

🐢 | **/soup [出題方向1 出題方向2 ...]**
🔸 海龜湯題目生成器

🎲 | **/choose [選項1 選項2 ...]**
🔸 幫你做選擇

🎲 | **/dice**
🔸 擲一顆六面骰子

🐧 | **/mygo [台詞]**
🔸 畢竟是一輩子的事

🎵 | **/play [YouTube-URL或關鍵字查詢]**
🔸 播放指定的 YouTube 音樂，支援YouTube連結與關鍵字查詢
        """

    @app_commands.command(name="help", description="查看功能指令")
    async def slash_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="豆白指令清單", description=self.help_message, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))

    