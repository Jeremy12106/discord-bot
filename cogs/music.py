from loguru import logger
from .music.player import YTMusic

async def setup(bot):
    """Initialize the music cog"""
    await bot.add_cog(YTMusic(bot))
    