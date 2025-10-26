import discord
import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from loguru import logger

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="vote", description="建立投票")
    @app_commands.describe(question="投票主題", options="投票選項，請以 ｢陣列｣ 形式提供", multiple="允許複選，預設為否", duration="投票時長（小時），預設為24")
    async def slash_vote(self, interaction: discord.Interaction, question: str, 
                         options: str, multiple: Optional[bool]=False, duration: Optional[float] = 24.0):
        poll = discord.Poll(
            question=question,
            duration=datetime.timedelta(hours=duration),
            multiple=multiple,
        )
        options_list = [x.strip().strip('"').strip("'") for x in options.strip("[]").split(",") if x.strip()]
        for option in options_list:
            poll.add_answer(text=option)

        await interaction.response.send_message(poll=poll)

async def setup(bot: commands.Bot):
    await bot.add_cog(Vote(bot))