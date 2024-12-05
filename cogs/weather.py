import os
import json
import discord
import requests
from loguru import logger
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(override=True)
weather_api_key = os.getenv('WEATHER_API_KEY')

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def normalize_location_name(location_name):
        """
        將地名正規化，解決「台」和「臺」的不同寫法問題。
        """
        replacements = {
            "台北市": "臺北市",
            "台中市": "臺中市",
            "台南市": "臺南市",
            "台東縣": "臺東縣"
        }
        return replacements.get(location_name, location_name)

    @commands.command(name="天氣")
    async def get_weather(self, ctx, location_name: str):
        async with ctx.typing():
            normalized_name = self.normalize_location_name(location_name)
            # API 設定
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
            params = {
                "Authorization": weather_api_key,
                "locationName": normalized_name,
            }

            # 呼叫 API 並處理回應
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = json.loads(response.text)
                try:
                    location = data["records"]["location"][0]["locationName"]  # 地點
                    weather_elements = data["records"]["location"][0]["weatherElement"]
                    start_time = weather_elements[0]["time"][0]["startTime"]  # 開始時間
                    end_time = weather_elements[0]["time"][0]["endTime"]  # 結束時間
                    weather_state = weather_elements[0]["time"][0]["parameter"]["parameterName"]  # 天氣狀態
                    rain_prob = weather_elements[1]["time"][0]["parameter"]["parameterName"]  # 降雨機率
                    min_tem = weather_elements[2]["time"][0]["parameter"]["parameterName"]  # 最低溫
                    comfort = weather_elements[3]["time"][0]["parameter"]["parameterName"]  # 舒適度
                    max_tem = weather_elements[4]["time"][0]["parameter"]["parameterName"]  # 最高溫

                    # 回傳天氣資訊給使用者
                    weather_message = (
                        f"🌍 **地點**: {location}\n"
                        f"⏰ **時間**: {start_time} ~ {end_time}\n"
                        f"🌤 **天氣狀態**: {weather_state}\n"
                        f"🌧 **降雨機率**: {rain_prob}%\n"
                        f"🌡 **氣溫**: {min_tem}°C ~ {max_tem}°C\n"
                        f"😌 **舒適度**: {comfort}"
                    )
                    await ctx.send(weather_message)
                except (KeyError, IndexError):
                    await ctx.send("⚠ 無法取得指定城市的天氣資訊，請確認名稱是否正確。")
            else:
                await ctx.send("⚠ 天氣服務目前不可用，請稍後再試！")

async def setup(bot):
    await bot.add_cog(Weather(bot))
    logger.info("天氣功能載入成功！")
