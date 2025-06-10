from discord.ext import commands
from .player import YTMusic
from .radio import Radio

async def setup(bot: commands.Bot):
    await bot.add_cog(YTMusic(bot))
    await bot.add_cog(Radio(bot))