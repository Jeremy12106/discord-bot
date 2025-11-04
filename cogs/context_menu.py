import io
import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from .quote import MakeItAQuote

class ContextMenu(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.stop_poll_menu = app_commands.ContextMenu(
            name='投票截止',
            callback=self.stop_poll,
        )
        self.quote_menu_monochrome = app_commands.ContextMenu(
            name='名言製作 (黑白)',
            callback=self.create_quote_monochrome,
        )
        self.quote_menu_color = app_commands.ContextMenu(
            name='名言製作 (彩色)',
            callback=self.create_quote_color,
        )
        self.bot.tree.add_command(self.stop_poll_menu)
        self.bot.tree.add_command(self.quote_menu_monochrome)
        self.bot.tree.add_command(self.quote_menu_color)
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    async def stop_poll(self, interaction: discord.Interaction, message: discord.Message):
        poll = message.poll

        if poll is None:
            await interaction.response.send_message("未找到投票...", ephemeral=True)
        else:
            await poll.end()
            await interaction.response.send_message("投票已提前截止", ephemeral=True)

    async def create_quote_monochrome(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=False)  # 需要較長時間處理，先 defer
        # 取得已載入的 MakeItAQuote Cog
        quote_cog: MakeItAQuote = self.bot.get_cog("MakeItAQuote")
        author = message.author
        author_name = author.display_name
        content = message.content

        try:
            avatar_url = author.display_avatar.url
            avatar = quote_cog.download_avatar(avatar_url, mode="黑白")
            img = quote_cog.create_quote_image(content, author_name, avatar)
        except Exception as e:
            logger.exception("建立名言圖片失敗")
            await interaction.followup.send("建立名言圖片時發生錯誤。", ephemeral=True)
            return

        # 傳送圖片
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.followup.send(file=discord.File(fp=image_binary, filename="quote.png"))
    
    async def create_quote_color(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=False)  # 需要較長時間處理，先 defer
        # 取得已載入的 MakeItAQuote Cog
        quote_cog: MakeItAQuote = self.bot.get_cog("MakeItAQuote")
        author = message.author
        author_name = author.display_name
        content = message.content

        try:
            avatar_url = author.display_avatar.url
            avatar = quote_cog.download_avatar(avatar_url, mode="彩色")
            img = quote_cog.create_quote_image(content, author_name, avatar)
        except Exception as e:
            logger.exception("建立名言圖片失敗")
            await interaction.followup.send("建立名言圖片時發生錯誤。", ephemeral=True)
            return

        # 傳送圖片
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.followup.send(file=discord.File(fp=image_binary, filename="quote.png"))
        

async def setup(bot: commands.Bot):
    await bot.add_cog(ContextMenu(bot))