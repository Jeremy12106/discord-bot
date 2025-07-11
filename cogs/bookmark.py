import discord
from discord.ext import commands
from loguru import logger

BOOKMARK_EMOJI = "📌"  # 書籤表情符號

class Bookmark(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if str(payload.emoji) != BOOKMARK_EMOJI:
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = self.bot.get_channel(payload.channel_id)

        if channel is None:
            logger.info("[書籤] Channel not found.")
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            logger.error(f"[書籤] 無法取得訊息：{e}")
            return

        if payload.user_id == self.bot.user.id:
            return  # 忽略機器人自己的反應

        try:
            user = await self.bot.fetch_user(payload.user_id)
            bookmark_message = (
                f"這是你在「 {channel.name} 」收藏的內容 by {message.author}\n\n"
                f"{message.content}\n\n"
                f"查看原始訊息：{message.jump_url}\n------\n"
            )
            await user.send(content=bookmark_message)
        except Exception as error:
            logger.error(f"[書籤] 無法發送私人訊息：{error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Bookmark(bot))