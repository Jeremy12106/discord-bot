import random
from discord.ext import commands

class Feature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """
        使用者選擇任意數量的選項，隨機回傳一個選項。
        """
        if not choices:
            await ctx.send("你要選什麼?")
            return

        # 隨機選擇一個選項
        chosen = random.choice(choices)
        await ctx.send(f"{chosen}")

async def setup(bot):
    await bot.add_cog(Feature(bot))
    print("追加功能載入成功！")