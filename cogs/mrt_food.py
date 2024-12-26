import os
import json
import random
import urllib.parse
from loguru import logger
from discord.ext import commands

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MRT:
    def __init__(self, data_path=f'{PROJECT_ROOT}/assets/data/mrt_food'):
        self.data_path = data_path
        self.stations = self.load_stations()
        self.ramen_shops = self.load_ramen_shops()

        self.line_mapping = {
            "紅線": "red_line", "淡水信義線": "red_line",
            "藍線": "blue_line", "板南線": "blue_line",
            "黃線": "yellow_line", "文湖線": "yellow_line",
            "棕線": "brown_line", "新蘆線": "brown_line",
            "綠線": "green_line", "松山新店線": "green_line",
            "橘線": "orange_line", "中和新蘆線": "orange_line"
        }

    def load_stations(self):
        """載入捷運線對應的站資料"""
        stations_file = f"{self.data_path}/stations.json"
        with open(stations_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_ramen_shops(self):
        """載入每條捷運線的拉麵店推薦資料"""
        ramen_shops = {}
        lines = ['red_line', 'blue_line', 'yellow_line', 'brown_line', 'green_line', 'orange_line']
        for line in lines:
            ramen_file = f"{self.data_path}/{line}.json"
            with open(ramen_file, 'r', encoding='utf-8') as f:
                ramen_shops[line] = json.load(f)
        return ramen_shops

    def get_random_station(self, line):
        """隨機選擇某條捷運線上的一個站"""
        if line in self.stations:
            return f"{random.choice(self.stations[line])}"
        else:
            return "?"

    def recommend_ramen(self, station_name):
        """根據站名名稱推薦拉麵店"""
        for line, stations in self.stations.items():
            if station_name in stations:
                line = self.line_mapping.get(line)
                ramen_list = self.ramen_shops[line].get(station_name)
                if ramen_list:
                    ramen = random.choice(ramen_list)
                    query = urllib.parse.quote(f"{station_name} {ramen} 拉麵")
                    return f"{ramen}好吃\nhttps://www.google.com/search?q={query}"
                else:
                    return f"{station_name}還沒有推薦的拉麵店。"
        return f"我只知道台北拉麵的資訊"


# MRTCog 類別，包含相關命令
class MRTCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mrt = MRT()  # 創建 MRT 類別實例

    @commands.command(name="捷運")
    async def mrt_select(self, ctx, line: str):
        """根據捷運線名稱隨機選擇一個站點並發送"""
        async with ctx.typing():
            message = self.mrt.get_random_station(line)
            logger.info(f"[捷運] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {line}, bot 輸出: {message}")
            await ctx.send(message)

    @commands.command(name="拉麵")
    async def ramen_select(self, ctx, station: str):
        """根據捷運線名稱隨機選擇一個站點並發送"""
        async with ctx.typing():
            message = self.mrt.recommend_ramen(station)
            logger.info(f"[拉麵] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {station}, bot 輸出: {message}")
            await ctx.send(message)

# 註冊並加載 MRTCog
async def setup(bot):
    await bot.add_cog(MRTCog(bot))
    
