import random
import discord
from loguru import logger
from discord.ext import commands
from cogs.gemini_api import LLMCommands

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
            logger.info(f"[choose] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {choices}, bot 輸出: {chosen}")
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

class SeaTurtleGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.llm = LLMCommands(bot)
    
    @commands.command(name="海龜湯")
    async def seaturtle_game(self, ctx, *directions):
        """
        生成海龜湯題目，根據使用者指定的多個方向。
        使用方式: 豆白 海龜湯 [出題方向1] [出題方向2] ...
        """
        async with ctx.typing():
            if not directions:
                await ctx.send("請至少提供一個出題方向，如：懸疑 恐怖 獵奇")
                return

            # 將多個方向合併成一個字串
            direction_str = "、".join(directions)

            try:
                # 使用 LLMCommands 取得題目與解答
                result = self.llm.get_seaturtle_question(direction_str)
                logger.info(f"[海龜湯] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {ctx.message.content}, bot 輸出: \n{result}")

                if "題目:" in result and "解答:" in result:
                    parts = result.split("解答:")
                    question = parts[0].replace("題目:", "").strip()
                    answer = parts[1].strip()

                    # 輸出題目與暴雷解答
                    embed = discord.Embed(title="海龜湯題目", description=question, color=discord.Color.blue())
                    await ctx.send(embed=embed)

                    spoiler_text = f"||{answer}||"  # 暴雷內容
                    await ctx.send(f"解答（點擊顯示）：\n{spoiler_text}")
                else:
                    await ctx.send("生成題目時發生錯誤，請稍後再試。")

            except Exception as e:
                logger.error(f"[海龜湯] 發生錯誤：{e}")
                await ctx.send(f"發生錯誤")

async def setup(bot):
    await bot.add_cog(Feature(bot))
    await bot.add_cog(UltimateNumberGame(bot))
    await bot.add_cog(SeaTurtleGame(bot))
    logger.info("追加功能載入成功！")