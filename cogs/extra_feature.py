import random
from loguru import logger
from discord.ext import commands

class Feature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """
        使用者選擇任意數量的選項，隨機回傳一個選項。
        """
        async with ctx.typing():
            if not choices:
                await ctx.send("你要選什麼?")
                return

            # 隨機選擇一個選項
            chosen = random.choice(choices)
            await ctx.send(f"{chosen}")

class UltimateNumberGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target = None
        self.lower_bound = None
        self.upper_bound = None
        self.game_active = False

    @commands.command(name="終極密碼")
    async def start_game(self, ctx):
        async with ctx.typing():
            if self.game_active:
                await ctx.send("遊戲已經在進行中！請先完成當前的遊戲。")
                return
            
            self.target = random.randint(1, 100)
            self.lower_bound = 1
            self.upper_bound = 100
            self.game_active = True
            await ctx.send("🎲 終極密碼遊戲開始！\n範圍：1 ~ 100\n請輸入 `豆白 guess <數字>` 來猜數字")

    @commands.command(name="guess")
    async def guess(self, ctx, number: int):
        async with ctx.typing():
            if not self.game_active:
                await ctx.send("目前沒有進行中的遊戲，請輸入 `豆白 終極密碼` 來開始一場遊戲！")
                return
            
            if number < self.lower_bound or number > self.upper_bound:
                await ctx.send(f"⚠️ 無效的猜測！請輸入 {self.lower_bound} ~ {self.upper_bound} 之間的數字。")
                return

            if number == self.target:
                await ctx.send(f"🎉 恭喜 {ctx.author.mention} 猜中了！答案是 {self.target}！\n遊戲結束！")
                self.game_active = False
            elif number < self.target:
                self.lower_bound = number + 1
                await ctx.send(f"🔽 太小了！新的範圍是 {self.lower_bound} ~ {self.upper_bound}。")
            else:
                self.upper_bound = number - 1
                await ctx.send(f"🔼 太大了！新的範圍是 {self.lower_bound} ~ {self.upper_bound}。")

    @commands.command(name="endgame")
    async def end_game(self, ctx):
        async with ctx.typing():
            if not self.game_active:
                await ctx.send("目前沒有進行中的遊戲！")
                return
            
            await ctx.send(f"⚠️ 遊戲已結束！正確答案是 {self.target}。\n下次再來玩吧！")
            self.game_active = False

async def setup(bot):
    await bot.add_cog(Feature(bot))
    await bot.add_cog(UltimateNumberGame(bot))
    logger.info("追加功能載入成功！")