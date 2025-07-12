import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """\
🌟 | **前綴**: @豆白 [文字內容]
🔸 想跟豆白聊天？ 直接 tag 他就對啦

💬 | ""@豆白 名言 [黑白or彩色]""
🔸 回覆一段訊息並 "@豆白 名言"，來製作酷酷的名言圖

📌 | **書籤功能**
🔸 想收藏的內容？ 對它加上 "📌" 反應即可

🍜 | **/ramen [捷運站名]**
🔸 讓豆白來推薦好吃的拉麵給你

☀️ | **/weather [縣市]**
🔸 豆白的天氣預報系統～

🐢 | **/soup [出題方向]**
🔸 想玩一局海龜湯嗎？ 讓豆白幫你出題吧！

🎂 | **/choose [選項1 選項2 ...]**
🔸 選擇困難症？交給豆白幫你選！

🎲 | **/dice**
🔸 讓豆白幫你丟一顆六面骰！

🐧 | **/mygo [台詞]**
🔸 畢竟是一輩子的事，豆白的台詞包搜尋器！

💰 | **/debt**
🔸 記帳找豆白，幫你管好誰欠誰錢！更多功能看 `/help-debt`

🎵 | **/play [YouTube-URL或關鍵字查詢] [即時串流模式]**
🔸 想放歌媽？ 放上連結或歌名，豆白來幫你！

🎧 | **/lofi**
🔸 豆白的音樂電台，讓豆白播點輕音樂，放鬆心情！
        """

        self.help_debt_message = """\
💰 | **/debt add**
🔸 紀錄一筆債務（由債主使用）
參數說明:
- `debtor` - 欠錢的人
- `amount` - 欠多少錢
- `description` - 債務內容描述

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
- `member` - 查看指定成員的債務，可不填（預設會列出所有人的）

💰 | **/debt top**
🔸 本群最會欠錢的是誰？來看債務排行榜！
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

    