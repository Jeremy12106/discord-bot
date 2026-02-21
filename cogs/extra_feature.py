import random
import discord
from loguru import logger
from discord import app_commands
from discord.ext import commands

from discord_bot import config
from utils.file_manager import FileManager
from utils.path_manager import PERSONALITY_DIR, OMIKUJI_DIR
from .llm import LLMService

class Feature(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.personality = config.llm.personality
        self.llm: LLMService = bot.get_cog('LLMService')
        
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="choose", description="隨機幫你做選擇")
    @app_commands.describe(choices="提供選擇的選項 (以空格間隔)")
    async def choose(self, interaction: discord.Interaction, choices: str):
        """
        使用者選擇任意數量的選項，隨機回傳一個選項。
        """
        # 將用戶輸入的選項字串轉換為列表
        options = choices.split(" ")

        if not options:
            await interaction.response.send_message("你要選什麼?")
            return

        # 隨機選擇一個選項
        chosen = random.choice(options)
        logger.info(f"[choose] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {choices}, bot 輸出: {chosen}")
        embed = discord.Embed(title="🎲 | 選擇器", description=f"> 輸入選項：{choices}", color=discord.Color.blue())
        embed.add_field(name="選擇結果", value=f"> {chosen}", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="擲一顆多面骰子，預設為6")
    @app_commands.describe(sides="骰子面數，最少為2，預設為6")
    async def dice(self, interaction: discord.Interaction, sides: int = 6):
        """
        擲一顆多面骰子，預設為6，最少為2。
        """
        sides = max(sides, 2)
        
        result = random.randint(1, sides)
        logger.info(f"[dice] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 擲骰子面數: {sides}, bot 輸出: {result}")
        await interaction.response.send_message(f"🎲 | 你擲出了一顆 {sides} 面骰，結果 {result}。")

    @app_commands.command(name="set_personality", description="設定頻道專屬的豆白個性")
    @app_commands.describe(personality="設定豆白個性 (頻道專屬)，可使用 `/check_personality` 查看當前設定")
    async def set_personality(self, interaction: discord.Interaction, personality: str):
        """
        設定頻道專屬的豆白個性。
        """
        filename = f"{interaction.channel.id}.json"
        data = {"personality": personality}
        
        FileManager.save_json_data(PERSONALITY_DIR, filename, data)

        logger.info(f"[個性] 伺服器 ID: {interaction.guild.id}, 頻道 ID: {interaction.channel.id}, 使用者名稱: {interaction.user.name}, 設定個性: {personality}")
        embed = discord.Embed(title="🐶 | 個性設定成功！", description=f"> 新個性：{personality}", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="check_personality", description="查看頻道專屬的豆白個性")
    async def check_personality(self, interaction: discord.Interaction):
        """
        查看頻道專屬的豆白個性。
        """
        filename = f"{interaction.channel.id}.json"
        data = FileManager.load_json_data(PERSONALITY_DIR, filename)

        if data and "personality" in data:
            description = f"> {data['personality']}"
        else:
            description = f"> 使用預設個性: {self.personality}"

        embed = discord.Embed(title="🐶 | 頻道專屬個性", description=description, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @commands.command(name="燒魚")
    async def sauyu(self, ctx: commands.Context):
        async with ctx.typing():
            await ctx.send("燒魚燒魚燒魚")
    
    @commands.command(name="關注度")
    async def attention_level(self, ctx: commands.Context):
        if not ctx.message.reference:
            await ctx.send("請回覆一則新聞來產生關注度！")
            return
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        content = replied_message.content
        
        async with ctx.typing():
            level = self.llm.get_attention_level(content)
            logger.info(f"[關注度] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {content}, bot 輸出: {level}")
            await ctx.send(f"本新聞關注度為 {level}！")
    
    @commands.command(name="抽籤")
    async def draw_omikuji(self, ctx: commands.Context):
        """
        抽籤功能。
        """
        omikuji_images = list(OMIKUJI_DIR.glob("*.png")) + list(OMIKUJI_DIR.glob("*.jpg"))
        if not omikuji_images:
            await ctx.send("目前沒有可用的籤語圖片！")
            return

        # 隨機選擇一個籤語圖片
        selected_image = random.choice(omikuji_images)
        await ctx.send(file=discord.File(selected_image))


class UltimateNumberGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target = None
        self.lower_bound = None
        self.upper_bound = None
        self.game_active = False
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @commands.command(name="終極密碼")
    async def start_game(self, ctx: commands.Context):
        async with ctx.typing():
            if self.game_active:
                await ctx.send("遊戲已經在進行中！請先完成當前的遊戲。")
                return
            
            self.target = random.randint(1, 100)
            self.lower_bound = 1
            self.upper_bound = 100
            self.game_active = True
            await ctx.send("🎲 | 終極密碼遊戲開始！\n範圍：1 ~ 100\n請輸入 `豆白 guess <數字>` 來猜數字")

    @commands.command(name="guess")
    async def guess(self, ctx: commands.Context, number: int):
        async with ctx.typing():
            if not self.game_active:
                await ctx.send("目前沒有進行中的遊戲，請輸入 `豆白 終極密碼` 來開始一場遊戲！")
                return
            
            if number < self.lower_bound or number > self.upper_bound:
                await ctx.send(f"⚠️ | 無效的猜測！請輸入 {self.lower_bound} ~ {self.upper_bound} 之間的數字。")
                return

            if number == self.target:
                await ctx.send(f"🎉 | 恭喜 {ctx.author.mention} 猜中了！答案是 {self.target}！\n遊戲結束！")
                self.game_active = False
            elif number < self.target:
                self.lower_bound = number + 1
                await ctx.send(f"🔽 | 太小了！新的範圍是 {self.lower_bound} ~ {self.upper_bound}。")
            else:
                self.upper_bound = number - 1
                await ctx.send(f"🔼 | 太大了！新的範圍是 {self.lower_bound} ~ {self.upper_bound}。")

    @commands.command(name="endgame")
    async def end_game(self, ctx: commands.Context):
        async with ctx.typing():
            if not self.game_active:
                await ctx.send("目前沒有進行中的遊戲！")
                return
            
            await ctx.send(f"⚠️ | 遊戲已結束！正確答案是 {self.target}。\n下次再來玩吧！")
            self.game_active = False

class SeaTurtleGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.llm: LLMService = bot.get_cog('LLMService')
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="soup", description="海龜湯題目產生器")
    @app_commands.describe(directions="設定出題方向")
    async def seaturtle_game(self, interaction: discord.Interaction, directions: str):
        """
        生成海龜湯題目，根據使用者指定的多個方向。
        使用方式: /soup 選擇多個出題方向
        """
        await interaction.response.defer()  # 延遲回應以避免超時
        if not directions:
            await interaction.followup.send("請至少提供一個出題方向，如：懸疑、恐怖、獵奇")
            return

        direction_str = directions.replace(" ", "、")

        try:
            # 使用 LLMCommands 取得題目與解答
            result = self.llm.get_seaturtle_question(direction_str)
            logger.info(f"[海龜湯] 伺服器 ID: {interaction.guild_id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {direction_str}, bot 輸出: \n{result}")

            if "題目:" in result and "解答:" in result:
                parts = result.split("解答:")
                question = parts[0].replace("題目:", "").strip()
                answer = parts[1].strip()

                # 輸出題目與暴雷內容的解答
                embed = discord.Embed(title="海龜湯題目", description=question, color=discord.Color.blue())
                await interaction.followup.send(embed=embed)

                spoiler_text = f"||{answer}||"  # 暴雷內容
                await interaction.followup.send(f"解答（點擊顯示）：\n{spoiler_text}")
            else:
                await interaction.followup.send("生成題目時發生錯誤，請稍後再試。")

        except Exception as e:
            logger.error(f"[海龜湯] 發生錯誤：{e}")
            await interaction.followup.send(f"發生錯誤")


async def setup(bot: commands.Bot):
    await bot.add_cog(Feature(bot))
    await bot.add_cog(UltimateNumberGame(bot))
    await bot.add_cog(SeaTurtleGame(bot))
    