import os
import json
import random
import discord
import urllib.parse
from loguru import logger
from discord.ext import commands
from discord import app_commands

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MRT:
    def __init__(self, data_path=f'{PROJECT_ROOT}/assets/data/mrt_food'):
        self.data_path = data_path
        self.stations = self.load_stations()
        self.ramen_shops = self.load_ramen_shops()

        self.line_mapping = {
            "紅線": "red_line", "淡水信義線": "red_line",
            "藍線": "blue_line", "板南線": "blue_line",
            "黃線": "yellow_line", "環狀線": "yellow_line",
            "棕線": "brown_line", "文湖線": "brown_line",
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

    def recommend_ramen(self, station_name):
        """根據站名名稱推薦拉麵店"""
        for line, stations in self.stations.items():
            if station_name in stations:
                line = self.line_mapping.get(line)
                try:
                    ramen_list = self.ramen_shops[line].get(station_name)
                    if ramen_list:
                        ramen = random.choice(ramen_list)
                        query = urllib.parse.quote(f"{station_name} {ramen} 拉麵")
                        return f"{ramen}好吃\nhttps://www.google.com/search?q={query}"
                    else:
                        return f"{station_name}還沒有推薦的拉麵店。"
                except  Exception:
                    logger.error(f"查詢 {station_name} 時，發生錯誤: {Exception}")
                    return f"發生錯誤!?"
        return f"我只知道台北拉麵的資訊"


class MRTCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mrt = MRT()

    @app_commands.command(name="ramen", description="推薦台北捷運站附近的拉麵")
    @app_commands.describe(station="輸入捷運站名")
    async def ramen_select(self, interaction: discord.Interaction, station: str):
        """根據捷運線名稱隨機選擇一個站點並發送"""
        message = self.mrt.recommend_ramen(station)
        logger.info(f"[拉麵] 伺服器 ID: {interaction.guild.id}, 使用者名稱: {interaction.user.name}, 使用者輸入: {station}, bot 輸出: {message}")
        await interaction.response.send_message(message)
    
    @ramen_select.autocomplete("station")
    async def query_autocomplete(self, interaction: discord.Interaction, current: str):
        stations = {
        station
        for station_list in self.mrt.stations.values()
        for station in station_list if station.startswith(current)
        }
        return [app_commands.Choice(name=station, value=station) for station in list(stations)[:25]]


async def setup(bot):
    await bot.add_cog(MRTCog(bot))


if __name__ == "__main__":
    mrt = MRT()
    a = mrt.recommend_ramen("中和")
    print(a)
    
