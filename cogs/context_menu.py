import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

class ContextMenu(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='投票截止',
            callback=self.stop_poll,
        )
        self.bot.tree.add_command(self.ctx_menu)
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    async def stop_poll(self, interaction: discord.Interaction, message: discord.Message):
        poll = message.poll

        if poll is None:
            await interaction.response.send_message("未找到投票...", ephemeral=True)
        else:
            await poll.end()
            await interaction.response.send_message("投票已提前截止", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ContextMenu(bot))