import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

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

💰 | **/debt**
🔸 伺服器記債系統，詳見 `/help-debt`

🎵 | **/play [YouTube-URL或關鍵字查詢]**
🔸 播放指定的 YouTube 音樂，支援YouTube連結與關鍵字查詢
        """

        self.help_debt_message = """\
💰 | **/debt add**
🔸 紀錄一筆債務（由債主使用）
參數說明:
- `debtor` - 債務人
- `amount` - 債務金額
- `description` - 債務描述

💰 | **/debt repay**
🔸 還債 (由債務人使用)
參數說明:
- `debt_description` - 債務項目

💰 | **/debt remove_by_creditor**
🔸 刪除債務 （由債主使用）
參數說明:
- `debt_description` - 債務項目

💰 | **/debt list**
🔸 列出債務項目
參數說明:
- `member` - 成員 (可選，預設為所有成員)

💰 | **/debt top**
🔸 負債排行榜
        """

        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="help", description="查看功能指令")
    async def slash_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="豆白指令清單", description=self.help_message, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help-debt", description="查看記債系統說明")
    async def slash_help_debt(self, interaction: discord.Interaction):
        embed = discord.Embed(title="記債系統說明", description=self.help_debt_message, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))

    