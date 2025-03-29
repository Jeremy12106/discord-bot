from loguru import logger
from .music.player import YTMusic
from .music.radio import Radio

async def setup(bot):
    """Initialize the music cog"""
    await bot.add_cog(YTMusic(bot))
    await bot.add_cog(Radio(bot))
    