from discord.ext import commands

from .music.player import YTMusic
from .music.radio import Radio

async def setup(bot: commands.Bot):
    """Initialize the music cog"""
    await bot.add_cog(YTMusic(bot))
    await bot.add_cog(Radio(bot))
    